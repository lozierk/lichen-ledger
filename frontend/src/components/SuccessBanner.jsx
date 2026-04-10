const SHEET_URLS = {
  2025: 'https://docs.google.com/spreadsheets/d/1LPu8pOIuPIf6CaHY4D5gnH9yfSYMl01UgRVuPBx6bjQ/edit',
  2026: 'https://docs.google.com/spreadsheets/d/1MW2qq5L2ITGOQSgZR3KbzSBYlY3bOboXl1Ro_mBmSLc/edit',
}

export default function SuccessBanner({ syncResult, year, month, onProcessNew }) {
  if (!syncResult) return null

  return (
    <div className="space-y-12">
      {/* Hero Banner */}
      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-12 md:col-span-8 bg-surface-container-lowest rounded-xl p-10 flex flex-col items-center justify-center text-center shadow-sm relative overflow-hidden">
          <div className="absolute top-0 right-0 p-8 opacity-5">
            <span className="material-symbols-outlined text-[120px] text-primary">check_circle</span>
          </div>
          <div className="w-20 h-20 bg-primary-fixed rounded-full flex items-center justify-center mb-6">
            <span
              className="material-symbols-outlined text-on-primary-fixed text-4xl"
              style={{ fontVariationSettings: "'FILL' 1" }}
            >
              check_circle
            </span>
          </div>
          <h2 className="text-3xl font-headline font-extrabold text-on-surface tracking-tight mb-2">
            Sync Complete
          </h2>
          <p className="text-on-surface-variant text-sm max-w-md mx-auto">
            All {syncResult.transaction_count} transactions from{' '}
            <span className="font-bold text-primary">{syncResult.filename}</span> have been
            successfully parsed and synced to your fiscal ledger.
          </p>
          <div className="mt-8 flex space-x-4">
            <a
              href={SHEET_URLS[year]}
              target="_blank"
              rel="noopener noreferrer"
              className="success-gradient text-white px-8 py-3 rounded-full font-bold text-sm shadow-lg hover:opacity-90 transition-all flex items-center"
            >
              <span className="material-symbols-outlined mr-2">grid_on</span>
              View Sheet
            </a>
            <button
              onClick={onProcessNew}
              className="bg-surface-container text-on-secondary-container px-8 py-3 rounded-full font-bold text-sm hover:bg-surface-container-high transition-all flex items-center"
            >
              Process New
            </button>
          </div>
        </div>

        <div className="col-span-12 md:col-span-4 bg-tertiary-fixed rounded-xl p-8 flex flex-col justify-between shadow-sm border border-tertiary-fixed-dim/20">
          <div>
            <h3 className="text-on-tertiary-fixed-variant font-bold text-sm uppercase tracking-widest mb-4">
              {month} Summary
            </h3>
            <div className="space-y-4">
              <div>
                <span className="text-xs text-on-tertiary-fixed/60 uppercase">Processed Today</span>
                <p className="text-2xl font-black text-on-tertiary-fixed">
                  {syncResult.total_amount || `${syncResult.transaction_count} items`}
                </p>
              </div>
              <div className="h-[1px] bg-on-tertiary-fixed/10"></div>
              <div>
                <span className="text-xs text-on-tertiary-fixed/60 uppercase">Sheet Records</span>
                <p className="text-2xl font-black text-on-tertiary-fixed">
                  {syncResult.sheet_total || 'Updated'}
                </p>
              </div>
            </div>
          </div>
          <div className="mt-6">
            <span className="text-[10px] font-bold text-on-tertiary-fixed/40 uppercase">
              Last Sync: just now
            </span>
          </div>
        </div>
      </div>

      {/* Empty Queue */}
      <section>
        <div className="flex justify-between items-end mb-6">
          <h3 className="text-lg font-bold text-on-surface tracking-tight">Active Workspace</h3>
          <span className="text-secondary bg-secondary-fixed px-3 py-1 rounded-full text-[10px] font-bold">
            QUEUE EMPTY
          </span>
        </div>
        <div className="bg-surface-container-low rounded-xl border border-dashed border-outline-variant/30 p-16 flex flex-col items-center justify-center text-center">
          <div className="w-16 h-16 bg-surface-container-lowest rounded-full flex items-center justify-center mb-4 text-outline">
            <span className="material-symbols-outlined text-3xl">inbox</span>
          </div>
          <p className="text-on-surface-variant font-medium">Your parsing queue is clear.</p>
          <p className="text-on-surface-variant/60 text-sm mt-1">
            Upload a PDF or CSV statement to begin the next reconciliation.
          </p>
        </div>
      </section>
    </div>
  )
}
