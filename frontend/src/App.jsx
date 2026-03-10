import { Routes, Route, Link } from 'react-router-dom'
import Home from './pages/Home'
import Players from './pages/Players'
import PlayerDetail from './pages/PlayerDetail'
import Friends from './pages/Friends'
import Leaderboard from './pages/Leaderboard'
import Search from './pages/Search'
import Dashboard from './pages/Dashboard'
import AdminDashboard from './pages/AdminDashboard'

function App() {
  return (
    <div className="app-container">
      <header className="header">
        <div className="header-content">
          <Link to="/" className="logo">
            <div className="logo-icon">G</div>
            <h1>GameBD</h1>
          </Link>
          <nav className="nav">
            <Link to="/" className="nav-link">Home</Link>
            <Link to="/players" className="nav-link">Players</Link>
            <Link to="/leaderboard" className="nav-link">Leaderboard</Link>
            <Link to="/search" className="nav-link">Search</Link>
            <Link to="/dashboard" className="nav-link primary">Docs</Link>
            <Link to="/interactive" className="nav-link primary">Console</Link>
          </nav>
        </div>
      </header>

      <main className="main-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/players" element={<Players />} />
          <Route path="/players/:playerId" element={<PlayerDetail />} />
          <Route path="/friends/:playerId" element={<Friends />} />
          <Route path="/leaderboard" element={<Leaderboard />} />
          <Route path="/leaderboard/:gameId" element={<Leaderboard />} />
          <Route path="/search" element={<Search />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/interactive" element={<AdminDashboard />} />
        </Routes>
      </main>

      <footer className="footer">
        <small>GameBD - MongoDB + Neo4j Gaming Platform</small>
      </footer>
    </div>
  )
}

export default App
