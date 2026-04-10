import { useState } from 'react'

const CATEGORY_ICONS = {
  'Groceries': 'shopping_cart',
  'Office Supplies': 'print',
  'Cloud Infrastructure': 'cloud',
  'Software/SaaS': 'terminal',
  'AI/ML Services': 'smart_toy',
  'Health/Compliance Platform': 'health_and_safety',
  'Subcontractors': 'engineering',
  'Banking Fees': 'account_balance',
  'Data & Analytics': 'analytics',
  'Professional Services': 'work',
  'Education/Training': 'school',
  'Regulatory/Legal': 'gavel',
  'Insurance': 'shield',
  'Taxes': 'receipt_long',
  'Domain & Web Hosting': 'dns',
  'Travel/Transport': 'flight',
}

function getIcon(category) {
  return CATEGORY_ICONS[category] || 'receipt'
}

function EditRow({ tx, categories, onSave, onCancel, year }) {
  const [vendor, setVendor] = useState(tx.vendor)
  const [amount, setAmount] = useState(tx.amount)
  const [category, setCategory] = useState(tx.category)
  const [client, setClient] = useState(tx.client || '')
  const [notes, setNotes] = useState(tx.notes || '')

  return (
    <div className="p-4 bg-surface-container-low space-y-3">
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="text-[10px] uppercase text-secondary font-bold">Vendor</label>
          <input
            value={vendor}
            onChange={(e) => setVendor(e.target.value)}
            className="w-full text-sm border-none rounded-lg bg-white focus:ring-primary py-1.5"
          />
        </div>
        <div>
          <label className="text-[10px] uppercase text-secondary font-bold">Amount</label>
          <input
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            className="w-full text-sm border-none rounded-lg bg-white focus:ring-primary py-1.5 font-mono"
          />
        </div>
        <div>
          <label className="text-[10px] uppercase text-secondary font-bold">Category</label>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="w-full text-sm border-none rounded-lg bg-white focus:ring-primary py-1.5"
          >
            {categories.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
            {!categories.includes(category) && (
              <option value={category}>{category} (new)</option>
            )}
          </select>
        </div>
        {year >= 2026 && (
          <div>
            <label className="text-[10px] uppercase text-secondary font-bold">Client</label>
            <input
              value={client}
              onChange={(e) => setClient(e.target.value)}
              className="w-full text-sm border-none rounded-lg bg-white focus:ring-primary py-1.5"
            />
          </div>
        )}
        <div>
          <label className="text-[10px] uppercase text-secondary font-bold">Notes</label>
          <input
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className="w-full text-sm border-none rounded-lg bg-white focus:ring-primary py-1.5"
          />
        </div>
      </div>
      <div className="flex gap-2 justify-end">
        <button onClick={onCancel} className="text-xs text-stone-500 px-3 py-1.5">Cancel</button>
        <button
          onClick={() => onSave({ vendor, amount, category, client, notes, is_new_category: !categories.includes(category) })}
          className="bg-primary text-white text-xs px-4 py-1.5 rounded-lg"
        >
          Save
        </button>
      </div>
    </div>
  )
}

export default function TransactionList({
  transactions,
  onApprove,
  onApproveAll,
  onEdit,
  onUpdate,
  onSync,
  categories,
  isSyncing,
  year,
}) {
  if (!transactions || transactions.length === 0) return null

  const approvedCount = transactions.filter((t) => t.approved).length
  const allApproved = approvedCount === transactions.length

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-xs uppercase tracking-wider text-secondary font-semibold">
          Parsed Transactions
        </h3>
        <span className="bg-primary-fixed text-on-primary-fixed px-3 py-1 rounded-full text-xs font-bold">
          {transactions.length} New Detected
        </span>
      </div>

      <div className="bg-surface-container-lowest rounded-xl overflow-hidden shadow-sm">
        <div className="divide-y divide-surface-container">
          {transactions.map((tx, i) =>
            tx._editing ? (
              <EditRow
                key={i}
                tx={tx}
                categories={categories}
                year={year}
                onSave={(updates) => onUpdate(i, updates)}
                onCancel={() => onEdit(i)}
              />
            ) : (
              <div
                key={i}
                className="p-4 flex items-center justify-between hover:bg-surface-variant transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-full bg-stone-100 flex items-center justify-center text-secondary">
                    <span className="material-symbols-outlined">{getIcon(tx.category)}</span>
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-on-surface">{tx.vendor}</h4>
                    <p className="text-xs text-on-surface-variant">{tx.date}</p>
                  </div>
                </div>
                <div className="flex items-center gap-6">
                  <span
                    className={`text-[10px] uppercase font-black px-2.5 py-1 rounded-full tracking-tighter ${
                      tx.is_new_category
                        ? 'bg-error-container text-on-error-container'
                        : 'bg-primary-fixed text-on-primary-fixed'
                    }`}
                  >
                    {tx.is_new_category ? 'New Category?' : tx.category}
                  </span>
                  <span className="font-mono font-bold text-on-surface">-{tx.amount}</span>
                  <div className="flex gap-1">
                    <button
                      onClick={() => onApprove(i)}
                      className="w-8 h-8 rounded-full flex items-center justify-center hover:bg-primary/10 text-primary transition-colors"
                    >
                      <span
                        className="material-symbols-outlined text-xl"
                        style={tx.approved ? { fontVariationSettings: "'FILL' 1" } : {}}
                      >
                        check_circle
                      </span>
                    </button>
                    <button
                      onClick={() => onEdit(i)}
                      className="w-8 h-8 rounded-full flex items-center justify-center hover:bg-secondary/10 text-secondary transition-colors"
                    >
                      <span className="material-symbols-outlined text-xl">edit</span>
                    </button>
                  </div>
                </div>
              </div>
            )
          )}
        </div>
        <div className="bg-surface-container-low p-4 flex items-center justify-center gap-4">
          {!allApproved && (
            <button
              onClick={onApproveAll}
              className="text-primary font-bold text-sm hover:underline"
            >
              Confirm All {transactions.length} Transactions
            </button>
          )}
          {approvedCount > 0 && (
            <button
              onClick={onSync}
              disabled={isSyncing}
              className="cta-gradient px-6 py-2 rounded-full text-white font-bold text-sm shadow-lg hover:opacity-90 active:scale-95 transition-all disabled:opacity-50 flex items-center gap-2"
            >
              {isSyncing ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  Syncing...
                </>
              ) : (
                <>
                  <span className="material-symbols-outlined text-sm">cloud_upload</span>
                  Sync {approvedCount} to Sheets
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
