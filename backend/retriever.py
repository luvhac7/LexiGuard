import os
import time
import logging
import re
from typing import Any, Dict, List, Tuple, Optional

import numpy as np

from embedder import SentenceEmbedder
from chroma_client import get_collection

logger = logging.getLogger(__name__)

# Config via env
CANDIDATE_SIZE = int(os.getenv("CANDIDATE_SIZE", "30"))
DEFAULT_K = int(os.getenv("DEFAULT_K", "5"))


def _clean_query(q: str) -> str:
    if not isinstance(q, str):
        return ""
    # Normalize whitespace and control chars; preserve case as indexing didn't lowercase
    q = q.replace("\r\n", "\n").replace("\r", "\n")
    q = re.sub(r"[\x00-\x1F\x7F]", " ", q)
    q = re.sub(r"\s+", " ", q).strip()
    return q


def _build_where(filters: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not filters:
        return None
    where: Dict[str, Any] = {}
    # Exact matches
    for key in ["court", "jurisdiction", "docket_number"]:
        if key in filters and filters[key] not in (None, ""):
            where[key] = filters[key]
    # Year range
    year_from = filters.get("year_from")
    year_to = filters.get("year_to")
    if year_from is not None or year_to is not None:
        yr: Dict[str, Any] = {}
        if year_from is not None:
            yr["$gte"] = int(year_from)
        if year_to is not None:
            yr["$lte"] = int(year_to)
        where["year"] = yr
    return where or None


def _and_where(criteria: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Build a Chroma where with $and over simple equality clauses, skipping null/empty values."""
    clauses = []
    for k, v in criteria.items():
        if v is None or v == "":
            continue
        clauses.append({k: v})
    if not clauses:
        return None
    if len(clauses) == 1:
        return clauses[0]
    return {"$and": clauses}


def _similarity_from_dist(distances: List[float]) -> List[float]:
    # Chroma with cosine returns distances; similarity = 1 - distance
    sims = [1.0 - float(d) for d in distances]
    # Clip to [0,1]
    return [max(0.0, min(1.0, s)) for s in sims]


def _doc_id_from_meta(meta: Dict[str, Any]) -> str:
    court = meta.get("court", "Court").replace(" ", "")
    src = meta.get("source_path", "")
    stem = os.path.splitext(os.path.basename(src))[0]
    year = meta.get("year")
    if isinstance(year, str) and year.isdigit():
        year = int(year)
    if not isinstance(year, int):
        year = -1
    return f"{court}_{stem}_{year}"


def _source_id_from_meta(meta: Dict[str, Any]) -> str:
    fh = meta.get("file_hash", "")
    return f"file_{fh[:8]}" if fh else "file_unknown"


STATUTE_PATTERNS = [
    r"\bSection\s+\d+[A-Za-z\-]*\b",
    r"\bSec\.\s*\d+[A-Za-z\-]*\b",
    r"\bArticle\s+\d+[A-Za-z\-]*\b",
    r"\(\d{4}\)\s*\d+\s*SCC\s*\d+",
    r"\b[A-Z][A-Za-z]+\s+vs\.?\s+[A-Z][A-Za-z]+\b",
]


def _extract_statutes(text: str) -> List[str]:
    tags: List[str] = []
    for pat in STATUTE_PATTERNS:
        for m in re.findall(pat, text or ""):
            if m not in tags:
                tags.append(m)
    return tags


def reranker_hook(query: str, docs: List[Dict[str, Any]], top_r: int = 20) -> List[Dict[str, Any]]:
    # Placeholder for future cross-encoder / Gemini re-rank. Do not modify order now.
    return docs


class Retriever:
    def __init__(self):
        # Lazy init of embedder to reduce cold-start and ease testing
        self.embedder: Optional[SentenceEmbedder] = None
        self.collection = get_collection()

    def query(self, query: str, filters: Optional[Dict[str, Any]] = None, k: Optional[int] = None) -> Tuple[Dict[str, Any], int, int, int]:
        t0 = time.time()
        q = _clean_query(query)
        try:
            if self.embedder is None:
                self.embedder = SentenceEmbedder()
            q_emb = np.array(self.embedder.encode([q])[0], dtype=np.float32)
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            raise RuntimeError("embedding_failed")
        t1 = time.time()

        where = _build_where(filters)
        n_results = int(os.getenv("CANDIDATE_SIZE", str(CANDIDATE_SIZE)))
        try:
            res = self.collection.query(
                query_embeddings=[q_emb.tolist()],
                n_results=n_results,
                where=where,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as e:
            logger.exception("Chroma query failed")
            raise RuntimeError("chroma_query_failed") from e
        t2 = time.time()

        ids = res.get("ids", [[]])[0]
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        dists = res.get("distances", [[]])[0]
        sims = _similarity_from_dist(dists) if dists else [0.0] * len(ids)

        # Build chunk hits
        chunk_hits: List[Dict[str, Any]] = []
        for cid, doc, meta, score in zip(ids, docs, metas, sims):
            if not meta:
                meta = {}
            chunk_hits.append({
                "chunk_id": cid,
                "text": doc,
                "score": float(score),
                "meta": meta,
            })

        # Aggregate by document
        agg_t0 = time.time()
        by_doc: Dict[str, Dict[str, Any]] = {}
        for ch in chunk_hits:
            meta = ch["meta"]
            doc_id = _doc_id_from_meta(meta)
            if doc_id not in by_doc:
                by_doc[doc_id] = {
                    "doc_id": doc_id,
                    "case_title": meta.get("case_title", ""),
                    "court": meta.get("court", ""),
                    "year": meta.get("year", None),
                    "source_path": meta.get("source_path", ""),
                    "file_hash": meta.get("file_hash", ""),
                    "chunks": [],
                }
            by_doc[doc_id]["chunks"].append(ch)

        aggregated: List[Dict[str, Any]] = []
        for doc_id, info in by_doc.items():
            scores = sorted([c["score"] for c in info["chunks"]], reverse=True)
            if not scores:
                continue
            max_score = scores[0]
            top3 = scores[:3]
            avg_top3 = sum(top3) / len(top3)
            combined = 0.6 * max_score + 0.4 * avg_top3

            # Excerpts: primary and secondary
            top_chunks = sorted(info["chunks"], key=lambda x: x["score"], reverse=True)[:2]
            excerpts_meta = []
            for tc in top_chunks:
                pr = tc["meta"].get("page_range")
                page_val: Optional[int]
                if isinstance(pr, str) and pr.isdigit():
                    page_val = int(pr)
                else:
                    page_val = None
                excerpts_meta.append({
                    "chunk_id": tc["chunk_id"],
                    "page": page_val,
                    "score": round(float(tc["score"]), 4),
                })

            primary_excerpt_text = top_chunks[0]["text"] if top_chunks else ""
            statutes = _extract_statutes(primary_excerpt_text)

            aggregated.append({
                "doc_id": doc_id,
                "case_title": info.get("case_title", ""),
                "court": info.get("court", ""),
                "year": info.get("year", None),
                "similarity": max(0.0, min(1.0, float(combined))),
                "excerpt": primary_excerpt_text[:500],
                "excerpts_meta": excerpts_meta,
                "statutes": statutes,
                "num_matching_chunks": len(info["chunks"]),
                "source_id": _source_id_from_meta({"file_hash": info.get("file_hash", "")}),
                "preview_available": bool(os.path.exists(info.get("source_path", ""))),
                "summary": "",
                "place": "",
                "full_text_available": True,
                "_internal": {
                    "source_path": info.get("source_path", "")
                }
            })

        # Sort by combined score desc
        aggregated.sort(key=lambda x: x["similarity"], reverse=True)
        agg_t1 = time.time()

        # Optional reranker hook (no-op now)
        aggregated = reranker_hook(q, aggregated, top_r=20)

        top_k = int(k or DEFAULT_K)
        results = aggregated[:top_k]

        timing = {
            "embed_ms": int((t1 - t0) * 1000),
            "chroma_ms": int((t2 - t1) * 1000),
            "aggregation_ms": int((agg_t1 - agg_t0) * 1000),
        }
        total_ms = int((time.time() - t0) * 1000)

        payload = {
            "query": query,
            "k": top_k,
            "results": [
                {
                    "doc_id": r["doc_id"],
                    "case_title": r["case_title"],
                    "court": r["court"],
                    "year": r["year"],
                    "jurisdiction": None,
                    "docket_number": None,
                    "similarity": round(float(r["similarity"]), 4),
                    "excerpt": r["excerpt"],
                    "excerpts_meta": r["excerpts_meta"],
                    "statutes": r["statutes"],
                    "num_matching_chunks": r["num_matching_chunks"],
                    "source_id": r["source_id"],
                    "preview_available": r["preview_available"],
                    "summary": r["summary"],
                    "place": r["place"],
                    "full_text_available": r["full_text_available"],
                }
                for r in results
            ],
            "timing": {**timing, "total_ms": total_ms},
        }

        return payload, timing["embed_ms"], timing["chroma_ms"], timing["aggregation_ms"]

    def resolve_doc_source(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Resolve doc_id to source_path via metadata in Chroma by case_title/court/year."""
        def pick_meta(res: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            metas = res.get("metadatas") or []
            if isinstance(metas, list) and metas:
                first = metas[0]
                if isinstance(first, dict):
                    return first
                if isinstance(first, list) and first:
                    inner = first[0]
                    if isinstance(inner, dict):
                        return inner
            return None

        try:
            parts = doc_id.rsplit("_", 1)
            if len(parts) != 2:
                return None
            prefix, year_str = parts
            try:
                year = int(year_str)
            except Exception:
                year = None
            court, _, stem = prefix.partition("_")
            # Normalize court token: 'HighCourt' -> 'High Court'
            if "Court" in court and " " not in court:
                court = court.replace("Court", " Court")
            # stem may still contain underscores from case name
            case_title = stem.replace("_", " ").title()
            stem_basename = stem  # used for filename matching

            # 0) Fast path: if DOCS_ROOT is set, check for a file named exactly like the stem
            docs_root = os.getenv("DOCS_ROOT")
            if docs_root and os.path.isdir(docs_root):
                for ext in (".PDF", ".pdf"):
                    candidate = os.path.join(docs_root, stem_basename + ext)
                    if os.path.exists(candidate):
                        return {"source_path": candidate, "case_title": case_title}

            # 1) Exact triple match (use $and for multiple fields)
            where = _and_where({"court": court, "year": year, "case_title": case_title})
            res = self.collection.get(where=where, include=["metadatas"], limit=1)
            meta = pick_meta(res)
            if meta and meta.get("source_path") and os.path.exists(meta.get("source_path")):
                return {"source_path": meta.get("source_path"), "case_title": meta.get("case_title")}

            # 2) court + case_title (no year)
            res2 = self.collection.get(where=_and_where({"court": court, "case_title": case_title}), include=["metadatas"], limit=1)
            meta2 = pick_meta(res2)
            if meta2 and meta2.get("source_path") and os.path.exists(meta2.get("source_path")):
                return {"source_path": meta2.get("source_path"), "case_title": meta2.get("case_title")}

            # 3) court + year (any title)
            res3 = self.collection.get(where=_and_where({"court": court, "year": year}), include=["metadatas"], limit=1)
            meta3 = pick_meta(res3)
            if meta3 and meta3.get("source_path") and os.path.exists(meta3.get("source_path")):
                return {"source_path": meta3.get("source_path"), "case_title": meta3.get("case_title")}

            # 4) Filesystem fallback: search DOCS_ROOT/DEFAULT_INGEST_PATH for a matching PDF basename
            import os
            roots = []
            for env_k in ("DOCS_ROOT", "DEFAULT_INGEST_PATH"):
                v = os.getenv(env_k)
                if v and os.path.isdir(v):
                    roots.append(v)
            # Also check a common docs folder under backend if present
            backend_dir = os.path.dirname(__file__)
            for name in ("docs", "pdfs", "data", ".."):
                p = os.path.abspath(os.path.join(backend_dir, name))
                if os.path.isdir(p):
                    roots.append(p)
            seen = set()
            for root in roots:
                if root in seen:
                    continue
                seen.add(root)
                for r, _dirs, files in os.walk(root):
                    for f in files:
                        if not f.lower().endswith('.pdf'):
                            continue
                        base = os.path.splitext(f)[0]
                        if base == stem_basename:
                            cand = os.path.join(r, f)
                            if os.path.exists(cand):
                                return {"source_path": cand, "case_title": case_title}
        except Exception as e:
            logger.warning(f"resolve_doc_source failed: {e}")
        return None
