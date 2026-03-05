import React, { useState } from 'react';
import { Search } from 'lucide-react';

const SearchBox = ({ onSearch, placeholder = 'Enter case name or keywords...', buttonText = 'Search' }) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-3xl mx-auto">
      <div className="flex gap-2">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-text-muted" size={20} />
          <input
            type="text"
            aria-label="Search legal cases"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={placeholder}
            className="input-premium w-full pl-10"
          />
        </div>
        <button
          type="submit"
          disabled={!query.trim()}
          className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
        >
          {buttonText}
        </button>
      </div>
    </form>
  );
};

export default SearchBox;

