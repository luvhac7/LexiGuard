import React from 'react';
import { CheckCircle2, XCircle, AlertCircle } from 'lucide-react';

const CompareTable = ({ comparisonData }) => {
  if (!comparisonData) {
    return (
      <div className="text-center text-gray-500 py-8">
        Compare cases to see detailed analysis
      </div>
    );
  }

  const caseA = comparisonData.caseA || {};
  const caseB = comparisonData.caseB || {};
  const similarities = comparisonData.similarities || [];
  const contradictions = comparisonData.contradictions || [];
  const evolution = comparisonData.evolution || [];

  return (
    <div className="space-y-6">
      {/* Side-by-side comparison */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-bold text-[var(--primary)] mb-4">Case A</h3>
          <div className="space-y-2">
            <p className="font-semibold">{caseA.title || 'N/A'}</p>
            <p className="text-sm text-gray-600">{caseA.year || ''} - {caseA.court || ''}</p>
            <p className="text-gray-700 mt-3">{caseA.summary || caseA.text || ''}</p>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-bold text-[var(--primary)] mb-4">Case B</h3>
          <div className="space-y-2">
            <p className="font-semibold">{caseB.title || 'N/A'}</p>
            <p className="text-sm text-gray-600">{caseB.year || ''} - {caseB.court || ''}</p>
            <p className="text-gray-700 mt-3">{caseB.summary || caseB.text || ''}</p>
          </div>
        </div>
      </div>

      {/* Similarities */}
      {similarities.length > 0 && (
        <div className="card bg-green-50 border-l-4 border-green-500">
          <div className="flex items-center mb-3">
            <CheckCircle2 className="text-green-600 mr-2" size={20} />
            <h4 className="font-bold text-green-800">Similar Reasoning</h4>
          </div>
          <ul className="space-y-2">
            {similarities.map((item, idx) => (
              <li key={idx} className="text-green-700 text-sm">
                • {typeof item === 'string' ? item : item.text || item.description}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Contradictions */}
      {contradictions.length > 0 && (
        <div className="card bg-red-50 border-l-4 border-red-500">
          <div className="flex items-center mb-3">
            <XCircle className="text-red-600 mr-2" size={20} />
            <h4 className="font-bold text-red-800">Contradictions</h4>
          </div>
          <ul className="space-y-2">
            {contradictions.map((item, idx) => (
              <li key={idx} className="text-red-700 text-sm">
                • {typeof item === 'string' ? item : item.text || item.description}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Legal Evolution */}
      {evolution.length > 0 && (
        <div className="card bg-yellow-50 border-l-4 border-yellow-500">
          <div className="flex items-center mb-3">
            <AlertCircle className="text-yellow-600 mr-2" size={20} />
            <h4 className="font-bold text-yellow-800">Legal Evolution</h4>
          </div>
          <ul className="space-y-2">
            {evolution.map((item, idx) => (
              <li key={idx} className="text-yellow-700 text-sm">
                • {typeof item === 'string' ? item : item.text || item.description}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Summary Score */}
      {comparisonData.score && (
        <div className="card bg-blue-50">
          <h4 className="font-bold text-[var(--primary)] mb-2">Comparison Score</h4>
          <div className="flex items-center">
            <div className="flex-1 bg-gray-200 rounded-full h-4 mr-3">
              <div
                className="bg-[var(--primary)] h-4 rounded-full"
                style={{ width: `${comparisonData.score * 100}%` }}
              />
            </div>
            <span className="font-semibold text-[var(--primary)]">
              {(comparisonData.score * 100).toFixed(0)}%
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default CompareTable;

