import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Scale, Search, AlertTriangle, BookOpen, Brain, Shield } from 'lucide-react';

const Home = () => {
  const navigate = useNavigate();

  const agents = [
    {
      id: 'legal-knowledge',
      icon: BookOpen,
      title: 'Legal Knowledge Agent',
      description: 'Retrieve and summarize judgments using advanced RAG techniques. Get comprehensive case summaries with citations.',
      color: 'blue',
      path: '/legal-knowledge',
      gradient: 'from-blue-500 to-cyan-500',
    },
    {
      id: 'comparison',
      icon: Brain,
      title: 'Case Comparison Agent',
      description: 'Compare rulings and highlight contradictions, similarities, and legal evolution over time.',
      color: 'purple',
      path: '/comparison',
      gradient: 'from-purple-500 to-pink-500',
    },
    {
      id: 'bias-detection',
      icon: Shield,
      title: 'Bias & Conflict Agent',
      description: 'Detect institutional or policy biases across rulings. Identify potential conflicts and contradictions.',
      color: 'red',
      path: '/bias-detection',
      gradient: 'from-red-500 to-orange-500',
    },
  ];

  const steps = [
    { number: '1', title: 'Ingest', description: 'Upload PDFs or search the Indian Kanoon database.' },
    { number: '2', title: 'Analyze', description: 'Legal-BERT embeds text while GPT-4 synthesizes insights.' },
    { number: '3', title: 'Deliver', description: 'Get cited summaries, comparisons, and bias reports.' },
  ];

  return (
    <div className="min-h-screen bg-[#0a0e1a]">
      {/* Hero Section */}
      <div className="relative overflow-hidden particles-bg bg-gradient-to-b from-[#0a0e1a] via-[#0f1117] to-[#0a0e1a]">
        {/* Animated Background */}
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-gradient-to-br from-indigo-900/30 via-purple-900/30 to-pink-900/30"></div>
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
        </div>

        {/* Hero Content */}
        <div className="container px-6 py-24 text-center relative z-10">
          {/* Hero Image */}
          <div className="mb-8 flex justify-center">
            <img
              src="/lexiguard-ai-logo.jpg"
              alt="LexiGuard AI - Legal Intelligence"
              className="w-80 h-80 object-contain drop-shadow-2xl animate-fade-in"
              style={{ filter: 'drop-shadow(0 0 40px rgba(139, 92, 246, 0.4))' }}
            />
          </div>

          <h1 className="text-6xl md:text-7xl font-bold mb-6 animate-fade-in text-white">
            LexiGuard <span className="text-gradient">AI</span>
          </h1>
          <p className="text-3xl md:text-4xl font-semibold text-gray-300 mb-4 animate-slide-up">
            The Future of <span className="text-gradient-gold">Legal Intelligence</span>
          </p>
          <p className="text-lg text-gray-400 max-w-3xl mx-auto mb-10 animate-slide-up leading-relaxed">
            A sophisticated 3-Agent RAG framework for comparative legal research, case analysis, and bias detection in judicial decisions.
          </p>
          <div className="flex items-center justify-center gap-4 animate-slide-up">
            <button
              onClick={() => navigate('/legal-knowledge')}
              className="btn-primary text-lg"
            >
              Explore Agents
            </button>
            <button
              onClick={() => navigate('/comparison')}
              className="btn-secondary text-lg"
            >
              Compare Cases
            </button>
          </div>
        </div>

        {/* Decorative Bottom Wave */}
        <div className="absolute bottom-0 left-0 right-0 h-24 bg-gradient-to-t from-background to-transparent"></div>
      </div>

      {/* Agents Grid */}
      <div className="container px-6 py-20 relative z-10 bg-[#0a0e1a]">
        <h2 className="text-4xl font-bold text-center mb-4 text-white">
          Our <span className="text-gradient">Agents</span>
        </h2>
        <p className="text-center text-gray-400 mb-12 text-lg">
          Powered by cutting-edge AI to transform legal research
        </p>

        <div className="grid md:grid-cols-3 gap-8 items-stretch max-w-6xl mx-auto">
          {agents.map((agent, idx) => {
            const Icon = agent.icon;

            return (
              <div
                key={agent.id}
                className="bg-gradient-to-br from-[#252b4a] to-[#1a1f3a] backdrop-blur-xl rounded-2xl border-2 border-white/40 shadow-2xl p-8 hover:shadow-purple-500/40 hover:-translate-y-2 hover:border-purple-400 hover:from-[#2d3561] hover:to-[#252b4a] transition-all duration-300 group cursor-pointer h-full flex flex-col"
                onClick={() => navigate(agent.path)}
                style={{ animationDelay: `${idx * 150}ms` }}
              >
                {/* Icon with Gradient Background */}
                <div className={`w-20 h-20 rounded-2xl bg-gradient-to-br ${agent.gradient} p-4 mb-6 group-hover:scale-110 transition-transform duration-300 shadow-2xl`}>
                  <Icon className="w-full h-full text-white drop-shadow-lg" />
                </div>

                <h3 className="text-2xl font-bold text-white mb-4 drop-shadow-lg">
                  {agent.title}
                </h3>

                <p className="text-gray-200 mb-6 flex-1 leading-relaxed text-base">
                  {agent.description}
                </p>

                <button className="w-full inline-flex items-center justify-center gap-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-3 rounded-xl font-bold shadow-lg hover:shadow-xl hover:scale-105 hover:from-indigo-500 hover:to-purple-500 transition-all duration-300 mt-auto">
                  Launch Agent →
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {/* How It Works Section */}
      <div className="container px-6 py-20 relative bg-[#0f1117]">
        <div className="section-divider"></div>

        <h2 className="text-4xl font-bold text-center mb-4 text-white">
          How It <span className="text-gradient">Works</span>
        </h2>
        <p className="text-center text-gray-400 mb-16 text-lg">
          Our advanced RAG pipeline transforms raw legal documents into actionable intelligence
        </p>

        <div className="grid md:grid-cols-3 gap-12 max-w-5xl mx-auto">
          {steps.map((step, idx) => (
            <div key={idx} className="relative flex flex-col items-center text-center">
              {/* Step Number Circle */}
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center mb-6 shadow-2xl glow">
                <span className="text-3xl font-black text-white">{step.number}</span>
              </div>

              {/* Connecting Line (except for last item) */}
              {idx < steps.length - 1 && (
                <div className="hidden md:block absolute top-10 left-[60%] w-full h-0.5 bg-gradient-to-r from-purple-500/50 to-transparent"></div>
              )}

              <h3 className="text-2xl font-bold text-white mb-3">{step.title}</h3>
              <p className="text-gray-300 leading-relaxed">{step.description}</p>
            </div>
          ))}
        </div>

        <div className="section-divider mt-16"></div>
      </div>

      {/* Features Section */}
      <div className="container px-6 py-20 bg-[#0a0e1a]">
        <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          <div className="bg-[#1a1f3a]/80 backdrop-blur-xl rounded-2xl border border-white/20 shadow-2xl p-6 hover:shadow-blue-500/20 hover:border-blue-500/50 transition-all duration-300">
            <div className="flex items-start gap-4 mb-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center flex-shrink-0 shadow-lg">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-2xl font-bold text-white mb-3">
                  Advanced RAG Technology
                </h3>
                <p className="text-gray-300 leading-relaxed">
                  Powered by Legal-BERT, RoBERTa-MNLI, GPT-4, and vector databases for accurate legal document retrieval and analysis.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-[#1a1f3a]/80 backdrop-blur-xl rounded-2xl border border-white/20 shadow-2xl p-6 hover:shadow-purple-500/20 hover:border-purple-500/50 transition-all duration-300">
            <div className="flex items-start gap-4 mb-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center flex-shrink-0 shadow-lg">
                <Scale className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-2xl font-bold text-white mb-3">
                  Explainable AI
                </h3>
                <p className="text-gray-300 leading-relaxed">
                  Every agent provides transparent reasoning traces, model information, and confidence scores for academic and professional use.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;

