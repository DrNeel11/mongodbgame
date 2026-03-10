import { useState } from 'react'
import { gamesAPI } from '../api'

export default function Search() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [searched, setSearched] = useState(false)

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setError(null)
    setSearched(true)

    try {
      const response = await gamesAPI.search(query)
      setResults(response.data || [])
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 className="hero-title" style={{ fontSize: '2rem', textAlign: 'left' }}>Search</h1>
        <p style={{ color: 'var(--gray-400)' }}>Find games and content</p>
      </div>

      <form onSubmit={handleSearch} style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <input
            type="text"
            className="input"
            placeholder="Search games..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            style={{ flex: 1 }}
          />
          <button type="submit" className="btn btn-primary">
            Search
          </button>
        </div>
      </form>

      {loading && (
        <div className="loading">
          <span className="spinner"></span> Searching...
        </div>
      )}

      {error && (
        <div className="error">Error: {error}</div>
      )}

      {searched && !loading && (
        <div className="card-grid">
          {results.length === 0 ? (
            <div className="card">
              <p style={{ color: 'var(--gray-400)' }}>No results found</p>
            </div>
          ) : (
            results.map((g, i) => (
              <div key={i} className="card">
                <h4 style={{ fontWeight: 600, marginBottom: '0.25rem' }}>{g.name || g.title}</h4>
                {g.description && (
                  <p style={{ color: 'var(--gray-400)', fontSize: '0.875rem' }}>{g.description.slice(0, 120)}</p>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  )
}
