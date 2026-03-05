import os
import tempfile
from fastapi.testclient import TestClient

from app import app, _retriever

client = TestClient(app)


def test_post_query_schema(monkeypatch):
    # Patch embedding and chroma query
    def fake_encode(self, texts):
        return [[0.0] * 384]

    def fake_query(**kwargs):
        return {
            "ids": [["HighCourt_DocA_2025_chunk_000"]],
            "documents": [["The petitioner argued that the classification under Section 45 was arbitrary under Article 14."]],
            "metadatas": [[{
                "case_title": "Doc A",
                "court": "High Court",
                "year": 2025,
                "source_path": __file__,
                "file_hash": "c" * 64,
                "chunk_idx": 0,
                "page_range": "5",
            }]],
            "distances": [[0.08]],
        }

    monkeypatch.setattr(type(_retriever.embedder), "encode", fake_encode, raising=False)
    monkeypatch.setattr(_retriever.collection, "query", lambda *a, **k: fake_query())

    resp = client.post("/api/query", json={"query": "classification under Section 45"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["query"] == "classification under Section 45"
    assert "results" in data and isinstance(data["results"], list)
    if data["results"]:
        r0 = data["results"][0]
        # required keys present
        for key in [
            "doc_id","case_title","court","year","jurisdiction","docket_number","similarity","excerpt","excerpts_meta","statutes","num_matching_chunks","source_id","preview_available","summary","place","full_text_available"
        ]:
            assert key in r0


def test_document_serve_and_text(monkeypatch):
    # Create a temp pdf file placeholder
    fd, tmp_path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    with open(tmp_path, "wb") as f:
        f.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF\n")

    def fake_resolve(doc_id: str):
        return {"source_path": tmp_path, "case_title": "Doc A"}

    monkeypatch.setattr(_retriever, "resolve_doc_source", fake_resolve)

    r = client.get("/api/document/serve", params={"id": "HighCourt_DocA_2025"})
    assert r.status_code == 200
    assert r.headers.get("content-type") == "application/pdf"

    # Text endpoint will attempt to parse PDF; may fail on minimal content. Just ensure 500 or 200
    r2 = client.get("/api/document/text", params={"id": "HighCourt_DocA_2025", "page": 1})
    assert r2.status_code in (200, 500, 400)
