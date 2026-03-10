import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { leaderboardsAPI } from '../api'
import { Loading, Error } from '../components/Loading'

export default function Leaderboard() {
  const { gameId } = useParams()
  const [entries, setEntries] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        const response = await leaderboardsAPI.get(50, gameId)
        setEntries(response.data || [])
      } catch (err) {
        setError(err.response?.data?.detail || err.message)
      } finally {
        setLoading(false)
      }
    }
    fetchLeaderboard()
  }, [gameId])

  if (loading) return <Loading />
  if (error) return <Error message={error} />

  return (
    <div>
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 className="hero-title" style={{ fontSize: '2rem', textAlign: 'left' }}>Leaderboard</h1>
        <p style={{ color: 'var(--gray-400)' }}>{gameId ? `Game: ${gameId}` : 'Global Rankings'}</p>
      </div>

      {entries.length === 0 ? (
        <p style={{ color: 'var(--gray-400)' }}>No entries</p>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Rank</th>
                <th>Player ID</th>
                <th style={{ textAlign: 'right' }}>Wins</th>
                <th style={{ textAlign: 'right' }}>K/D Ratio</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((e, i) => (
                <tr key={i}>
                  <td style={{ color: 'var(--gray-400)', fontWeight: '600' }}>#{i + 1}</td>
                  <td>{e.player_id}</td>
                  <td style={{ textAlign: 'right' }}>{e.wins}</td>
                  <td style={{ textAlign: 'right' }}>{e.kd_ratio}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
