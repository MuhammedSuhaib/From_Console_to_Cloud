import React, { useState } from 'react';
import { Search, X } from 'lucide-react';

interface SearchBarProps {
  onSearch: (keyword: string) => void;
  onClear: () => void;
}

const SearchBar: React.FC<SearchBarProps> = ({ onSearch, onClear }) => {
  const [keyword, setKeyword] = useState<string>('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (keyword.trim()) onSearch(keyword.trim());
  };

  return (
    <div className="mb-4">
      <form onSubmit={handleSubmit} className="relative flex items-center">
        <Search className="absolute left-4 text-slate-500" size={16} />
        <input
          title="Search Tasks"
          aria-label="Search Tasks"
          type="text"
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          placeholder="Search micro-tasks..."
          className="w-full pl-11 pr-12 py-3 bg-slate-900/50 border border-slate-800 rounded-xl text-white outline-none focus:ring-2 focus:ring-indigo-500 transition-all text-sm"
        />
        {keyword && (
          <button
            type="button"
            title="Clear Search"
            onClick={() => { setKeyword(''); onClear(); }}
            className="absolute right-3 p-1 hover:bg-slate-800 focus:bg-slate-800 active:bg-slate-800 rounded-lg text-slate-400"
          >
            <X size={16} />
          </button>
        )}
      </form>
    </div>
  );
};

export default SearchBar;