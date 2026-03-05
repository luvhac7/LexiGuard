import os
from typing import Any, Dict

import requests
from flask import Flask, render_template_string
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
TOKEN = os.getenv("INDIANKANOON_TOKEN", "YOUR_API_TOKEN_HERE")
API_BASE = "https://api.indiankanoon.org"


BASE_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{{ title }}</title>
  <style>
    :root {
      --bg: #f7f8fa;
      --fg: #111827;
      --muted: #6b7280;
      --card: #ffffff;
      --border: #e5e7eb;
      --accent: #2563eb;
    }
    html, body {
      margin: 0;
      padding: 0;
      background: var(--bg);
      color: var(--fg);
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
        Ubuntu, Cantarell, 'Helvetica Neue', 'Noto Sans', Arial, 'Apple Color Emoji',
        'Segoe UI Emoji', 'Noto Color Emoji', sans-serif;
      line-height: 1.6;
    }
    .container {
      max-width: 900px;
      margin: 2rem auto;
      padding: 1.25rem;
    }
    .card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
      box-shadow: 0 1px 2px rgba(0,0,0,0.03);
      padding: 1.25rem 1.25rem 2rem;
    }
    h1 {
      font-size: 1.5rem;
      margin: 0 0 0.5rem;
    }
    .meta {
      color: var(--muted);
      font-size: 0.95rem;
      margin-bottom: 1rem;
    }
    .doc-html {
      margin-top: 1rem;
    }
    .error {
      color: #b91c1c;
      background: #fef2f2;
      border: 1px solid #fecaca;
      padding: 0.75rem 1rem;
      border-radius: 10px;
    }
    a { color: var(--accent); text-decoration: none; }
    a:hover { text-decoration: underline; }
    code { background: #f3f4f6; padding: 2px 6px; border-radius: 6px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="card">
      {{ content|safe }}
    </div>
  </div>
</body>
</html>
"""

DOC_BODY_TEMPLATE = """
  <h1>{{ data.title or 'Untitled' }}</h1>
  <div class="meta">
    <div><strong>Source:</strong> {{ data.docsource or '-' }}</div>
    <div><strong>Date:</strong> {{ data.date or '-' }}</div>
    <div><strong>Doc ID:</strong> {{ docid }}</div>
  </div>
  {% if data.doc %}
    <div class="doc-html">{{ data.doc | safe }}</div>
  {% else %}
    <div class="error">No document HTML found in response.</div>
  {% endif %}
"""


ERROR_BODY_TEMPLATE = """
  <h1>Error</h1>
  <div class="error">{{ message }}</div>
"""


@app.route("/view/<docid>")
def view_doc(docid: str):
    if not TOKEN or TOKEN == "YOUR_API_TOKEN_HERE":
        content = render_template_string(
            ERROR_BODY_TEMPLATE,
            message="API token not configured. Set INDIANKANOON_TOKEN in .env",
        )
        html = render_template_string(BASE_TEMPLATE, title="Error", content=content)
        return html, 500

    url = f"{API_BASE}/doc/{docid}/"
    headers = {
        "Authorization": f"Token {TOKEN}",
        "Accept": "application/json",
    }

    try:
        # API requires POST for /doc/ endpoint; GET returns 405
        # Separate connect/read timeouts for better UX under network hiccups
        res = requests.post(url, headers=headers, timeout=(10, 25))
    except requests.exceptions.RequestException as e:
        content = render_template_string(
            ERROR_BODY_TEMPLATE,
            message=f"Network error: {e}",
        )
        html = render_template_string(BASE_TEMPLATE, title="Network error", content=content)
        return html, 502

    if res.status_code != 200:
        detail = res.text.strip()
        if len(detail) > 500:
            detail = detail[:500] + "..."
        content = render_template_string(
            ERROR_BODY_TEMPLATE,
            message=f"Error {res.status_code} from API: {detail}",
        )
        html = render_template_string(BASE_TEMPLATE, title="Error", content=content)
        return html, res.status_code

    try:
        data: Dict[str, Any] = res.json()
    except ValueError:
        content = render_template_string(
            ERROR_BODY_TEMPLATE,
            message="Failed to parse JSON from API.",
        )
        html = render_template_string(BASE_TEMPLATE, title="Error", content=content)
        return html, 500

    content = render_template_string(
        DOC_BODY_TEMPLATE,
        data=data,
        docid=docid,
    )
    html = render_template_string(BASE_TEMPLATE, title=data.get("title") or "Document", content=content)
    return html


if __name__ == "__main__":
    example = os.getenv("EXAMPLE_DOCID", "143202244")
    print(f"\n🚀 Open http://localhost:5000/view/{example}\n")
    app.run(host="127.0.0.1", port=5000, debug=True)
