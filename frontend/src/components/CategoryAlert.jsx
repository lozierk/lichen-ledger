import { useState } from 'react'

export default function CategoryAlert({ newCategories, existingCategories, onMapCategory, onKeepCategory }) {
  const [mappings, setMappings] = useState({})

  if (!newCategories || newCategories.length === 0) return null

  return (
    <div className="space-y-3">
      {newCategories.map((cat) => (
        <div
          key={cat}
          className="bg-secondary-fixed/50 border-l-4 border-secondary p-4 rounded-r-xl flex items-center justify-between"
        >
          <div className="flex items-center gap-3">
            <span className="material-symbols-outlined text-secondary">new_releases</span>
            <div>
              <p className="text-on-secondary-fixed text-sm font-bold">New Category Detected</p>
              <p className="text-xs text-on-surface-variant">
                "{cat}" doesn't match your ledger.
              </p>
            </div>
          </div>
          <div className="flex gap-2">
            <input
              type="text"
              list={`categories-${cat}`}
              placeholder="Map to..."
              value={mappings[cat] || ''}
              onChange={(e) => setMappings({ ...mappings, [cat]: e.target.value })}
              className="bg-white border-none rounded-lg text-xs py-1.5 focus:ring-secondary"
            />
            <datalist id={`categories-${cat}`}>
              {existingCategories.map((c) => (
                <option key={c} value={c} />
              ))}
            </datalist>
            <button
              onClick={() => {
                if (mappings[cat]) onMapCategory(cat, mappings[cat])
              }}
              className="bg-secondary text-white px-3 py-1.5 rounded-lg text-xs"
            >
              Save
            </button>
            <button
              onClick={() => onKeepCategory(cat)}
              className="bg-stone-200 text-stone-700 px-3 py-1.5 rounded-lg text-xs"
            >
              Keep
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}
