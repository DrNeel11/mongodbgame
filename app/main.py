"""
Multiplayer Gaming System API
FastAPI application with MongoDB and Neo4j
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database.mongodb import connect_mongodb, close_mongodb
from app.database.neo4j_db import connect_neo4j, close_neo4j, is_neo4j_connected
from app.routes.mongodb_routes import (
    players_router,
    games_router,
    stats_router,
    matches_router,
    leaderboards_router,
    achievements_router,
    player_achievements_router,
    sessions_router,
    notifications_router,
    inventory_router,
)
from app.routes.neo4j_routes import (
    player_nodes_router,
    friends_router,
    blocking_router,
    messaging_router,
    party_router,
    clan_router,
    follow_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print("=" * 50)
    print("Starting up Multiplayer Gaming System API...")
    print("=" * 50)
    await connect_mongodb()
    await connect_neo4j()
    print("=" * 50)
    print("Startup complete!")
    print("=" * 50)
    
    yield
    
    # Shutdown
    print("Shutting down...")
    await close_mongodb()
    await close_neo4j()
    print("All connections closed!")


app = FastAPI(
    title="Multiplayer Gaming System API",
    description="""
## Cross-Platform Multiplayer Gaming System

A unified multiplayer system supporting crossplay across all gaming platforms.

### Features

#### MongoDB Collections (Stats & Records)
- **Players**: Core player profiles and settings
- **Games**: Game catalog with platform support
- **Player Stats**: Per-game statistics (kills, wins, K/D ratio, etc.)
- **Match History**: Detailed match records
- **Leaderboards**: Ranked standings
- **Achievements**: Achievement definitions and player progress
- **Game Sessions**: Active/historical gaming sessions
- **Notifications**: System notifications
- **Inventory**: Player items and currency

#### Neo4j Graph (Social & Messaging)
- **Player Nodes**: Social graph representation
- **Friendships**: Friend requests, friends list, mutual friends
- **Blocking**: Block/unblock players
- **Messaging**: Direct and group conversations
- **Parties**: Gaming lobbies/parties
- **Clans**: Player organizations/guilds
- **Following**: One-way follow relationships

### CRUD Operations
All endpoints demonstrate Create, Read, Update, and Delete operations.
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Routes
app.include_router(players_router, prefix="/api/v1")
app.include_router(games_router, prefix="/api/v1")
app.include_router(stats_router, prefix="/api/v1")
app.include_router(matches_router, prefix="/api/v1")
app.include_router(leaderboards_router, prefix="/api/v1")
app.include_router(achievements_router, prefix="/api/v1")
app.include_router(player_achievements_router, prefix="/api/v1")
app.include_router(sessions_router, prefix="/api/v1")
app.include_router(notifications_router, prefix="/api/v1")
app.include_router(inventory_router, prefix="/api/v1")

# Neo4j Routes
app.include_router(player_nodes_router, prefix="/api/v1")
app.include_router(friends_router, prefix="/api/v1")
app.include_router(blocking_router, prefix="/api/v1")
app.include_router(messaging_router, prefix="/api/v1")
app.include_router(party_router, prefix="/api/v1")
app.include_router(clan_router, prefix="/api/v1")
app.include_router(follow_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """API Root - Health Check"""
    return {
        "message": "Multiplayer Gaming System API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "databases": {
            "mongodb": "connected",
            "neo4j": "connected" if is_neo4j_connected() else "not connected"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
