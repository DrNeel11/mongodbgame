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
  messagesAPI,
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
        <CommandCard
          title="Update Username"
          method="PATCH"
          inputs={[
            { name: 'player_id', placeholder: 'Player ID' },
            { name: 'username', placeholder: 'New Username' }
          ]}
          onExecute={(v) => playerNodesAPI.updateUsername(v.player_id, v.username)}
        />
        <CommandCard
          title="Delete Node"
          method="DELETE"
          description="DETACH DELETE"
          inputs={[{ name: 'player_id', placeholder: 'Player ID' }]}
          onExecute={(v) => playerNodesAPI.delete(v.player_id)}
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
        <CommandCard
          title="Suggestions"
          method="GET"
          description="Friends of friends"
          inputs={[
            { name: 'player_id', placeholder: 'Player ID' },
            { name: 'limit', type: 'number', placeholder: 'Limit', defaultValue: '10' }
          ]}
          onExecute={(v) => friendsAPI.getSuggestions(v.player_id, v.limit || 10)}
        />
        <CommandCard
          title="Mutual Friends"
          method="GET"
          inputs={[
            { name: 'player1', placeholder: 'Player 1 ID' },
            { name: 'player2', placeholder: 'Player 2 ID' }
          ]}
          onExecute={(v) => friendsAPI.getMutual(v.player1, v.player2)}
        />
        <CommandCard
          title="Set Nickname"
          method="PATCH"
          inputs={[
            { name: 'player_id', placeholder: 'Your ID' },
            { name: 'friend_id', placeholder: 'Friend ID' },
            { name: 'nickname', placeholder: 'Nickname' }
          ]}
          onExecute={(v) => friendsAPI.setNickname(v.player_id, v.friend_id, v.nickname)}
        />
        <CommandCard
          title="Remove Nickname"
          method="DELETE"
          description="REMOVE"
          inputs={[
            { name: 'player_id', placeholder: 'Your ID' },
            { name: 'friend_id', placeholder: 'Friend ID' }
          ]}
          onExecute={(v) => friendsAPI.removeNickname(v.player_id, v.friend_id)}
        />
        <CommandCard
          title="Decline Request"
          method="DELETE"
          inputs={[
            { name: 'from', placeholder: 'From ID' },
            { name: 'to', placeholder: 'To ID' }
          ]}
          onExecute={(v) => friendsAPI.declineRequest(v.from, v.to)}
        />
        <CommandCard
          title="Remove Friend"
          method="DELETE"
          inputs={[
            { name: 'player_id', placeholder: 'Your ID' },
            { name: 'friend_id', placeholder: 'Friend ID' }
          ]}
          onExecute={(v) => friendsAPI.remove(v.player_id, v.friend_id)}
        />
      </div>

      {/* Block */}
      <h3 className="section-subtitle">3. Block</h3>
      <div className="command-grid">
        <CommandCard
          title="Block Player"
          method="POST"
          inputs={[
            { name: 'blocker', placeholder: 'Your ID' },
            { name: 'blocked', placeholder: 'Target ID' },
            { name: 'reason', placeholder: 'Reason (optional)' }
          ]}
          onExecute={(v) => blockAPI.block({ blocker_id: v.blocker, blocked_id: v.blocked, reason: v.reason || null })}
        />
        <CommandCard
          title="Get Blocked"
          method="GET"
          inputs={[{ name: 'player_id', placeholder: 'Player ID' }]}
          onExecute={(v) => blockAPI.getBlocked(v.player_id)}
        />
        <CommandCard
          title="Unblock"
          method="DELETE"
          inputs={[
            { name: 'blocker', placeholder: 'Your ID' },
            { name: 'blocked', placeholder: 'Blocked ID' }
          ]}
          onExecute={(v) => blockAPI.unblock(v.blocker, v.blocked)}
        />
      </div>

      {/* Messaging */}
      <h3 className="section-subtitle">4. Messaging</h3>
      <div className="command-grid">
        <CommandCard
          title="Create Conversation"
          method="POST"
          // '''
          // inputs={[
          //   { name: 'type', type: 'select', options: [
          //     { value: 'direct', label: 'Direct' },
          //     { value: 'group', label: 'Group' }
          //   ]},
          //   { name: 'participants', placeholder: 'IDs (comma sep)' },
          //   { name: 'name', placeholder: 'Name (optional)' }
          // ]}
          inputs={[
             { name: 'participants', placeholder: 'IDs (comma sep)' },
             { name: 'name', placeholder: 'Name (optional)' }
          ]}
          onExecute={(v) => messagesAPI.createConversation({ 
            conversation_type: 'group', 
            participant_ids: v.participants.split(',').map(s => s.trim()),
            name: v.name || null
          })}
        />
        <CommandCard
          title="Get Conversation"
          method="GET"
          inputs={[{ name: 'conversation_id', placeholder: 'Conversation ID' }]}
          onExecute={(v) => messagesAPI.getConversation(v.conversation_id)}
        />
        <CommandCard
          title="My Conversations"
          method="GET"
          inputs={[{ name: 'player_id', placeholder: 'Player ID' }]}
          onExecute={(v) => messagesAPI.getConversations(v.player_id)}
        />
        <CommandCard
          title="Get Messages"
          method="GET"
          inputs={[
            { name: 'conversation_id', placeholder: 'Conversation ID' },
            { name: 'limit', type: 'number', placeholder: 'Limit', defaultValue: '50' }
          ]}
          onExecute={(v) => messagesAPI.getMessages(v.conversation_id, v.limit || 50, 0)}
        />
        <CommandCard
          title="Send Message"
          method="POST"
          inputs={[
            { name: 'conversation_id', placeholder: 'Conversation ID' },
            { name: 'sender_id', placeholder: 'Sender ID' },
            { name: 'content', placeholder: 'Message' }
          ]}
          onExecute={(v) => messagesAPI.send({ conversation_id: v.conversation_id, sender_id: v.sender_id, content: v.content })}
        />
        <CommandCard
          title="Edit Message"
          method="PUT"
          inputs={[
            { name: 'message_id', placeholder: 'Message ID' },
            { name: 'content', placeholder: 'New Content' }
          ]}
          onExecute={(v) => messagesAPI.edit(v.message_id, v.content)}
        />
        <CommandCard
          title="Delete Message"
          method="DELETE"
          description="DETACH DELETE"
          inputs={[{ name: 'message_id', placeholder: 'Message ID' }]}
          onExecute={(v) => messagesAPI.delete(v.message_id)}
        />
        <CommandCard
          title="Mute Conversation"
          method="PATCH"
          inputs={[
            { name: 'conversation_id', placeholder: 'Conversation ID' },
            { name: 'player_id', placeholder: 'Player ID' },
            { name: 'muted', type: 'select', options: [
              { value: 'true', label: 'Mute' },
              { value: 'false', label: 'Unmute' }
            ]}
          ]}
          onExecute={(v) => messagesAPI.mute(v.conversation_id, v.player_id, v.muted === 'true')}
        />
        <CommandCard
          title="Clear Muted Status"
          method="PATCH"
          description="REMOVE"
          inputs={[
            { name: 'conversation_id', placeholder: 'Conversation ID' },
            { name: 'player_id', placeholder: 'Player ID' }
          ]}
          onExecute={(v) => messagesAPI.unmute(v.conversation_id, v.player_id)}
        />
        <CommandCard
          title="Leave Conversation"
          method="DELETE"
          inputs={[
            { name: 'conversation_id', placeholder: 'Conversation ID' },
            { name: 'player_id', placeholder: 'Player ID' }
          ]}
          onExecute={(v) => messagesAPI.leave(v.conversation_id, v.player_id)}
        />
      </div>

      {/* Parties */}
      <h3 className="section-subtitle">5. Parties</h3>
      <div className="command-grid">
        <CommandCard
          title="Create"
          method="POST"
          inputs={[
            { name: 'leader_id', placeholder: 'Leader ID' },
            { name: 'game_id', placeholder: 'Game ID' },
            { name: 'max_size', type: 'number', placeholder: 'Max Size', defaultValue: '4' },
            { name: 'is_public', type: 'select', options: [
              { value: 'true', label: 'Public' },
              { value: 'false', label: 'Private' }
            ]}
          ]}
          onExecute={(v) => partiesAPI.create({ leader_id: v.leader_id, game_id: v.game_id, max_size: parseInt(v.max_size) || 4, is_public: v.is_public === 'true' })}
        />
        <CommandCard
          title="View"
          method="GET"
          inputs={[{ name: 'party_id', placeholder: 'Party ID' }]}
          onExecute={(v) => partiesAPI.get(v.party_id)}
        />
        <CommandCard
          title="My Parties"
          method="GET"
          inputs={[{ name: 'player_id', placeholder: 'Player ID' }]}
          onExecute={(v) => partiesAPI.getPlayerParties(v.player_id)}
        />
        <CommandCard
          title="Invite"
          method="POST"
          inputs={[
            { name: 'party_id', placeholder: 'Party ID' },
            { name: 'inviter_id', placeholder: 'Inviter ID' },
            { name: 'invitee_id', placeholder: 'Invitee ID' }
          ]}
          onExecute={(v) => partiesAPI.invite(v.party_id, v.inviter_id, v.invitee_id)}
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
          title="Update Party"
          method="PATCH"
          inputs={[
            { name: 'party_id', placeholder: 'Party ID' },
            { name: 'max_size', type: 'number', placeholder: 'Max Size' },
            { name: 'is_public', type: 'select', options: [
              { value: 'true', label: 'Public' },
              { value: 'false', label: 'Private' }
            ]}
          ]}
          onExecute={(v) => partiesAPI.update(v.party_id, { max_size: v.max_size ? parseInt(v.max_size) : undefined, is_public: v.is_public === 'true' })}
        />
        <CommandCard
          title="Leave Party"
          method="DELETE"
          inputs={[
            { name: 'party_id', placeholder: 'Party ID' },
            { name: 'player_id', placeholder: 'Player ID' }
          ]}
          onExecute={(v) => partiesAPI.leave(v.party_id, v.player_id)}
        />
        <CommandCard
          title="Disband Party"
          method="DELETE"
          description="DETACH DELETE"
          inputs={[{ name: 'party_id', placeholder: 'Party ID' }]}
          onExecute={(v) => partiesAPI.disband(v.party_id)}
        />
      </div>

      {/* Clans */}
      <h3 className="section-subtitle">6. Clans</h3>
      <div className="command-grid">
        <CommandCard
          title="Create"
          method="POST"
          inputs={[
            { name: 'name', placeholder: 'Clan Name' },
            { name: 'tag', placeholder: 'Tag (2-6 chars)' },
            { name: 'owner_id', placeholder: 'Owner ID' },
            { name: 'description', placeholder: 'Description (optional)' }
          ]}
          onExecute={(v) => clansAPI.create({ name: v.name, tag: v.tag, owner_id: v.owner_id, description: v.description || null })}
        />
        <CommandCard
          title="View"
          method="GET"
          inputs={[{ name: 'clan_id', placeholder: 'Clan ID' }]}
          onExecute={(v) => clansAPI.get(v.clan_id)}
        />
        <CommandCard
          title="List All"
          method="GET"
          onExecute={() => clansAPI.getAll()}
        />
        <CommandCard
          title="Get Members"
          method="GET"
          inputs={[{ name: 'clan_id', placeholder: 'Clan ID' }]}
          onExecute={(v) => clansAPI.getMembers(v.clan_id)}
        />
        <CommandCard
          title="Search"
          method="GET"
          inputs={[
            { name: 'term', placeholder: 'Search term' },
            { name: 'limit', type: 'number', placeholder: 'Limit', defaultValue: '20' }
          ]}
          onExecute={(v) => clansAPI.search(v.term, v.limit || 20)}
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
          title="Update Clan"
          method="PATCH"
          inputs={[
            { name: 'clan_id', placeholder: 'Clan ID' },
            { name: 'name', placeholder: 'New Name (optional)' },
            { name: 'tag', placeholder: 'New Tag (optional)' },
            { name: 'description', placeholder: 'New Description (optional)' }
          ]}
          onExecute={(v) => clansAPI.update(v.clan_id, { 
            name: v.name || undefined, 
            tag: v.tag || undefined, 
            description: v.description || undefined 
          })}
        />
        <CommandCard
          title="Leave Clan"
          method="DELETE"
          inputs={[
            { name: 'clan_id', placeholder: 'Clan ID' },
            { name: 'player_id', placeholder: 'Player ID' }
          ]}
          onExecute={(v) => clansAPI.leave(v.clan_id, v.player_id)}
        />
        <CommandCard
          title="Update Member Role"
          method="PATCH"
          inputs={[
            { name: 'clan_id', placeholder: 'Clan ID' },
            { name: 'player_id', placeholder: 'Player ID' },
            { name: 'role', type: 'select', options: [
              { value: 'owner', label: 'Owner' },
              { value: 'admin', label: 'Admin' },
              { value: 'moderator', label: 'Moderator' },
              { value: 'member', label: 'Member' }
            ]},
            { name: 'rank', type: 'number', placeholder: 'Rank (optional)' }
          ]}
          onExecute={(v) => clansAPI.updateMemberRole(v.clan_id, v.player_id, v.role, v.rank ? parseInt(v.rank) : undefined)}
        />
        <CommandCard
          title="Clear Description"
          method="DELETE"
          description="REMOVE"
          inputs={[{ name: 'clan_id', placeholder: 'Clan ID' }]}
          onExecute={(v) => clansAPI.clearDescription(v.clan_id)}
        />
        <CommandCard
          title="Disband Clan"
          method="DELETE"
          description="DETACH DELETE"
          inputs={[{ name: 'clan_id', placeholder: 'Clan ID' }]}
          onExecute={(v) => clansAPI.disband(v.clan_id)}
        />
      </div>

      {/* Follow */}
      <h3 className="section-subtitle">7. Follow</h3>
      <div className="command-grid">
        <CommandCard
          title="Follow"
          method="POST"
          inputs={[
            { name: 'follower', placeholder: 'Your ID' },
            { name: 'following', placeholder: 'Target ID' }
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
          title="Following"
          method="GET"
          inputs={[{ name: 'player_id', placeholder: 'Player ID' }]}
          onExecute={(v) => followAPI.getFollowing(v.player_id)}
        />
        <CommandCard
          title="Unfollow"
          method="DELETE"
          inputs={[
            { name: 'follower', placeholder: 'Your ID' },
            { name: 'following', placeholder: 'Target ID' }
          ]}
          onExecute={(v) => followAPI.unfollow(v.follower, v.following)}
        />
      </div>

      {/* Analytics - Advanced CQL */}
      <h3 className="section-subtitle">8. Analytics <span style={{color: 'var(--gray-500)', fontWeight: 400, fontSize: '0.8rem'}}>— advanced CQL</span></h3>
      <div className="command-grid">
        <CommandCard
          title="Leaderboard"
          method="GET"
          description="ORDER BY, LIMIT"
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
            { name: 'limit', type: 'number', placeholder: 'Limit', defaultValue: '1' }
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
          description="Count mutual friends"
          inputs={[
            { name: 'player1_id', placeholder: 'Player 1 ID' },
            { name: 'player2_id', placeholder: 'Player 2 ID' }
          ]}
          onExecute={(v) => analyticsAPI.getMutualFriendsCount(v.player1_id, v.player2_id)}
        />
        <CommandCard
  title="Bulk Add Property"
  method="POST"
  description="Add a property to all nodes of a given label"
  inputs={[
    { name: 'label', placeholder: 'Node Label (e.g., Player)' },
    { name: 'propertyName', placeholder: 'Property Name (e.g., status)' },
    { name: 'propertyValue', placeholder: 'Property Value (e.g., active)' }
  ]}
  onExecute={(v) => 
    analyticsAPI.bulkAddProperty(
      v.label,
      v.propertyName,
      v.propertyValue
    )
  }
      />
        
      </div>
    </div>
  )
}
