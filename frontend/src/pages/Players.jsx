import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { playersAPI } from '../api'
import { Loading, Error } from '../components/Loading'

export default function Players() {
  const [players, setPlayers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchPlayers = async () => {
      try {
        const response = await playersAPI.getAll(0, 50)
        setPlayers(response.data || [])
      } catch (err) {
        setError(err.response?.data?.detail || err.message)
      } finally {
        setLoading(false)
      }
    }
    fetchPlayers()
  }, [])

  if (loading) return <Loading />
  if (error) return <Error message={error} />

  return (
    <div>
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 className="hero-title" style={{ fontSize: '2rem', textAlign: 'left' }}>Players</h1>
        <p style={{ color: 'var(--gray-400)' }}>{players.length} players found</p>
      </div>
      
      {players.length === 0 ? (
        <p style={{ color: 'var(--gray-400)' }}>No players found</p>
      ) : (
        <div className="card-grid">
          {players.map((p, i) => (
            <Link to={`/players/${p.player_id || p._id}`} key={i} className="card" style={{ textDecoration: 'none' }}>
              <h4 style={{ fontWeight: 600, marginBottom: '0.25rem' }}>{p.username || p.name}</h4>
              <p style={{ color: 'var(--gray-400)', fontSize: '0.875rem' }}>{p.email || 'No email'}</p>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
