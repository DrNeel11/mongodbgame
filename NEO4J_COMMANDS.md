# Neo4j Commands Reference

## Overview

Neo4j in the GameBD system manages all graph-based social relationships and interactions. These commands are designed to handle real-time social features and relationship management.

## All Neo4j Commands (Organized by Category)

### 1. PLAYER NODES (5 commands)

Player nodes represent players in the graph database. Each player gets a node with identity and status properties.

| # | Command | HTTP | Path | Parameters | Purpose |
|---|---------|------|------|------------|---------|
| 1 | Create Player Node | POST | `/player-nodes` | player_id, username, status | Create a new player node in the graph (required for all social features) |
| 2 | Get Player Node | GET | `/player-nodes/{player_id}` | player_id | Retrieve player node details including status |
| 3 | Update Player Status | PATCH | `/player-nodes/{player_id}/status` | player_id, status | Change player's online status (online/offline/away) |
| 4 | Update Player Username | PATCH | `/player-nodes/{player_id}/username` | player_id, username | Update player's username in graph |
| 5 | Delete Player Node | DELETE | `/player-nodes/{player_id}` | player_id | Remove player and all relationships (permanent deletion) |

### 2. FRIENDS (8 commands)

Friend management handles bidirectional friendship relationships, requests, and suggestions.

| # | Command | HTTP | Path | Parameters | Purpose |
|---|---------|------|------|------------|---------|
| 6 | Send Friend Request | POST | `/friends/request` | from_player_id, to_player_id, message | Initiate a friendship request with optional message |
| 7 | Accept Friend Request | POST | `/friends/accept` | from_player_id, to_player_id | Convert pending request into active friendship |
| 8 | Get Pending Requests | GET | `/friends/requests/{player_id}` | player_id | List all incoming friend requests |
| 9 | Get Friends List | GET | `/friends/{player_id}` | player_id | Get all confirmed friends of a player |
| 10 | Get Mutual Friends | GET | `/friends/mutual/{player1_id}/{player2_id}` | player1_id, player2_id | Find common friends between two players |
| 11 | Get Friend Suggestions | GET | `/friends/suggestions/{player_id}` | player_id, limit | Get recommended friends using "friends-of-friends" algorithm |
| 12 | Set Friend Nickname | PATCH | `/friends/nickname` | player_id, friend_id, nickname | Add custom nickname for a friend |
| 13 | Remove Friend | DELETE | `/friends/` | player_id, friend_id | Unfriend a player (removes bidirectional friendship) |

**Decline Friend Request** (Alternative): DELETE `/friends/request` with from_player_id, to_player_id

### 3. BLOCKING (3 commands)

Block operations handle negative relationships preventing communication.

| # | Command | HTTP | Path | Parameters | Purpose |
|---|---------|------|------|------------|---------|
| 14 | Block Player | POST | `/block` | blocker_id, blocked_id, reason | Prevent a player from sending messages or friend requests |
| 15 | Get Blocked Players | GET | `/block/{player_id}` | player_id | List all players you have blocked |
| 16 | Unblock Player | DELETE | `/block/` | blocker_id, blocked_id | Remove a player from your blocked list |

### 4. MESSAGING (7 commands)

Messaging handles direct communication through conversations (1-on-1 or group chats).

| # | Command | HTTP | Path | Parameters | Purpose |
|---|---------|------|------|------------|---------|
| 17 | Create Conversation | POST | `/messages/conversation` | type, participant_ids, name | Start a new private or group conversation |
| 18 | Send Message | POST | `/messages/` | conversation_id, sender_id, content | Post a message to a conversation |
| 19 | Get Conversation | GET | `/messages/conversation/{conversation_id}` | conversation_id | Retrieve conversation details and participants |
| 20 | Get Player Conversations | GET | `/messages/player/{player_id}/conversations` | player_id | List all conversations a player is in |
| 21 | Get Messages | GET | `/messages/conversation/{conversation_id}/messages` | conversation_id, limit, offset | Fetch messages with pagination |
| 22 | Edit Message | PUT | `/messages/{message_id}` | message_id, content | Modify sent message content |
| 23 | Delete Message | DELETE | `/messages/{message_id}` | message_id | Remove a message permanently |
| 24 | Mute Conversation | PATCH | `/messages/conversation/{conversation_id}/mute` | conversation_id, player_id, muted | Silence notifications for a conversation |
| 25 | Leave Conversation | DELETE | `/messages/conversation/{conversation_id}/leave` | conversation_id, player_id | Exit a conversation (removes participation) |

### 5. PARTIES (7 commands)

Parties are temporary gaming groups for coordinating playtime.

| # | Command | HTTP | Path | Parameters | Purpose |
|---|---------|------|------|------------|---------|
| 26 | Create Party | POST | `/parties` | leader_id, game_id, max_size, is_public | Establish a new party (leader is creator) |
| 27 | Invite to Party | POST | `/parties/{party_id}/invite` | party_id, inviter_id, invitee_id | Send party invitation to player |
| 28 | Join Party | POST | `/parties/{party_id}/join` | party_id, player_id | Add yourself to a party |
| 29 | Get Party | GET | `/parties/{party_id}` | party_id | View party details including members and leader |
| 30 | Get Player Party | GET | `/parties/player/{player_id}` | player_id | Find which party a player is currently in |
| 31 | Update Party | PATCH | `/parties/{party_id}` | party_id, max_size, is_public, game_id | Modify party settings |
| 32 | Leave Party | DELETE | `/parties/{party_id}/leave` | party_id, player_id | Exit current party |
| 33 | Disband Party | DELETE | `/parties/{party_id}` | party_id | Delete party (leader only) |

### 6. CLANS (8 commands)

Clans are persistent organizations for long-term grouping and hierarchy.

| # | Command | HTTP | Path | Parameters | Purpose |
|---|---------|------|------|------------|---------|
| 34 | Create Clan | POST | `/clans` | name, tag, owner_id, description | Establish a new clan with founder |
| 35 | Join Clan | POST | `/clans/{clan_id}/join` | clan_id, player_id | Become member of existing clan |
| 36 | Get Clan | GET | `/clans/{clan_id}` | clan_id | View clan info, members, and hierarchy |
| 37 | Get Player Clan | GET | `/clans/player/{player_id}` | player_id | Find which clan a player belongs to |
| 38 | Search Clans | GET | `/clans/search/{search_term}` | search_term, limit | Find clans by name or tag |
| 39 | Update Clan | PATCH | `/clans/{clan_id}` | clan_id, name, tag, description | Modify clan details (leader only) |
| 40 | Update Member Role | PATCH | `/clans/{clan_id}/member/{player_id}` | clan_id, player_id, role, rank | Change member's position in clan hierarchy |
| 41 | Leave Clan | DELETE | `/clans/{clan_id}/leave` | clan_id, player_id | Exit clan (revokes membership) |
| 42 | Disband Clan | DELETE | `/clans/{clan_id}` | clan_id | Delete clan (leader only) |

### 7. FOLLOW (4 commands)

Follow relationships allow players to track other players' activities.

| # | Command | HTTP | Path | Parameters | Purpose |
|---|---------|------|------|------------|---------|
| 43 | Follow Player | POST | `/follow` | follower_id, following_id | Subscribe to a player's activity feed |
| 44 | Get Following | GET | `/follow/following/{player_id}` | player_id | List all players you follow |
| 45 | Get Followers | GET | `/follow/followers/{player_id}` | player_id | See who follows you |
| 46 | Unfollow Player | DELETE | `/follow/` | follower_id, following_id | Stop following a player |

---

## Neo4j Command Summary

**Total Neo4j Commands:** 52
- Player Nodes: 5 commands
- Friends: 9 commands (+ guardrail for duplicate requests/friendships)  
- Blocking: 3 commands (+ guardrail for duplicate blocks)
- Messaging: 10 commands (+ guardrail for duplicate participants)
- Parties: 8 commands (+ guardrail for duplicate invites/members)
- Clans: 10 commands (+ guardrail for duplicate members)
- Follow: 4 commands (+ guardrail for duplicate follows)
- Analytics: 11+ commands

**HTTP Methods Used:**
- GET: 18+ commands (read/query)
- POST: 18+ commands (create)
- PATCH: 9+ commands (update)
- DELETE: 9 commands (remove/delete)
- PUT: 1 command (message edit)

**New Features:**
- **REMOVE Queries (Cypher REMOVE clause)**: Remove attributes from relationships and properties
  - Remove friend nickname
  - Clear conversation muted status
  - Clear clan description
- **Duplicate Relationship Guardrails**: Frontend now prevents duplicate relationships with 409 Conflict responses
  - Cannot send friend request if already friends or request pending
  - Cannot follow if already following
  - Cannot block if already blocked
  - Cannot invite to party if already invited/member
  - Cannot join clan if already member

---

## Graph Data Model

### Nodes (Entity Types)
- **Player** - Individual player node with status
- **Conversation** - Private or group chat space
- **Message** - Individual message in conversation
- **Party** - Temporary gaming group
- **Clan** - Persistent organization

### Relationship Types
- **FRIEND_OF** - Bidirectional friendship
- **FRIEND_REQUEST_FROM** - Pending request
- **BLOCKED_BY** - Negative relationship
- **MEMBER_OF** - Clan or party membership
- **PARTICIPANT_IN** - Message conversation membership
- **FOLLOWS** - One-directional follow
- **SENT** - Message authorship

### Key Graph Features
1. **Bidirectional Relationships** - Friendships work both ways
2. **Hierarchy** - Clan member roles and ranks
3. **Temporal Data** - Message timestamps and edited flags
4. **Real-Time Updates** - Status changes instantly propagate
5. **Transitive Relationships** - Can find friends-of-friends

---

## Usage Patterns

### For Admin/Moderation
- Use Player Nodes to manage player states
- Use Blocking to enforce community rules
- Use Clan commands to organize player groups

### For Players
- Friends for social networking
- Parties for quick grouping
- Clans for long-term team building
- Messaging for direct communication
- Follow to track favorite players

### For Game Features
- Leaderboard integration with friend scores
- Party-based matchmaking
- Clan wars and competitions
- Social achievement tracking

---

## Integration with MongoDB

While Neo4j handles relationships, MongoDB handles associated data:

| Neo4j Feature | MongoDB Counterpart | Purpose |
|---------------|-------------------|---------|
| Player Node | Player Document | Identity with graph-specific status |
| Clan Membership | Clan Data | Clan stats and configurations |
| Party Members | Match Data | Who played together |
| Friends List | Player Connections | Friendship count/stats |

---

## Performance Considerations

1. **Friend Suggestions** - Uses 2-hop graph traversal (friends-of-friends)
2. **Mutual Friends** - Efficient relationship intersection
3. **Clan Search** - Full-text search on name/tag
4. **Message Retrieval** - Paginated for large conversations
5. **Blocking** - Prevents unwanted relationship creation

---

## Access the Interactive Console

Execute any Neo4j command directly in the browser:
- **URL:** `http://localhost:8001/ui/interactive`
- **View:** Switch to "Neo4j Commands" section
- **Role:** Use Admin View for all commands, Player View for subset

See [INTERACTIVE_DASHBOARD.md](./INTERACTIVE_DASHBOARD.md) for detailed usage examples.
