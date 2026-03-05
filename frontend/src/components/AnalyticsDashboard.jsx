import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, ResponsiveContainer, PieChart, Pie, Cell, Sector,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
} from 'recharts';
import {
  Scale, Search, Zap, Database, TrendingUp, BarChart2,
  PieChart as PieIcon, Activity, AlertTriangle, RefreshCw,
} from 'lucide-react';

// ─── palette ────────────────────────────────────────────────
const C = {
  indigo:  '#6366f1',
  purple:  '#a855f7',
  blue:    '#3b82f6',
  cyan:    '#06b6d4',
  pink:    '#ec4899',
  emerald: '#10b981',
  amber:   '#f59e0b',
  rose:    '#f43f5e',
  slate:   '#94a3b8',
};

const PIE_COLORS = [C.indigo, C.purple, C.blue, C.cyan, C.pink, C.emerald, C.amber];

const CHART_THEME = {
  background: 'transparent',
  text:       '#cbd5e1',
  grid:       'rgba(148,163,184,0.12)',
  tooltip: {
    bg:     '#1a1f3a',
    border: 'rgba(99,102,241,0.4)',
    text:   '#e2e8f0',
  },
};

// Legal topics for the pie chart (derived / illustrative)
const LEGAL_TOPICS = [
  { name: 'Criminal Law',    value: 34 },
  { name: 'Civil Disputes',  value: 22 },
  { name: 'Constitutional',  value: 16 },
  { name: 'Tax Law',         value: 12 },
  { name: 'Commercial',      value: 9  },
  { name: 'Family Law',      value: 4  },
  { name: 'Other',           value: 3  },
];

const API = 'http://localhost:8000';

// ─── Custom shared tooltip ─────────────────────────────────
const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: CHART_THEME.tooltip.bg,
      border: `1px solid ${CHART_THEME.tooltip.border}`,
      borderRadius: 10,
      padding: '10px 14px',
      color: CHART_THEME.tooltip.text,
      fontSize: 13,
    }}>
      {label && <p style={{ marginBottom: 6, fontWeight: 600, color: '#e2e8f0' }}>{label}</p>}
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.color || C.indigo, margin: '2px 0' }}>
          {p.name}: <strong>{p.value}</strong>
        </p>
      ))}
    </div>
  );
};

// ─── KPI Card ─────────────────────────────────────────────
const KpiCard = ({ icon: Icon, label, value, sub, gradient, loading }) => (
  <div className="relative overflow-hidden rounded-2xl border border-white/10 p-5 flex flex-col gap-3"
    style={{
      background: 'linear-gradient(135deg, rgba(37,43,74,0.9) 0%, rgba(26,31,58,0.9) 100%)',
      backdropFilter: 'blur(20px)',
      transition: 'transform 0.2s, box-shadow 0.2s',
    }}
    onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-3px)'; e.currentTarget.style.boxShadow = `0 12px 40px rgba(99,102,241,0.25)`; }}
    onMouseLeave={e => { e.currentTarget.style.transform = ''; e.currentTarget.style.boxShadow = ''; }}
  >
    {/* Glow blob */}
    <div className="absolute -top-6 -right-6 w-24 h-24 rounded-full blur-2xl opacity-30"
      style={{ background: gradient }} />

    <div className="relative z-10 flex items-center gap-3">
      <div className="w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0"
        style={{ background: gradient }}>
        <Icon size={20} className="text-white" />
      </div>
      <span className="text-sm font-medium text-slate-400">{label}</span>
    </div>

    <div className="relative z-10">
      {loading
        ? <div className="h-8 w-24 rounded-lg animate-pulse" style={{ background: 'rgba(148,163,184,0.15)' }} />
        : <p className="text-3xl font-bold text-white tracking-tight">{value}</p>
      }
      {sub && !loading && (
        <p className="text-xs text-slate-500 mt-0.5">{sub}</p>
      )}
    </div>
  </div>
);

// ─── Section header ───────────────────────────────────────
const SectionTitle = ({ icon: Icon, title, color = C.indigo }) => (
  <div className="flex items-center gap-2 mb-5">
    <div className="w-7 h-7 rounded-lg flex items-center justify-center"
      style={{ background: `${color}22` }}>
      <Icon size={15} style={{ color }} />
    </div>
    <h3 className="text-base font-semibold text-white">{title}</h3>
  </div>
);

// ─── Chart card wrapper ───────────────────────────────────
const ChartCard = ({ children, className = '' }) => (
  <div className={`rounded-2xl border border-white/10 p-6 ${className}`}
    style={{
      background: 'linear-gradient(135deg, rgba(37,43,74,0.85) 0%, rgba(26,31,58,0.85) 100%)',
      backdropFilter: 'blur(20px)',
    }}>
    {children}
  </div>
);

// ─── Category badge ────────────────────────────────────────
const CAT_COLORS = {
  Criminal:       { bg: 'rgba(244,63,94,0.15)',  text: '#fb7185' },
  Civil:          { bg: 'rgba(59,130,246,0.15)', text: '#60a5fa' },
  Constitutional: { bg: 'rgba(168,85,247,0.15)', text: '#c084fc' },
  Tax:            { bg: 'rgba(245,158,11,0.15)', text: '#fbbf24' },
  Commercial:     { bg: 'rgba(16,185,129,0.15)', text: '#34d399' },
};
const CategoryBadge = ({ cat }) => {
  const s = CAT_COLORS[cat] || { bg: 'rgba(148,163,184,0.15)', text: '#94a3b8' };
  return (
    <span className="px-2 py-0.5 rounded-full text-xs font-medium"
      style={{ background: s.bg, color: s.text }}>{cat}</span>
  );
};

// ─── Active pie sector (for highlight) ────────────────────
const renderActiveShape = (props) => {
  const { cx, cy, innerRadius, outerRadius, startAngle, endAngle, fill, payload, percent } = props;
  return (
    <g>
      <text x={cx} y={cy - 8} textAnchor="middle" fill="#e2e8f0" fontSize={13} fontWeight={600}>
        {payload.name}
      </text>
      <text x={cx} y={cy + 12} textAnchor="middle" fill="#94a3b8" fontSize={12}>
        {(percent * 100).toFixed(1)}%
      </text>
      <Sector cx={cx} cy={cy} innerRadius={innerRadius} outerRadius={outerRadius + 6}
        startAngle={startAngle} endAngle={endAngle} fill={fill} />
    </g>
  );
};

// ─── Main Component ────────────────────────────────────────
const AnalyticsDashboard = () => {
  const [system,  setSystem]  = useState(null);
  const [cases,   setCases]   = useState(null);
  const [queries, setQueries] = useState(null);
  const [bias,    setBias]    = useState(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState(null);
  const [pieIdx,  setPieIdx]  = useState(0);
  const [lastRefresh, setLastRefresh] = useState(new Date());

  const fetchAll = async () => {
    setLoading(true);
    setError(null);
    try {
      const [sysRes, casesRes, queriesRes, biasRes] = await Promise.all([
        axios.get(`${API}/api/dashboard/system`),
        axios.get(`${API}/api/dashboard/cases`),
        axios.get(`${API}/api/dashboard/queries`),
        axios.get(`${API}/api/dashboard/bias`),
      ]);
      setSystem(sysRes.data);
      setCases(casesRes.data);
      setQueries(queriesRes.data);
      setBias(biasRes.data);
      setLastRefresh(new Date());
    } catch (err) {
      setError('Could not load dashboard data. Ensure the backend is running on port 8000.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAll(); }, []);

  // Normalize bias scores to 0–100 for radar
  const radarData = bias?.metrics?.map(m => ({
    metric: m.metric.replace(' Bias', ''),
    score:  Math.round(m.score * 100),
    fullMark: 100,
  })) ?? [];

  const kpis = [
    {
      icon: Scale, label: 'Total Cases Indexed', gradient: 'linear-gradient(135deg,#6366f1,#818cf8)',
      value: system ? system.total_cases.toLocaleString() : '—',
      sub: 'Documents in vector store',
    },
    {
      icon: Search, label: 'Total Queries Run', gradient: 'linear-gradient(135deg,#a855f7,#c084fc)',
      value: system ? system.total_queries.toLocaleString() : '—',
      sub: 'Across all agents',
    },
    {
      icon: Zap, label: 'Avg Response Time', gradient: 'linear-gradient(135deg,#06b6d4,#22d3ee)',
      value: system ? `${system.avg_response_time_ms} ms` : '—',
      sub: 'End-to-end latency',
    },
    {
      icon: Database, label: 'Embeddings Stored', gradient: 'linear-gradient(135deg,#10b981,#34d399)',
      value: system ? system.embeddings_stored.toLocaleString() : '—',
      sub: 'Chroma vector chunks',
    },
  ];

  return (
    <div className="w-full min-h-screen px-4 sm:px-6 lg:px-8 py-8" style={{ color: '#e2e8f0' }}>

      {/* ── header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">
            Analytics <span className="text-gradient">Dashboard</span>
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Legal intelligence metrics · Last updated {lastRefresh.toLocaleTimeString()}
          </p>
        </div>
        <button
          onClick={fetchAll}
          disabled={loading}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold border border-white/20 text-slate-300 hover:text-white hover:bg-white/10 transition-all duration-200"
        >
          <RefreshCw size={15} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {/* ── error banner ── */}
      {error && (
        <div className="mb-6 flex items-center gap-3 px-5 py-4 rounded-xl border border-rose-500/30 bg-rose-950/30 text-rose-300 text-sm">
          <AlertTriangle size={16} className="flex-shrink-0" />
          {error}
        </div>
      )}

      {/* ══ ROW 1 – KPI Cards ══ */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {kpis.map((kpi, i) => (
          <KpiCard key={i} loading={loading} {...kpi} />
        ))}
      </div>

      {/* ══ ROW 2 – Line + Bar ══ */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-5 mb-5">

        {/* Line Chart */}
        <ChartCard>
          <SectionTitle icon={TrendingUp} title="Cases Processed Over Time" color={C.indigo} />
          {loading
            ? <div className="h-64 rounded-xl animate-pulse" style={{ background: 'rgba(148,163,184,0.08)' }} />
            : (
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={cases?.timeline ?? []} margin={{ top: 5, right: 20, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={CHART_THEME.grid} />
                  <XAxis dataKey="month" tick={{ fill: CHART_THEME.text, fontSize: 11 }} tickLine={false} axisLine={false} />
                  <YAxis tick={{ fill: CHART_THEME.text, fontSize: 11 }} tickLine={false} axisLine={false} />
                  <Tooltip content={<CustomTooltip />} />
                  <defs>
                    <linearGradient id="lineGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor={C.indigo} stopOpacity={0.3} />
                      <stop offset="95%" stopColor={C.indigo} stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <Line
                    type="monotone" dataKey="count" name="Cases"
                    stroke={C.indigo} strokeWidth={2.5} dot={{ r: 3.5, fill: C.indigo, strokeWidth: 0 }}
                    activeDot={{ r: 6, fill: C.indigo }}
                  />
                </LineChart>
              </ResponsiveContainer>
            )
          }
        </ChartCard>

        {/* Bar Chart */}
        <ChartCard>
          <SectionTitle icon={BarChart2} title="Cases by Court" color={C.purple} />
          {loading
            ? <div className="h-64 rounded-xl animate-pulse" style={{ background: 'rgba(148,163,184,0.08)' }} />
            : (
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={cases?.by_court ?? []} layout="vertical" margin={{ top: 0, right: 20, left: 10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={CHART_THEME.grid} horizontal={false} />
                  <XAxis type="number" tick={{ fill: CHART_THEME.text, fontSize: 11 }} tickLine={false} axisLine={false} />
                  <YAxis type="category" dataKey="court" width={160} tick={{ fill: CHART_THEME.text, fontSize: 11 }} tickLine={false} axisLine={false} />
                  <Tooltip content={<CustomTooltip />} />
                  <defs>
                    <linearGradient id="barGrad" x1="0" y1="0" x2="1" y2="0">
                      <stop offset="0%"   stopColor={C.indigo} />
                      <stop offset="100%" stopColor={C.purple} />
                    </linearGradient>
                  </defs>
                  <Bar dataKey="count" name="Cases" fill="url(#barGrad)" radius={[0, 5, 5, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )
          }
        </ChartCard>
      </div>

      {/* ══ ROW 3 – Pie + Radar + Query Table ══ */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">

        {/* Pie Chart */}
        <ChartCard>
          <SectionTitle icon={PieIcon} title="Legal Topic Distribution" color={C.cyan} />
          {loading
            ? <div className="h-64 rounded-xl animate-pulse" style={{ background: 'rgba(148,163,184,0.08)' }} />
            : (
              <>
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={LEGAL_TOPICS} cx="50%" cy="50%"
                      innerRadius={55} outerRadius={85}
                      dataKey="value" nameKey="name"
                      activeIndex={pieIdx}
                      activeShape={renderActiveShape}
                      onMouseEnter={(_, idx) => setPieIdx(idx)}
                    >
                      {LEGAL_TOPICS.map((_, i) => (
                        <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} stroke="transparent" />
                      ))}
                    </Pie>
                    <Tooltip content={<CustomTooltip />} />
                  </PieChart>
                </ResponsiveContainer>
                {/* Legend */}
                <div className="grid grid-cols-2 gap-x-4 gap-y-1 mt-3">
                  {LEGAL_TOPICS.map((t, i) => (
                    <div key={i} className="flex items-center gap-1.5 text-xs text-slate-400">
                      <span className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                        style={{ background: PIE_COLORS[i % PIE_COLORS.length] }} />
                      {t.name}
                    </div>
                  ))}
                </div>
              </>
            )
          }
        </ChartCard>

        {/* Radar Chart */}
        <ChartCard>
          <SectionTitle icon={Activity} title="Bias Detection Metrics" color={C.rose} />
          {loading
            ? <div className="h-64 rounded-xl animate-pulse" style={{ background: 'rgba(148,163,184,0.08)' }} />
            : (
              <ResponsiveContainer width="100%" height={260}>
                <RadarChart data={radarData} margin={{ top: 10, right: 20, bottom: 10, left: 20 }}>
                  <PolarGrid stroke={CHART_THEME.grid} />
                  <PolarAngleAxis dataKey="metric" tick={{ fill: CHART_THEME.text, fontSize: 11 }} />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: CHART_THEME.text, fontSize: 9 }} />
                  <defs>
                    <linearGradient id="radarGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%"   stopColor={C.rose}   stopOpacity={0.6} />
                      <stop offset="100%" stopColor={C.purple} stopOpacity={0.2} />
                    </linearGradient>
                  </defs>
                  <Radar
                    name="Bias Score (%)" dataKey="score" fullMark={100}
                    stroke={C.rose} fill="url(#radarGrad)" strokeWidth={2}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend
                    iconType="circle" iconSize={8}
                    wrapperStyle={{ fontSize: 12, color: CHART_THEME.text }}
                  />
                </RadarChart>
              </ResponsiveContainer>
            )
          }
        </ChartCard>

        {/* Query Heatmap Table */}
        <ChartCard>
          <SectionTitle icon={Search} title="Most Searched Queries" color={C.amber} />
          {loading
            ? <div className="h-64 rounded-xl animate-pulse" style={{ background: 'rgba(148,163,184,0.08)' }} />
            : (
              <div className="overflow-hidden rounded-xl border border-white/5">
                <table className="w-full text-xs">
                  <thead>
                    <tr style={{ background: 'rgba(99,102,241,0.12)' }}>
                      <th className="px-3 py-2.5 text-left text-slate-400 font-semibold">#</th>
                      <th className="px-3 py-2.5 text-left text-slate-400 font-semibold">Query</th>
                      <th className="px-3 py-2.5 text-left text-slate-400 font-semibold">Cat</th>
                      <th className="px-3 py-2.5 text-right text-slate-400 font-semibold">Hits</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(queries?.top_queries ?? []).map((q, i) => {
                      const maxCount = queries.top_queries[0]?.count || 1;
                      const heatPct  = q.count / maxCount;          // 0–1
                      // heat: low count → cool blue, high count → warm violet/indigo
                      const heatAlpha = 0.1 + heatPct * 0.35;
                      const rowBg = `rgba(99,102,241,${heatAlpha.toFixed(2)})`;
                      return (
                        <tr key={i} style={{ background: rowBg, borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                          <td className="px-3 py-2 text-slate-500 font-mono">{i + 1}</td>
                          <td className="px-3 py-2 text-slate-200 max-w-0 truncate" style={{ maxWidth: 1 }}>
                            <span title={q.query}>{q.query}</span>
                          </td>
                          <td className="px-3 py-2"><CategoryBadge cat={q.category} /></td>
                          <td className="px-3 py-2 text-right font-semibold text-white">{q.count}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )
          }
        </ChartCard>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
