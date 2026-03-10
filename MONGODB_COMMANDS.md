# MongoDB Commands Reference

## Overview

MongoDB in the GameBD system manages all game data, player statistics, and persistent game state. These commands handle player profiles, game definitions, match records, and achievements.

## All MongoDB Commands (Organized by Category)

### 1. PLAYERS (5 commands)

Player profiles store core identity and progression data.

| # | Command | HTTP | Path | Parameters | Purpose |
|---|---------|------|------|------------|---------|
| 1 | Create Player | POST | `/players` | username, email, level, platforms | Register a new player with initial stats |
| 2 | Get All Players | GET | `/players` | skip, limit | List players with pagination |
| 3 | Get Player by ID | GET | `/players/{player_id}` | player_id | Retrieve specific player profile |
| 4 | Update Player | PATCH | `/players/{player_id}` | player_id, level, xp, ... | Modify player profile data |
| 5 | Delete Player | DELETE | `/players/{player_id}` | player_id | Remove player account |

**Player Profile Includes:**
- Player ID (MongoDB ObjectId)
- Username (unique identifier)
- Email address
- Current level
- Total XP
- Joined date
- Last login
- Profile image
- Bio/description
- Preferred platforms

### 2. GAMES (4+ commands)

Game definitions catalog available games and their attributes.

| # | Command | HTTP | Path | Parameters | Purpose |
|---|---------|------|------|------------|---------|
| 6 | Get All Games | GET | `/games` | skip, limit | List all games in system |
| 7 | Create Game | POST | `/games` | title, genre, max_players, description | Add new game definition |
| 8 | Get Game by ID | GET | `/games/{game_id}` | game_id | Retrieve game details and settings |
| 9 | Update Game | PATCH | `/games/{game_id}` | game_id, title, genre, max_players | Modify game properties |

**Game Properties:**
- Title (game name)
- Genre (action, strategy, RPG, etc.)
- Description
- Max players per match
- Min/max level requirements
- Release date
- Developer info
- Cover art

### 3. PLAYER STATS (3+ commands)

Player statistics track performance and achievements.

| # | Command | HTTP | Path | Parameters | Purpose |
|---|---------|------|------|------------|---------|
| 10 | Create Player Stats | POST | `/players/{player_id}/stats` | player_id, wins, losses, draws | Initialize statistics record |
| 11 | Get Player Stats | GET | `/players/{player_id}/stats` | player_id | View comprehensive player statistics |
| 12 | Update Player Stats | PATCH | `/players/{player_id}/stats` | player_id, wins, losses, ... | Update stat values |

**Stats Include:**
- Total matches played
- Wins / Losses / Draws
- Win rate percentage
- Average K/D ratio
- Total kills / deaths
- Headshots
- Accuracy percentage
- Play time (hours)
- Favorite game
- Peak rank achieved

### 4. MATCHES (4+ commands)

Match history records detailed information about completed games.

| # | Command | HTTP | Path | Parameters | Purpose |
|---|---------|------|------|------------|---------|
| 13 | Create Match | POST | `/matches` | game_id, players, winner_id, duration | Record a completed match |
| 14 | Get All Matches | GET | `/matches` | skip, limit | List all matches in system |
| 15 | Get Match by ID | GET | `/matches/{match_id}` | match_id | Retrieve specific match details |
| 16 | Get Player Matches | GET | `/players/{player_id}/matches` | player_id, skip, limit | Get match history for a player |

**Match Data Includes:**
- Game ID
- Participating players
- Match start/end time
- Duration
- Winner/loser
- Final scores
- Map/mode
- Performance stats
- MVP designation

### 5. LEADERBOARDS (3 commands)

Leaderboards rank players by performance metrics.

| # | Command | HTTP | Path | Parameters | Purpose |
|---|---------|------|------|------------|---------|
| 17 | Create Leaderboard | POST | `/leaderboards` | name, game_id, criteria | Set up new leaderboard |
| 18 | Get Leaderboard | GET | `/leaderboards` | game_id, limit, offset | View rankings (default: by total wins) |
| 19 | Get Player Rank | GET | `/players/{player_id}/leaderboards` | player_id | Find player's position on leaderboards |

**Leaderboard Types:**
- Overall (all players, all time)
- By Game (ranked within each game)
- Monthly (current month only)
- Weekly (current week only)
- Friends (among your friends only)
- Seasonal (by season/battle pass)

### 6. ACHIEVEMENTS (3+ commands)

Achievements are badges and progress milestones for players.

| # | Command | HTTP | Path | Parameters | Purpose |
|---|---------|------|------|------------|---------|
| 20 | Create Achievement | POST | `/achievements` | name, description, icon, points | Define new achievement type |
| 21 | Get All Achievements | GET | `/achievements` | skip, limit | List all possible achievements |
| 22 | Create Player Achievement | POST | `/players/{player_id}/achievements` | player_id, achievement_id, earned_at | Award achievement to player |

**Achievement Examples:**
- "First Blood" - First match win
- "Veteran" - 100 matches played
- "Sharpshooter" - 90%+ accuracy
- "Social Butterfly" - 50 friends
- "Clan Leader" - Lead a clan
- "Streak Master" - 10 consecutive wins
- "Legendary" - Reach level 100

### 7. GAME SESSIONS (3 commands)

Game sessions track active play sessions.

| # | Command | HTTP | Path | Parameters | Purpose |
|---|---------|------|------|------------|---------|
| 23 | Create Game Session | POST | `/players/{player_id}/sessions` | player_id, game_id, start_time | Begin a play session |
| 24 | Get Player Sessions | GET | `/players/{player_id}/sessions` | player_id, skip, limit | View session history |
| 25 | Update Game Session | PATCH | `/players/{player_id}/sessions/{session_id}` | session_id, end_time, duration | Complete session |

**Session Data:**
- Start timestamp
- End timestamp
- Duration
- Game played
- Matches in session
- XP earned
- Achievements unlocked

### 8. NOTIFICATIONS (2 commands)

Notifications inform players of events and achievements.

| # | Command | HTTP | Path | Parameters | Purpose |
|---|---------|------|------|------------|---------|
| 26 | Create Notification | POST | `/players/{player_id}/notifications` | player_id, type, message, data | Send notification to player |
| 27 | Get Notifications | GET | `/players/{player_id}/notifications` | player_id, unread_only | Retrieve player's notifications |

**Notification Types:**
- Friend request received
- Achievement unlocked
- Match result
- Clan invitation
- Level up
- Weekly reward
- Season end
- Server maintenance

### 9. INVENTORY (2+ commands)

Player inventory tracks items, cosmetics, and currency.

| # | Command | HTTP | Path | Parameters | Purpose |
|---|---------|------|------|------------|---------|
| 28 | Get Player Inventory | GET | `/players/{player_id}/inventory` | player_id | View owned items and currency |
| 29 | Add Inventory Item | POST | `/players/{player_id}/inventory` | player_id, item_id, quantity | Add item or currency to inventory |

**Inventory Includes:**
- Cosmetic skins
- Weapon camos
- Emotes/sprays
- Battle pass status
- Coins (premium currency)
- Credits (earned currency)
- Loot boxes
- Vouchers

---

## MongoDB Command Summary

**Total MongoDB Commands:** 29+
- Players: 5 commands
- Games: 4 commands
- Player Stats: 3 commands
- Matches: 4 commands
- Leaderboards: 3 commands
- Achievements: 3 commands
- Game Sessions: 3 commands
- Notifications: 2 commands
- Inventory: 2+ commands

**HTTP Methods Used:**
- GET: 11+ commands (read/query)
- POST: 11+ commands (create)
- PATCH: 5+ commands (update)
- DELETE: 2+ commands (remove)

---

## Data Collections

### players
```javascript
{
  _id: ObjectId,
  username: String (unique),
  email: String (unique),
  level: Number,
  xp: Number,
  created_at: Date,
  last_login: Date,
  platforms: [String],
  bio: String,
  avatar_url: String
}
```

### games
```javascript
{
  _id: ObjectId,
  title: String,
  genre: String,
  description: String,
  max_players: Number,
  min_level_required: Number,
  release_date: Date,
  icon_url: String,
  is_active: Boolean
}
```

### player_stats
```javascript
{
  _id: ObjectId,
  player_id: ObjectId,
  matches_played: Number,
  wins: Number,
  losses: Number,
  draws: Number,
  win_rate: Number,
  total_kills: Number,
  total_deaths: Number,
  kd_ratio: Number,
  accuracy: Number,
  headshots: Number,
  playtime_hours: Number,
  peak_rank: String
}
```

### matches
```javascript
{
  _id: ObjectId,
  game_id: ObjectId,
  players: [ObjectId],
  winner_id: ObjectId,
  loser_ids: [ObjectId],
  start_time: Date,
  end_time: Date,
  duration: Number,
  scores: {player_id: Number},
  map: String,
  mode: String,
  mvp_player: ObjectId
}
```

### leaderboards
```javascript
{
  _id: ObjectId,
  name: String,
  game_id: ObjectId,
  criteria: String,  // 'wins', 'level', 'xp', 'winrate'
  period: String,    // 'all_time', 'monthly', 'weekly'
  entries: [{
    player_id: ObjectId,
    rank: Number,
    value: Number,
    updated_at: Date
  }]
}
```

### achievements
```javascript
{
  _id: ObjectId,
  name: String,
  description: String,
  icon_url: String,
  reward_points: Number,
  criteria: String,
  difficulty: String
}
```

### player_achievements
```javascript
{
  _id: ObjectId,
  player_id: ObjectId,
  achievement_id: ObjectId,
  earned_at: Date,
  progress: Number  // 0-100% for multi-step achievements
}
```

### notifications
```javascript
{
  _id: ObjectId,
  player_id: ObjectId,
  type: String,
  message: String,
  data: Object,
  created_at: Date,
  read: Boolean,
  action_url: String
}
```

### player_inventory
```javascript
{
  _id: ObjectId,
  player_id: ObjectId,
  items: [{
    item_id: String,
    quantity: Number,
    acquired_at: Date
  }],
  coins: Number,    // Premium currency
  credits: Number   // Earned currency
}
```

---

## Common Query Patterns

### Get Top Players by Wins
```
GET /leaderboards?limit=10
```
Returns top 10 players ranked by wins

### Get Player's Full Profile
```
GET /players/{player_id}
GET /players/{player_id}/stats
GET /players/{player_id}/achievements
GET /players/{player_id}/inventory
```

### Track Player Progress
```
GET /players/{player_id}/matches?limit=20
GET /players/{player_id}/sessions
Track wins, playtime, and achievements

### Check Game Activity
```
GET /matches?skip=0&limit=20
GET /games
```

### Player Progression
```
Level increases with XP
XP earned per match varies with:
- Match duration
- Player performance (K/D, accuracy)
- Match type (ranked vs casual)
- Win/loss outcome
```

---

## Indexing Strategy

For optimal performance, these fields are indexed:
- `players.username` - unique index
- `players.email` - unique index
- `player_stats.wins` - for leaderboard sorting
- `matches.game_id` - filter by game
- `matches.start_time` - recent match queries
- `player_achievements.player_id` - quick achievement lookup
- `notifications.player_id` - player notifications
- `leaderboards.criteria` - leaderboard filtering

---

## Integration with Neo4j

MongoDB focuses on game state while Neo4j handles relationships:

| MongoDB Data | Neo4j Relationship | Use Case |
|-------------|-------------------|----------|
| Player profile | Player node identity | Profile lookup |
| Match results | Who played together | Party/clan matchmaking |
| Achievements | Achievement milestones | Social proofing |
| Level/XP | Player progression | Rankings display |
| Playtime | Engagement metric | Loyalty rewards |

---

## Access the Interactive Console

Execute any MongoDB command directly in the browser:
- **URL:** `http://localhost:8001/ui/interactive`
- **View:** Switch to "MongoDB Commands" section
- **Role:** Use Admin View for all commands, Player View restricted subset

**For Players:**
- Browse other players
- View leaderboards
- Check own stats and achievements
- View own inventory

**For Admins:**
- Full CRUD on all collections
- Create test data
- Audit matches and sessions
- Manage achievements
- Issue notifications

See [INTERACTIVE_DASHBOARD.md](./INTERACTIVE_DASHBOARD.md) for detailed usage examples.
