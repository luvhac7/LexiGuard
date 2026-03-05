# LexiGuard

AI-Powered Legal Research & Analysis Platform

A comprehensive full-stack application for legal research, case analysis, and AI-assisted legal consultation.

## Project Structure

```
PROJECT-1/
├── frontend/          # React frontend application
│   ├── src/
│   │   ├── components/
│   │   │   ├── modules/    # Feature modules (Search, Compare, etc.)
│   │   │   ├── Header.jsx
│   │   │   ├── Navigation.jsx
│   │   │   ├── SettingsPanel.jsx
│   │   │   └── Footer.jsx
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── public/
│   └── package.json
│
└── backend/           # Python backend API
    ├── main.py
    ├── main_integrated.py
    ├── agents.py
    └── requirement.txt
```

## Features

- **Case Search**: Intelligent search through legal database
- **Compare Cases**: Comparative analysis of legal judgments
- **Contradiction Detection**: Identify conflicting rulings
- **Legal Reasoning**: AI-powered explainable legal analysis
- **Interactive Assistant**: Chat-based legal consultation
- **Document Upload**: Upload and index legal documents

## Quick Start

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:3000`

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirement.txt
python main.py
```

Backend runs on `http://localhost:8000`

## Tech Stack

### Frontend
- React 18
- Vite
- Tailwind CSS
- Lucide React
- Axios

### Backend
- Python
- (Add your backend framework here - FastAPI, Flask, etc.)

## Development

See individual README files in `frontend/` and `backend/` directories for detailed setup and development instructions.

## License

© 2025 Intelligent Legal Assistant

