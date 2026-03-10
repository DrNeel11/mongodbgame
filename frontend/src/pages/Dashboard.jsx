import { useState } from 'react'

const ENDPOINTS = {
  mongodb: [
    { method: 'GET', path: '/players', desc: 'List players' },
    { method: 'POST', path: '/players', desc: 'Create player' },
    { method: 'GET', path: '/players/{id}', desc: 'Get player' },
    { method: 'DELETE', path: '/players/{id}', desc: 'Delete player' },
    { method: 'GET', path: '/games', desc: 'List games' },
    { method: 'GET', path: '/stats/{player_id}', desc: 'Player stats' },
    { method: 'GET', path: '/leaderboards', desc: 'Leaderboard' },
  ],
  neo4j: [
    { method: 'POST', path: '/graph/player-nodes', desc: 'Create node' },
    { method: 'GET', path: '/graph/player-nodes/{id}', desc: 'Get node' },
    { method: 'POST', path: '/graph/friends/request', desc: 'Send friend request' },
    { method: 'POST', path: '/graph/friends/accept', desc: 'Accept friend' },
    { method: 'GET', path: '/graph/friends/{id}', desc: 'List friends' },
    { method: 'POST', path: '/graph/parties', desc: 'Create party' },
    { method: 'POST', path: '/graph/clans', desc: 'Create clan' },
    { method: 'POST', path: '/graph/follow', desc: 'Follow player' },
    { method: 'POST', path: '/graph/block', desc: 'Block player' },
  ]
}

export default function Dashboard() {
  const [activeDb, setActiveDb] = useState('neo4j')

  const endpoints = ENDPOINTS[activeDb]

  const copyPath = (path) => {
    navigator.clipboard.writeText(`http://localhost:8001/api/v1${path}`)
  }

  return (
    <div>
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 className="hero-title" style={{ fontSize: '2rem', textAlign: 'left' }}>API Docs</h1>
        <p style={{ color: 'var(--gray-400)' }}>Endpoint reference</p>
      </div>

      <div className="tabs" style={{ marginBottom: '1.5rem' }}>
        <button className={`tab ${activeDb === 'mongodb' ? 'active' : ''}`} onClick={() => setActiveDb('mongodb')}>
          MongoDB
        </button>
        <button className={`tab ${activeDb === 'neo4j' ? 'active' : ''}`} onClick={() => setActiveDb('neo4j')}>
          Neo4j
        </button>
      </div>

      <div className="card" style={{ marginBottom: '1rem', padding: '0.75rem 1rem', borderLeft: '3px solid var(--primary)' }}>
        <code style={{ color: 'var(--gray-300)' }}>Base: http://localhost:8001/api/v1</code>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        {endpoints.map((ep, i) => (
          <div key={i} className="endpoint-card">
            <span className={`method-badge method-${ep.method.toLowerCase()}`}>{ep.method}</span>
            <div className="endpoint-info">
              <div className="endpoint-path">/api/v1{ep.path}</div>
              <div className="endpoint-desc">{ep.desc}</div>
            </div>
            <button className="endpoint-copy" onClick={() => copyPath(ep.path)}>Copy</button>
          </div>
        ))}
      </div>

      <div className="card" style={{ marginTop: '1.5rem' }}>
        <p style={{ color: 'var(--gray-500)', fontSize: '0.8rem', marginBottom: '0.5rem' }}>Swagger UI</p>
        <a href="http://localhost:8001/docs" target="_blank" rel="noreferrer" style={{ color: 'var(--primary)' }}>
          http://localhost:8001/docs
        </a>
      </div>
    </div>
  )
}
