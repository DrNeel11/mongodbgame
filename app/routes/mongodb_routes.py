"""
MongoDB API Routes - Players, Games, Stats, Matches, Leaderboards, Achievements
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models.mongodb_models import (
    PlayerCreate, PlayerUpdate, PlayerResponse,
    GameCreate, GameUpdate, GameResponse,
    PlayerStatsCreate, PlayerStatsUpdate, PlayerStatsResponse,
    MatchCreate, MatchResponse,
    LeaderboardCreate, LeaderboardResponse, LeaderboardEntry,
    AchievementCreate, AchievementUpdate, AchievementResponse,
    PlayerAchievementCreate, PlayerAchievementUpdate, PlayerAchievementResponse,
    GameSessionCreate, GameSessionResponse,
    NotificationCreate, NotificationResponse,
    PlayerInventoryResponse,
)
from app.crud.mongodb_crud import (
    PlayersCRUD, GamesCRUD, PlayerStatsCRUD, MatchHistoryCRUD,
    LeaderboardsCRUD, AchievementsCRUD, PlayerAchievementsCRUD,
    GameSessionsCRUD, NotificationsCRUD, PlayerInventoryCRUD,
)


# ==================== PLAYERS ROUTER ====================
players_router = APIRouter(prefix="/players", tags=["Players (MongoDB)"])


@players_router.post("/", response_model=dict, status_code=201)
async def create_player(player: PlayerCreate):
    """CREATE: Register a new player"""
    # Check if username exists
    existing = await PlayersCRUD.get_player_by_username(player.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    player_data = player.model_dump()
    player_data["platforms"] = [p.value for p in player.platforms]
    result = await PlayersCRUD.create_player(player_data)
    return result


@players_router.get("/", response_model=List[dict])
async def get_all_players(skip: int = 0, limit: int = Query(default=100, le=100)):
    """READ: Get all players with pagination"""
    return await PlayersCRUD.get_all_players(skip=skip, limit=limit)


@players_router.get("/{player_id}", response_model=dict)
async def get_player(player_id: str):
    """READ: Get a single player by ID"""
    player = await PlayersCRUD.get_player(player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@players_router.put("/{player_id}", response_model=dict)
async def update_player(player_id: str, player: PlayerUpdate):
    """UPDATE: Update player information"""
    existing = await PlayersCRUD.get_player(player_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Player not found")
    
    update_data = player.model_dump(exclude_unset=True)
    if "platforms" in update_data and update_data["platforms"]:
        update_data["platforms"] = [p.value for p in update_data["platforms"]]
    
    return await PlayersCRUD.update_player(player_id, update_data)


@players_router.post("/{player_id}/login", response_model=dict)
async def player_login(player_id: str):
    """UPDATE: Record player login"""
    player = await PlayersCRUD.update_last_login(player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@players_router.delete("/{player_id}")
async def delete_player(player_id: str):
    """DELETE: Remove a player"""
    deleted = await PlayersCRUD.delete_player(player_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Player not found")
    return {"message": "Player deleted successfully"}


# ==================== GAMES ROUTER ====================
games_router = APIRouter(prefix="/games", tags=["Games (MongoDB)"])


@games_router.post("/", response_model=dict, status_code=201)
async def create_game(game: GameCreate):
    """CREATE: Add a new game to the catalog"""
    game_data = game.model_dump()
    game_data["platforms"] = [p.value for p in game.platforms]
    return await GamesCRUD.create_game(game_data)


@games_router.get("/", response_model=List[dict])
async def get_all_games(
    skip: int = 0, 
    limit: int = Query(default=100, le=100),
    platform: Optional[str] = None
):
    """READ: Get all games, optionally filtered by platform"""
    if platform:
        return await GamesCRUD.get_games_by_platform(platform)
    return await GamesCRUD.get_all_games(skip=skip, limit=limit)


@games_router.get("/{game_id}", response_model=dict)
async def get_game(game_id: str):
    """READ: Get a single game by ID"""
    game = await GamesCRUD.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


@games_router.put("/{game_id}", response_model=dict)
async def update_game(game_id: str, game: GameUpdate):
    """UPDATE: Update game information"""
    existing = await GamesCRUD.get_game(game_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Game not found")
    
    update_data = game.model_dump(exclude_unset=True)
    if "platforms" in update_data and update_data["platforms"]:
        update_data["platforms"] = [p.value for p in update_data["platforms"]]
    
    return await GamesCRUD.update_game(game_id, update_data)


@games_router.delete("/{game_id}")
async def delete_game(game_id: str):
    """DELETE: Remove a game"""
    deleted = await GamesCRUD.delete_game(game_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Game not found")
    return {"message": "Game deleted successfully"}


# ==================== PLAYER STATS ROUTER ====================
stats_router = APIRouter(prefix="/stats", tags=["Player Stats (MongoDB)"])


@stats_router.post("/", response_model=dict, status_code=201)
async def create_player_stats(stats: PlayerStatsCreate):
    """CREATE: Initialize stats for a player in a game"""
    # Check if stats already exist
    existing = await PlayerStatsCRUD.get_player_stats(stats.player_id, stats.game_id)
    if existing:
        raise HTTPException(status_code=400, detail="Stats already exist for this player/game")
    
    return await PlayerStatsCRUD.create_player_stats(stats.player_id, stats.game_id)


@stats_router.get("/{player_id}/{game_id}", response_model=dict)
async def get_player_stats(player_id: str, game_id: str):
    """READ: Get stats for a player in a specific game"""
    stats = await PlayerStatsCRUD.get_player_stats(player_id, game_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Stats not found")
    return stats


@stats_router.get("/{player_id}", response_model=List[dict])
async def get_all_player_stats(player_id: str):
    """READ: Get all game stats for a player"""
    return await PlayerStatsCRUD.get_all_stats_for_player(player_id)


@stats_router.patch("/{player_id}/{game_id}", response_model=dict)
async def increment_stats(player_id: str, game_id: str, increments: PlayerStatsUpdate):
    """UPDATE: Increment player stats (after a match)"""
    stats = await PlayerStatsCRUD.get_player_stats(player_id, game_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Stats not found")
    
    increment_data = increments.model_dump(exclude_unset=True)
    return await PlayerStatsCRUD.increment_stats(player_id, game_id, increment_data)


@stats_router.delete("/{player_id}/{game_id}")
async def delete_player_stats(player_id: str, game_id: str):
    """DELETE: Remove player stats for a game"""
    deleted = await PlayerStatsCRUD.delete_player_stats(player_id, game_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Stats not found")
    return {"message": "Stats deleted successfully"}


# ==================== MATCH HISTORY ROUTER ====================
matches_router = APIRouter(prefix="/matches", tags=["Match History (MongoDB)"])


@matches_router.post("/", response_model=dict, status_code=201)
async def create_match(match: MatchCreate):
    """CREATE: Record a completed match"""
    match_data = match.model_dump()
    match_data["players"] = [p.model_dump() for p in match.players]
    return await MatchHistoryCRUD.create_match(match_data)


@matches_router.get("/{match_id}", response_model=dict)
async def get_match(match_id: str):
    """READ: Get a match by ID"""
    match = await MatchHistoryCRUD.get_match(match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match


@matches_router.get("/player/{player_id}", response_model=List[dict])
async def get_player_matches(player_id: str, limit: int = Query(default=50, le=100)):
    """READ: Get match history for a player"""
    return await MatchHistoryCRUD.get_player_matches(player_id, limit=limit)


@matches_router.get("/game/{game_id}", response_model=List[dict])
async def get_game_matches(game_id: str, limit: int = Query(default=100, le=200)):
    """READ: Get recent matches for a game"""
    return await MatchHistoryCRUD.get_game_matches(game_id, limit=limit)


@matches_router.delete("/{match_id}")
async def delete_match(match_id: str):
    """DELETE: Remove a match record"""
    deleted = await MatchHistoryCRUD.delete_match(match_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Match not found")
    return {"message": "Match deleted successfully"}


# ==================== LEADERBOARDS ROUTER ====================
leaderboards_router = APIRouter(prefix="/leaderboards", tags=["Leaderboards (MongoDB)"])


@leaderboards_router.post("/", response_model=dict, status_code=201)
async def create_leaderboard(leaderboard: LeaderboardCreate):
    """CREATE: Create a new leaderboard"""
    return await LeaderboardsCRUD.create_leaderboard(leaderboard.model_dump())


@leaderboards_router.get("/{leaderboard_id}", response_model=dict)
async def get_leaderboard(leaderboard_id: str):
    """READ: Get a leaderboard by ID"""
    leaderboard = await LeaderboardsCRUD.get_leaderboard(leaderboard_id)
    if not leaderboard:
        raise HTTPException(status_code=404, detail="Leaderboard not found")
    return leaderboard


@leaderboards_router.get("/game/{game_id}", response_model=dict)
async def get_game_leaderboard(
    game_id: str, 
    leaderboard_type: str = "wins",
    timeframe: str = "all_time"
):
    """READ: Get a specific leaderboard for a game"""
    leaderboard = await LeaderboardsCRUD.get_game_leaderboard(game_id, leaderboard_type, timeframe)
    if not leaderboard:
        raise HTTPException(status_code=404, detail="Leaderboard not found")
    return leaderboard


@leaderboards_router.put("/{leaderboard_id}/entries", response_model=dict)
async def update_leaderboard_entries(leaderboard_id: str, entries: List[LeaderboardEntry]):
    """UPDATE: Replace all leaderboard entries"""
    leaderboard = await LeaderboardsCRUD.get_leaderboard(leaderboard_id)
    if not leaderboard:
        raise HTTPException(status_code=404, detail="Leaderboard not found")
    
    entries_data = [e.model_dump() for e in entries]
    return await LeaderboardsCRUD.update_leaderboard_entries(leaderboard_id, entries_data)


@leaderboards_router.post("/{leaderboard_id}/entry", response_model=dict)
async def add_leaderboard_entry(
    leaderboard_id: str, 
    player_id: str,
    username: str,
    score: int
):
    """UPDATE: Add or update a single player's entry"""
    result = await LeaderboardsCRUD.add_or_update_entry(leaderboard_id, player_id, username, score)
    if not result:
        raise HTTPException(status_code=404, detail="Leaderboard not found")
    return result


@leaderboards_router.delete("/{leaderboard_id}")
async def delete_leaderboard(leaderboard_id: str):
    """DELETE: Remove a leaderboard"""
    deleted = await LeaderboardsCRUD.delete_leaderboard(leaderboard_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Leaderboard not found")
    return {"message": "Leaderboard deleted successfully"}


# ==================== ACHIEVEMENTS ROUTER ====================
achievements_router = APIRouter(prefix="/achievements", tags=["Achievements (MongoDB)"])


@achievements_router.post("/", response_model=dict, status_code=201)
async def create_achievement(achievement: AchievementCreate):
    """CREATE: Create a new achievement"""
    return await AchievementsCRUD.create_achievement(achievement.model_dump())


@achievements_router.get("/{achievement_id}", response_model=dict)
async def get_achievement(achievement_id: str):
    """READ: Get an achievement by ID"""
    achievement = await AchievementsCRUD.get_achievement(achievement_id)
    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")
    return achievement


@achievements_router.get("/game/{game_id}", response_model=List[dict])
async def get_game_achievements(game_id: str):
    """READ: Get all achievements for a game"""
    return await AchievementsCRUD.get_game_achievements(game_id)


@achievements_router.put("/{achievement_id}", response_model=dict)
async def update_achievement(achievement_id: str, achievement: AchievementUpdate):
    """UPDATE: Update an achievement"""
    existing = await AchievementsCRUD.get_achievement(achievement_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Achievement not found")
    
    return await AchievementsCRUD.update_achievement(
        achievement_id, 
        achievement.model_dump(exclude_unset=True)
    )


@achievements_router.delete("/{achievement_id}")
async def delete_achievement(achievement_id: str):
    """DELETE: Remove an achievement"""
    deleted = await AchievementsCRUD.delete_achievement(achievement_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Achievement not found")
    return {"message": "Achievement deleted successfully"}


# ==================== PLAYER ACHIEVEMENTS ROUTER ====================
player_achievements_router = APIRouter(prefix="/player-achievements", tags=["Player Achievements (MongoDB)"])


@player_achievements_router.post("/", response_model=dict, status_code=201)
async def start_tracking_achievement(data: PlayerAchievementCreate):
    """CREATE: Start tracking an achievement for a player"""
    existing = await PlayerAchievementsCRUD.get_player_achievement(data.player_id, data.achievement_id)
    if existing:
        raise HTTPException(status_code=400, detail="Already tracking this achievement")
    
    return await PlayerAchievementsCRUD.start_achievement(data.player_id, data.achievement_id)


@player_achievements_router.get("/{player_id}", response_model=List[dict])
async def get_player_achievements(player_id: str, completed_only: bool = False):
    """READ: Get all achievements for a player"""
    return await PlayerAchievementsCRUD.get_player_achievements(player_id, completed_only)


@player_achievements_router.get("/{player_id}/{achievement_id}", response_model=dict)
async def get_player_achievement_progress(player_id: str, achievement_id: str):
    """READ: Get player's progress on a specific achievement"""
    pa = await PlayerAchievementsCRUD.get_player_achievement(player_id, achievement_id)
    if not pa:
        raise HTTPException(status_code=404, detail="Achievement not found for player")
    return pa


@player_achievements_router.patch("/{player_id}/{achievement_id}/progress", response_model=dict)
async def update_achievement_progress(player_id: str, achievement_id: str, data: PlayerAchievementUpdate):
    """UPDATE: Update achievement progress"""
    result = await PlayerAchievementsCRUD.update_progress(player_id, achievement_id, data.progress)
    if not result:
        raise HTTPException(status_code=404, detail="Achievement not found for player")
    return result


@player_achievements_router.post("/{player_id}/{achievement_id}/complete", response_model=dict)
async def complete_achievement(player_id: str, achievement_id: str):
    """UPDATE: Mark an achievement as completed"""
    result = await PlayerAchievementsCRUD.complete_achievement(player_id, achievement_id)
    if not result:
        raise HTTPException(status_code=404, detail="Achievement not found for player")
    return result


@player_achievements_router.delete("/{player_id}/{achievement_id}")
async def delete_player_achievement(player_id: str, achievement_id: str):
    """DELETE: Remove a player's achievement progress"""
    deleted = await PlayerAchievementsCRUD.delete_player_achievement(player_id, achievement_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Achievement not found for player")
    return {"message": "Player achievement deleted successfully"}


# ==================== GAME SESSIONS ROUTER ====================
sessions_router = APIRouter(prefix="/sessions", tags=["Game Sessions (MongoDB)"])


@sessions_router.post("/", response_model=dict, status_code=201)
async def start_session(session: GameSessionCreate):
    """CREATE: Start a new game session"""
    session_data = session.model_dump()
    session_data["platform"] = session.platform.value
    return await GameSessionsCRUD.create_session(session_data)


@sessions_router.get("/{session_id}", response_model=dict)
async def get_session(session_id: str):
    """READ: Get a session by ID"""
    session = await GameSessionsCRUD.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@sessions_router.get("/active/{player_id}", response_model=List[dict])
async def get_active_sessions(player_id: str):
    """READ: Get active sessions for a player"""
    return await GameSessionsCRUD.get_active_sessions(player_id)


@sessions_router.post("/{session_id}/end", response_model=dict)
async def end_session(session_id: str):
    """UPDATE: End a game session"""
    session = await GameSessionsCRUD.end_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@sessions_router.delete("/{session_id}")
async def delete_session(session_id: str):
    """DELETE: Remove an abandoned session"""
    deleted = await GameSessionsCRUD.delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted successfully"}


# ==================== NOTIFICATIONS ROUTER ====================
notifications_router = APIRouter(prefix="/notifications", tags=["Notifications (MongoDB)"])


@notifications_router.post("/", response_model=dict, status_code=201)
async def create_notification(notification: NotificationCreate):
    """CREATE: Create a new notification"""
    notification_data = notification.model_dump()
    notification_data["notification_type"] = notification.notification_type.value
    return await NotificationsCRUD.create_notification(notification_data)


@notifications_router.get("/{notification_id}", response_model=dict)
async def get_notification(notification_id: str):
    """READ: Get a notification by ID"""
    notification = await NotificationsCRUD.get_notification(notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification


@notifications_router.get("/player/{player_id}", response_model=List[dict])
async def get_player_notifications(
    player_id: str, 
    unread_only: bool = False,
    limit: int = Query(default=50, le=100)
):
    """READ: Get notifications for a player"""
    return await NotificationsCRUD.get_player_notifications(player_id, unread_only, limit)


@notifications_router.post("/{notification_id}/read", response_model=dict)
async def mark_notification_read(notification_id: str):
    """UPDATE: Mark a notification as read"""
    notification = await NotificationsCRUD.mark_as_read(notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification


@notifications_router.post("/player/{player_id}/read-all")
async def mark_all_notifications_read(player_id: str):
    """UPDATE: Mark all notifications as read for a player"""
    count = await NotificationsCRUD.mark_all_as_read(player_id)
    return {"message": f"{count} notifications marked as read"}


@notifications_router.delete("/{notification_id}")
async def delete_notification(notification_id: str):
    """DELETE: Remove a notification"""
    deleted = await NotificationsCRUD.delete_notification(notification_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification deleted successfully"}


@notifications_router.delete("/player/{player_id}/old")
async def delete_old_notifications(player_id: str, days_old: int = 30):
    """DELETE: Remove old read notifications"""
    count = await NotificationsCRUD.delete_old_notifications(player_id, days_old)
    return {"message": f"{count} old notifications deleted"}


# ==================== PLAYER INVENTORY ROUTER ====================
inventory_router = APIRouter(prefix="/inventory", tags=["Player Inventory (MongoDB)"])


@inventory_router.post("/{player_id}/{game_id}", response_model=dict, status_code=201)
async def create_inventory(player_id: str, game_id: str):
    """CREATE: Initialize inventory for a player in a game"""
    existing = await PlayerInventoryCRUD.get_inventory(player_id, game_id)
    if existing:
        raise HTTPException(status_code=400, detail="Inventory already exists")
    
    return await PlayerInventoryCRUD.create_inventory(player_id, game_id)


@inventory_router.get("/{player_id}/{game_id}", response_model=dict)
async def get_inventory(player_id: str, game_id: str):
    """READ: Get player's inventory for a game"""
    inventory = await PlayerInventoryCRUD.get_inventory(player_id, game_id)
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory


@inventory_router.post("/{player_id}/{game_id}/item", response_model=dict)
async def add_item_to_inventory(
    player_id: str, 
    game_id: str,
    item_id: str,
    item_name: str,
    item_type: str,
    quantity: int = 1
):
    """UPDATE: Add an item to inventory"""
    item = {
        "item_id": item_id,
        "item_name": item_name,
        "item_type": item_type,
        "quantity": quantity
    }
    result = await PlayerInventoryCRUD.add_item(player_id, game_id, item)
    if not result:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return result


@inventory_router.patch("/{player_id}/{game_id}/currency", response_model=dict)
async def update_currency(player_id: str, game_id: str, amount: int):
    """UPDATE: Add or subtract currency"""
    result = await PlayerInventoryCRUD.update_currency(player_id, game_id, amount)
    if not result:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return result


@inventory_router.delete("/{player_id}/{game_id}/item/{item_id}", response_model=dict)
async def remove_item_from_inventory(player_id: str, game_id: str, item_id: str):
    """UPDATE: Remove an item from inventory"""
    result = await PlayerInventoryCRUD.remove_item(player_id, game_id, item_id)
    if not result:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return result


@inventory_router.delete("/{player_id}/{game_id}")
async def delete_inventory(player_id: str, game_id: str):
    """DELETE: Remove player's inventory for a game"""
    deleted = await PlayerInventoryCRUD.delete_inventory(player_id, game_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return {"message": "Inventory deleted successfully"}
