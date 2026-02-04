from motor.motor_asyncio import AsyncIOMotorClient
from app.config import get_settings

settings = get_settings()


class MongoDB:
    client: AsyncIOMotorClient = None
    database = None


mongodb = MongoDB()


async def connect_mongodb():
    """Connect to MongoDB"""
    mongodb.client = AsyncIOMotorClient(settings.mongodb_url)
    mongodb.database = mongodb.client[settings.mongodb_database]
    print(f"Connected to MongoDB: {settings.mongodb_database}")


async def close_mongodb():
    """Close MongoDB connection"""
    if mongodb.client:
        mongodb.client.close()
        print("MongoDB connection closed")


def get_database():
    """Get database instance"""
    return mongodb.database


# Collection getters
def get_players_collection():
    return mongodb.database["players"]


def get_games_collection():
    return mongodb.database["games"]


def get_player_stats_collection():
    return mongodb.database["player_stats"]


def get_match_history_collection():
    return mongodb.database["match_history"]


def get_leaderboards_collection():
    return mongodb.database["leaderboards"]


def get_achievements_collection():
    return mongodb.database["achievements"]


def get_player_achievements_collection():
    return mongodb.database["player_achievements"]


def get_game_sessions_collection():
    return mongodb.database["game_sessions"]


def get_notifications_collection():
    return mongodb.database["notifications"]


def get_player_inventory_collection():
    return mongodb.database["player_inventory"]
