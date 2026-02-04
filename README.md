# Multiplayer Gaming System API

A cross-platform multiplayer gaming system built with **FastAPI**, **MongoDB**, and **Neo4j**.

## Architecture Overview

### MongoDB (Document Store)
Used for high-volume stats, records, and structured data:
- **players** - Core player profiles
- **games** - Game catalog
- **player_stats** - Per-game statistics
- **match_history** - Match records
- **leaderboards** - Ranked standings
- **achievements** - Achievement definitions
- **player_achievements** - Player progress
- **game_sessions** - Gaming sessions
- **notifications** - System notifications
- **player_inventory** - Items and currency

### Neo4j (Graph Database)
Used for relationships and social features:
- **Player nodes** - Social graph representation
- **FRIENDS_WITH** - Friendships
- **SENT_REQUEST** - Friend requests
- **BLOCKED** - Blocked players
- **Conversations & Messages** - Messaging system
- **Parties** - Gaming lobbies
- **Clans** - Player organizations
- **FOLLOWS** - One-way follow

## Project Structure

```
mongodbproj/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── database/
│   │   ├── __init__.py
│   │   ├── mongodb.py       # MongoDB connection
│   │   └── neo4j_db.py      # Neo4j connection
│   ├── models/
│   │   ├── __init__.py
│   │   ├── mongodb_models.py    # Pydantic models for MongoDB
│   │   └── neo4j_models.py      # Pydantic models for Neo4j
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── mongodb_crud.py  # MongoDB CRUD operations
│   │   └── neo4j_crud.py    # Neo4j CRUD operations
│   └── routes/
│       ├── __init__.py
│       ├── mongodb_routes.py    # MongoDB API endpoints
│       └── neo4j_routes.py      # Neo4j API endpoints
├── requirements.txt
├── .env.example
└── README.md
```

## Setup Instructions

### 1. Prerequisites
- Python 3.9+
- MongoDB (local or Atlas)
- Neo4j (local or Aura)

### 2. Install Dependencies

```bash
cd mongodbproj
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and update with your database credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=multiplayer_gaming

NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here
```

### 4. Start Databases

**MongoDB** (if using Docker):
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

**Neo4j** (if using Docker):
```bash
docker run -d -p 7474:7474 -p 7687:7687 --name neo4j -e NEO4J_AUTH=neo4j/your_password neo4j:latest
```

### 5. Run the Application

```bash
uvicorn app.main:app --reload
```

Or:
```bash
python -m app.main
```

The API will be available at: http://localhost:8000

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## CRUD Operations Summary

### MongoDB Endpoints

| Resource | Create | Read | Update | Delete |
|----------|--------|------|--------|--------|
| Players | POST /api/v1/players | GET /api/v1/players/{id} | PUT /api/v1/players/{id} | DELETE /api/v1/players/{id} |
| Games | POST /api/v1/games | GET /api/v1/games/{id} | PUT /api/v1/games/{id} | DELETE /api/v1/games/{id} |
| Stats | POST /api/v1/stats | GET /api/v1/stats/{player}/{game} | PATCH /api/v1/stats/{player}/{game} | DELETE /api/v1/stats/{player}/{game} |
| Matches | POST /api/v1/matches | GET /api/v1/matches/{id} | - | DELETE /api/v1/matches/{id} |
| Leaderboards | POST /api/v1/leaderboards | GET /api/v1/leaderboards/{id} | PUT /api/v1/leaderboards/{id}/entries | DELETE /api/v1/leaderboards/{id} |
| Achievements | POST /api/v1/achievements | GET /api/v1/achievements/{id} | PUT /api/v1/achievements/{id} | DELETE /api/v1/achievements/{id} |
| Sessions | POST /api/v1/sessions | GET /api/v1/sessions/{id} | POST /api/v1/sessions/{id}/end | DELETE /api/v1/sessions/{id} |
| Notifications | POST /api/v1/notifications | GET /api/v1/notifications/{id} | POST /api/v1/notifications/{id}/read | DELETE /api/v1/notifications/{id} |
| Inventory | POST /api/v1/inventory/{p}/{g} | GET /api/v1/inventory/{p}/{g} | POST /api/v1/inventory/{p}/{g}/item | DELETE /api/v1/inventory/{p}/{g} |

### Neo4j Endpoints

| Resource | Create | Read | Update | Delete |
|----------|--------|------|--------|--------|
| Player Nodes | POST /api/v1/player-nodes | GET /api/v1/player-nodes/{id} | PATCH /api/v1/player-nodes/{id}/status | DELETE /api/v1/player-nodes/{id} |
| Friends | POST /api/v1/friends/request | GET /api/v1/friends/{id} | PATCH /api/v1/friends/nickname | DELETE /api/v1/friends |
| Blocking | POST /api/v1/block | GET /api/v1/block/{id} | - | DELETE /api/v1/block |
| Messages | POST /api/v1/messages | GET /api/v1/messages/conversation/{id}/messages | PUT /api/v1/messages/{id} | DELETE /api/v1/messages/{id} |
| Parties | POST /api/v1/parties | GET /api/v1/parties/{id} | PATCH /api/v1/parties/{id} | DELETE /api/v1/parties/{id} |
| Clans | POST /api/v1/clans | GET /api/v1/clans/{id} | PATCH /api/v1/clans/{id} | DELETE /api/v1/clans/{id} |
| Follow | POST /api/v1/follow | GET /api/v1/follow/following/{id} | - | DELETE /api/v1/follow |

## Example Usage

### Create a Player (MongoDB)
```bash
curl -X POST "http://localhost:8000/api/v1/players" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "GamerPro123",
    "email": "gamer@example.com",
    "platforms": ["xbox", "pc"]
  }'
```

### Create Player Node (Neo4j)
```bash
curl -X POST "http://localhost:8000/api/v1/player-nodes" \
  -H "Content-Type: application/json" \
  -d '{
    "player_id": "PLAYER_ID_FROM_MONGODB",
    "username": "GamerPro123",
    "status": "online"
  }'
```

### Send Friend Request
```bash
curl -X POST "http://localhost:8000/api/v1/friends/request" \
  -H "Content-Type: application/json" \
  -d '{
    "from_player_id": "PLAYER1_ID",
    "to_player_id": "PLAYER2_ID",
    "message": "Lets play together!"
  }'
```

### Record a Match
```bash
curl -X POST "http://localhost:8000/api/v1/matches" \
  -H "Content-Type: application/json" \
  -d '{
    "game_id": "GAME_ID",
    "players": [
      {"player_id": "P1", "team": "red", "score": 15, "kills": 10, "deaths": 5},
      {"player_id": "P2", "team": "blue", "score": 12, "kills": 8, "deaths": 7}
    ],
    "game_mode": "deathmatch",
    "duration": 600,
    "winner_team": "red"
  }'
```

## License

MIT License
