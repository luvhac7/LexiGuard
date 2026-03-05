import React from 'react';

const BiasGraph = ({ data }) => {
  if (!data || !Array.isArray(data) || data.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        No bias data available. Run analysis to see results.
      </div>
    );
  }

  const maxScore = Math.max(...data.map(item => item.score || item.bias_score || 0), 1);

  return (
    <div className="card">
      <h3 className="text-lg font-bold text-[var(--primary)] mb-4">Bias Score Distribution</h3>
      <div className="space-y-4">
        {data.map((item, idx) => {
          const score = item.score || item.bias_score || 0;
          const percentage = (score / maxScore) * 100;
          const label = item.label || item.case_pair || `Case Pair ${idx + 1}`;
          
          return (
            <div key={idx} className="space-y-1">
              <div className="flex justify-between text-sm">
                <span className="font-medium text-gray-700">{label}</span>
                <span className="text-gray-600">{score.toFixed(2)}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-6 relative overflow-hidden">
                <div
                  className={`h-6 rounded-full transition-all duration-500 ${
                    score > 0.7
                      ? 'bg-red-500'
                      : score > 0.4
                      ? 'bg-yellow-500'
                      : 'bg-green-500'
                  }`}
                  style={{ width: `${percentage}%` }}
                >
                  <div className="absolute inset-0 flex items-center justify-center text-white text-xs font-semibold">
                    {score > 0.05 && `${(score * 100).toFixed(0)}%`}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default BiasGraph;

