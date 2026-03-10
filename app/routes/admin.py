from fastapi import APIRouter, HTTPException
import time
from app.crud.mongodb_crud import AdvancedMongoQueries
from app.crud.neo4j_crud import AdvancedNeo4jQueries
from app.database.neo4j_db import is_neo4j_connected
from app.config import get_settings
from app.database.mongodb import (
    get_players_collection,
    get_games_collection,
    get_player_stats_collection,
    get_match_history_collection,
    get_leaderboards_collection,
    get_achievements_collection,
    get_player_achievements_collection,
    get_game_sessions_collection,
    get_notifications_collection,
    get_player_inventory_collection,
)

router = APIRouter(prefix="/admin", tags=["Admin"])
settings = get_settings()


@router.get("/health")
async def health_check():
    """Return connectivity status for MongoDB and Neo4j and basic counts."""
    status = {"mongo": {}, "neo4j": {}}
    # MongoDB checks
    try:
        player_count = await AdvancedMongoQueries.count_players()
        status["mongo"]["connected"] = True
        status["mongo"]["player_count"] = player_count
    except Exception as e:
        status["mongo"]["connected"] = False
        status["mongo"]["error"] = str(e)

    # Neo4j checks
    try:
        status["neo4j"]["connected"] = bool(is_neo4j_connected())
        if status["neo4j"]["connected"]:
            # simple node count
            from app.database.neo4j_db import get_neo4j_driver
            driver = get_neo4j_driver()
            async with driver.session() as session:
                result = await session.run("MATCH (n) RETURN count(n) as nodes")
                rec = await result.single()
                status["neo4j"]["nodes"] = int(rec["nodes"]) if rec else 0
    except Exception as e:
        status["neo4j"]["connected"] = False
        status["neo4j"]["error"] = str(e)

    status["config"] = {
        "neo4j_uri": settings.neo4j_uri,
        "mongo_db": settings.mongodb_database
    }
    return status


@router.post("/bench")
async def run_benchmarks(sample_player_id: str = None):
    """Run quick benchmarks for common DB operations and return timings."""
    results = {}
    # Mongo: fetch players (small sample)
    try:
        t0 = time.perf_counter()
        players = await AdvancedMongoQueries.count_players()
        t1 = time.perf_counter()
        results["mongo_count_players_ms"] = round((t1 - t0) * 1000, 2)
    except Exception as e:
        results["mongo_error"] = str(e)

    try:
        t0 = time.perf_counter()
        games = await AdvancedMongoQueries.text_search_games("test", limit=10)
        t1 = time.perf_counter()
        results["mongo_text_search_games_ms"] = round((t1 - t0) * 1000, 2)
    except Exception as e:
        results["mongo_text_search_error"] = str(e)

    # Neo4j benchmarks: if connected
    if is_neo4j_connected():
        try:
            t0 = time.perf_counter()
            # if sample_player_id provided, run recommendation; otherwise run a lightweight query
            if sample_player_id:
                recs = await AdvancedNeo4jQueries.recommend_friends_by_common_friends(sample_player_id, limit=10)
            else:
                # run a small degree centrality on a random player (requires players exist)
                # we'll try to fetch any player id via node sample
                from app.database.neo4j_db import get_neo4j_driver
                driver = get_neo4j_driver()
                async with driver.session() as session:
                    res = await session.run("MATCH (p:Player) RETURN p.player_id as id LIMIT 1")
                    r = await res.single()
                    pid = r["id"] if r else None
                if pid:
                    recs = await AdvancedNeo4jQueries.degree_centrality(pid)
                else:
                    recs = None
            t1 = time.perf_counter()
            results["neo4j_sample_query_ms"] = round((t1 - t0) * 1000, 2)
        except Exception as e:
            results["neo4j_error"] = str(e)
    else:
        results["neo4j"] = "not_connected"

    return results


@router.post('/setup-indexes')
async def setup_indexes():
    """Create recommended MongoDB indexes for performance."""
    created = []
    try:
        # players: username unique
        players = get_players_collection()
        players.create_index('username', unique=True)
        created.append('players.username:unique')

        # games: text index on name/description/tags
        games = get_games_collection()
        games.create_index([('name', 'text'), ('description', 'text'), ('tags', 'text')], default_language='english')
        created.append('games.text')

        # player_stats: compound index
        ps = get_player_stats_collection()
        ps.create_index([('player_id', 1), ('game_id', 1)])
        created.append('player_stats.player_game')

        # match_history: index on timestamp and game_id
        mh = get_match_history_collection()
        mh.create_index('timestamp')
        mh.create_index('game_id')
        created.append('match_history.timestamp,game_id')

        # leaderboards: game_id
        lb = get_leaderboards_collection()
        lb.create_index('game_id')
        created.append('leaderboards.game_id')

        # notifications: player_id + created_at
        notif = get_notifications_collection()
        notif.create_index([('player_id', 1), ('created_at', -1)])
        created.append('notifications.player_created')

        # player_inventory: player+game
        inv = get_player_inventory_collection()
        inv.create_index([('player_id', 1), ('game_id', 1)])
        created.append('player_inventory.player_game')

    except Exception as e:
        return {"error": str(e), "created": created}

    return {"created": created}
