import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import LegalKnowledgeAgent from './pages/LegalKnowledgeAgent';
import CaseComparisonAgent from './pages/CaseComparisonAgent';
import BiasConflictAgent from './pages/BiasConflictAgent';
import CaseSummary from './pages/CaseSummary';
import Analytics from './pages/Analytics';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-b from-background via-primary to-background">
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/legal-knowledge" element={<LegalKnowledgeAgent />} />
          <Route path="/comparison" element={<CaseComparisonAgent />} />
          <Route path="/bias-detection" element={<BiasConflictAgent />} />
          <Route path="/summary/:id" element={<CaseSummary />} />
          <Route path="/analytics" element={<Analytics />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
