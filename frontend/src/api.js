const API = '/api'

export async function uploadDocument(file, year, month) {
  const form = new FormData()
  form.append('file', file)
  form.append('year', year)
  form.append('month', month)

  const res = await fetch(`${API}/upload`, { method: 'POST', body: form })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Upload failed' }))
    throw new Error(err.detail || 'Upload failed')
  }
  return res.json()
}

export async function getCategories(year) {
  const res = await fetch(`${API}/categories?year=${year}`)
  const data = await res.json()
  return data.categories
}

export async function getAccounts(year) {
  const res = await fetch(`${API}/accounts?year=${year}`)
  const data = await res.json()
  return data.accounts
}

export async function syncTransactions(year, month, transactions, filename) {
  const res = await fetch(`${API}/sync`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ year, month, transactions, filename }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Sync failed' }))
    throw new Error(err.detail || 'Sync failed')
  }
  return res.json()
}

export async function getLog() {
  const res = await fetch(`${API}/log`)
  const data = await res.json()
  return data.entries
}

export async function getSummary(year, month) {
  const res = await fetch(`${API}/summary/${year}/${month}`)
  return res.json()
}
