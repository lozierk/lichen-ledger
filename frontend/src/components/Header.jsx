export default function Header({ month, year }) {
  return (
    <header className="glass-header sticky top-0 z-40 w-full px-12 py-6 flex justify-between items-center">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-on-surface">Command Center</h2>
        <p className="text-on-surface-variant text-sm">
          Tax Season Transition &middot; {month} {year}
        </p>
      </div>
      <div className="flex items-center gap-4">
        <button className="p-2 rounded-full hover:bg-stone-200/50 transition-colors">
          <span className="material-symbols-outlined">notifications</span>
        </button>
        <button className="p-2 rounded-full hover:bg-stone-200/50 transition-colors">
          <span className="material-symbols-outlined">account_circle</span>
        </button>
      </div>
    </header>
  )
}
