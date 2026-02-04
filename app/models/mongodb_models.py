from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class Platform(str, Enum):
    XBOX = "xbox"
    PLAYSTATION = "playstation"
    PC = "pc"
    NINTENDO = "nintendo"
    MOBILE = "mobile"


class PlayerSettings(BaseModel):
    notifications_enabled: bool = True
    crossplay_enabled: bool = True
    privacy_level: str = "friends"  # public, friends, private
    language: str = "en"
    region: str = "NA"


# ==================== PLAYER ====================
class PlayerCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    platforms: List[Platform] = []
    settings: Optional[PlayerSettings] = PlayerSettings()


class PlayerUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    platforms: Optional[List[Platform]] = None
    settings: Optional[PlayerSettings] = None


class PlayerResponse(BaseModel):
    player_id: str = Field(..., alias="_id")
    username: str
    email: str
    platforms: List[str]
    settings: PlayerSettings
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        populate_by_name = True


# ==================== GAME ====================
class GameCreate(BaseModel):
    title: str
    publisher: str
    platforms: List[Platform]
    crossplay_enabled: bool = True
    max_players: int = 100
    genres: List[str] = []


class GameUpdate(BaseModel):
    title: Optional[str] = None
    publisher: Optional[str] = None
    platforms: Optional[List[Platform]] = None
    crossplay_enabled: Optional[bool] = None
    max_players: Optional[int] = None
    genres: Optional[List[str]] = None


class GameResponse(BaseModel):
    game_id: str = Field(..., alias="_id")
    title: str
    publisher: str
    platforms: List[str]
    crossplay_enabled: bool
    max_players: int
    genres: List[str]
    release_date: datetime
    
    class Config:
        populate_by_name = True


# ==================== PLAYER STATS ====================
class PlayerStatsCreate(BaseModel):
    player_id: str
    game_id: str
    

class PlayerStatsUpdate(BaseModel):
    total_playtime: Optional[int] = None  # in minutes
    wins: Optional[int] = None
    losses: Optional[int] = None
    kills: Optional[int] = None
    deaths: Optional[int] = None
    xp: Optional[int] = None
    level: Optional[int] = None


class PlayerStatsResponse(BaseModel):
    stats_id: str = Field(..., alias="_id")
    player_id: str
    game_id: str
    total_playtime: int = 0
    wins: int = 0
    losses: int = 0
    kills: int = 0
    deaths: int = 0
    xp: int = 0
    level: int = 1
    kd_ratio: float = 0.0
    win_rate: float = 0.0
    last_updated: datetime
    
    class Config:
        populate_by_name = True


# ==================== MATCH HISTORY ====================
class MatchPlayerData(BaseModel):
    player_id: str
    team: Optional[str] = None
    score: int = 0
    kills: int = 0
    deaths: int = 0
    assists: int = 0


class MatchCreate(BaseModel):
    game_id: str
    players: List[MatchPlayerData]
    game_mode: str
    map_name: Optional[str] = None
    duration: int  # in seconds
    winner_team: Optional[str] = None
    winner_player_id: Optional[str] = None


class MatchResponse(BaseModel):
    match_id: str = Field(..., alias="_id")
    game_id: str
    players: List[MatchPlayerData]
    game_mode: str
    map_name: Optional[str]
    duration: int
    winner_team: Optional[str]
    winner_player_id: Optional[str]
    timestamp: datetime
    
    class Config:
        populate_by_name = True


# ==================== LEADERBOARD ====================
class LeaderboardEntry(BaseModel):
    player_id: str
    username: str
    score: int
    rank: int


class LeaderboardCreate(BaseModel):
    game_id: str
    leaderboard_type: str  # kills, wins, xp, etc.
    timeframe: str = "all_time"  # daily, weekly, monthly, all_time


class LeaderboardResponse(BaseModel):
    leaderboard_id: str = Field(..., alias="_id")
    game_id: str
    leaderboard_type: str
    timeframe: str
    entries: List[LeaderboardEntry] = []
    last_updated: datetime
    
    class Config:
        populate_by_name = True


# ==================== ACHIEVEMENTS ====================
class AchievementCreate(BaseModel):
    game_id: str
    name: str
    description: str
    xp_reward: int = 0
    rarity: str = "common"  # common, rare, epic, legendary
    icon_url: Optional[str] = None
    criteria: dict = {}  # e.g., {"kills": 100} or {"wins": 10}


class AchievementUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    xp_reward: Optional[int] = None
    rarity: Optional[str] = None
    icon_url: Optional[str] = None
    criteria: Optional[dict] = None


class AchievementResponse(BaseModel):
    achievement_id: str = Field(..., alias="_id")
    game_id: str
    name: str
    description: str
    xp_reward: int
    rarity: str
    icon_url: Optional[str]
    criteria: dict
    created_at: datetime
    
    class Config:
        populate_by_name = True


# ==================== PLAYER ACHIEVEMENTS ====================
class PlayerAchievementCreate(BaseModel):
    player_id: str
    achievement_id: str


class PlayerAchievementUpdate(BaseModel):
    progress: Optional[dict] = None
    completed: Optional[bool] = None


class PlayerAchievementResponse(BaseModel):
    id: str = Field(..., alias="_id")
    player_id: str
    achievement_id: str
    progress: dict = {}
    completed: bool = False
    unlocked_at: Optional[datetime] = None
    started_at: datetime
    
    class Config:
        populate_by_name = True


# ==================== GAME SESSION ====================
class GameSessionCreate(BaseModel):
    player_id: str
    game_id: str
    platform: Platform
    server_region: str = "NA"


class GameSessionEnd(BaseModel):
    session_id: str


class GameSessionResponse(BaseModel):
    session_id: str = Field(..., alias="_id")
    player_id: str
    game_id: str
    platform: str
    server_region: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[int] = None  # in minutes
    
    class Config:
        populate_by_name = True


# ==================== NOTIFICATIONS ====================
class NotificationType(str, Enum):
    FRIEND_REQUEST = "friend_request"
    ACHIEVEMENT = "achievement"
    PARTY_INVITE = "party_invite"
    SYSTEM = "system"
    GAME_INVITE = "game_invite"


class NotificationCreate(BaseModel):
    player_id: str
    notification_type: NotificationType
    title: str
    message: str
    data: Optional[dict] = {}


class NotificationResponse(BaseModel):
    notification_id: str = Field(..., alias="_id")
    player_id: str
    notification_type: str
    title: str
    message: str
    data: dict
    read: bool = False
    created_at: datetime
    
    class Config:
        populate_by_name = True


# ==================== PLAYER INVENTORY ====================
class InventoryItem(BaseModel):
    item_id: str
    item_name: str
    item_type: str  # skin, weapon, emote, etc.
    quantity: int = 1
    acquired_at: datetime


class PlayerInventoryCreate(BaseModel):
    player_id: str
    game_id: str


class PlayerInventoryUpdate(BaseModel):
    items: Optional[List[InventoryItem]] = None
    currency: Optional[int] = None


class PlayerInventoryResponse(BaseModel):
    inventory_id: str = Field(..., alias="_id")
    player_id: str
    game_id: str
    items: List[InventoryItem] = []
    currency: int = 0
    last_updated: datetime
    
    class Config:
        populate_by_name = True
