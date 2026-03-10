# Quick Start - API Testing Guide

## Access Points

1. **Home Page** (Fast, no auto-load)
   ```
   http://localhost:8001/ui/
   ```
   - Click "Players", "Games", or "Leaderboard" to load data on-demand
   - Instant page load (< 100ms)

2. **Admin Dashboard** (Complete API Reference)
   ```
   http://localhost:8001/ui/dashboard
   ```
   - All 70+ API endpoints with cURL examples
   - Copy-to-clipboard buttons
   - Organized by operation type

3. **Swagger UI** (Interactive Testing)
   ```
   http://localhost:8001/docs
   ```
   - Try out endpoints directly
   - See request/response schemas
   - Real-time API docs

---

## Most Useful MongoDB Commands

### List All Players
```bash
curl http://localhost:8001/api/v1/players?skip=0&limit=20
```

### Create a New Player
```bash
curl -X POST http://localhost:8001/api/v1/players \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "newplayer",
    "email": "newplayer@example.com",
    "platforms": ["pc", "xbox"]
  }'
```

### Get Player Details
```bash
curl http://localhost:8001/api/v1/players/PLAYER_ID
```

### Update Player
```bash
curl -X PUT http://localhost:8001/api/v1/players/PLAYER_ID \
  -H 'Content-Type: application/json' \
  -d '{"settings": {"language": "es"}}'
```

### List All Games
```bash
curl http://localhost:8001/api/v1/games?skip=0&limit=20
```

### Get Global Leaderboard
```bash
curl http://localhost:8001/api/v1/leaderboards?limit=50
```

### View Player Stats
```bash
curl http://localhost:8001/api/v1/stats/PLAYER_ID/GAME_ID
```

### Update Player Stats (After Match)
```bash
curl -X PATCH http://localhost:8001/api/v1/stats/PLAYER_ID/GAME_ID \
  -H 'Content-Type: application/json' \
  -d '{
    "wins": 1,
    "kills": 5,
    "deaths": 2,
    "total_playtime": 60
  }'
```

---

## Most Useful Neo4j Commands

### Get Player Friends
```bash
curl http://localhost:8001/api/v1/friends/PLAYER_ID
```

### Send Friend Request
```bash
curl -X POST http://localhost:8001/api/v1/friends/request \
  -H 'Content-Type: application/json' \
  -d '{
    "from_player_id": "PLAYER_ID_1",
    "to_player_id": "PLAYER_ID_2",
    "message": "Lets team up!"
  }'
```

### Create a Party/Lobby
```bash
curl -X POST http://localhost:8001/api/v1/parties \
  -H 'Content-Type: application/json' \
  -d '{
    "leader_id": "PLAYER_ID",
    "game_name": "Fortnite"
  }'
```

### Send a Direct Message
```bash
curl -X POST http://localhost:8001/api/v1/messages \
  -H 'Content-Type: application/json' \
  -d '{
    "conversation_id": "CONV_ID",
    "sender_id": "PLAYER_ID",
    "text": "Hey, how are you?"
  }'
```

### Create a Clan
```bash
curl -X POST http://localhost:8001/api/v1/clans \
  -H 'Content-Type: application/json' \
  -d '{
    "owner_id": "PLAYER_ID",
    "clan_name": "Elite Squad",
    "description": "Competitive esports team"
  }'
```

### Follow a Player
```bash
curl -X POST http://localhost:8001/api/v1/follow \
  -H 'Content-Type: application/json' \
  -d '{
    "follower_id": "PLAYER_ID_1",
    "following_id": "PLAYER_ID_2"
  }'
```

---

## Health Checks

### System Health
```bash
curl http://localhost:8001/health
```

### Admin Health (DB Status)
```bash
curl http://localhost:8001/admin/health
```

---

## Tips for Testing

1. **Get Real IDs First**
   - Run: `curl http://localhost:8001/api/v1/players?skip=0&limit=1`
   - Copy the `_id` or `player_id` from response

2. **Use with jq for Pretty Output**
   ```bash
   curl http://localhost:8001/api/v1/players | jq
   ```

3. **Chain Multiple Requests**
   ```bash
   # Get players, extract ID, then get their stats
   PLAYER_ID=$(curl -s http://localhost:8001/api/v1/players?limit=1 | jq -r '.[0]._id')
   curl http://localhost:8001/api/v1/stats/$PLAYER_ID
   ```

4. **For Windows PowerShell**
   ```powershell
   # Instead of curl, use Invoke-WebRequest
   Invoke-WebRequest -Uri "http://localhost:8001/api/v1/players" | ConvertTo-Json
   ```

5. **Common Pagination Pattern**
   - Use `skip` and `limit` parameters
   - Max limit is 100 records
   - Example: `?skip=0&limit=20`

---

## MongoDB Query Examples

### Aggregation for Leaderboard
```bash
# Get top 50 players by score (auto-aggregated)
curl "http://localhost:8001/api/v1/leaderboards?limit=50"
```

### Filter by Platform
```bash
curl "http://localhost:8001/api/v1/games?platform=pc"
```

---

## Neo4j Graph Queries

### Common Patterns

**Get Friend-of-Friend**
```bash
# Get PLAYER_A's friends, then their friends
curl http://localhost:8001/api/v1/friends/PLAYER_A
```

**Find Mutual Friends**
```bash
curl http://localhost:8001/api/v1/friends/PLAYER_A/mutual/PLAYER_B
```

**Get Friend Recommendations**
```bash
curl http://localhost:8001/api/v1/friends/PLAYER_ID/recommendations?limit=10
```

---

## Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 200 | Success | Great! |
| 400 | Bad Request | Check JSON format |
| 404 | Not Found | Check ID is correct |
| 503 | Neo4j Down | Start Neo4j service |

---

## Performance Expectations

- **Page Load**: < 100ms
- **First Data Load**: < 500ms
- **API Call**: < 200ms average
- **Bulk Results (100 items)**: < 1 second

---

## Troubleshooting

### Getting: "Neo4j not connected"
- Need to start Neo4j database
- Social features (friends, messaging) will be unavailable
- MongoDB operations still work fine

### Getting: "Cannot connect to localhost:8001"
- Is the server running?
- Run: `python -m uvicorn app.main:app --port 8001`

### API returns empty results
- Database might be empty
- Try creating test data first
- Or check if data exists: `curl http://localhost:8001/api/v1/players?limit=1`

---

## Next: Integrate with Postman/Insomnia

1. Export endpoint list from Admin Dashboard
2. Import into **Postman** or **Insomnia**
3. Set up environment variables for IDs
4. Use collections to test workflows

---

**Happy Testing! 🎮**

For complete API reference, visit: `http://localhost:8001/ui/dashboard`
