import React, { useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import LegalResultCard from '../components/LegalResultCard';
import { useToast } from '../components/ToastProvider';
import BiasDetectionDisplay from '../components/BiasDetectionDisplay';
import { kanoonDetectBias } from '../utils/api';
import { AlertTriangle } from 'lucide-react';

const BiasConflictAgent = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const toast = useToast();
  const primary = location.state?.primary;
  const all = Array.isArray(location.state?.all) ? location.state.all : [];
  const [selected, setSelected] = useState(null);
  const [biasLoading, setBiasLoading] = useState(false);
  const [biasError, setBiasError] = useState(null);
  const [biasData, setBiasData] = useState(null);

  const others = useMemo(() => {
    const pid = primary?.tid || primary?.doc_id;
    return all.filter((d) => (d?.tid || d?.doc_id) !== pid);
  }, [all, primary]);

  if (!primary) {
    return (
      <div className="min-h-screen">
        <div className="container px-6 py-10">
          <div className="card-glass text-center">
            <h1 className="text-2xl font-bold text-white mb-2">No primary case selected</h1>
            <p className="text-text-secondary mb-4">Go back to search and choose Detect Bias on a case.</p>
            <button className="btn-primary" onClick={() => navigate('/legal-knowledge')}>Back to Search</button>
          </div>
        </div>
      </div>
    );
  }

  const getId = (d) => d?.tid || d?.doc_id;
  const isSelected = (d) => getId(d) && getId(selected) && getId(d) === getId(selected);

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0e1a] via-[#1f0f0f] to-[#2d1a1a]">
      <div className="container px-6 py-8">
        <div className="flex items-center gap-3 mb-6">
          <AlertTriangle className="text-red-400" size={32} />
          <h1 className="text-3xl font-bold text-white drop-shadow-lg">Bias Detection Agent</h1>
        </div>
        <div className="grid md:grid-cols-2 gap-6 items-start">
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-gray-200">Primary case</h2>
            <LegalResultCard r={primary} className="animate-slide-up" />
          </div>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-200">Select a case to compare</h2>
              <button
                className="btn-primary bg-gradient-to-r from-red-500 to-orange-500 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={!selected || biasLoading}
                onClick={async () => {
                  if (!selected) return;
                  try {
                    setBiasLoading(true);
                    setBiasError(null);
                    setBiasData(null);
                    toast.info({ title: 'Detecting bias…' });
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
                    const data = await kanoonDetectBias(docs);
                    setBiasData(data);
                    toast.success({ title: 'Bias analysis ready' });
                  } catch (e) {
                    const msg = e?.message || 'Failed to detect bias';
                    setBiasError(msg);
                    toast.error({ title: 'Bias detection failed', description: msg });
                  } finally {
                    setBiasLoading(false);
                  }
                }}
              >
                Detect Bias
              </button>
            </div>
            <div className="grid lg:grid-cols-2 gap-4">
              {others.map((doc, idx) => (
                <div key={getId(doc) || idx} className={isSelected(doc) ? 'ring-2 ring-red-500 rounded-xl' : ''}>
                  <LegalResultCard
                    r={doc}
                    className="animate-slide-up"
                    style={{ animationDelay: `${idx * 40}ms` }}
                    onDetectBias={() => setSelected(doc)}
                  />
                </div>
              ))}
              {others.length === 0 && (
                <div className="card-glass">
                  <p className="text-text-secondary">No other cases available to compare.</p>
                </div>
              )}
            </div>
          </div>
        </div>
        {biasLoading && (
          <div className="card-glass mt-6">
            <h3 className="text-lg font-semibold text-white mb-2">Detecting bias…</h3>
            <div className="bg-white/10 rounded-full h-2">
              <div className="bg-gradient-to-r from-red-500 to-orange-500 h-2 rounded-full animate-pulse" style={{ width: '60%' }} />
            </div>
          </div>
        )}
        {biasError && (
          <div className="card-glass bg-red-900/20 border-l-4 border-red-500 p-4 rounded mt-6">
            <p className="text-red-300">{biasError}</p>
          </div>
        )}
        {biasData && (
          <div className="mt-6">
            <BiasDetectionDisplay biasData={biasData} />
          </div>
        )}
      </div>
    </div>
  );
};

export default BiasConflictAgent;
