import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { summarizeKanoonDoc } from '../utils/api';

const CaseSummary = () => {
  const { id } = useParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  useEffect(() => {
    let cancelled = false;
    async function run() {
      setLoading(true);
      setError(null);
      try {
        const res = await summarizeKanoonDoc(id);
        if (!cancelled) setData(res);
      } catch (e) {
        if (!cancelled) setError(e?.response?.data?.detail || 'Failed to load summary');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    if (id) run();
    return () => { cancelled = true; };
  }, [id]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0e1a] via-[#0f1f1f] to-[#1a2d2d] p-4">
      <div className="max-w-4xl mx-auto">
        <div className="mb-4 flex items-center justify-between">
          <h1 className="text-2xl font-semibold text-white">Case Summary</h1>
          <Link className="btn btn-sm btn-outline" to={id ? `/api/kanoon/doc?id=${encodeURIComponent(id)}` : '#'} target="_blank" rel="noreferrer">
            View Full Document
          </Link>
        </div>

        {loading && (
          <div className="card-glass p-4">Generating summary…</div>
        )}

        {error && (
          <div className="card-glass bg-red-900/20 border-l-4 border-red-500 p-4 rounded">
            <p className="text-red-300">{String(error)}</p>
          </div>
        )}

        {!loading && !error && data && (
          <div className="card-glass p-6">
            <div className="mb-3">
              <div className="text-lg font-medium text-white">{data.title || '—'}</div>
              <div className="text-sm text-text-muted flex gap-3">
                <span>{data.source || '—'}</span>
                <span>{data.date || '—'}</span>
                <span>ID: {data.id}</span>
              </div>
            </div>
            <hr className="my-3 border-white/10" />
            <article className="prose prose-invert max-w-none">
              <div className="text-text-secondary" style={{ whiteSpace: 'pre-wrap' }}>{data.summary_markdown}</div>
            </article>
          </div>
        )}
      </div>
    </div>
  );
};

export default CaseSummary;
