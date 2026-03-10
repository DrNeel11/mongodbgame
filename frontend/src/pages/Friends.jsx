import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { friendsAPI } from '../api'
import { Loading, Error } from '../components/Loading'

export default function Friends() {
  const { playerId } = useParams()
  const [friends, setFriends] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchFriends = async () => {
      try {
        const response = await friendsAPI.getAll(playerId)
        setFriends(response.data || [])
      } catch (err) {
        setError(err.response?.data?.detail || err.message)
      } finally {
        setLoading(false)
      }
    }
    fetchFriends()
  }, [playerId])

  if (loading) return <Loading />
  if (error) return <Error message={error} />

  return (
    <div>
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 className="hero-title" style={{ fontSize: '2rem', textAlign: 'left' }}>Friends</h1>
        <p style={{ color: 'var(--gray-400)' }}>Player: {playerId}</p>
      </div>
      
      {friends.length === 0 ? (
        <p style={{ color: 'var(--gray-400)' }}>No friends</p>
      ) : (
        <div className="card-grid">
          {friends.map((f, i) => (
            <div key={i} className="card">
              <h4 style={{ fontWeight: 600 }}>{f.username || f.player_id}</h4>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
