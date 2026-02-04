"""
MongoDB CRUD Operations for the Multiplayer Gaming System
Demonstrates: Create, Read, Update, Delete operations
"""

from datetime import datetime
from typing import List, Optional
from bson import ObjectId
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


# ==================== HELPER FUNCTIONS ====================
def serialize_doc(doc):
    """Convert MongoDB document ObjectId to string"""
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


def serialize_docs(docs):
    """Convert list of MongoDB documents"""
    return [serialize_doc(doc) for doc in docs]


# ==================== PLAYERS CRUD ====================
class PlayersCRUD:
    
    # CREATE
    @staticmethod
    async def create_player(player_data: dict) -> dict:
        """Create a new player"""
        collection = get_players_collection()
        player_data["created_at"] = datetime.utcnow()
        player_data["last_login"] = None
        result = await collection.insert_one(player_data)
        player_data["_id"] = str(result.inserted_id)
        return player_data
    
    # READ
    @staticmethod
    async def get_player(player_id: str) -> Optional[dict]:
        """Get a single player by ID"""
        collection = get_players_collection()
        player = await collection.find_one({"_id": ObjectId(player_id)})
        return serialize_doc(player)
    
    @staticmethod
    async def get_player_by_username(username: str) -> Optional[dict]:
        """Get a player by username"""
        collection = get_players_collection()
        player = await collection.find_one({"username": username})
        return serialize_doc(player)
    
    @staticmethod
    async def get_all_players(skip: int = 0, limit: int = 100) -> List[dict]:
        """Get all players with pagination"""
        collection = get_players_collection()
        cursor = collection.find().skip(skip).limit(limit)
        players = await cursor.to_list(length=limit)
        return serialize_docs(players)
    
    # UPDATE
    @staticmethod
    async def update_player(player_id: str, update_data: dict) -> Optional[dict]:
        """Update a player"""
        collection = get_players_collection()
        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}
        if update_data:
            await collection.update_one(
                {"_id": ObjectId(player_id)},
                {"$set": update_data}
            )
        return await PlayersCRUD.get_player(player_id)
    
    @staticmethod
    async def update_last_login(player_id: str) -> Optional[dict]:
        """Update player's last login timestamp"""
        collection = get_players_collection()
        await collection.update_one(
            {"_id": ObjectId(player_id)},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        return await PlayersCRUD.get_player(player_id)
    
    # DELETE
    @staticmethod
    async def delete_player(player_id: str) -> bool:
        """Delete a player"""
        collection = get_players_collection()
        result = await collection.delete_one({"_id": ObjectId(player_id)})
        return result.deleted_count > 0


# ==================== GAMES CRUD ====================
class GamesCRUD:
    
    # CREATE
    @staticmethod
    async def create_game(game_data: dict) -> dict:
        """Create a new game"""
        collection = get_games_collection()
        game_data["release_date"] = datetime.utcnow()
        result = await collection.insert_one(game_data)
        game_data["_id"] = str(result.inserted_id)
        return game_data
    
    # READ
    @staticmethod
    async def get_game(game_id: str) -> Optional[dict]:
        """Get a single game by ID"""
        collection = get_games_collection()
        game = await collection.find_one({"_id": ObjectId(game_id)})
        return serialize_doc(game)
    
    @staticmethod
    async def get_all_games(skip: int = 0, limit: int = 100) -> List[dict]:
        """Get all games with pagination"""
        collection = get_games_collection()
        cursor = collection.find().skip(skip).limit(limit)
        games = await cursor.to_list(length=limit)
        return serialize_docs(games)
    
    @staticmethod
    async def get_games_by_platform(platform: str) -> List[dict]:
        """Get games available on a specific platform"""
        collection = get_games_collection()
        cursor = collection.find({"platforms": platform})
        games = await cursor.to_list(length=100)
        return serialize_docs(games)
    
    # UPDATE
    @staticmethod
    async def update_game(game_id: str, update_data: dict) -> Optional[dict]:
        """Update a game"""
        collection = get_games_collection()
        update_data = {k: v for k, v in update_data.items() if v is not None}
        if update_data:
            await collection.update_one(
                {"_id": ObjectId(game_id)},
                {"$set": update_data}
            )
        return await GamesCRUD.get_game(game_id)
    
    # DELETE
    @staticmethod
    async def delete_game(game_id: str) -> bool:
        """Delete a game"""
        collection = get_games_collection()
        result = await collection.delete_one({"_id": ObjectId(game_id)})
        return result.deleted_count > 0


# ==================== PLAYER STATS CRUD ====================
class PlayerStatsCRUD:
    
    # CREATE
    @staticmethod
    async def create_player_stats(player_id: str, game_id: str) -> dict:
        """Create initial stats for a player in a game"""
        collection = get_player_stats_collection()
        stats_data = {
            "player_id": player_id,
            "game_id": game_id,
            "total_playtime": 0,
            "wins": 0,
            "losses": 0,
            "kills": 0,
            "deaths": 0,
            "xp": 0,
            "level": 1,
            "kd_ratio": 0.0,
            "win_rate": 0.0,
            "last_updated": datetime.utcnow()
        }
        result = await collection.insert_one(stats_data)
        stats_data["_id"] = str(result.inserted_id)
        return stats_data
    
    # READ
    @staticmethod
    async def get_player_stats(player_id: str, game_id: str) -> Optional[dict]:
        """Get stats for a player in a specific game"""
        collection = get_player_stats_collection()
        stats = await collection.find_one({
            "player_id": player_id,
            "game_id": game_id
        })
        return serialize_doc(stats)
    
    @staticmethod
    async def get_all_stats_for_player(player_id: str) -> List[dict]:
        """Get all game stats for a player"""
        collection = get_player_stats_collection()
        cursor = collection.find({"player_id": player_id})
        stats = await cursor.to_list(length=100)
        return serialize_docs(stats)
    
    # UPDATE
    @staticmethod
    async def increment_stats(player_id: str, game_id: str, increments: dict) -> Optional[dict]:
        """Increment player stats (kills, deaths, wins, etc.)"""
        collection = get_player_stats_collection()
        
        # Build increment operations
        inc_ops = {k: v for k, v in increments.items() if v is not None and v != 0}
        
        if inc_ops:
            await collection.update_one(
                {"player_id": player_id, "game_id": game_id},
                {
                    "$inc": inc_ops,
                    "$set": {"last_updated": datetime.utcnow()}
                }
            )
        
        # Recalculate ratios
        stats = await PlayerStatsCRUD.get_player_stats(player_id, game_id)
        if stats:
            kd_ratio = stats["kills"] / max(stats["deaths"], 1)
            total_matches = stats["wins"] + stats["losses"]
            win_rate = (stats["wins"] / max(total_matches, 1)) * 100
            
            await collection.update_one(
                {"player_id": player_id, "game_id": game_id},
                {"$set": {"kd_ratio": round(kd_ratio, 2), "win_rate": round(win_rate, 2)}}
            )
        
        return await PlayerStatsCRUD.get_player_stats(player_id, game_id)
    
    # DELETE
    @staticmethod
    async def delete_player_stats(player_id: str, game_id: str) -> bool:
        """Delete player stats for a game"""
        collection = get_player_stats_collection()
        result = await collection.delete_one({
            "player_id": player_id,
            "game_id": game_id
        })
        return result.deleted_count > 0


# ==================== MATCH HISTORY CRUD ====================
class MatchHistoryCRUD:
    
    # CREATE
    @staticmethod
    async def create_match(match_data: dict) -> dict:
        """Record a completed match"""
        collection = get_match_history_collection()
        match_data["timestamp"] = datetime.utcnow()
        result = await collection.insert_one(match_data)
        match_data["_id"] = str(result.inserted_id)
        return match_data
    
    # READ
    @staticmethod
    async def get_match(match_id: str) -> Optional[dict]:
        """Get a single match by ID"""
        collection = get_match_history_collection()
        match = await collection.find_one({"_id": ObjectId(match_id)})
        return serialize_doc(match)
    
    @staticmethod
    async def get_player_matches(player_id: str, limit: int = 50) -> List[dict]:
        """Get match history for a player"""
        collection = get_match_history_collection()
        cursor = collection.find(
            {"players.player_id": player_id}
        ).sort("timestamp", -1).limit(limit)
        matches = await cursor.to_list(length=limit)
        return serialize_docs(matches)
    
    @staticmethod
    async def get_game_matches(game_id: str, limit: int = 100) -> List[dict]:
        """Get recent matches for a game"""
        collection = get_match_history_collection()
        cursor = collection.find(
            {"game_id": game_id}
        ).sort("timestamp", -1).limit(limit)
        matches = await cursor.to_list(length=limit)
        return serialize_docs(matches)
    
    # UPDATE (typically matches are immutable, but for demonstration)
    @staticmethod
    async def update_match(match_id: str, update_data: dict) -> Optional[dict]:
        """Update match data (admin use)"""
        collection = get_match_history_collection()
        update_data = {k: v for k, v in update_data.items() if v is not None}
        if update_data:
            await collection.update_one(
                {"_id": ObjectId(match_id)},
                {"$set": update_data}
            )
        return await MatchHistoryCRUD.get_match(match_id)
    
    # DELETE
    @staticmethod
    async def delete_match(match_id: str) -> bool:
        """Delete a match record"""
        collection = get_match_history_collection()
        result = await collection.delete_one({"_id": ObjectId(match_id)})
        return result.deleted_count > 0


# ==================== LEADERBOARDS CRUD ====================
class LeaderboardsCRUD:
    
    # CREATE
    @staticmethod
    async def create_leaderboard(leaderboard_data: dict) -> dict:
        """Create a new leaderboard"""
        collection = get_leaderboards_collection()
        leaderboard_data["entries"] = []
        leaderboard_data["last_updated"] = datetime.utcnow()
        result = await collection.insert_one(leaderboard_data)
        leaderboard_data["_id"] = str(result.inserted_id)
        return leaderboard_data
    
    # READ
    @staticmethod
    async def get_leaderboard(leaderboard_id: str) -> Optional[dict]:
        """Get a leaderboard by ID"""
        collection = get_leaderboards_collection()
        leaderboard = await collection.find_one({"_id": ObjectId(leaderboard_id)})
        return serialize_doc(leaderboard)
    
    @staticmethod
    async def get_game_leaderboard(game_id: str, leaderboard_type: str, timeframe: str = "all_time") -> Optional[dict]:
        """Get a specific leaderboard for a game"""
        collection = get_leaderboards_collection()
        leaderboard = await collection.find_one({
            "game_id": game_id,
            "leaderboard_type": leaderboard_type,
            "timeframe": timeframe
        })
        return serialize_doc(leaderboard)
    
    # UPDATE
    @staticmethod
    async def update_leaderboard_entries(leaderboard_id: str, entries: List[dict]) -> Optional[dict]:
        """Update leaderboard entries"""
        collection = get_leaderboards_collection()
        # Sort and rank entries
        sorted_entries = sorted(entries, key=lambda x: x["score"], reverse=True)
        for i, entry in enumerate(sorted_entries):
            entry["rank"] = i + 1
        
        await collection.update_one(
            {"_id": ObjectId(leaderboard_id)},
            {
                "$set": {
                    "entries": sorted_entries,
                    "last_updated": datetime.utcnow()
                }
            }
        )
        return await LeaderboardsCRUD.get_leaderboard(leaderboard_id)
    
    @staticmethod
    async def add_or_update_entry(leaderboard_id: str, player_id: str, username: str, score: int) -> Optional[dict]:
        """Add or update a single player's entry in the leaderboard"""
        leaderboard = await LeaderboardsCRUD.get_leaderboard(leaderboard_id)
        if not leaderboard:
            return None
        
        entries = leaderboard.get("entries", [])
        
        # Find existing entry or add new
        found = False
        for entry in entries:
            if entry["player_id"] == player_id:
                entry["score"] = score
                entry["username"] = username
                found = True
                break
        
        if not found:
            entries.append({
                "player_id": player_id,
                "username": username,
                "score": score,
                "rank": 0
            })
        
        return await LeaderboardsCRUD.update_leaderboard_entries(leaderboard_id, entries)
    
    # DELETE
    @staticmethod
    async def delete_leaderboard(leaderboard_id: str) -> bool:
        """Delete a leaderboard"""
        collection = get_leaderboards_collection()
        result = await collection.delete_one({"_id": ObjectId(leaderboard_id)})
        return result.deleted_count > 0


# ==================== ACHIEVEMENTS CRUD ====================
class AchievementsCRUD:
    
    # CREATE
    @staticmethod
    async def create_achievement(achievement_data: dict) -> dict:
        """Create a new achievement"""
        collection = get_achievements_collection()
        achievement_data["created_at"] = datetime.utcnow()
        result = await collection.insert_one(achievement_data)
        achievement_data["_id"] = str(result.inserted_id)
        return achievement_data
    
    # READ
    @staticmethod
    async def get_achievement(achievement_id: str) -> Optional[dict]:
        """Get an achievement by ID"""
        collection = get_achievements_collection()
        achievement = await collection.find_one({"_id": ObjectId(achievement_id)})
        return serialize_doc(achievement)
    
    @staticmethod
    async def get_game_achievements(game_id: str) -> List[dict]:
        """Get all achievements for a game"""
        collection = get_achievements_collection()
        cursor = collection.find({"game_id": game_id})
        achievements = await cursor.to_list(length=500)
        return serialize_docs(achievements)
    
    # UPDATE
    @staticmethod
    async def update_achievement(achievement_id: str, update_data: dict) -> Optional[dict]:
        """Update an achievement"""
        collection = get_achievements_collection()
        update_data = {k: v for k, v in update_data.items() if v is not None}
        if update_data:
            await collection.update_one(
                {"_id": ObjectId(achievement_id)},
                {"$set": update_data}
            )
        return await AchievementsCRUD.get_achievement(achievement_id)
    
    # DELETE
    @staticmethod
    async def delete_achievement(achievement_id: str) -> bool:
        """Delete an achievement"""
        collection = get_achievements_collection()
        result = await collection.delete_one({"_id": ObjectId(achievement_id)})
        return result.deleted_count > 0


# ==================== PLAYER ACHIEVEMENTS CRUD ====================
class PlayerAchievementsCRUD:
    
    # CREATE
    @staticmethod
    async def start_achievement(player_id: str, achievement_id: str) -> dict:
        """Start tracking an achievement for a player"""
        collection = get_player_achievements_collection()
        achievement_data = {
            "player_id": player_id,
            "achievement_id": achievement_id,
            "progress": {},
            "completed": False,
            "unlocked_at": None,
            "started_at": datetime.utcnow()
        }
        result = await collection.insert_one(achievement_data)
        achievement_data["_id"] = str(result.inserted_id)
        return achievement_data
    
    # READ
    @staticmethod
    async def get_player_achievement(player_id: str, achievement_id: str) -> Optional[dict]:
        """Get a player's progress on an achievement"""
        collection = get_player_achievements_collection()
        pa = await collection.find_one({
            "player_id": player_id,
            "achievement_id": achievement_id
        })
        return serialize_doc(pa)
    
    @staticmethod
    async def get_player_achievements(player_id: str, completed_only: bool = False) -> List[dict]:
        """Get all achievements for a player"""
        collection = get_player_achievements_collection()
        query = {"player_id": player_id}
        if completed_only:
            query["completed"] = True
        cursor = collection.find(query)
        achievements = await cursor.to_list(length=500)
        return serialize_docs(achievements)
    
    # UPDATE
    @staticmethod
    async def update_progress(player_id: str, achievement_id: str, progress: dict) -> Optional[dict]:
        """Update achievement progress"""
        collection = get_player_achievements_collection()
        await collection.update_one(
            {"player_id": player_id, "achievement_id": achievement_id},
            {"$set": {"progress": progress}}
        )
        return await PlayerAchievementsCRUD.get_player_achievement(player_id, achievement_id)
    
    @staticmethod
    async def complete_achievement(player_id: str, achievement_id: str) -> Optional[dict]:
        """Mark an achievement as completed"""
        collection = get_player_achievements_collection()
        await collection.update_one(
            {"player_id": player_id, "achievement_id": achievement_id},
            {"$set": {"completed": True, "unlocked_at": datetime.utcnow()}}
        )
        return await PlayerAchievementsCRUD.get_player_achievement(player_id, achievement_id)
    
    # DELETE
    @staticmethod
    async def delete_player_achievement(player_id: str, achievement_id: str) -> bool:
        """Delete a player's achievement progress"""
        collection = get_player_achievements_collection()
        result = await collection.delete_one({
            "player_id": player_id,
            "achievement_id": achievement_id
        })
        return result.deleted_count > 0


# ==================== GAME SESSIONS CRUD ====================
class GameSessionsCRUD:
    
    # CREATE
    @staticmethod
    async def create_session(session_data: dict) -> dict:
        """Start a new game session"""
        collection = get_game_sessions_collection()
        session_data["start_time"] = datetime.utcnow()
        session_data["end_time"] = None
        session_data["duration"] = None
        result = await collection.insert_one(session_data)
        session_data["_id"] = str(result.inserted_id)
        return session_data
    
    # READ
    @staticmethod
    async def get_session(session_id: str) -> Optional[dict]:
        """Get a session by ID"""
        collection = get_game_sessions_collection()
        session = await collection.find_one({"_id": ObjectId(session_id)})
        return serialize_doc(session)
    
    @staticmethod
    async def get_active_sessions(player_id: str) -> List[dict]:
        """Get active (ongoing) sessions for a player"""
        collection = get_game_sessions_collection()
        cursor = collection.find({
            "player_id": player_id,
            "end_time": None
        })
        sessions = await cursor.to_list(length=10)
        return serialize_docs(sessions)
    
    # UPDATE
    @staticmethod
    async def end_session(session_id: str) -> Optional[dict]:
        """End a game session"""
        collection = get_game_sessions_collection()
        session = await GameSessionsCRUD.get_session(session_id)
        if session and session.get("start_time"):
            end_time = datetime.utcnow()
            start_time = session["start_time"]
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            duration = int((end_time - start_time).total_seconds() / 60)
            
            await collection.update_one(
                {"_id": ObjectId(session_id)},
                {"$set": {"end_time": end_time, "duration": duration}}
            )
        return await GameSessionsCRUD.get_session(session_id)
    
    # DELETE
    @staticmethod
    async def delete_session(session_id: str) -> bool:
        """Delete a session (e.g., abandoned sessions)"""
        collection = get_game_sessions_collection()
        result = await collection.delete_one({"_id": ObjectId(session_id)})
        return result.deleted_count > 0


# ==================== NOTIFICATIONS CRUD ====================
class NotificationsCRUD:
    
    # CREATE
    @staticmethod
    async def create_notification(notification_data: dict) -> dict:
        """Create a new notification"""
        collection = get_notifications_collection()
        notification_data["read"] = False
        notification_data["created_at"] = datetime.utcnow()
        result = await collection.insert_one(notification_data)
        notification_data["_id"] = str(result.inserted_id)
        return notification_data
    
    # READ
    @staticmethod
    async def get_notification(notification_id: str) -> Optional[dict]:
        """Get a notification by ID"""
        collection = get_notifications_collection()
        notification = await collection.find_one({"_id": ObjectId(notification_id)})
        return serialize_doc(notification)
    
    @staticmethod
    async def get_player_notifications(player_id: str, unread_only: bool = False, limit: int = 50) -> List[dict]:
        """Get notifications for a player"""
        collection = get_notifications_collection()
        query = {"player_id": player_id}
        if unread_only:
            query["read"] = False
        cursor = collection.find(query).sort("created_at", -1).limit(limit)
        notifications = await cursor.to_list(length=limit)
        return serialize_docs(notifications)
    
    # UPDATE
    @staticmethod
    async def mark_as_read(notification_id: str) -> Optional[dict]:
        """Mark a notification as read"""
        collection = get_notifications_collection()
        await collection.update_one(
            {"_id": ObjectId(notification_id)},
            {"$set": {"read": True}}
        )
        return await NotificationsCRUD.get_notification(notification_id)
    
    @staticmethod
    async def mark_all_as_read(player_id: str) -> int:
        """Mark all notifications as read for a player"""
        collection = get_notifications_collection()
        result = await collection.update_many(
            {"player_id": player_id, "read": False},
            {"$set": {"read": True}}
        )
        return result.modified_count
    
    # DELETE
    @staticmethod
    async def delete_notification(notification_id: str) -> bool:
        """Delete a notification"""
        collection = get_notifications_collection()
        result = await collection.delete_one({"_id": ObjectId(notification_id)})
        return result.deleted_count > 0
    
    @staticmethod
    async def delete_old_notifications(player_id: str, days_old: int = 30) -> int:
        """Delete notifications older than specified days"""
        collection = get_notifications_collection()
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=days_old)
        result = await collection.delete_many({
            "player_id": player_id,
            "created_at": {"$lt": cutoff},
            "read": True
        })
        return result.deleted_count


# ==================== PLAYER INVENTORY CRUD ====================
class PlayerInventoryCRUD:
    
    # CREATE
    @staticmethod
    async def create_inventory(player_id: str, game_id: str) -> dict:
        """Create inventory for a player in a game"""
        collection = get_player_inventory_collection()
        inventory_data = {
            "player_id": player_id,
            "game_id": game_id,
            "items": [],
            "currency": 0,
            "last_updated": datetime.utcnow()
        }
        result = await collection.insert_one(inventory_data)
        inventory_data["_id"] = str(result.inserted_id)
        return inventory_data
    
    # READ
    @staticmethod
    async def get_inventory(player_id: str, game_id: str) -> Optional[dict]:
        """Get player's inventory for a game"""
        collection = get_player_inventory_collection()
        inventory = await collection.find_one({
            "player_id": player_id,
            "game_id": game_id
        })
        return serialize_doc(inventory)
    
    # UPDATE
    @staticmethod
    async def add_item(player_id: str, game_id: str, item: dict) -> Optional[dict]:
        """Add an item to inventory"""
        collection = get_player_inventory_collection()
        item["acquired_at"] = datetime.utcnow()
        await collection.update_one(
            {"player_id": player_id, "game_id": game_id},
            {
                "$push": {"items": item},
                "$set": {"last_updated": datetime.utcnow()}
            }
        )
        return await PlayerInventoryCRUD.get_inventory(player_id, game_id)
    
    @staticmethod
    async def update_currency(player_id: str, game_id: str, amount: int) -> Optional[dict]:
        """Update player's currency (add or subtract)"""
        collection = get_player_inventory_collection()
        await collection.update_one(
            {"player_id": player_id, "game_id": game_id},
            {
                "$inc": {"currency": amount},
                "$set": {"last_updated": datetime.utcnow()}
            }
        )
        return await PlayerInventoryCRUD.get_inventory(player_id, game_id)
    
    @staticmethod
    async def remove_item(player_id: str, game_id: str, item_id: str) -> Optional[dict]:
        """Remove an item from inventory"""
        collection = get_player_inventory_collection()
        await collection.update_one(
            {"player_id": player_id, "game_id": game_id},
            {
                "$pull": {"items": {"item_id": item_id}},
                "$set": {"last_updated": datetime.utcnow()}
            }
        )
        return await PlayerInventoryCRUD.get_inventory(player_id, game_id)
    
    # DELETE
    @staticmethod
    async def delete_inventory(player_id: str, game_id: str) -> bool:
        """Delete player's inventory for a game"""
        collection = get_player_inventory_collection()
        result = await collection.delete_one({
            "player_id": player_id,
            "game_id": game_id
        })
        return result.deleted_count > 0
