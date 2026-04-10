import { useState, useEffect, useCallback } from 'react'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import UploadZone from './components/UploadZone'
import TransactionList from './components/TransactionList'
import CategoryAlert from './components/CategoryAlert'
import ProcessedLog from './components/ProcessedLog'
import SuccessBanner from './components/SuccessBanner'
import { uploadDocumentStream, getCategories, syncTransactions, getLog, getDemoData, createSheet, getSheetStatus } from './api'

export default function App() {
  const [year, setYear] = useState(2025)
  const [month, setMonth] = useState('March')
  const [view, setView] = useState('main') // 'main' | 'success'
  const [transactions, setTransactions] = useState([])
  const [logEntries, setLogEntries] = useState([])
  const [categories, setCategories] = useState([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [isSyncing, setIsSyncing] = useState(false)
  const [syncResult, setSyncResult] = useState(null)
  const [parseResult, setParseResult] = useState(null)
  const [error, setError] = useState(null)
  const [progressMessage, setProgressMessage] = useState(null)
  const [monthMismatch, setMonthMismatch] = useState(null)
  const [sheetUrl, setSheetUrl] = useState(null)
  const [isCreatingSheet, setIsCreatingSheet] = useState(false)

  const newCategories = transactions
    .filter((t) => t.is_new_category)
    .map((t) => t.category)
    .filter((v, i, a) => a.indexOf(v) === i)

  // Fetch categories, log, and sheet status on mount and when year changes
  const fetchData = useCallback(async () => {
    try {
      const [cats, log, status] = await Promise.all([
        getCategories(year).catch(() => []),
        getLog().catch(() => []),
        getSheetStatus(year).catch(() => ({ exists: false })),
      ])
      setCategories(cats)
      setLogEntries(log)
      setSheetUrl(status.url || null)
    } catch (err) {
      console.error('Failed to fetch data:', err)
    }
  }, [year])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  async function handleFileSelected(file) {
    setError(null)
    setIsProcessing(true)
    setProgressMessage('Uploading document...')
    try {
      const result = await uploadDocumentStream(file, year, month, (event) => {
        setProgressMessage(event.message)
      })
      setParseResult(result)
      setTransactions(result.transactions || [])
      setProgressMessage(null)
      // Check for month mismatch
      if (result.statement_period) {
        const detectedMonth = result.statement_period.split(' ')[0]
        if (detectedMonth && detectedMonth.toLowerCase() !== month.toLowerCase()) {
          setMonthMismatch({ detected: result.statement_period, selected: month })
        } else {
          setMonthMismatch(null)
        }
      }
    } catch (err) {
      setError(err.message)
      setProgressMessage(null)
    } finally {
      setIsProcessing(false)
    }
  }

  function handleApprove(index) {
    setTransactions((prev) =>
      prev.map((t, i) => (i === index ? { ...t, approved: !t.approved } : t))
    )
  }

  function handleApproveAll() {
    setTransactions((prev) => prev.map((t) => ({ ...t, approved: true })))
  }

  function handleEdit(index) {
    // Toggle inline edit mode (handled inside TransactionList)
    setTransactions((prev) =>
      prev.map((t, i) => (i === index ? { ...t, _editing: !t._editing } : t))
    )
  }

  function handleUpdateTransaction(index, updates) {
    setTransactions((prev) =>
      prev.map((t, i) => (i === index ? { ...t, ...updates, _editing: false } : t))
    )
  }

  function handleMapCategory(oldCat, newCat) {
    setTransactions((prev) =>
      prev.map((t) =>
        t.category === oldCat ? { ...t, category: newCat, is_new_category: false } : t
      )
    )
  }

  function handleKeepCategory(cat) {
    setTransactions((prev) =>
      prev.map((t) =>
        t.category === cat ? { ...t, is_new_category: false } : t
      )
    )
  }

  async function handleSync() {
    const approved = transactions.filter((t) => t.approved)
    if (approved.length === 0) {
      setError('No transactions approved. Approve at least one before syncing.')
      return
    }

    setError(null)
    setIsSyncing(true)
    try {
      const result = await syncTransactions(year, month, transactions, parseResult?.filename || 'unknown.pdf')
      setSyncResult(result)
      setView('success')
      // Refresh log
      const log = await getLog()
      setLogEntries(log)
    } catch (err) {
      setError(err.message)
    } finally {
      setIsSyncing(false)
    }
  }

  async function handleCreateSheet() {
    setError(null)
    setIsCreatingSheet(true)
    try {
      const result = await createSheet(year)
      setSheetUrl(result.url)
      // Refresh categories from the new sheet
      const cats = await getCategories(year).catch(() => [])
      setCategories(cats)
    } catch (err) {
      setError(err.message)
    } finally {
      setIsCreatingSheet(false)
    }
  }

  async function handleLoadDemo() {
    setError(null)
    setIsProcessing(true)
    try {
      const result = await getDemoData()
      setParseResult(result)
      setTransactions(result.transactions || [])
      setYear(2025)
      setMonth('March')
    } catch (err) {
      setError(err.message)
    } finally {
      setIsProcessing(false)
    }
  }

  function handleProcessNew() {
    setView('main')
    setTransactions([])
    setParseResult(null)
    setSyncResult(null)
    setError(null)
    setMonthMismatch(null)
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar
        year={year}
        onYearChange={setYear}
        activeMonth={month}
        onMonthSelect={setMonth}
        sheetUrl={sheetUrl}
        onCreateSheet={handleCreateSheet}
        isCreatingSheet={isCreatingSheet}
      />

      <main className="ml-64 min-h-screen flex-grow">
        <Header month={month} year={year} />

        <div className="px-12 py-8 max-w-7xl mx-auto space-y-12">
          {error && (
            <div className="bg-error-container text-on-error-container p-4 rounded-xl flex items-center gap-3">
              <span className="material-symbols-outlined">error</span>
              <p className="text-sm font-medium">{error}</p>
              <button onClick={() => setError(null)} className="ml-auto">
                <span className="material-symbols-outlined text-sm">close</span>
              </button>
            </div>
          )}

          {view === 'main' && (
            <>
              <UploadZone onFileSelected={handleFileSelected} isProcessing={isProcessing} onLoadDemo={handleLoadDemo} progressMessage={progressMessage} />

              {monthMismatch && (
                <div className="bg-amber-50 border border-amber-300 text-amber-900 p-4 rounded-xl flex items-center gap-3">
                  <span className="material-symbols-outlined text-amber-600">warning</span>
                  <p className="text-sm font-medium">
                    This looks like a <strong>{monthMismatch.detected}</strong> statement, but you have <strong>{monthMismatch.selected}</strong> selected.
                    Transactions will sync to the {monthMismatch.selected} tab. Change the month in the sidebar if needed.
                  </p>
                  <button onClick={() => setMonthMismatch(null)} className="ml-auto text-amber-600 hover:text-amber-800">
                    <span className="material-symbols-outlined text-sm">close</span>
                  </button>
                </div>
              )}

              {transactions.length > 0 && (
                <section className="grid grid-cols-1 lg:grid-cols-5 gap-8 items-start">
                  {/* Statement Preview */}
                  <div className="lg:col-span-2 space-y-4">
                    <div className="flex items-center justify-between">
                      <h3 className="text-xs uppercase tracking-wider text-secondary font-semibold">
                        Statement Preview
                      </h3>
                      <span className="text-xs text-on-surface-variant">
                        {parseResult?.filename || ''}
                      </span>
                    </div>
                    <div className="aspect-[3/4] bg-white rounded-xl shadow-sm border border-outline-variant/10 overflow-hidden relative">
                      {parseResult?.preview_image ? (
                        <img
                          src={`data:image/png;base64,${parseResult.preview_image}`}
                          alt="Document preview"
                          className="w-full h-full object-contain"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-on-surface-variant">
                          <div className="text-center">
                            <span className="material-symbols-outlined text-5xl mb-2 block">description</span>
                            <p className="text-sm">Document preview</p>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="lg:col-span-3 space-y-4">
                    <CategoryAlert
                      newCategories={newCategories}
                      existingCategories={categories}
                      onMapCategory={handleMapCategory}
                      onKeepCategory={handleKeepCategory}
                    />
                    <TransactionList
                      transactions={transactions}
                      onApprove={handleApprove}
                      onApproveAll={() => {
                        handleApproveAll()
                        // Auto-sync after confirming all
                      }}
                      onEdit={handleEdit}
                      onUpdate={handleUpdateTransaction}
                      onSync={handleSync}
                      categories={categories}
                      isSyncing={isSyncing}
                      year={year}
                    />
                  </div>
                </section>
              )}

              <ProcessedLog entries={logEntries} />
            </>
          )}

          {view === 'success' && (
            <>
              <SuccessBanner
                syncResult={syncResult}
                year={year}
                month={month}
                onProcessNew={handleProcessNew}
              />
              <ProcessedLog entries={logEntries} />
            </>
          )}
        </div>
      </main>

      {/* Floating Action Button */}
      <button
        onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
        className="fixed bottom-8 right-8 cta-gradient w-14 h-14 rounded-full flex items-center justify-center text-white shadow-2xl hover:scale-110 active:scale-90 transition-all z-50"
      >
        <span className="material-symbols-outlined text-2xl">add</span>
      </button>
    </div>
  )
}
