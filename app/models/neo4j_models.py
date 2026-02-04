from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class PlayerStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    AWAY = "away"
    IN_GAME = "in_game"
    DO_NOT_DISTURB = "dnd"


class ConversationType(str, Enum):
    DIRECT = "direct"
    GROUP = "group"


class PartyRole(str, Enum):
    LEADER = "leader"
    MEMBER = "member"


class ClanRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MODERATOR = "moderator"
    MEMBER = "member"


# ==================== PLAYER NODE ====================
class PlayerNodeCreate(BaseModel):
    player_id: str
    username: str
    status: PlayerStatus = PlayerStatus.OFFLINE


class PlayerNodeUpdate(BaseModel):
    username: Optional[str] = None
    status: Optional[PlayerStatus] = None


class PlayerNodeResponse(BaseModel):
    player_id: str
    username: str
    status: str


# ==================== FRIEND RELATIONSHIPS ====================
class FriendRequestCreate(BaseModel):
    from_player_id: str
    to_player_id: str
    message: Optional[str] = ""


class FriendRequestResponse(BaseModel):
    from_player_id: str
    from_username: str
    to_player_id: str
    to_username: str
    message: str
    sent_at: datetime


class FriendshipCreate(BaseModel):
    player1_id: str
    player2_id: str
    nickname: Optional[str] = None


class FriendResponse(BaseModel):
    player_id: str
    username: str
    status: str
    friends_since: datetime
    nickname: Optional[str] = None


class BlockCreate(BaseModel):
    blocker_id: str
    blocked_id: str
    reason: Optional[str] = None


class BlockResponse(BaseModel):
    blocked_player_id: str
    blocked_username: str
    blocked_since: datetime
    reason: Optional[str]


# ==================== MESSAGING ====================
class ConversationCreate(BaseModel):
    conversation_type: ConversationType
    participant_ids: List[str]
    name: Optional[str] = None  # For group conversations


class ConversationResponse(BaseModel):
    conversation_id: str
    conversation_type: str
    name: Optional[str]
    participants: List[PlayerNodeResponse]
    created_at: datetime
    last_message_at: Optional[datetime] = None


class MessageCreate(BaseModel):
    conversation_id: str
    sender_id: str
    content: str


class MessageUpdate(BaseModel):
    content: str


class MessageResponse(BaseModel):
    message_id: str
    conversation_id: str
    sender_id: str
    sender_username: str
    content: str
    timestamp: datetime
    edited: bool = False
    edited_at: Optional[datetime] = None


# ==================== PARTY/LOBBY ====================
class PartyCreate(BaseModel):
    leader_id: str
    game_id: str
    max_size: int = 4
    is_public: bool = False


class PartyUpdate(BaseModel):
    max_size: Optional[int] = None
    is_public: Optional[bool] = None
    game_id: Optional[str] = None


class PartyInviteCreate(BaseModel):
    party_id: str
    inviter_id: str
    invitee_id: str


class PartyMemberResponse(BaseModel):
    player_id: str
    username: str
    role: str
    joined_at: datetime


class PartyResponse(BaseModel):
    party_id: str
    game_id: str
    max_size: int
    is_public: bool
    created_at: datetime
    members: List[PartyMemberResponse] = []


# ==================== CLAN/GUILD ====================
class ClanCreate(BaseModel):
    name: str
    tag: str = Field(..., min_length=2, max_length=6)
    owner_id: str
    description: Optional[str] = None


class ClanUpdate(BaseModel):
    name: Optional[str] = None
    tag: Optional[str] = None
    description: Optional[str] = None


class ClanMemberResponse(BaseModel):
    player_id: str
    username: str
    role: str
    rank: int
    joined_at: datetime


class ClanResponse(BaseModel):
    clan_id: str
    name: str
    tag: str
    description: Optional[str]
    created_at: datetime
    member_count: int = 0
    members: List[ClanMemberResponse] = []


class ClanMembershipUpdate(BaseModel):
    role: Optional[ClanRole] = None
    rank: Optional[int] = None


# ==================== FOLLOW ====================
class FollowCreate(BaseModel):
    follower_id: str
    following_id: str


class FollowResponse(BaseModel):
    player_id: str
    username: str
    following_since: datetime
