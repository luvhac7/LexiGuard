# LexiGuard

**AI-Powered Legal Analytics & Decision Intelligence Platform**

A data-driven analytics platform for Indian judicial decisions using SQL-based data pipelines, AI-powered text analysis, and interactive BI dashboards.

![Analytics Dashboard Overview](https://github.com/user-attachments/assets/6e8af7f4-c02a-4a15-a3d5-1ef5caa99647)

## Architecture (BIE Style)

```
Legal Documents (PDF)
        │
        ▼
ETL Pipeline (Python + PyMuPDF)
        │
        ▼
Structured Data Warehouse (PostgreSQL)
        │
        ├── Vector Search (ChromaDB)
        │
        ▼
Analytics Layer (SQL Queries)
        │
        ▼
BI Dashboard (Power BI / React Analytics)
```

## Project Structure

```
LexiGuard/
├── backend/
│   ├── app.py                 # FastAPI entry point
│   ├── ingest.py              # ETL pipeline orchestration
│   ├── cleaner.py             # Text normalization
│   ├── extractor.py           # PDF → text extraction (PyMuPDF)
│   ├── embedder.py            # Sentence embedding (InLegalBERT)
│   ├── chunker.py             # Document chunking
│   ├── chroma_client.py       # ChromaDB vector store
│   ├── retriever.py           # RAG retrieval engine
│   ├── case_comparer.py       # Juris-AI case comparison
│   ├── similarity_pipeline.py # Semantic similarity scoring
│   ├── warehouse.py           # PostgreSQL data warehouse
│   ├── db_config.py           # Database configuration
│   ├── setup_db.py            # One-time DB setup script
│   ├── export_for_powerbi.py  # CSV export for Power BI
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AnalyticsDashboard.jsx  # Power BI-style dashboard
│   │   │   ├── BiasDetectionDisplay.jsx
│   │   │   ├── CaseComparisonDisplay.jsx
│   │   │   └── ...
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── Analytics.jsx
│   │   │   ├── LegalKnowledgeAgent.jsx
│   │   │   └── ...
│   │   ├── App.jsx
│   │   └── index.css
│   └── package.json
├── powerbi/
│   ├── LexiGuard_Dashboard.pbids  # Auto-connect Power BI file
│   ├── queries.sql                # SQL analytics queries
│   ├── power_queries.m            # Power Query M code
│   ├── dax_measures.dax           # DAX measures for KPIs
│   ├── POWERBI_SETUP.md           # This documentation
│   └── data/                      # CSV exports
│       ├── cases.csv
│       ├── bias_metrics.csv
│       ├── case_similarity.csv
│       ├── judge_workload.csv
│       ├── domain_trends.csv
│       ├── high_bias_cases.csv
│       ├── similar_precedents.csv
│       └── domain_bias.csv
└── .env                       # Environment variables
```

## Data Warehouse Schema

### Table: `cases`
| Column | Type | Description |
|--------|------|-------------|
| case_id | SERIAL | Primary key |
| case_name | TEXT | Full case title |
| court | TEXT | Court of origin |
| judge | TEXT | Presiding judge |
| decision_date | DATE | Date of judgment |
| legal_domain | TEXT | Legal practice area |

### Table: `bias_metrics`
| Column | Type | Description |
|--------|------|-------------|
| case_id | INTEGER | FK → cases |
| gender_bias_score | REAL | 0.0–1.0 |
| power_dynamics_score | REAL | 0.0–1.0 |
| emotional_language_score | REAL | 0.0–1.0 |

### Table: `case_similarity`
| Column | Type | Description |
|--------|------|-------------|
| case1 | INTEGER | FK → cases |
| case2 | INTEGER | FK → cases |
| similarity_score | REAL | 0.0–1.0 |

## SQL Analytics Examples

```sql
-- 1. Judge workload analysis
SELECT judge, COUNT(case_id) AS total_cases
FROM cases GROUP BY judge ORDER BY total_cases DESC;

-- 2. Legal domain trends
SELECT legal_domain, COUNT(*) AS case_volume
FROM cases GROUP BY legal_domain ORDER BY case_volume DESC;

-- 3. High bias judgments
SELECT c.case_name, b.gender_bias_score
FROM cases c JOIN bias_metrics b ON c.case_id = b.case_id
WHERE b.gender_bias_score > 0.7;

-- 4. Similar precedent discovery
SELECT c1.case_name, c2.case_name, cs.similarity_score
FROM case_similarity cs
JOIN cases c1 ON cs.case1 = c1.case_id
JOIN cases c2 ON cs.case2 = c2.case_id
ORDER BY cs.similarity_score DESC LIMIT 10;
```

---

# Power BI Desktop — LexiGuard Report Setup

Build a 4-page Power BI dashboard from the LexiGuard PostgreSQL data warehouse.

## Quick Start (2 Options)

### Option A: Direct PostgreSQL Connection (Recommended)
1. Double-click **`LexiGuard_Dashboard.pbids`** — Power BI opens auto-connected
2. Enter credentials: User `postgres`, Password `postgres`
3. Select all 3 tables → **Load**

### Option B: CSV Import (No Npgsql Needed)
1. Run the export script:
   ```bash
   cd backend
   python export_for_powerbi.py
   ```
2. Open Power BI Desktop → **Get Data** → **Text/CSV**
3. Import each file from `powerbi/data/`:
   - `cases.csv`, `bias_metrics.csv`, `case_similarity.csv`
   - `judge_workload.csv`, `domain_trends.csv`, `high_bias_cases.csv`
   - `similar_precedents.csv`, `domain_bias.csv`

---

## Files in This Folder

| File | Purpose |
|------|---------|
| `LexiGuard_Dashboard.pbids` | Auto-opens Power BI connected to PostgreSQL |
| `queries.sql` | 9 SQL analytics queries |
| `power_queries.m` | Power Query M code for Advanced Editor |
| `dax_measures.dax` | 20+ DAX measures for KPIs |
| `data/*.csv` | Pre-exported data files for CSV import |

---

## Building Report Pages

After loading data, create 4 report pages:

### Page 1: Legal Case Trends

![Legal Case Trends - Dashboard Overview](https://github.com/user-attachments/assets/6e8af7f4-c02a-4a15-a3d5-1ef5caa99647)

| Visual | Fields |
|--------|--------|
| **KPI Cards** | Total Cases (30), Total Queries (180), Avg Response (430ms), Embeddings (664), Similarity Pairs (110), Bias Records (30) |
| **Area Chart** | X: `decision_date` (Month) · Y: Count of `case_id` |
| **Donut Chart** | Legend: `legal_domain` · Values: Count of `case_id` |
| **Bar Chart** | Axis: `court` · Values: Count of `case_id` |

### Page 2: Judicial Analytics

![Judicial Analytics](https://github.com/user-attachments/assets/0e797ab0-255d-43f1-9955-b6d1d97c2ac6)

| Visual | Fields |
|--------|--------|
| **Bar Chart** | Axis: `judge` · Values: Count of `case_id` · Sort: descending |
| **Query Table** | Top legal query patterns with category badges (Criminal, Civil, Tax, Constitutional, Commercial) and hit counts |
| **KPI Cards** | Judge workload distribution metrics |

### Page 3: Bias Detection Analytics

![Bias Detection Analytics](https://github.com/user-attachments/assets/ce4255d2-1f56-4de4-a22e-8e7ed4091df7)

| Visual | Fields |
|--------|--------|
| **Radar Chart** | Average bias across dimensions (Gender, Power Dynamics, Emotional Language) |
| **Grouped Bar Chart** | Axis: `legal_domain` · Values: Avg of 3 bias scores (Emotion-purple, Gender-rose, Power-amber) |
| **High Bias Cards** | Cases with gender bias > 70% (e.g., Meena Kumari vs Suresh Kumar: 86%, Geeta Devi vs Husband & In-Laws: 84%) |

**Interactive Hover State:**

![Bias Detection Hover](https://github.com/user-attachments/assets/19484812-1967-4045-b91b-e22e7ace89ad)

### Page 4: Case Similarity Network

![Case Similarity Network - Table View](https://github.com/user-attachments/assets/714977cb-548d-4e4d-b069-725f581b83aa)

| Visual | Fields |
|--------|--------|
| **Similarity Table** | Case A, Case B, Similarity Score with color-coded progress bars (Green >70%, Orange 40-70%, Red <40%) |
| **Scatter Plot** | Pairwise case similarity scores distribution |

**Similarity Distribution Detail:**

![Case Similarity Distribution](https://github.com/user-attachments/assets/68fb5714-5885-4f94-b2d2-cdd8654a2c47)

| Visual | Fields |
|--------|--------|
| **Scatter/Bubble Chart** | X: Case pairs · Y: Similarity % · Color: Similarity Level (High/Medium/Low) · Tooltip: Case Pair details |

---

## Adding DAX Measures

1. Go to **Modeling** → **New Measure**
2. Copy each measure from `dax_measures.dax`
3. Key measures to add first:
   - `Total Cases`, `Avg Gender Bias`, `High Bias Cases`, `High Bias %`

---

## Dark Theme (Matching LexiGuard UI)

1. **View** → **Themes** → **Customize current theme**
2. Background: `#0a0e1a`
3. Foreground text: `#e2e8f0`
4. Accent 1: `#6366f1` (indigo)
5. Accent 2: `#a855f7` (purple)
6. Accent 3: `#f43f5e` (rose)

---

## Refreshing Data

- **Manual**: Click **Refresh** button in Power BI
- **If using CSV**: Re-run `python export_for_powerbi.py`, then refresh
- **If using PostgreSQL**: Data refreshes directly from the database

---

## Quick Start

### 1. Install PostgreSQL

Download from [postgresql.org](https://www.postgresql.org/download/) and install with default settings (user: `postgres`, password: `postgres`).

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
python setup_db.py          # Creates lexiguard database
uvicorn app:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 4. Power BI (Optional)

See [`powerbi/POWERBI_SETUP.md`](powerbi/POWERBI_SETUP.md) for connecting Power BI Desktop to the PostgreSQL warehouse.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python, FastAPI, PyMuPDF, LangChain |
| **Data Warehouse** | PostgreSQL |
| **Vector Store** | ChromaDB |
| **Embeddings** | InLegalBERT, Sentence-Transformers |
| **AI** | Google Gemini 2.5 Flash |
| **Frontend** | React 18, Vite, Tailwind CSS, Recharts |
| **Visualization** | Power BI Desktop, React Analytics Dashboard |

## Dashboard Panels

1. **Legal Case Trends** — Cases/year, domain distribution, court-wise volume
2. **Judicial Analytics** — Judge workload, decision patterns, query heatmap
3. **Bias Detection** — Gender bias, emotional language, sentencing disparity
4. **Case Similarity** — Similarity heatmap, precedent clusters

## Skills Demonstrated

| Skill | Demonstrated |
|-------|-------------|
| SQL | Analytical queries on PostgreSQL |
| Data Engineering | ETL pipeline (PDF → PostgreSQL) |
| Data Modeling | Relational schema design |
| Data Visualization | Power BI + React dashboards |
| Large Data Processing | Document analytics at scale |
| Decision Intelligence | Trend analysis & bias detection |

## License

© 2025 LexiGuard — Legal Analytics & Decision Intelligence
