import React from 'react';
import { Calendar, Building2, BookOpen, AlertTriangle, Scale } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const CaseCard = ({ caseData, onCompare, onDetectBias }) => {
  const navigate = useNavigate();

  const handleCompare = () => {
    if (onCompare) {
      onCompare(caseData);
    } else {
      navigate('/comparison', { state: { caseA: caseData } });
    }
  };

  const handleDetectBias = () => {
    if (onDetectBias) {
      onDetectBias(caseData);
    } else {
      navigate('/bias-detection', { state: { case: caseData } });
    }
  };

  return (
    <div className="card hover:shadow-xl transition-all duration-300">
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-xl font-bold text-[var(--primary)] flex-1">
          {caseData.title || caseData.case_title || 'Case Title'}
        </h3>
        {caseData.relevance && (
          <span className="ml-4 px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-semibold">
            {(caseData.relevance * 100).toFixed(0)}% Match
          </span>
        )}
      </div>

      <div className="space-y-2 mb-4 text-sm text-gray-600">
        {caseData.year && (
          <div className="flex items-center">
            <Calendar size={16} className="mr-2" />
            <span className="font-semibold">{caseData.year}</span>
          </div>
        )}
        {caseData.court && (
          <div className="flex items-center">
            <Building2 size={16} className="mr-2" />
            <span>{caseData.court}</span>
          </div>
        )}
        {caseData.citation && (
          <div className="flex items-center">
            <BookOpen size={16} className="mr-2" />
            <span className="font-mono text-xs">{caseData.citation}</span>
          </div>
        )}
      </div>

      {caseData.summary && (
        <p className="text-gray-700 mb-4 line-clamp-3">{caseData.summary}</p>
      )}

      {caseData.keywords && caseData.keywords.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {caseData.keywords.slice(0, 5).map((keyword, idx) => (
            <span
              key={idx}
              className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs"
            >
              {keyword}
            </span>
          ))}
        </div>
      )}

      <div className="flex gap-2 mt-4">
        <button
          onClick={handleCompare}
          className="flex-1 flex items-center justify-center gap-2 bg-[var(--primary)] text-white px-4 py-2 rounded-lg hover:bg-opacity-90 transition-all text-sm font-medium"
        >
          <Scale size={16} />
          Compare
        </button>
        <button
          onClick={handleDetectBias}
          className="flex-1 flex items-center justify-center gap-2 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-all text-sm font-medium"
        >
          <AlertTriangle size={16} />
          Detect Bias
        </button>
      </div>
    </div>
  );
};

export default CaseCard;

