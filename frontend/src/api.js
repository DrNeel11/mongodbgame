import axios from 'axios'

const API_BASE = 'http://localhost:8001/api/v1'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const playersAPI = {
  getAll: (skip = 0, limit = 20) => api.get(`/players?skip=${skip}&limit=${limit}`),
  getById: (id) => api.get(`/players/${id}`),
  create: (data) => api.post('/players', data),
  update: (id, data) => api.put(`/players/${id}`, data),
  delete: (id) => api.delete(`/players/${id}`),
  login: (id) => api.post(`/players/${id}/login`),
  getStats: (id) => api.get(`/stats/${id}`),
  getAchievements: (id) => api.get(`/players/${id}/achievements`)
}

export const gamesAPI = {
  getAll: (skip = 0, limit = 20) => api.get(`/games?skip=${skip}&limit=${limit}`),
  getById: (id) => api.get(`/games/${id}`),
  create: (data) => api.post('/games', data),
  update: (id, data) => api.put(`/games/${id}`, data),
  delete: (id) => api.delete(`/games/${id}`),
  search: (query) => api.get(`/games/search?q=${query}`)
}

export const statsAPI = {
  get: (playerId, gameId) => api.get(`/stats/${playerId}/${gameId}`),
  getAll: (playerId) => api.get(`/stats/${playerId}`),
  create: (data) => api.post('/stats', data),
  update: (playerId, gameId, data) => api.patch(`/stats/${playerId}/${gameId}`, data)
}

export const leaderboardsAPI = {
  get: (limit = 50, gameId = null) => {
    const params = new URLSearchParams({ limit })
    if (gameId) params.append('game_id', gameId)
    return api.get(`/leaderboards?${params}`)
  }
}

export const matchesAPI = {
  getById: (id) => api.get(`/matches/${id}`),
  create: (data) => api.post('/matches', data)
}

export const achievementsAPI = {
  getAll: () => api.get('/achievements')
}

// ============================================================
// Neo4j Graph APIs - Social Features
// All Neo4j routes use /graph prefix for social graph operations
// ============================================================

// Neo4j APIs - Player Nodes
// Creates player nodes in the social graph to enable relationships (friends, messages, etc.)
export const playerNodesAPI = {
  create: (data) => api.post('/graph/player-nodes', data),
  get: (playerId) => api.get(`/graph/player-nodes/${playerId}`),
  updateStatus: (playerId, status) => api.patch(`/graph/player-nodes/${playerId}/status?status=${status}`),
  updateUsername: (playerId, username) => api.patch(`/graph/player-nodes/${playerId}/username?username=${username}`),
  delete: (playerId) => api.delete(`/graph/player-nodes/${playerId}`)
}

// Neo4j APIs - Friends
// Manages friend requests, friendships, mutual friends, and friend suggestions
export const friendsAPI = {
  sendRequest: (data) => api.post('/graph/friends/request', data),
  accept: (fromPlayerId, toPlayerId) => api.post(`/graph/friends/accept?from_player_id=${fromPlayerId}&to_player_id=${toPlayerId}`),
  getAll: (playerId) => api.get(`/graph/friends/${playerId}`),
  getRequests: (playerId) => api.get(`/graph/friends/requests/${playerId}`),
  getMutual: (player1Id, player2Id) => api.get(`/graph/friends/mutual/${player1Id}/${player2Id}`),
  getSuggestions: (playerId, limit = 10) => api.get(`/graph/friends/suggestions/${playerId}?limit=${limit}`),
  setNickname: (playerId, friendId, nickname) => api.patch(`/graph/friends/nickname?player_id=${playerId}&friend_id=${friendId}&nickname=${nickname}`),
  removeNickname: (playerId, friendId) => api.delete(`/graph/friends/nickname?player_id=${playerId}&friend_id=${friendId}`),
  declineRequest: (fromPlayerId, toPlayerId) => api.delete(`/graph/friends/request?from_player_id=${fromPlayerId}&to_player_id=${toPlayerId}`),
  remove: (playerId, friendId) => api.delete(`/graph/friends?player_id=${playerId}&friend_id=${friendId}`)
}

// Neo4j APIs - Blocking
// Block/unblock players to prevent them from contacting you
export const blockAPI = {
  block: (data) => api.post('/graph/block', data),
  getBlocked: (playerId) => api.get(`/graph/block/${playerId}`),
  unblock: (blockerId, blockedId) => api.delete(`/graph/block?blocker_id=${blockerId}&blocked_id=${blockedId}`)
}

// Neo4j APIs - Messaging
// Direct and group messaging with conversations, message history, and muting
export const messagesAPI = {
  createConversation: (data) => api.post('/graph/messages/conversation', data),
  getConversation: (conversationId) => api.get(`/graph/messages/conversation/${conversationId}`),
  getConversations: (playerId) => api.get(`/graph/messages/player/${playerId}/conversations`),
  getMessages: (conversationId, limit = 50, offset = 0) => api.get(`/graph/messages/conversation/${conversationId}/messages?limit=${limit}&offset=${offset}`),
  send: (data) => api.post('/graph/messages', data),
  edit: (messageId, content) => api.put(`/graph/messages/${messageId}`, { content }),
  delete: (messageId) => api.delete(`/graph/messages/${messageId}`),
  mute: (conversationId, playerId, muted = true) => api.patch(`/graph/messages/conversation/${conversationId}/mute?player_id=${playerId}&muted=${muted}`),
  unmute: (conversationId, playerId) => api.patch(`/graph/messages/conversation/${conversationId}/unmute?player_id=${playerId}`),
  leave: (conversationId, playerId) => api.delete(`/graph/messages/conversation/${conversationId}/leave?player_id=${playerId}`)
}

// Neo4j APIs - Parties
// Gaming lobbies/parties - create, join, invite players, and manage party settings
export const partiesAPI = {
  create: (data) => api.post('/graph/parties', data),
  get: (partyId) => api.get(`/graph/parties/${partyId}`),
  getPlayerParties: (playerId) => api.get(`/graph/parties/player/${playerId}`),
  invite: (partyId, inviterId, inviteeId) => api.post(`/graph/parties/${partyId}/invite`, { inviter_id: inviterId, invitee_id: inviteeId }),
  join: (partyId, playerId) => api.post(`/graph/parties/${partyId}/join?player_id=${playerId}`),
  leave: (partyId, playerId) => api.delete(`/graph/parties/${partyId}/${playerId}`),
  update: (partyId, data) => api.patch(`/graph/parties/${partyId}`, data),
  disband: (partyId) => api.delete(`/graph/parties/${partyId}`)
}

// Neo4j APIs - Clans
// Player organizations/guilds - create clans, manage members, search clans
export const clansAPI = {
  getAll: () => api.get('/graph/clans'),
  create: (data) => api.post('/graph/clans', data),
  get: (clanId) => api.get(`/graph/clans/${clanId}`),
  getMembers: (clanId) => api.get(`/graph/clans/${clanId}/members`),
  join: (clanId, playerId) => api.post(`/graph/clans/${clanId}/join?player_id=${playerId}`),
  leave: (clanId, playerId) => api.delete(`/graph/clans/${clanId}/${playerId}`),
  search: (term, limit = 20) => api.get(`/graph/clans/search?term=${term}&limit=${limit}`),
  update: (clanId, data) => api.patch(`/graph/clans/${clanId}`, data),
  updateMemberRole: (clanId, playerId, role, rank) => api.patch(`/graph/clans/${clanId}/member/${playerId}`, { role, rank }),
  clearDescription: (clanId) => api.delete(`/graph/clans/${clanId}/description`),
  disband: (clanId) => api.delete(`/graph/clans/${clanId}`)
}

// Neo4j APIs - Follow
// One-way follow relationships - follow/unfollow players without mutual friendship
export const followAPI = {
  follow: (data) => api.post('/graph/follow', data),
  getFollowers: (playerId) => api.get(`/graph/follow/followers/${playerId}`),
  getFollowing: (playerId) => api.get(`/graph/follow/following/${playerId}`),
  unfollow: (followerId, followingId) => api.delete(`/graph/follow?follower_id=${followerId}&following_id=${followingId}`)
}

// Neo4j APIs - Analytics
// Advanced graph queries using ORDER BY, LIMIT, SKIP, WITH, UNION, aggregation
export const analyticsAPI = {
  // Leaderboard with ORDER BY, LIMIT, SKIP
  getLeaderboard: (orderBy = 'friends', limit = 10, skip = 0) => 
    api.get(`/graph/analytics/leaderboard?order_by=${orderBy}&limit=${limit}&skip=${skip}`),
  
  // Player stats using WITH and aggregation
  getPlayerStats: (playerId) => api.get(`/graph/analytics/player/${playerId}/stats`),
  
  // Social graph using UNION
  getSocialGraph: (playerId) => api.get(`/graph/analytics/player/${playerId}/social-graph`),
  
  // Global stats using WITH
  getGlobalStats: () => api.get('/graph/analytics/global-stats'),
  
  // Find influencers using WITH, WHERE, ORDER BY, LIMIT
  findInfluencers: (minFollowers = 3, limit = 10) => 
    api.get(`/graph/analytics/influencers?min_followers=${minFollowers}&limit=${limit}`),
  
  // Connection chain between players
  getConnectionChain: (startId, endId, maxDepth = 4) => 
    api.get(`/graph/analytics/connection-chain?start_id=${startId}&end_id=${endId}&max_depth=${maxDepth}`),
  
  // Shortest path between players
  getShortestPath: (player1Id, player2Id) => 
    api.get(`/graph/analytics/shortest-path?player1_id=${player1Id}&player2_id=${player2Id}`),
  
  // Friend recommendations
  getFriendRecommendations: (playerId, limit = 5) => 
    api.get(`/graph/analytics/friend-recommendations/${playerId}?limit=${limit}`),
  
  // Degree centrality
  getDegreeCentrality: (playerId) => api.get(`/graph/analytics/player/${playerId}/degree`),
  
  // Mutual friends count
  getMutualFriendsCount: (player1Id, player2Id) => 
    api.get(`/graph/analytics/mutual-friends?player1_id=${player1Id}&player2_id=${player2Id}`),
  
  // Clan rankings
  getClanRankings: (limit = 10) => api.get(`/graph/analytics/clan-rankings?limit=${limit}`),
  
  // Activity feed using UNION ALL
  getActivityFeed: (playerId, limit = 20) => 
    api.get(`/graph/analytics/player/${playerId}/activity-feed?limit=${limit}`),
  
  // Bulk add property using FOREACH
  bulkAddProperty: (label, propertyName, propertyValue) => 
    api.post(`/graph/analytics/bulk-property?label=${label}&property_name=${propertyName}&property_value=${propertyValue}`)
}

// Admin/System APIs
export const adminAPI = {
  health: () => api.get('/admin/health'),
  benchmarks: () => api.get('/admin/benchmarks')
}

export default api
