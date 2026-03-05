import React, { useState } from 'react';
import { ChevronRight, Bot, Brain, FileText, Award } from 'lucide-react';

const ExplainPanel = ({ agentInfo, models = [], confidence, citations = [] }) => {
  const [isExpanded, setIsExpanded] = useState(true);

  const defaultAgentInfo = {
    name: 'Agent',
    description: 'Multi-agent RAG system for legal research',
  };

  const agent = agentInfo || defaultAgentInfo;
  const defaultModels = models.length > 0 ? models : ['Legal-BERT', 'GPT-4', 'RoBERTa-MNLI'];

  return (
    <div className={`bg-gradient-to-b from-[#1a1f3a] to-[#252b4a] border-l-2 border-purple-500/50 shadow-2xl transition-all duration-300 sticky top-16 h-[calc(100vh-64px)] ${isExpanded ? 'w-80' : 'w-12 overflow-hidden'
      }`}>
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white flex items-center justify-between hover:from-indigo-500 hover:to-purple-500 transition-all shadow-lg"
      >
        <div className="flex items-center gap-2">
          <Bot size={20} />
          {isExpanded && <span className="font-semibold">Explainability</span>}
        </div>
        <ChevronRight
          size={20}
          className={`transition-transform ${isExpanded ? '' : 'rotate-180'}`}
        />
      </button>

      {isExpanded && (
        <div className="p-4 space-y-4 h-[calc(100%-52px)] overflow-y-auto">
          {/* Agent Info */}
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Bot size={18} className="text-purple-400" />
              <h4 className="font-bold text-white">Agent Used</h4>
            </div>
            <p className="text-sm text-gray-200 font-semibold">{agent.name}</p>
            {agent.description && (
              <p className="text-xs text-gray-300 mt-1">{agent.description}</p>
            )}
          </div>

          {/* Models */}
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Brain size={18} className="text-purple-400" />
              <h4 className="font-bold text-white">Models</h4>
            </div>
            <ul className="space-y-1">
              {defaultModels.map((model, idx) => (
                <li key={idx} className="text-xs bg-white/10 border border-white/20 text-gray-200 px-2 py-1 rounded">
                  {model}
                </li>
              ))}
            </ul>
          </div>

          {/* Confidence */}
          {confidence !== undefined && confidence !== null && (
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Award size={18} className="text-purple-400" />
                <h4 className="font-bold text-white">Confidence</h4>
              </div>
              <div className="flex items-center gap-2">
                <div className="flex-1 bg-white/10 rounded-full h-3">
                  <div
                    className="bg-gradient-to-r from-indigo-500 to-purple-500 h-3 rounded-full"
                    style={{ width: `${confidence * 100}%` }}
                  />
                </div>
                <span className="text-xs font-semibold text-gray-200">
                  {(confidence * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          )}

          {/* Citations */}
          {citations.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-2">
                <FileText size={18} className="text-purple-400" />
                <h4 className="font-bold text-white">Citations</h4>
              </div>
              <ul className="space-y-2 text-xs">
                {citations.map((citation, idx) => (
                  <li key={idx} className="bg-white/10 border border-white/20 p-2 rounded text-gray-200">
                    {typeof citation === 'string' ? citation : citation.text || citation.title}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Additional Info */}
          {agent.additionalInfo && (
            <div className="pt-2 border-t border-white/20">
              <p className="text-xs text-gray-300">{agent.additionalInfo}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ExplainPanel;

