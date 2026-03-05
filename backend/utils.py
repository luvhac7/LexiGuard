import hashlib
import json
import os
import time
from datetime import datetime
from typing import Dict, Any, Tuple

MANIFEST_PATH = os.path.join(os.path.dirname(__file__), 'manifest.json')
INGEST_REPORT_PATH = os.path.join(os.path.dirname(__file__), 'ingest_report.json')
LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')

os.makedirs(LOG_DIR, exist_ok=True)


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8', errors='ignore')).hexdigest()


def load_manifest() -> Dict[str, Any]:
    if not os.path.exists(MANIFEST_PATH):
        return {}
    try:
        with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def save_manifest(manifest: Dict[str, Any]) -> None:
    with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


def append_ingest_report(entry: Dict[str, Any]) -> None:
    report = []
    if os.path.exists(INGEST_REPORT_PATH):
        try:
            with open(INGEST_REPORT_PATH, 'r', encoding='utf-8') as f:
                report = json.load(f)
        except Exception:
            report = []
    report.append(entry)
    with open(INGEST_REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)


def utc_now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat()


def timeit() -> Tuple[Any, Any]:
    start = time.time()
    def end():
        return time.time() - start
    return start, end
