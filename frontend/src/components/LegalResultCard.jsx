import React from 'react';

function toPct(sim) {
  return `${Math.round((sim || 0) * 100)}%`;
}

function Highlighted({ text, query }) {
  if (!text || !query) return <>{text}</>;
  const pattern = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, 'ig');
  const parts = text.split(pattern);
  return (
    <>
      {parts.map((p, i) => pattern.test(p) ? <mark key={i}>{p}</mark> : <span key={i}>{p}</span>)}
    </>
  );
}

function extractYearFromTitle(title) {
  if (!title || typeof title !== 'string') return undefined;
  const m = title.match(/(\d{4})(?!.*\d)/);
  return m ? m[1] : undefined;
}

import { useNavigate } from 'react-router-dom';

const LegalResultCard = ({ r, originalQuery, className = '', style, onCompare, onDetectBias, similarityPercentage }) => {
  const navigate = useNavigate();
  const displayTitle = r.case_title || r.title || '—';
  const derivedYear = r.year ?? extractYearFromTitle(displayTitle);
  const lawyerFields = [
    r.lawyers,
    r.advocates,
    r.counsel,
    r.counsels,
    r.petitioner_advocate,
    r.respondent_advocate,
    r.petitioner_counsel,
    r.respondent_counsel,
  ]
    .filter(Boolean)
    .flatMap(v => Array.isArray(v) ? v : (typeof v === 'string' ? v.split(/;|,|\n/).map(s => s.trim()).filter(Boolean) : []));
  const uniqueLawyers = Array.from(new Set(lawyerFields)).slice(0, 6);
  const hasLawyers = uniqueLawyers.length > 0;
  return (
    <div className={`card p-4 ${className}`} style={style}>
      {/* Header row */}
      <div className="flex items-center justify-between mb-3">
        <div className="font-semibold text-lg text-white">{displayTitle}</div>
        <div className="flex gap-2 text-xs items-center">
          {similarityPercentage !== undefined && (
            <span className="px-2 py-1 rounded bg-green-500/20 text-green-300 border border-green-500/30 font-semibold">
              {similarityPercentage}% Match
            </span>
          )}
          <span className="px-2 py-0.5 rounded bg-white/10 text-text-secondary border border-white/10">{r.court || r.docsource || '—'}</span>
          <span className="px-2 py-0.5 rounded bg-white/10 text-text-secondary border border-white/10">{derivedYear ?? '—'}</span>
        </div>
      </div>

      {/* Meta removed per requirements */}

      {/* Body removed per requirements */}

      {/* Tags */}
      <div className="mt-3 flex flex-wrap gap-2">
        {r.statutes && r.statutes.length > 0 ? (
          r.statutes.map((s, i) => (
            <span key={i} className="px-2 py-1 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 text-xs">{s}</span>
          ))
        ) : (
          <span className="text-xs text-text-muted">No statutes detected</span>
        )}
      </div>

      <div className="mt-3 text-sm">
        <span className="font-medium text-text-secondary">Lawyers:</span>{' '}
        {hasLawyers ? (
          <span className="text-white">{uniqueLawyers.join(' · ')}</span>
        ) : (
          <span className="text-text-muted">—</span>
        )}
      </div>

      {/* Actions */}
      <div className="mt-4 flex items-center gap-3 flex-wrap">
        <a
          className="btn btn-sm bg-gradient-to-r from-blue-500 to-purple-500 text-white hover:scale-105"
          href={r.tid ? `/api/kanoon/doc?id=${encodeURIComponent(r.tid)}` : `/api/document/serve?id=${encodeURIComponent(r.doc_id || '')}`}
          target="_blank" rel="noreferrer"
        >
          View Full Document
        </a>
        {onCompare && (
          <button
            className="btn btn-sm btn-outline"
            onClick={() => onCompare(r)}
          >
            Compare
          </button>
        )}
        {onDetectBias && (
          <button
            className="btn btn-sm bg-red-500/20 text-red-300 border border-red-500/30 hover:bg-red-500/30"
            onClick={() => onDetectBias(r)}
          >
            Detect Bias
          </button>
        )}
        <button
          className="btn btn-sm btn-outline"
          onClick={() => {
            if (r.tid) {
              navigate(`/summary/${encodeURIComponent(r.tid)}`);
            }
          }}
        >
          Summarize
        </button>
      </div>
      {/* Footer and provenance removed per requirements */}
    </div>
  );
};

export default LegalResultCard;
