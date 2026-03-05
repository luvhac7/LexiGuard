# Legal Assistant Frontend

AI-Powered Legal Research & Analysis Platform - Frontend Application

## Features

- **Case Search**: Search through legal database for relevant cases
- **Compare Cases**: Compare multiple judgments and track legal evolution
- **Contradiction Detection**: Identify conflicting rulings and potential biases
- **Legal Reasoning**: Get transparent, citation-backed legal analysis
- **Interactive Assistant**: Chat with Lexi, your legal research assistant
- **Document Upload**: Upload and index legal documents

## Tech Stack

- React 18
- Vite
- Tailwind CSS
- Lucide React (Icons)
- Axios (HTTP Client)

## Setup Instructions

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

3. Build for production:
```bash
npm run build
```

## Configuration

The frontend expects a backend API running on `http://localhost:8000`. Make sure your backend server is running before using the application.

API endpoints expected:
- `POST /api/search` - Search legal cases
- `POST /api/compare` - Compare two cases
- `POST /api/contradiction` - Detect contradictions
- `POST /api/reasoning` - Get legal reasoning
- `POST /api/chat` - Chat with assistant
- `POST /api/upload` - Upload documents

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── modules/      # Feature modules
│   │   ├── Header.jsx
│   │   ├── Navigation.jsx
│   │   ├── SettingsPanel.jsx
│   │   └── Footer.jsx
│   ├── App.jsx           # Main application component
│   ├── main.jsx          # Entry point
│   └── index.css         # Global styles
├── public/               # Static assets
├── package.json
└── vite.config.js
```

## Environment Variables

Create a `.env` file in the frontend directory if needed:
```
VITE_API_URL=http://localhost:8000
```

