import React from 'react';

const Section = ({ title, children }) => (
  <div className="card animate-fade-in">
    <h3 className="text-lg font-bold text-[var(--primary)] mb-3">{title}</h3>
    {children}
  </div>
);

const TwoCol = ({ a, b, aTitle = 'Case A', bTitle = 'Case B' }) => (
  <div className="grid md:grid-cols-2 gap-4">
    <div>
      <div className="text-sm font-semibold text-gray-700 mb-1">{aTitle}</div>
      <div className="text-gray-700 text-sm whitespace-pre-wrap">{a || '—'}</div>
    </div>
    <div>
      <div className="text-sm font-semibold text-gray-700 mb-1">{bTitle}</div>
      <div className="text-gray-700 text-sm whitespace-pre-wrap">{b || '—'}</div>
    </div>
  </div>
);

const Table = ({ rows }) => (
  <div className="overflow-x-auto">
    <table className="w-full text-sm">
      <thead>
        <tr className="bg-gray-100">
          <th className="px-4 py-2 text-left font-semibold text-gray-700 w-48">Dimension</th>
          <th className="px-4 py-2 text-left font-semibold text-gray-700">Left</th>
          <th className="px-4 py-2 text-left font-semibold text-gray-700">Right</th>
        </tr>
      </thead>
      <tbody>
        {(rows || []).map((r, idx) => (
          <tr key={idx} className="border-b">
            <td className="px-4 py-2 font-medium text-gray-800 align-top">{r.label || '—'}</td>
            <td className="px-4 py-2 text-gray-700 whitespace-pre-wrap align-top">{r.a || '—'}</td>
            <td className="px-4 py-2 text-gray-700 whitespace-pre-wrap align-top">{r.b || '—'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

const ComparisonPhases = ({ data }) => {
  if (!data) return null;
  const phases = data.phases || {};
  const radar = phases.radar || {};
  const eco = phases.ecosystem || {};
  const deep = phases.deep_dive || {};
  const swot = phases.swot || {};

  return (
    <div className="space-y-6">
      {/* Phase 1: Radar */}
      <Section title="Phase 1: The Radar (Similarities)">
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
            <div className="text-sm font-semibold text-blue-800 mb-1">Contextual</div>
            <div className="text-sm text-blue-900 whitespace-pre-wrap">{radar.contextual || '—'}</div>
          </div>
          <div className="bg-purple-50 border border-purple-200 rounded-xl p-4">
            <div className="text-sm font-semibold text-purple-800 mb-1">Procedural</div>
            <div className="text-sm text-purple-900 whitespace-pre-wrap">{radar.procedural || '—'}</div>
          </div>
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
            <div className="text-sm font-semibold text-amber-800 mb-1">Legal</div>
            <div className="text-sm text-amber-900 whitespace-pre-wrap">{radar.legal || '—'}</div>
          </div>
          <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4">
            <div className="text-sm font-semibold text-emerald-800 mb-1">Real-World Impact</div>
            <div className="text-sm text-emerald-900 whitespace-pre-wrap">{radar.impact || '—'}</div>
          </div>
        </div>
      </Section>

      {/* Phase 2: Ecosystem */}
      <Section title="Phase 2: The Ecosystem (The Narrative)">
        <div className="space-y-4">
          <div>
            <div className="text-sm font-semibold text-gray-700 mb-1">Shared Ecosystem</div>
            <div className="text-gray-700 text-sm whitespace-pre-wrap">{eco.shared_ecosystem || '—'}</div>
          </div>
          <TwoCol a={eco.chaos?.a} b={eco.chaos?.b} aTitle="Chaos (Left)" bTitle="Chaos (Right)" />
          <TwoCol a={eco.gatekeepers?.a} b={eco.gatekeepers?.b} aTitle="Gatekeepers (Left)" bTitle="Gatekeepers (Right)" />
          <TwoCol a={eco.paper_truth?.a} b={eco.paper_truth?.b} aTitle="Paper Truth (Left)" bTitle="Paper Truth (Right)" />
          <div>
            <div className="text-sm font-semibold text-gray-700 mb-1">Mirror Effect</div>
            <div className="text-gray-700 text-sm whitespace-pre-wrap">{eco.mirror_effect || '—'}</div>
          </div>
        </div>
      </Section>

      {/* Phase 3: 12-Point Deep Dive */}
      <Section title="Phase 3: The 12-Point Deep Dive">
        <Table rows={deep.rows || []} />
      </Section>

      {/* Phase 4: Strategy Engine (SWOT) */}
      <Section title="Phase 4: Strategy Engine (SWOT)">
        <div className="space-y-4">
          <TwoCol a={swot.precedent_strength?.a} b={swot.precedent_strength?.b} aTitle="Precedent Strength (Left)" bTitle="Precedent Strength (Right)" />
          <div className="grid md:grid-cols-2 gap-4">
            <TwoCol a={swot.attorneys_edge?.prosecutor?.a} b={swot.attorneys_edge?.prosecutor?.b} aTitle="Prosecutor (Left)" bTitle="Prosecutor (Right)" />
            <TwoCol a={swot.attorneys_edge?.defense?.a} b={swot.attorneys_edge?.defense?.b} aTitle="Defense (Left)" bTitle="Defense (Right)" />
          </div>
        </div>
      </Section>
    </div>
  );
};

export default ComparisonPhases;
