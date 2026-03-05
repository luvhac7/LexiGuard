import React, { useMemo, useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import LegalResultCard from '../components/LegalResultCard';
import { useToast } from '../components/ToastProvider';
import CaseComparisonDisplay from '../components/CaseComparisonDisplay';
import { kanoonCompare, kanoonCompareRadarBatch } from '../utils/api';

const CaseComparisonAgent = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const toast = useToast();
  const primary = location.state?.primary;
  const all = Array.isArray(location.state?.all) ? location.state.all : [];
  const [selected, setSelected] = useState(null);
  const [cmpLoading, setCmpLoading] = useState(false);
  const [cmpError, setCmpError] = useState(null);
  const [cmpData, setCmpData] = useState(null);

  // Batch Radar State
  const [batchRadarData, setBatchRadarData] = useState(null);
  const [batchRadarLoading, setBatchRadarLoading] = useState(false);

  const others = useMemo(() => {
    const pid = primary?.tid || primary?.doc_id;
    return all.filter((d) => (d?.tid || d?.doc_id) !== pid);
  }, [all, primary]);

  const getId = (d) => d?.tid || d?.doc_id;

  // Fetch batch radar data on mount
  useEffect(() => {
    if (primary && others.length > 0) {
      const fetchBatchRadar = async () => {
        setBatchRadarLoading(true);
        try {
          const primaryDoc = {
            tid: getId(primary),
            title: primary.title,
            date: primary.publishdate || primary.date,
            headline: primary.headline
          };
          const otherDocs = others.map(d => ({
            tid: getId(d),
            title: d.title,
            date: d.publishdate || d.date,
            headline: d.headline
          }));

          const data = await kanoonCompareRadarBatch(primaryDoc, otherDocs);
          setBatchRadarData(data);
        } catch (error) {
          console.error("Failed to fetch batch radar:", error);
        } finally {
          setBatchRadarLoading(false);
        }
      };

      fetchBatchRadar();
    }
  }, [primary, others]);

  if (!primary) {
    return (
      <div className="min-h-screen">
        <div className="container px-6 py-10">
          <div className="card-glass text-center">
            <h1 className="text-2xl font-bold text-white mb-2">No primary case selected</h1>
            <p className="text-text-secondary mb-4">Go back to search and choose Compare on a case.</p>
            <button className="btn-primary" onClick={() => navigate('/legal-knowledge')}>Back to Search</button>
          </div>
        </div>
      </div>
    );
  }

  const isSelected = (d) => getId(d) && getId(selected) && getId(d) === getId(selected);

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0e1a] via-[#1a0f30] to-[#2d1b4e]">
      <div className="container px-6 py-8">
        <h1 className="text-3xl font-bold text-white mb-6 drop-shadow-lg">Case Comparison</h1>
        <div className="grid md:grid-cols-2 gap-6 items-start">
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-gray-200">Primary case</h2>
            <LegalResultCard r={primary} className="animate-slide-up" />
          </div>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-200">Select a case to compare</h2>
              <button
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={!selected || cmpLoading}
                onClick={async () => {
                  if (!selected) return;
                  try {
                    setCmpLoading(true);
                    setCmpError(null);
                    setCmpData(null);
                    toast.info({ title: 'Generating comparison…' });
                    const docs = [
                      {
                        tid: getId(primary),
                        title: primary.title,
                        date: primary.publishdate || primary.date,
                        headline: primary.headline
                      },
                      {
                        tid: getId(selected),
                        title: selected.title,
                        date: selected.publishdate || selected.date,
                        headline: selected.headline
                      }
                    ];
                    const data = await kanoonCompare(docs);
                    setCmpData(data);
                    toast.success({ title: 'Comparison ready' });
                  } catch (e) {
                    const msg = e?.message || 'Failed to generate comparison';
                    setCmpError(msg);
                    toast.error({ title: 'Comparison failed', description: msg });
                  } finally {
                    setCmpLoading(false);
                  }
                }}
              >
                Compare Selected
              </button>
            </div>
            <div className="grid lg:grid-cols-2 gap-4">
              {others.map((doc, idx) => (
                <div key={getId(doc) || idx} className={`relative ${isSelected(doc) ? 'ring-2 ring-purple-500 rounded-xl' : ''}`}>
                  {/* Number Badge */}
                  <div className="absolute -top-2 -left-2 z-10 bg-gradient-to-br from-indigo-600 to-purple-600 text-white text-xs font-bold w-6 h-6 flex items-center justify-center rounded-full shadow-lg">
                    #{idx + 1}
                  </div>
                  <LegalResultCard
                    r={doc}
                    className="animate-slide-up"
                    style={{ animationDelay: `${idx * 40}ms` }}
                    onCompare={() => setSelected(doc)}
                  />
                </div>
              ))}
              {others.length === 0 && (
                <div className="card-glass">
                  <p className="text-text-secondary">No other cases available to compare.</p>
                </div>
              )}
            </div>

            {/* Batch Radar Heatmap */}
            {batchRadarLoading && (
              <div className="card-glass mt-4 p-4 text-center">
                <p className="text-sm text-text-muted animate-pulse">Generating batch similarity heatmap...</p>
              </div>
            )}

            {batchRadarData?.heatmap_image && (
              <div className="card-glass mt-4 p-4 border border-purple-500/30 bg-purple-900/20">
                <h3 className="text-sm font-bold text-purple-300 mb-3 uppercase tracking-wider text-center">Batch Similarity Heatmap</h3>
                <div className="flex justify-center">
                  <img
                    src={batchRadarData.heatmap_image}
                    alt="Batch Similarity Heatmap"
                    className="max-w-full rounded-lg shadow-sm"
                  />
                </div>
              </div>
            )}
          </div>
        </div>
        {cmpLoading && (
          <div className="card-glass mt-6">
            <h3 className="text-lg font-semibold text-white mb-2">Generating comparison…</h3>
            <div className="bg-white/10 rounded-full h-2">
              <div className="bg-gradient-to-r from-indigo-600 to-purple-600 h-2 rounded-full animate-pulse" style={{ width: '60%' }} />
            </div>
          </div>
        )}
        {cmpError && (
          <div className="card-glass bg-red-900/20 border-l-4 border-red-500 p-4 rounded mt-6">
            <p className="text-red-300">{cmpError}</p>
          </div>
        )}
        {cmpData && (
          <div className="mt-6 space-y-4">
            {(cmpData.left_url || cmpData.right_url) && (
              <div className="card-glass">
                <div className="text-sm text-text-secondary">
                  {cmpData.left_url && (
                    <a href={cmpData.left_url} target="_blank" rel="noreferrer" className="text-blue-400 hover:text-blue-300 hover:underline mr-4">Left Doc</a>
                  )}
                  {cmpData.right_url && (
                    <a href={cmpData.right_url} target="_blank" rel="noreferrer" className="text-blue-400 hover:text-blue-300 hover:underline">Right Doc</a>
                  )}
                </div>
              </div>
            )}
            <CaseComparisonDisplay comparisonData={cmpData} />
          </div>
        )}
      </div>
    </div>
  );
};

export default CaseComparisonAgent;

