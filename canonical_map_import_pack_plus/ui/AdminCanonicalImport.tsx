
import React, { useState } from 'react'

export default function AdminCanonicalImport() {
  const [file, setFile] = useState<File | null>(null)
  const [dryRun, setDryRun] = useState(true)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string>('')

  const upload = async () => {
    if (!file) return
    const form = new FormData()
    form.append('file', file)
    form.append('dry_run', String(dryRun))
    setError(''); setResult(null)
    const res = await fetch('/admin/canonical/import', { method: 'POST', body: form })
    if (!res.ok) {
      const payload = await res.json().catch(() => ({}))
      setError(JSON.stringify(payload, null, 2))
      return
    }
    setResult(await res.json())
  }

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-xl font-semibold mb-4">Canonical Map Import</h1>
      <input type="file" accept=".csv" onChange={e => setFile(e.target.files?.[0] ?? null)} />
      <label className="ml-4">
        <input type="checkbox" checked={dryRun} onChange={() => setDryRun(!dryRun)} /> Dry run
      </label>
      <button className="ml-4 px-3 py-1 border rounded" onClick={upload}>Upload</button>

      <section className="mt-6">
        <h2 className="font-medium">Health</h2>
        <a className="text-blue-600 underline" href="/admin/canonical/health" target="_blank" rel="noreferrer">/admin/canonical/health</a>
      </section>

      {error && (
        <pre className="mt-6 p-3 bg-red-50 border border-red-200 text-red-800 whitespace-pre-wrap text-sm">{error}</pre>
      )}
      {result && (
        <pre className="mt-6 p-3 bg-gray-50 border text-sm whitespace-pre-wrap">{JSON.stringify(result, null, 2)}</pre>
      )}
    </div>
  )
}
