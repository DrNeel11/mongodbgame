"""
Neo4j API Routes - Friends, Messaging, Parties, Clans, Social Features
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from app.models.neo4j_models import (
    PlayerNodeCreate, PlayerNodeUpdate, PlayerNodeResponse,
    FriendRequestCreate, FriendRequestResponse, FriendshipCreate, FriendResponse,
    BlockCreate, BlockResponse,
    ConversationCreate, ConversationResponse, MessageCreate, MessageUpdate, MessageResponse,
    PartyCreate, PartyUpdate, PartyInviteCreate, PartyResponse,
    ClanCreate, ClanUpdate, ClanResponse, ClanMembershipUpdate,
    FollowCreate, FollowResponse,
)
from app.crud.neo4j_crud import (
    PlayerNodesCRUD, FriendshipsCRUD, BlockingCRUD, 
    MessagingCRUD, PartyCRUD, ClanCRUD, FollowCRUD,
)
from app.database.neo4j_db import is_neo4j_connected


def require_neo4j():
    """Dependency to check if Neo4j is connected"""
    if not is_neo4j_connected():
        raise HTTPException(
            status_code=503,
            detail="Neo4j is not connected. Social features are unavailable. Please start Neo4j and restart the server."
        )
    return True


# ==================== PLAYER NODES ROUTER ====================
player_nodes_router = APIRouter(prefix="/player-nodes", tags=["Player Nodes (Neo4j)"], dependencies=[Depends(require_neo4j)])


@player_nodes_router.post("/", response_model=dict, status_code=201)
async def create_player_node(player: PlayerNodeCreate):
    """CREATE: Create a player node in the graph"""
    result = await PlayerNodesCRUD.create_player_node(
        player.player_id, 
        player.username, 
        player.status.value
    )
    if not result:
        raise HTTPException(status_code=400, detail="Failed to create player node")
    return result


@player_nodes_router.get("/{player_id}", response_model=dict)
async def get_player_node(player_id: str):
    """READ: Get a player node"""
    player = await PlayerNodesCRUD.get_player_node(player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@player_nodes_router.patch("/{player_id}/status", response_model=dict)
async def update_player_status(player_id: str, status: str):
    """UPDATE: Update player's online status"""
    result = await PlayerNodesCRUD.update_player_status(player_id, status)
    if not result:
        raise HTTPException(status_code=404, detail="Player not found")
    return result


@player_nodes_router.patch("/{player_id}/username", response_model=dict)
async def update_player_username(player_id: str, username: str):
    """UPDATE: Update player's username in graph"""
    result = await PlayerNodesCRUD.update_player_username(player_id, username)
    if not result:
        raise HTTPException(status_code=404, detail="Player not found")
    return result


@player_nodes_router.delete("/{player_id}")
async def delete_player_node(player_id: str):
    """DELETE: Delete a player node and all relationships"""
    deleted = await PlayerNodesCRUD.delete_player_node(player_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Player not found")
    return {"message": "Player node deleted successfully"}


# ==================== FRIENDS ROUTER ====================
friends_router = APIRouter(prefix="/friends", tags=["Friends (Neo4j)"], dependencies=[Depends(require_neo4j)])


@friends_router.post("/request", response_model=dict, status_code=201)
async def send_friend_request(request: FriendRequestCreate):
    """CREATE: Send a friend request"""
    result = await FriendshipsCRUD.send_friend_request(
        request.from_player_id, 
        request.to_player_id, 
        request.message or ""
    )
    if not result:
        raise HTTPException(status_code=400, detail="Failed to send friend request")
    return result


@friends_router.post("/accept", response_model=dict)
async def accept_friend_request(from_player_id: str, to_player_id: str):
    """CREATE: Accept a friend request (creates friendship)"""
    result = await FriendshipsCRUD.accept_friend_request(from_player_id, to_player_id)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to accept friend request")
    return result


@friends_router.get("/requests/{player_id}", response_model=List[dict])
async def get_pending_requests(player_id: str):
    """READ: Get pending friend requests"""
    return await FriendshipsCRUD.get_pending_requests(player_id)


@friends_router.get("/{player_id}", response_model=List[dict])
async def get_friends_list(player_id: str):
    """READ: Get all friends of a player"""
    return await FriendshipsCRUD.get_friends(player_id)


@friends_router.get("/mutual/{player1_id}/{player2_id}", response_model=List[dict])
async def get_mutual_friends(player1_id: str, player2_id: str):
    """READ: Get mutual friends between two players"""
    return await FriendshipsCRUD.get_mutual_friends(player1_id, player2_id)


@friends_router.get("/suggestions/{player_id}", response_model=List[dict])
async def get_friend_suggestions(player_id: str, limit: int = Query(default=10, le=50)):
    """READ: Get friend suggestions based on friends-of-friends"""
    return await FriendshipsCRUD.get_friend_suggestions(player_id, limit)


@friends_router.patch("/nickname", response_model=dict)
async def set_friend_nickname(player_id: str, friend_id: str, nickname: str):
    """UPDATE: Set a nickname for a friend"""
    result = await FriendshipsCRUD.set_friend_nickname(player_id, friend_id, nickname)
    if not result:
        raise HTTPException(status_code=404, detail="Friendship not found")
    return result


@friends_router.delete("/request")
async def decline_friend_request(from_player_id: str, to_player_id: str):
    """DELETE: Decline a friend request"""
    deleted = await FriendshipsCRUD.decline_friend_request(from_player_id, to_player_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Friend request not found")
    return {"message": "Friend request declined"}


@friends_router.delete("/")
async def remove_friend(player_id: str, friend_id: str):
    """DELETE: Remove a friend (unfriend)"""
    deleted = await FriendshipsCRUD.remove_friend(player_id, friend_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Friendship not found")
    return {"message": "Friend removed successfully"}


# ==================== BLOCKING ROUTER ====================
blocking_router = APIRouter(prefix="/block", tags=["Blocking (Neo4j)"], dependencies=[Depends(require_neo4j)])


@blocking_router.post("/", response_model=dict, status_code=201)
async def block_player(block: BlockCreate):
    """CREATE: Block a player"""
    result = await BlockingCRUD.block_player(
        block.blocker_id, 
        block.blocked_id, 
        block.reason
    )
    if not result:
        raise HTTPException(status_code=400, detail="Failed to block player")
    return result


@blocking_router.get("/{player_id}", response_model=List[dict])
async def get_blocked_players(player_id: str):
    """READ: Get list of blocked players"""
    return await BlockingCRUD.get_blocked_players(player_id)


@blocking_router.delete("/")
async def unblock_player(blocker_id: str, blocked_id: str):
    """DELETE: Unblock a player"""
    deleted = await BlockingCRUD.unblock_player(blocker_id, blocked_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Block not found")
    return {"message": "Player unblocked successfully"}


# ==================== MESSAGING ROUTER ====================
messaging_router = APIRouter(prefix="/messages", tags=["Messaging (Neo4j)"], dependencies=[Depends(require_neo4j)])


@messaging_router.post("/conversation", response_model=dict, status_code=201)
async def create_conversation(conversation: ConversationCreate):
    """CREATE: Create a new conversation"""
    result = await MessagingCRUD.create_conversation(
        conversation.conversation_type.value,
        conversation.participant_ids,
        conversation.name
    )
    if not result:
        raise HTTPException(status_code=400, detail="Failed to create conversation")
    return result


@messaging_router.post("/", response_model=dict, status_code=201)
async def send_message(message: MessageCreate):
    """CREATE: Send a message in a conversation"""
    result = await MessagingCRUD.send_message(
        message.conversation_id,
        message.sender_id,
        message.content
    )
    if not result:
        raise HTTPException(status_code=400, detail="Failed to send message")
    return result


@messaging_router.get("/conversation/{conversation_id}", response_model=dict)
async def get_conversation(conversation_id: str):
    """READ: Get a conversation with participants"""
    conversation = await MessagingCRUD.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@messaging_router.get("/player/{player_id}/conversations", response_model=List[dict])
async def get_player_conversations(player_id: str):
    """READ: Get all conversations for a player"""
    return await MessagingCRUD.get_player_conversations(player_id)


@messaging_router.get("/conversation/{conversation_id}/messages", response_model=List[dict])
async def get_messages(
    conversation_id: str, 
    limit: int = Query(default=50, le=100),
    offset: int = 0
):
    """READ: Get messages in a conversation"""
    return await MessagingCRUD.get_messages(conversation_id, limit, offset)


@messaging_router.put("/{message_id}", response_model=dict)
async def edit_message(message_id: str, update: MessageUpdate):
    """UPDATE: Edit a message"""
    result = await MessagingCRUD.edit_message(message_id, update.content)
    if not result:
        raise HTTPException(status_code=404, detail="Message not found")
    return result


@messaging_router.patch("/conversation/{conversation_id}/mute")
async def mute_conversation(conversation_id: str, player_id: str, muted: bool = True):
    """UPDATE: Mute or unmute a conversation"""
    success = await MessagingCRUD.mute_conversation(player_id, conversation_id, muted)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation membership not found")
    return {"message": f"Conversation {'muted' if muted else 'unmuted'} successfully"}


@messaging_router.delete("/{message_id}")
async def delete_message(message_id: str):
    """DELETE: Delete a message"""
    deleted = await MessagingCRUD.delete_message(message_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"message": "Message deleted successfully"}


@messaging_router.delete("/conversation/{conversation_id}/leave")
async def leave_conversation(conversation_id: str, player_id: str):
    """DELETE: Leave a conversation"""
    deleted = await MessagingCRUD.leave_conversation(player_id, conversation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation membership not found")
    return {"message": "Left conversation successfully"}


# ==================== PARTY ROUTER ====================
party_router = APIRouter(prefix="/parties", tags=["Parties (Neo4j)"], dependencies=[Depends(require_neo4j)])


@party_router.post("/", response_model=dict, status_code=201)
async def create_party(party: PartyCreate):
    """CREATE: Create a new party"""
    result = await PartyCRUD.create_party(
        party.leader_id,
        party.game_id,
        party.max_size,
        party.is_public
    )
    if not result:
        raise HTTPException(status_code=400, detail="Failed to create party")
    return result


@party_router.post("/{party_id}/invite", response_model=dict)
async def invite_to_party(party_id: str, invite: PartyInviteCreate):
    """CREATE: Invite a player to a party"""
    result = await PartyCRUD.invite_to_party(party_id, invite.inviter_id, invite.invitee_id)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to invite player")
    return result


@party_router.post("/{party_id}/join", response_model=dict)
async def join_party(party_id: str, player_id: str):
    """CREATE: Join a party"""
    result = await PartyCRUD.join_party(party_id, player_id)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to join party")
    return result


@party_router.get("/{party_id}", response_model=dict)
async def get_party(party_id: str):
    """READ: Get party details with members"""
    party = await PartyCRUD.get_party(party_id)
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")
    return party


@party_router.get("/player/{player_id}", response_model=dict)
async def get_player_party(player_id: str):
    """READ: Get the party a player is in"""
    party = await PartyCRUD.get_player_party(player_id)
    if not party:
        raise HTTPException(status_code=404, detail="Player not in a party")
    return party


@party_router.patch("/{party_id}", response_model=dict)
async def update_party(party_id: str, update: PartyUpdate):
    """UPDATE: Update party settings"""
    result = await PartyCRUD.update_party(
        party_id,
        update.max_size,
        update.is_public,
        update.game_id
    )
    if not result:
        raise HTTPException(status_code=404, detail="Party not found")
    return result


@party_router.delete("/{party_id}/leave")
async def leave_party(party_id: str, player_id: str):
    """DELETE: Leave a party"""
    deleted = await PartyCRUD.leave_party(party_id, player_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Party membership not found")
    return {"message": "Left party successfully"}


@party_router.delete("/{party_id}")
async def disband_party(party_id: str):
    """DELETE: Disband a party"""
    deleted = await PartyCRUD.disband_party(party_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Party not found")
    return {"message": "Party disbanded successfully"}


# ==================== CLAN ROUTER ====================
clan_router = APIRouter(prefix="/clans", tags=["Clans (Neo4j)"], dependencies=[Depends(require_neo4j)])


@clan_router.post("/", response_model=dict, status_code=201)
async def create_clan(clan: ClanCreate):
    """CREATE: Create a new clan"""
    result = await ClanCRUD.create_clan(
        clan.name,
        clan.tag,
        clan.owner_id,
        clan.description
    )
    if not result:
        raise HTTPException(status_code=400, detail="Failed to create clan")
    return result


@clan_router.post("/{clan_id}/join", response_model=dict)
async def join_clan(clan_id: str, player_id: str):
    """CREATE: Join a clan"""
    result = await ClanCRUD.join_clan(clan_id, player_id)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to join clan")
    return result


@clan_router.get("/{clan_id}", response_model=dict)
async def get_clan(clan_id: str):
    """READ: Get clan details with members"""
    clan = await ClanCRUD.get_clan(clan_id)
    if not clan:
        raise HTTPException(status_code=404, detail="Clan not found")
    return clan


@clan_router.get("/player/{player_id}", response_model=dict)
async def get_player_clan(player_id: str):
    """READ: Get the clan a player belongs to"""
    clan = await ClanCRUD.get_player_clan(player_id)
    if not clan:
        raise HTTPException(status_code=404, detail="Player not in a clan")
    return clan


@clan_router.get("/search/{search_term}", response_model=List[dict])
async def search_clans(search_term: str, limit: int = Query(default=20, le=50)):
    """READ: Search for clans by name or tag"""
    return await ClanCRUD.search_clans(search_term, limit)


@clan_router.patch("/{clan_id}", response_model=dict)
async def update_clan(clan_id: str, update: ClanUpdate):
    """UPDATE: Update clan details"""
    result = await ClanCRUD.update_clan(
        clan_id,
        update.name,
        update.tag,
        update.description
    )
    if not result:
        raise HTTPException(status_code=404, detail="Clan not found")
    return result


@clan_router.patch("/{clan_id}/member/{player_id}", response_model=dict)
async def update_member_role(clan_id: str, player_id: str, update: ClanMembershipUpdate):
    """UPDATE: Update a member's role in the clan"""
    result = await ClanCRUD.update_member_role(
        clan_id,
        player_id,
        update.role.value if update.role else None,
        update.rank
    )
    if not result:
        raise HTTPException(status_code=404, detail="Clan membership not found")
    return result


@clan_router.delete("/{clan_id}/leave")
async def leave_clan(clan_id: str, player_id: str):
    """DELETE: Leave a clan"""
    deleted = await ClanCRUD.leave_clan(clan_id, player_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Clan membership not found")
    return {"message": "Left clan successfully"}


@clan_router.delete("/{clan_id}")
async def disband_clan(clan_id: str):
    """DELETE: Disband a clan"""
    deleted = await ClanCRUD.disband_clan(clan_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Clan not found")
    return {"message": "Clan disbanded successfully"}


# ==================== FOLLOW ROUTER ====================
follow_router = APIRouter(prefix="/follow", tags=["Follow (Neo4j)"], dependencies=[Depends(require_neo4j)])


@follow_router.post("/", response_model=dict, status_code=201)
async def follow_player(follow: FollowCreate):
    """CREATE: Follow a player"""
    result = await FollowCRUD.follow_player(follow.follower_id, follow.following_id)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to follow player")
    return result


@follow_router.get("/following/{player_id}", response_model=List[dict])
async def get_following(player_id: str):
    """READ: Get players that this player follows"""
    return await FollowCRUD.get_following(player_id)


@follow_router.get("/followers/{player_id}", response_model=List[dict])
async def get_followers(player_id: str):
    """READ: Get players that follow this player"""
    return await FollowCRUD.get_followers(player_id)


@follow_router.delete("/")
async def unfollow_player(follower_id: str, following_id: str):
    """DELETE: Unfollow a player"""
    deleted = await FollowCRUD.unfollow_player(follower_id, following_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Follow relationship not found")
    return {"message": "Unfollowed successfully"}
