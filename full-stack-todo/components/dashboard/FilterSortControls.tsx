import React, { useState } from 'react';
import { Filter, ChevronDown } from 'lucide-react';
import { FilterSortParams } from '../../types';


const FilterSortControls: React.FC<{ onApplyFilters: (f: FilterSortParams) => void; onResetFilters: () => void }> = ({ onApplyFilters, onResetFilters }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="mb-6">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest text-slate-500 hover:text-indigo-400 focus:text-indigo-400 active:text-indigo-400 transition-colors"
      >
        <Filter size={12} /> Filter & Sort <ChevronDown size={12} className={isOpen ? 'rotate-180' : ''} />
      </button>
      
      {isOpen && (
        <div className="mt-3 p-4 bg-slate-900/80 border border-slate-800 rounded-2xl grid grid-cols-2 gap-3 animate-in fade-in slide-in-from-top-2">
          <select 
            title="Status"
            className="bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white outline-none"
            onChange={(e) => onApplyFilters({ status: e.target.value as any })}
          >
            <option value="all">All Status</option>
            <option value="pending">Pending</option>
            <option value="completed">Done</option>
          </select>
          <select 
            title="Sort By"
            className="bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white outline-none"
            onChange={(e) => onApplyFilters({ sort_by: e.target.value as any })}
          >
            <option value="created_at">Newest</option>
            <option value="due_date">Due Date</option>
            <option value="priority">Priority</option>
          </select>
          <button onClick={onResetFilters} className="col-span-2 text-[10px] text-slate-500 hover:text-red-400 focus:text-red-400 active:text-red-400 uppercase font-bold">Reset All</button>
        </div>
      )}
    </div>
  );
};

export default FilterSortControls;