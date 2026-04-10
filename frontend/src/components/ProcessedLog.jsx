export default function ProcessedLog({ entries }) {
  return (
    <section className="space-y-4">
      <h3 className="text-xs uppercase tracking-wider text-secondary font-semibold">
        Processed Statements Log
      </h3>
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-surface-container-low">
            <tr>
              <th className="px-6 py-4 text-[10px] text-secondary font-bold tracking-widest uppercase">
                Statement Name
              </th>
              <th className="px-6 py-4 text-[10px] text-secondary font-bold tracking-widest uppercase">
                Date Processed
              </th>
              <th className="px-6 py-4 text-[10px] text-secondary font-bold tracking-widest uppercase">
                Entries
              </th>
              <th className="px-6 py-4 text-[10px] text-secondary font-bold tracking-widest uppercase">
                Status
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-container">
            {(!entries || entries.length === 0) && (
              <tr>
                <td colSpan={4} className="px-6 py-8 text-center text-on-surface-variant text-sm">
                  No statements processed yet.
                </td>
              </tr>
            )}
            {entries?.map((entry, i) => (
              <tr key={i} className="hover:bg-surface-container-low transition-colors group">
                <td className="px-6 py-4 flex items-center gap-3">
                  <span className="material-symbols-outlined text-primary">
                    {entry.filename?.endsWith('.pdf') ? 'picture_as_pdf' : 'image'}
                  </span>
                  <span className="text-sm font-medium">{entry.filename}</span>
                </td>
                <td className="px-6 py-4 text-on-surface-variant text-sm italic">
                  {entry.date_processed}
                </td>
                <td className="px-6 py-4 text-on-surface-variant font-mono">
                  {entry.transaction_count}
                </td>
                <td className="px-6 py-4">
                  <div
                    className={`flex items-center gap-2 font-bold text-xs uppercase tracking-tight ${
                      entry.status === 'Synced'
                        ? 'text-emerald-700'
                        : 'text-secondary'
                    }`}
                  >
                    <span
                      className="material-symbols-outlined text-sm"
                      style={
                        entry.status === 'Synced'
                          ? { fontVariationSettings: "'FILL' 1" }
                          : {}
                      }
                    >
                      {entry.status === 'Synced' ? 'cloud_done' : 'hourglass_empty'}
                    </span>
                    {entry.status === 'Synced' ? 'Synced to Sheets' : 'Pending Confirmation'}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
