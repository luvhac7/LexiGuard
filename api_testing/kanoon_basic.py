import os
import sys
import json
import re
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv


def _print_hr(char: str = "-", width: int = 60) -> None:
    """Print a horizontal rule for nicer terminal formatting."""
    print(char * width)


def search_kanoon_basic(query: str, token: str, fromdate: str = "01-01-2024", page: int = 0) -> bool:
    """
    Fetch top relevant documents for the given query using Indian Kanoon Search API.

    - Sends POST request with only `formInput` and `pagenum=0`.
    - Prints the top 5 documents with: title, tid, source, and headline.
    - Handles HTTP and network errors gracefully.

    Returns True if the call succeeded (HTTP 200 and parsed), else False.
    """
    url = "https://api.indiankanoon.org/search/"
    params = {"formInput": query, "pagenum": int(page or 0), "fromdate": fromdate}
    headers = {
        "Authorization": f"Token {token}",
        "Accept": "application/json",
    }

    try:
        # API requires POST for /search/; GET returns 405.
        resp = requests.post(url, headers=headers, data=params, timeout=15)
    except requests.exceptions.RequestException as e:
        _print_hr("=")
        print("Request failed:")
        print(f"  {e}")
        _print_hr("=")
        return False

    if resp.status_code != 200:
        _print_hr("=")
        print(f"Error {resp.status_code} from API")
        # Show a short snippet of the response text for debugging.
        snippet = (resp.text or "").strip().replace("\n", " ")
        if len(snippet) > 300:
            snippet = snippet[:300] + "..."
        if snippet:
            print(f"Details: {snippet}")
        _print_hr("=")
        return False

    try:
        payload: Dict[str, Any] = resp.json()
    except ValueError:
        _print_hr("=")
        print("Failed to parse JSON response from API.")
        _print_hr("=")
        return False

    docs: List[Dict[str, Any]] = payload.get("docs", []) or []
    total_found = payload.get("found", 0)

    # Save full JSON payload to outputs/ with a timestamped filename.
    try:
        out_dir = Path("outputs")
        out_dir.mkdir(parents=True, exist_ok=True)
        slug = re.sub(r"[^a-zA-Z0-9]+", "_", query).strip("_").lower() or "query"
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = out_dir / f"search_{ts}_{slug}.json"
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except Exception as e:
        _print_hr("=")
        print(f"Warning: failed to save JSON output: {e}")
        _print_hr("=")

    _print_hr("=")
    print(f"Found {total_found} results for: '{query}'")
    _print_hr("=")
    try:
        print(f"Saved full JSON to: {out_path}")
    except NameError:
        # out_path not defined if saving failed
        pass

    if not docs:
        print("No documents returned.")
        _print_hr("=")
        return True

    # Print top 5 docs with clean formatting.
    for i, doc in enumerate(docs[:5], start=1):
        title = (doc.get("title") or "Untitled").strip()
        tid = doc.get("tid", "-")
        source = doc.get("docsource", "-")
        headline = (doc.get("headline") or "").strip()

        print(f"{i}. {title}")
        print(f"   Doc ID: {tid}")
        print(f"   Source: {source}")
        if headline:
            wrapped = textwrap.fill(headline, width=80, initial_indent="   Snippet: ", subsequent_indent="            ")
            print(wrapped)
        _print_hr()

    return True


if __name__ == "__main__":
    # Read token from env if available; otherwise, edit the placeholder below.
    load_dotenv()  # load variables from .env if present
    TOKEN = os.getenv("INDIANKANOON_TOKEN", "YOUR_API_TOKEN_HERE")
    QUERY = "Supreme Court case discussing Protocol to Prevent Trafficking in Persons"

    if not TOKEN or TOKEN == "YOUR_API_TOKEN_HERE":
        print("Please set your Indian Kanoon API token.")
        print("- Option 1: export INDIANKANOON_TOKEN=\"<YOUR_TOKEN>\"")
        print("- Option 2: edit TOKEN in kanoon_basic.py")
        sys.exit(1)

    ok = search_kanoon_basic(QUERY, TOKEN)
    sys.exit(0 if ok else 2)