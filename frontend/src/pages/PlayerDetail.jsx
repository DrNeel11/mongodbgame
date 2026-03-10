import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { playersAPI, friendsAPI } from '../api'
import { Loading, Error } from '../components/Loading'

export default function PlayerDetail() {
  const { playerId } = useParams()
  const [player, setPlayer] = useState(null)
  const [friends, setFriends] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const playerRes = await playersAPI.getById(playerId)
        setPlayer(playerRes.data)
        
        try {
          const friendsRes = await friendsAPI.getAll(playerId)
          setFriends(friendsRes.data || [])
        } catch {
          // Neo4j may be offline
          setFriends([])
        }
      } catch (err) {
        setError(err.response?.data?.detail || err.message)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [playerId])

  if (loading) return <Loading />
  if (error) return <Error message={error} />
  if (!player) return <Error message="Player not found" />

  return (
    <div>
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 className="hero-title" style={{ fontSize: '2rem', textAlign: 'left' }}>{player.username || player.name}</h1>
        <p style={{ color: 'var(--gray-400)' }}>ID: {player.player_id || player._id}</p>
      </div>

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h4 style={{ marginBottom: '0.75rem', fontWeight: 600 }}>Player Info</h4>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.5rem', fontSize: '0.875rem' }}>
          <div><span style={{ color: 'var(--gray-500)' }}>Email:</span> {player.email || 'N/A'}</div>
          <div><span style={{ color: 'var(--gray-500)' }}>Level:</span> {player.level || 1}</div>
        </div>
      </div>

      <h3 className="section-subtitle">Friends</h3>
      {friends.length > 0 ? (
        <div className="card-grid">
          {friends.map((f, i) => (
            <div key={i} className="card">
              <h4 style={{ fontWeight: 600 }}>{f.username || f.to_username || f.player_id}</h4>
            </div>
          ))}
        </div>
      ) : (
        <p style={{ color: 'var(--gray-400)' }}>No social data (Neo4j may be offline)</p>
      )}

      <div style={{ marginTop: '1.5rem' }}>
        <Link to={`/friends/${playerId}`} className="btn btn-primary">
          View All Friends
        </Link>
      </div>
    </div>
  )
}
