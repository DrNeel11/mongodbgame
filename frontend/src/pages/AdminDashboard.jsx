import { useState } from 'react'
import CommandCard from '../components/CommandCard'
import {
  playersAPI,
  gamesAPI,
  leaderboardsAPI,
  playerNodesAPI,
  friendsAPI,
  partiesAPI,
  clansAPI,
  followAPI,
  blockAPI,
  analyticsAPI
} from '../api'

export default function AdminDashboard() {
  const [activeDb, setActiveDb] = useState('neo4j')

  return (
    <div>
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 className="hero-title" style={{ fontSize: '2rem', textAlign: 'left' }}>Console</h1>
        <p style={{ color: 'var(--gray-400)' }}>Run database commands</p>
      </div>

      <div className="db-toggle" style={{ marginBottom: '1.5rem' }}>
        <button
          className={`btn ${activeDb === 'mongodb' ? 'active-mongodb' : ''}`}
          onClick={() => setActiveDb('mongodb')}
        >
          MongoDB
        </button>
        <button
          className={`btn ${activeDb === 'neo4j' ? 'active-neo4j' : ''}`}
          onClick={() => setActiveDb('neo4j')}
        >
          Neo4j
        </button>
      </div>

      {activeDb === 'mongodb' ? <MongoSection /> : <Neo4jSection />}
    </div>
  )
}

// ===================== MONGODB =====================
function MongoSection() {
  return (
    <div>
      <h3 className="section-subtitle">Players</h3>
      <div className="command-grid">
        <CommandCard
          title="List All"
          method="GET"
          onExecute={() => playersAPI.getAll()}
        />
        <CommandCard
          title="Get by ID"
          method="GET"
          inputs={[{ name: 'id', placeholder: 'Player ID' }]}
          onExecute={(v) => playersAPI.getById(v.id)}
        />
        <CommandCard
          title="Create"
          method="POST"
          inputs={[
            { name: 'username', placeholder: 'Username' },
            { name: 'email', placeholder: 'Email' }
          ]}
          onExecute={(v) => playersAPI.create({ username: v.username, email: v.email })}
        />
        <CommandCard
          title="Delete"
          method="DELETE"
          inputs={[{ name: 'id', placeholder: 'Player ID' }]}
          onExecute={(v) => playersAPI.delete(v.id)}
        />
      </div>

      <h3 className="section-subtitle">Games</h3>
      <div className="command-grid">
        <CommandCard
          title="List All"
          method="GET"
          onExecute={() => gamesAPI.getAll()}
        />
        <CommandCard
          title="Get by ID"
          method="GET"
          inputs={[{ name: 'id', placeholder: 'Game ID' }]}
          onExecute={(v) => gamesAPI.getById(v.id)}
        />
      </div>

      <h3 className="section-subtitle">Leaderboard</h3>
      <div className="command-grid">
        <CommandCard
          title="Top Players"
          method="GET"
          inputs={[{ name: 'limit', type: 'number', placeholder: 'Limit', defaultValue: '10' }]}
          onExecute={(v) => leaderboardsAPI.get(v.limit)}
        />
      </div>
    </div>
  )
}

// ===================== NEO4J =====================
function Neo4jSection() {
  return (
    <div>
      {/* Player Nodes - Required First */}
      <h3 className="section-subtitle">1. Player Nodes <span style={{color: 'var(--gray-500)', fontWeight: 400, fontSize: '0.8rem'}}>— create first</span></h3>
      <div className="command-grid">
        <CommandCard
          title="Create Node"
          method="POST"
          inputs={[
            { name: 'player_id', placeholder: 'ID (e.g., p1)' },
            { name: 'username', placeholder: 'Username' },
            { name: 'status', type: 'select', options: [
              { value: 'online', label: 'Online' },
              { value: 'offline', label: 'Offline' },
              { value: 'in_game', label: 'In Game' }
            ]}
          ]}
          onExecute={(v) => playerNodesAPI.create({ player_id: v.player_id, username: v.username, status: v.status })}
        />
        <CommandCard
          title="Get Node"
          method="GET"
          inputs={[{ name: 'player_id', placeholder: 'Player ID' }]}
          onExecute={(v) => playerNodesAPI.get(v.player_id)}
        />
        <CommandCard
          title="Set Status"
          method="PATCH"
          inputs={[
            { name: 'player_id', placeholder: 'Player ID' },
            { name: 'status', type: 'select', options: [
              { value: 'online', label: 'Online' },
              { value: 'offline', label: 'Offline' },
              { value: 'in_game', label: 'In Game' }
            ]}
          ]}
          onExecute={(v) => playerNodesAPI.updateStatus(v.player_id, v.status)}
        />
      </div>

      {/* Friends */}
      <h3 className="section-subtitle">2. Friends</h3>
      <div className="command-grid">
        <CommandCard
          title="Send Request"
          method="POST"
          inputs={[
            { name: 'from', placeholder: 'From ID' },
            { name: 'to', placeholder: 'To ID' }
          ]}
          onExecute={(v) => friendsAPI.sendRequest({ from_player_id: v.from, to_player_id: v.to })}
        />
        <CommandCard
          title="Accept"
          method="POST"
          inputs={[
            { name: 'from', placeholder: 'From ID' },
            { name: 'to', placeholder: 'To ID' }
          ]}
          onExecute={(v) => friendsAPI.accept(v.from, v.to)}
        />
        <CommandCard
          title="List Friends"
          method="GET"
          inputs={[{ name: 'player_id', placeholder: 'Player ID' }]}
          onExecute={(v) => friendsAPI.getAll(v.player_id)}
        />
        <CommandCard
          title="Pending"
          method="GET"
          inputs={[{ name: 'player_id', placeholder: 'Player ID' }]}
          onExecute={(v) => friendsAPI.getRequests(v.player_id)}
        />
      </div>

      {/* Parties */}
      <h3 className="section-subtitle">3. Parties</h3>
      <div className="command-grid">
        <CommandCard
          title="Create"
          method="POST"
          inputs={[
            { name: 'leader_id', placeholder: 'Leader ID' },
            { name: 'game_id', placeholder: 'Game ID' }
          ]}
          onExecute={(v) => partiesAPI.create({ leader_id: v.leader_id, game_id: v.game_id, max_size: 4, is_public: true })}
        />
        <CommandCard
          title="Join"
          method="POST"
          inputs={[
            { name: 'party_id', placeholder: 'Party ID' },
            { name: 'player_id', placeholder: 'Player ID' }
          ]}
          onExecute={(v) => partiesAPI.join(v.party_id, v.player_id)}
        />
        <CommandCard
          title="View"
          method="GET"
          inputs={[{ name: 'party_id', placeholder: 'Party ID' }]}
          onExecute={(v) => partiesAPI.get(v.party_id)}
        />
      </div>

      {/* Clans */}
      <h3 className="section-subtitle">4. Clans</h3>
      <div className="command-grid">
        <CommandCard
          title="Create"
          method="POST"
          inputs={[
            { name: 'name', placeholder: 'Clan Name' },
            { name: 'tag', placeholder: 'Tag (2-6 chars)' },
            { name: 'owner_id', placeholder: 'Owner ID' }
          ]}
          onExecute={(v) => clansAPI.create({ name: v.name, tag: v.tag, owner_id: v.owner_id })}
        />
        <CommandCard
          title="Join"
          method="POST"
          inputs={[
            { name: 'clan_id', placeholder: 'Clan ID' },
            { name: 'player_id', placeholder: 'Player ID' }
          ]}
          onExecute={(v) => clansAPI.join(v.clan_id, v.player_id)}
        />
        <CommandCard
          title="View"
          method="GET"
          inputs={[{ name: 'clan_id', placeholder: 'Clan ID' }]}
          onExecute={(v) => clansAPI.get(v.clan_id)}
        />
      </div>

      {/* Follow / Block */}
      <h3 className="section-subtitle">5. Follow & Block</h3>
      <div className="command-grid">
        <CommandCard
          title="Follow"
          method="POST"
          inputs={[
            { name: 'follower', placeholder: 'You' },
            { name: 'following', placeholder: 'Target' }
          ]}
          onExecute={(v) => followAPI.follow({ follower_id: v.follower, following_id: v.following })}
        />
        <CommandCard
          title="Followers"
          method="GET"
          inputs={[{ name: 'player_id', placeholder: 'Player ID' }]}
          onExecute={(v) => followAPI.getFollowers(v.player_id)}
        />
        <CommandCard
          title="Block"
          method="POST"
          inputs={[
            { name: 'blocker', placeholder: 'You' },
            { name: 'blocked', placeholder: 'Target' }
          ]}
          onExecute={(v) => blockAPI.block({ blocker_id: v.blocker, blocked_id: v.blocked })}
        />
      </div>

      {/* Analytics - Advanced CQL */}
      <h3 className="section-subtitle">6. Analytics <span style={{color: 'var(--gray-500)', fontWeight: 400, fontSize: '0.8rem'}}>— advanced CQL</span></h3>
      <div className="command-grid">
        <CommandCard
          title="Leaderboard"
          method="GET"
          description="ORDER BY, LIMIT, SKIP"
          inputs={[
            { name: 'order_by', type: 'select', options: [
              { value: 'friends', label: 'By Friends' },
              { value: 'followers', label: 'By Followers' },
              { value: 'messages', label: 'By Messages' },
              { value: 'username', label: 'By Username' }
            ]},
            { name: 'limit', type: 'number', placeholder: 'Limit', defaultValue: '10' }
          ]}
          onExecute={(v) => analyticsAPI.getLeaderboard(v.order_by, v.limit, 0)}
        />
        <CommandCard
          title="Player Stats"
          method="GET"
          description="WITH + Aggregation"
          inputs={[{ name: 'player_id', placeholder: 'Player ID' }]}
          onExecute={(v) => analyticsAPI.getPlayerStats(v.player_id)}
        />
        <CommandCard
          title="Social Graph"
          method="GET"
          description="UNION query"
          inputs={[{ name: 'player_id', placeholder: 'Player ID' }]}
          onExecute={(v) => analyticsAPI.getSocialGraph(v.player_id)}
        />
        <CommandCard
          title="Global Stats"
          method="GET"
          description="WITH chain"
          onExecute={() => analyticsAPI.getGlobalStats()}
        />
        <CommandCard
          title="Influencers"
          method="GET"
          description="WITH + WHERE + ORDER BY"
          inputs={[
            { name: 'min_followers', type: 'number', placeholder: 'Min followers', defaultValue: '1' },
            { name: 'limit', type: 'number', placeholder: 'Limit', defaultValue: '10' }
          ]}
          onExecute={(v) => analyticsAPI.findInfluencers(v.min_followers, v.limit)}
        />
        <CommandCard
          title="Connection Chain"
          method="GET"
          description="Variable path"
          inputs={[
            { name: 'start_id', placeholder: 'Start ID' },
            { name: 'end_id', placeholder: 'End ID' }
          ]}
          onExecute={(v) => analyticsAPI.getConnectionChain(v.start_id, v.end_id)}
        />
        <CommandCard
          title="Friend Recs"
          method="GET"
          description="Common friends"
          inputs={[
            { name: 'player_id', placeholder: 'Player ID' },
            { name: 'limit', type: 'number', placeholder: 'Limit', defaultValue: '5' }
          ]}
          onExecute={(v) => analyticsAPI.getFriendRecommendations(v.player_id, v.limit)}
        />
        <CommandCard
          title="Clan Rankings"
          method="GET"
          description="Aggregation + ORDER BY"
          inputs={[{ name: 'limit', type: 'number', placeholder: 'Limit', defaultValue: '10' }]}
          onExecute={(v) => analyticsAPI.getClanRankings(v.limit)}
        />
        <CommandCard
          title="Activity Feed"
          method="GET"
          description="UNION ALL"
          inputs={[
            { name: 'player_id', placeholder: 'Player ID' },
            { name: 'limit', type: 'number', placeholder: 'Limit', defaultValue: '20' }
          ]}
          onExecute={(v) => analyticsAPI.getActivityFeed(v.player_id, v.limit)}
        />
        <CommandCard
          title="Mutual Friends"
          method="GET"
          description="Path matching"
          inputs={[
            { name: 'player1_id', placeholder: 'Player 1 ID' },
            { name: 'player2_id', placeholder: 'Player 2 ID' }
          ]}
          onExecute={(v) => analyticsAPI.getMutualFriendsCount(v.player1_id, v.player2_id)}
        />
      </div>
    </div>
  )
}
