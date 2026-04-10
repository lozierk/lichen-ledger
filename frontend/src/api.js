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

export async function uploadDocumentStream(file, year, month, onProgress) {
  const form = new FormData()
  form.append('file', file)
  form.append('year', year)
  form.append('month', month)

  const res = await fetch(`${API}/upload-stream`, { method: 'POST', body: form })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Upload failed' }))
    throw new Error(err.detail || 'Upload failed')
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let finalResult = null
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    const lines = buffer.split('\n\n')
    buffer = lines.pop() // keep incomplete chunk

    for (const line of lines) {
      if (!line.startsWith('data: ')) continue
      try {
        const event = JSON.parse(line.slice(6))
        if (event.stage === 'complete') {
          finalResult = event.result
        }
        onProgress?.(event)
      } catch { /* ignore parse errors */ }
    }
  }

  if (!finalResult) throw new Error('No result received from server')
  return finalResult
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

export async function getDemoData() {
  const res = await fetch(`${API}/demo`)
  if (!res.ok) throw new Error('Demo data unavailable')
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
