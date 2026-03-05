import React, { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

const CaseComparisonDisplay = ({ comparisonData }) => {
  const [expandedSections, setExpandedSections] = useState({
    radar: true,
    ecosystem: true,
    deepDive: true,
  });

  const toggleSection = (section) => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }));
  };

  if (!comparisonData) {
    return (
      <div className="text-center py-12">
        <p className="text-text-muted text-lg">No comparison data available</p>
      </div>
    );
  }

  const { meta, radar_analysis, ecosystem_analysis, deep_dive_matrix } = comparisonData;

  if (!meta || !radar_analysis || !ecosystem_analysis || !deep_dive_matrix) {
    if (comparisonData.comparison) {
      return (
        <div className="text-center py-8 text-red-400 card-glass">
          Received old format data. Please refresh or check backend.
        </div>
      );
    }
    return (
      <div className="text-center py-8 card-glass">
        <p className="text-text-muted">Incomplete comparison data.</p>
        <p className="text-xs mt-2 text-text-muted">Received keys: {JSON.stringify(Object.keys(comparisonData || {}))}</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 p-6">
      {/* Header */}
      <div className="card-glass">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center flex-shrink-0 shadow-lg">
            <span className="text-2xl">⚖️</span>
          </div>
          <h2 className="text-3xl font-bold text-white drop-shadow-lg">Juris-AI Deep Dive Analysis</h2>
        </div>

        <div className="grid md:grid-cols-2 gap-4 mt-6">
          <div className="bg-blue-500/20 border-2 border-blue-400/50 rounded-xl p-4">
            <div className="text-xs font-semibold text-blue-300 uppercase tracking-wider mb-2">Case A</div>
            <div className="text-white font-medium">{meta.case_a_title}</div>
          </div>
          <div className="bg-purple-500/20 border-2 border-purple-400/50 rounded-xl p-4">
            <div className="text-xs font-semibold text-purple-300 uppercase tracking-wider mb-2">Case B</div>
            <div className="text-white font-medium">{meta.case_b_title}</div>
          </div>
        </div>

        <div className="mt-4 inline-flex items-center gap-2 px-3 py-1.5 bg-gradient-to-r from-indigo-500/30 to-purple-500/30 border-2 border-indigo-400/50 rounded-lg">
          <span className="text-xs font-semibold text-gray-200 uppercase tracking-wider">Domain:</span>
          <span className="text-sm text-white font-medium">{meta.domain_detected}</span>
        </div>
      </div>

      {/* PHASE 1: THE RADAR */}
      <CollapsibleSection
        title="Phase 1: The Radar"
        subtitle="Similarity Analysis"
        isExpanded={expandedSections.radar}
        onToggle={() => toggleSection('radar')}
        badge="PHASE 1"
        badgeColor="from-blue-600 to-cyan-600"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <RadarCard
            title="Contextual"
            score={radar_analysis.contextual_score}
            reasoning={radar_analysis.contextual_reasoning}
            gradient="from-blue-500 to-cyan-500"
          />
          <RadarCard
            title="Procedural"
            score={radar_analysis.procedural_score}
            reasoning={radar_analysis.procedural_reasoning}
            gradient="from-indigo-500 to-blue-500"
          />
          <RadarCard
            title="Legal"
            score={radar_analysis.legal_score}
            reasoning={radar_analysis.legal_reasoning}
            gradient="from-purple-500 to-indigo-500"
          />
          <RadarCard
            title="Real-World Impact"
            score={radar_analysis.real_world_score}
            reasoning={radar_analysis.real_world_reasoning}
            gradient="from-pink-500 to-purple-500"
          />
        </div>
      </CollapsibleSection>

      {/* PHASE 2: THE ECOSYSTEM */}
      <CollapsibleSection
        title="Phase 2: The Ecosystem"
        subtitle={ecosystem_analysis.shared_ecosystem_name}
        isExpanded={expandedSections.ecosystem}
        onToggle={() => toggleSection('ecosystem')}
        badge="PHASE 2"
        badgeColor="from-green-600 to-emerald-600"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <EcosystemCard
            title="The Chaos"
            content={ecosystem_analysis.the_chaos}
            icon="🌪️"
          />
          <EcosystemCard
            title="The Gatekeepers"
            content={ecosystem_analysis.the_gatekeepers}
            icon="🛡️"
          />
          <EcosystemCard
            title="The Paper Truth"
            content={ecosystem_analysis.the_paper_truth}
            icon="📄"
          />
          <EcosystemCard
            title="The Mirror Effect"
            content={ecosystem_analysis.the_mirror_effect}
            icon="🪞"
          />
        </div>
      </CollapsibleSection>

      {/* PHASE 3: THE 12-POINT DEEP DIVE */}
      <CollapsibleSection
        title="Phase 3: 12-Point Deep Dive"
        subtitle="Comprehensive Dimensional Analysis"
        isExpanded={expandedSections.deepDive}
        onToggle={() => toggleSection('deepDive')}
        badge="PHASE 3"
        badgeColor="from-orange-600 to-red-600"
      >
        <div className="overflow-x-auto rounded-xl border border-white/10">
          <table className="min-w-full divide-y divide-white/10">
            <thead className="bg-surface/50">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider w-1/6">
                  Dimension
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-blue-400 uppercase tracking-wider w-1/3">
                  Case A
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-purple-400 uppercase tracking-wider w-1/3">
                  Case B
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider w-1/6">
                  Insight
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {deep_dive_matrix.map((row, idx) => (
                <tr
                  key={idx}
                  className="hover:bg-white/5 transition-colors duration-150"
                >
                  <td className="px-6 py-4">
                    <span className="text-sm font-semibold text-white">{row.dimension}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-sm text-text-secondary leading-relaxed">{row.case_a}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-sm text-text-secondary leading-relaxed">{row.case_b}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-sm text-text-muted italic">{row.insight}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CollapsibleSection>
    </div>
  );
};

const CollapsibleSection = ({ title, subtitle, isExpanded, onToggle, badge, badgeColor, children }) => (
  <div className="card-glass">
    <button
      onClick={onToggle}
      className="w-full flex items-center justify-between mb-6 group"
    >
      <div className="flex items-center gap-4">
        <span className={`inline-block px-3 py-1 bg-gradient-to-r ${badgeColor} text-white text-xs font-bold rounded-lg shadow-lg`}>
          {badge}
        </span>
        <div className="text-left">
          <h3 className="text-2xl font-bold text-white drop-shadow-lg group-hover:text-gradient transition-colors">
            {title}
          </h3>
          {subtitle && <p className="text-sm text-gray-300 mt-1">{subtitle}</p>}
        </div>
      </div>
      <div className="text-text-muted group-hover:text-white transition-colors">
        {isExpanded ? <ChevronUp size={24} /> : <ChevronDown size={24} />}
      </div>
    </button>
    {isExpanded && <div className="animate-fade-in">{children}</div>}
  </div>
);

const RadarCard = ({ title, score, reasoning, gradient }) => {
  return (
    <div className={`relative overflow-hidden bg-gradient-to-br ${gradient} p-[1px] rounded-2xl`}>
      <div className="bg-surface/90 backdrop-blur-xl rounded-2xl p-6 h-full flex flex-col">
        <div className="flex justify-between items-center mb-4">
          <h4 className="font-bold text-white text-lg">{title}</h4>
          <div className="text-3xl font-black text-white/40">{score}</div>
        </div>

        {/* Progress Bar */}
        <div className="relative w-full h-3 bg-white/10 rounded-full mb-4 overflow-hidden">
          <div
            className={`absolute top-0 left-0 h-full bg-gradient-to-r ${gradient} rounded-full transition-all duration-1000 ease-out shadow-lg`}
            style={{ width: `${score}%` }}
          >
            <div className="absolute inset-0 bg-white/20 animate-pulse"></div>
          </div>
        </div>

        <p className="text-sm text-text-secondary flex-grow leading-relaxed">{reasoning}</p>
      </div>
    </div>
  );
};

const EcosystemCard = ({ title, content, icon }) => (
  <div className="card-glass group hover:scale-[1.02] transition-transform duration-300">
    <div className="flex items-center gap-3 mb-4">
      <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center text-2xl group-hover:scale-110 transition-transform">
        {icon}
      </div>
      <h4 className="font-bold text-white text-lg">{title}</h4>
    </div>
    <p className="text-text-secondary text-sm leading-relaxed">{content}</p>
  </div>
);

export default CaseComparisonDisplay;
