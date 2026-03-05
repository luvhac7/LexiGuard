import React from 'react';
import AnalyticsDashboard from '../components/AnalyticsDashboard';

const Analytics = () => {
    return (
        <div className="min-h-screen bg-[#0a0e1a]">
            {/* Page header hero strip */}
            <div className="relative overflow-hidden bg-gradient-to-b from-[#0f1117] to-[#0a0e1a] px-6 py-10 border-b border-white/10">
                <div className="absolute inset-0 pointer-events-none">
                    <div className="absolute top-0 left-1/4 w-72 h-72 bg-indigo-600/15 rounded-full blur-3xl" />
                    <div className="absolute bottom-0 right-1/4 w-72 h-72 bg-purple-600/15 rounded-full blur-3xl" />
                </div>
                <div className="relative z-10 max-w-7xl mx-auto">
                    <p className="text-xs font-semibold uppercase tracking-widest text-indigo-400 mb-1">
                        LexiGuard AI · Intelligence Hub
                    </p>
                    <h1 className="text-4xl font-bold text-white">
                        Analytics <span className="text-gradient">Overview</span>
                    </h1>
                    <p className="text-slate-400 mt-2 max-w-2xl">
                        Real-time metrics on indexed legal cases, query activity, bias signals, and system performance — in one unified view.
                    </p>
                </div>
            </div>

            {/* Dashboard component */}
            <div className="max-w-7xl mx-auto">
                <AnalyticsDashboard />
            </div>
        </div>
    );
};

export default Analytics;
