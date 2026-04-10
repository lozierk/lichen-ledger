import { useState } from 'react'

const MONTHS = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
]

export default function Sidebar({ year, onYearChange, activeMonth, onMonthSelect, sheetUrl, onCreateSheet, isCreatingSheet }) {
  return (
    <aside className="bg-stone-100 h-screen w-64 fixed left-0 top-0 overflow-y-auto z-50 flex flex-col py-8 px-4 space-y-1">
      <div className="mb-8 px-4">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-8 h-8 rounded bg-primary flex items-center justify-center text-white">
            <span className="material-symbols-outlined text-sm">potted_plant</span>
          </div>
          <h1 className="text-lg font-bold text-emerald-900">Lichen Ledger</h1>
        </div>

        <div className="mt-6 p-4 bg-white rounded-xl shadow-sm">
          <p className="font-['Inter'] text-sm uppercase tracking-wider text-stone-500 mb-1">Fiscal Year</p>
          <div className="flex items-center justify-between">
            <select
              value={year}
              onChange={(e) => onYearChange(Number(e.target.value))}
              className="text-lg font-bold text-emerald-900 bg-transparent border-none p-0 focus:ring-0 cursor-pointer"
            >
              <option value={2025}>2025</option>
              <option value={2026}>2026</option>
              <option value={2027}>2027</option>
            </select>
            <span className="material-symbols-outlined text-emerald-800">calendar_month</span>
          </div>
        </div>
      </div>

      <nav className="flex-1 space-y-1">
        {MONTHS.map((month) => (
          <button
            key={month}
            onClick={() => onMonthSelect(month)}
            className={`w-full text-left px-4 py-2 flex items-center justify-between transition-all duration-300 font-['Inter'] text-sm uppercase tracking-wider ${
              activeMonth === month
                ? 'bg-white text-emerald-900 font-bold rounded-lg ml-2 shadow-sm'
                : 'text-stone-600 hover:text-emerald-700 hover:bg-white/50'
            }`}
          >
            <span>{month}</span>
            <span className="material-symbols-outlined text-xs">chevron_right</span>
          </button>
        ))}
      </nav>

      <div className="pt-8 border-t border-stone-200 mt-auto">
        {sheetUrl ? (
          <a
            href={sheetUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-3 px-4 py-2 text-stone-600 hover:text-primary transition-colors text-sm font-medium"
          >
            <span className="material-symbols-outlined">table_chart</span>
            Open Google Sheet
          </a>
        ) : (
          <button
            onClick={onCreateSheet}
            disabled={isCreatingSheet}
            className="flex items-center gap-3 px-4 py-2 w-full text-left text-emerald-700 hover:text-emerald-900 hover:bg-emerald-50 rounded-lg transition-colors text-sm font-medium disabled:opacity-50"
          >
            {isCreatingSheet ? (
              <>
                <div className="w-4 h-4 border-2 border-emerald-300 border-t-emerald-700 rounded-full animate-spin"></div>
                Creating Sheet...
              </>
            ) : (
              <>
                <span className="material-symbols-outlined">add_circle</span>
                Create {year} Sheet
              </>
            )}
          </button>
        )}
        <div className="flex flex-col mt-4 space-y-1">
          <button className="px-4 py-2 text-stone-500 text-xs flex items-center gap-2">
            <span className="material-symbols-outlined text-sm">settings</span> Settings
          </button>
          <button className="px-4 py-2 text-stone-500 text-xs flex items-center gap-2">
            <span className="material-symbols-outlined text-sm">help</span> Support
          </button>
        </div>
      </div>
    </aside>
  )
}
