import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Scale } from 'lucide-react';

const Navbar = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Home' },
    { path: '/legal-knowledge', label: 'Legal Knowledge' },
    { path: '/comparison', label: 'Case Comparison' },
    { path: '/bias-detection', label: 'Bias Detection' },
    { path: '/analytics', label: 'Analytics' },
  ];

  return (
    <nav className="sticky top-0 z-50 bg-[#1a1f3a]/95 backdrop-blur-xl border-b-2 border-white/20 shadow-2xl">
      <div className="container px-6 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="p-2 rounded-xl bg-gradient-to-br from-indigo-600 to-purple-600 text-white shadow-lg group-hover:shadow-xl group-hover:scale-105 transition-all duration-200">
              <Scale size={20} />
            </div>
            <span className="text-2xl font-bold">
              <span className="text-white drop-shadow-lg">LexiGuard</span> <span className="text-gradient">AI</span>
            </span>
          </Link>

          <div className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  aria-current={isActive ? 'page' : undefined}
                  className={`px-4 py-2 rounded-xl font-semibold transition-all duration-200 ${isActive
                    ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg'
                    : 'text-gray-200 hover:text-white hover:bg-white/15'
                    }`}
                >
                  {item.label}
                </Link>
              );
            })}
            <Link to="/legal-knowledge" className="btn-secondary ml-2 !py-2">
              Get Started
            </Link>
          </div>
        </div>
      </div>
      <div className="h-px bg-gradient-to-r from-transparent via-purple-400/60 to-transparent" />
    </nav>
  );
};

export default Navbar;
