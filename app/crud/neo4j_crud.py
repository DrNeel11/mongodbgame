"""
Neo4j CRUD Operations for the Multiplayer Gaming System
Demonstrates: Create, Read, Update, Delete operations for graph data
"""

from datetime import datetime
from typing import List, Optional
import uuid
from app.database.neo4j_db import get_neo4j_driver


def generate_id():
    """Generate a unique ID"""
    return str(uuid.uuid4())


# ==================== PLAYER NODES CRUD ====================
class PlayerNodesCRUD:
    
    # CREATE
    @staticmethod
    async def create_player_node(player_id: str, username: str, status: str = "offline") -> dict:
        """Create a player node in the graph"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            CREATE (p:Player {
                player_id: $player_id,
                username: $username,
                status: $status,
                created_at: datetime()
            })
            RETURN p.player_id as player_id, p.username as username, p.status as status
            """
            result = await session.run(query, player_id=player_id, username=username, status=status)
            record = await result.single()
            return dict(record) if record else None
    
    # READ
    @staticmethod
    async def get_player_node(player_id: str) -> Optional[dict]:
        """Get a player node"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (p:Player {player_id: $player_id})
            RETURN p.player_id as player_id, p.username as username, p.status as status
            """
            result = await session.run(query, player_id=player_id)
            record = await result.single()
            return dict(record) if record else None
    
    # UPDATE
    @staticmethod
    async def update_player_status(player_id: str, status: str) -> Optional[dict]:
        """Update player's online status"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (p:Player {player_id: $player_id})
            SET p.status = $status
            RETURN p.player_id as player_id, p.username as username, p.status as status
            """
            result = await session.run(query, player_id=player_id, status=status)
            record = await result.single()
            return dict(record) if record else None
    
    @staticmethod
    async def update_player_username(player_id: str, username: str) -> Optional[dict]:
        """Update player's username in graph"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (p:Player {player_id: $player_id})
            SET p.username = $username
            RETURN p.player_id as player_id, p.username as username, p.status as status
            """
            result = await session.run(query, player_id=player_id, username=username)
            record = await result.single()
            return dict(record) if record else None
    
    # DELETE
    @staticmethod
    async def delete_player_node(player_id: str) -> bool:
        """Delete a player node and all its relationships"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (p:Player {player_id: $player_id})
            DETACH DELETE p
            RETURN count(p) as deleted
            """
            result = await session.run(query, player_id=player_id)
            record = await result.single()
            return record["deleted"] > 0 if record else False


# ==================== FRIENDSHIPS CRUD ====================
class FriendshipsCRUD:
    
    # CREATE - Send friend request
    @staticmethod
    async def send_friend_request(from_player_id: str, to_player_id: str, message: str = "") -> dict:
        """Send a friend request"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (from:Player {player_id: $from_id})
            MATCH (to:Player {player_id: $to_id})
            CREATE (from)-[r:SENT_REQUEST {
                sent_at: datetime(),
                message: $message
            }]->(to)
            RETURN from.player_id as from_player_id, from.username as from_username,
                   to.player_id as to_player_id, to.username as to_username,
                   r.message as message, r.sent_at as sent_at
            """
            result = await session.run(query, from_id=from_player_id, to_id=to_player_id, message=message)
            record = await result.single()
            return dict(record) if record else None
    
    # CREATE - Accept friend request (creates FRIENDS_WITH relationship)
    @staticmethod
    async def accept_friend_request(from_player_id: str, to_player_id: str) -> dict:
        """Accept a friend request and create friendship"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (from:Player {player_id: $from_id})-[r:SENT_REQUEST]->(to:Player {player_id: $to_id})
            DELETE r
            CREATE (from)-[f:FRIENDS_WITH {since: datetime()}]->(to)
            CREATE (to)-[f2:FRIENDS_WITH {since: datetime()}]->(from)
            RETURN from.player_id as player1_id, to.player_id as player2_id, f.since as since
            """
            result = await session.run(query, from_id=from_player_id, to_id=to_player_id)
            record = await result.single()
            return dict(record) if record else None
    
    # READ - Get pending friend requests
    @staticmethod
    async def get_pending_requests(player_id: str) -> List[dict]:
        """Get pending friend requests for a player"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (from:Player)-[r:SENT_REQUEST]->(to:Player {player_id: $player_id})
            RETURN from.player_id as from_player_id, from.username as from_username,
                   to.player_id as to_player_id, to.username as to_username,
                   r.message as message, r.sent_at as sent_at
            """
            result = await session.run(query, player_id=player_id)
            records = await result.data()
            return records
    
    # READ - Get friends list
    @staticmethod
    async def get_friends(player_id: str) -> List[dict]:
        """Get all friends of a player"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (p:Player {player_id: $player_id})-[f:FRIENDS_WITH]->(friend:Player)
            RETURN friend.player_id as player_id, friend.username as username,
                   friend.status as status, f.since as friends_since, f.nickname as nickname
            """
            result = await session.run(query, player_id=player_id)
            records = await result.data()
            return records
    
    # READ - Get mutual friends
    @staticmethod
    async def get_mutual_friends(player1_id: str, player2_id: str) -> List[dict]:
        """Get mutual friends between two players"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (p1:Player {player_id: $player1_id})-[:FRIENDS_WITH]->(mutual:Player)<-[:FRIENDS_WITH]-(p2:Player {player_id: $player2_id})
            RETURN mutual.player_id as player_id, mutual.username as username, mutual.status as status
            """
            result = await session.run(query, player1_id=player1_id, player2_id=player2_id)
            records = await result.data()
            return records
    
    # READ - Get friends of friends (for suggestions)
    @staticmethod
    async def get_friend_suggestions(player_id: str, limit: int = 10) -> List[dict]:
        """Get friend suggestions based on friends of friends"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (p:Player {player_id: $player_id})-[:FRIENDS_WITH]->(friend:Player)-[:FRIENDS_WITH]->(suggestion:Player)
            WHERE NOT (p)-[:FRIENDS_WITH]->(suggestion) 
              AND NOT (p)-[:BLOCKED]->(suggestion)
              AND suggestion.player_id <> $player_id
            RETURN suggestion.player_id as player_id, suggestion.username as username, 
                   suggestion.status as status, count(friend) as mutual_friends
            ORDER BY mutual_friends DESC
            LIMIT $limit
            """
            result = await session.run(query, player_id=player_id, limit=limit)
            records = await result.data()
            return records
    
    # UPDATE - Set nickname for friend
    @staticmethod
    async def set_friend_nickname(player_id: str, friend_id: str, nickname: str) -> Optional[dict]:
        """Set a nickname for a friend"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (p:Player {player_id: $player_id})-[f:FRIENDS_WITH]->(friend:Player {player_id: $friend_id})
            SET f.nickname = $nickname
            RETURN friend.player_id as player_id, friend.username as username, f.nickname as nickname
            """
            result = await session.run(query, player_id=player_id, friend_id=friend_id, nickname=nickname)
            record = await result.single()
            return dict(record) if record else None
    
    # DELETE - Decline friend request
    @staticmethod
    async def decline_friend_request(from_player_id: str, to_player_id: str) -> bool:
        """Decline a friend request"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (from:Player {player_id: $from_id})-[r:SENT_REQUEST]->(to:Player {player_id: $to_id})
            DELETE r
            RETURN count(r) as deleted
            """
            result = await session.run(query, from_id=from_player_id, to_id=to_player_id)
            record = await result.single()
            return record["deleted"] > 0 if record else False
    
    # DELETE - Remove friend
    @staticmethod
    async def remove_friend(player_id: str, friend_id: str) -> bool:
        """Remove a friend (unfriend)"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (p:Player {player_id: $player_id})-[f:FRIENDS_WITH]-(friend:Player {player_id: $friend_id})
            DELETE f
            RETURN count(f) as deleted
            """
            result = await session.run(query, player_id=player_id, friend_id=friend_id)
            record = await result.single()
            return record["deleted"] > 0 if record else False


# ==================== BLOCKING CRUD ====================
class BlockingCRUD:
    
    # CREATE
    @staticmethod
    async def block_player(blocker_id: str, blocked_id: str, reason: str = None) -> dict:
        """Block a player"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            # Also remove any friendship
            query = """
            MATCH (blocker:Player {player_id: $blocker_id})
            MATCH (blocked:Player {player_id: $blocked_id})
            OPTIONAL MATCH (blocker)-[f:FRIENDS_WITH]-(blocked)
            DELETE f
            CREATE (blocker)-[b:BLOCKED {since: datetime(), reason: $reason}]->(blocked)
            RETURN blocked.player_id as blocked_player_id, blocked.username as blocked_username,
                   b.since as blocked_since, b.reason as reason
            """
            result = await session.run(query, blocker_id=blocker_id, blocked_id=blocked_id, reason=reason)
            record = await result.single()
            return dict(record) if record else None
    
    # READ
    @staticmethod
    async def get_blocked_players(player_id: str) -> List[dict]:
        """Get list of blocked players"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (p:Player {player_id: $player_id})-[b:BLOCKED]->(blocked:Player)
            RETURN blocked.player_id as blocked_player_id, blocked.username as blocked_username,
                   b.since as blocked_since, b.reason as reason
            """
            result = await session.run(query, player_id=player_id)
            records = await result.data()
            return records
    
    # DELETE
    @staticmethod
    async def unblock_player(blocker_id: str, blocked_id: str) -> bool:
        """Unblock a player"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (blocker:Player {player_id: $blocker_id})-[b:BLOCKED]->(blocked:Player {player_id: $blocked_id})
            DELETE b
            RETURN count(b) as deleted
            """
            result = await session.run(query, blocker_id=blocker_id, blocked_id=blocked_id)
            record = await result.single()
            return record["deleted"] > 0 if record else False


# ==================== MESSAGING CRUD ====================
class MessagingCRUD:
    
    # CREATE - Conversation
    @staticmethod
    async def create_conversation(conversation_type: str, participant_ids: List[str], name: str = None) -> dict:
        """Create a new conversation"""
        driver = get_neo4j_driver()
        conversation_id = generate_id()
        async with driver.session() as session:
            # Create conversation node
            query = """
            CREATE (c:Conversation {
                conversation_id: $conv_id,
                type: $conv_type,
                name: $name,
                created_at: datetime(),
                last_message_at: null
            })
            RETURN c.conversation_id as conversation_id, c.type as conversation_type, 
                   c.name as name, c.created_at as created_at
            """
            result = await session.run(query, conv_id=conversation_id, conv_type=conversation_type, name=name)
            conv_record = await result.single()
            
            # Add participants
            for player_id in participant_ids:
                add_query = """
                MATCH (c:Conversation {conversation_id: $conv_id})
                MATCH (p:Player {player_id: $player_id})
                CREATE (p)-[m:MEMBER_OF {joined_at: datetime(), role: 'member', muted: false}]->(c)
                """
                await session.run(add_query, conv_id=conversation_id, player_id=player_id)
            
            return dict(conv_record) if conv_record else None
    
    # CREATE - Message
    @staticmethod
    async def send_message(conversation_id: str, sender_id: str, content: str) -> dict:
        """Send a message in a conversation"""
        driver = get_neo4j_driver()
        message_id = generate_id()
        async with driver.session() as session:
            query = """
            MATCH (c:Conversation {conversation_id: $conv_id})
            MATCH (sender:Player {player_id: $sender_id})
            CREATE (m:Message {
                message_id: $msg_id,
                content: $content,
                timestamp: datetime(),
                edited: false
            })
            CREATE (sender)-[:SENT]->(m)
            CREATE (c)-[:CONTAINS]->(m)
            SET c.last_message_at = datetime()
            RETURN m.message_id as message_id, $conv_id as conversation_id,
                   sender.player_id as sender_id, sender.username as sender_username,
                   m.content as content, m.timestamp as timestamp, m.edited as edited
            """
            result = await session.run(
                query, conv_id=conversation_id, sender_id=sender_id, 
                msg_id=message_id, content=content
            )
            record = await result.single()
            return dict(record) if record else None
    
    # READ - Get conversation
    @staticmethod
    async def get_conversation(conversation_id: str) -> Optional[dict]:
        """Get a conversation with its participants"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (c:Conversation {conversation_id: $conv_id})
            OPTIONAL MATCH (p:Player)-[m:MEMBER_OF]->(c)
            RETURN c.conversation_id as conversation_id, c.type as conversation_type,
                   c.name as name, c.created_at as created_at, c.last_message_at as last_message_at,
                   collect({player_id: p.player_id, username: p.username, status: p.status}) as participants
            """
            result = await session.run(query, conv_id=conversation_id)
            record = await result.single()
            return dict(record) if record else None
    
    # READ - Get player's conversations
    @staticmethod
    async def get_player_conversations(player_id: str) -> List[dict]:
        """Get all conversations for a player"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (p:Player {player_id: $player_id})-[:MEMBER_OF]->(c:Conversation)
            OPTIONAL MATCH (other:Player)-[:MEMBER_OF]->(c) WHERE other.player_id <> $player_id
            RETURN c.conversation_id as conversation_id, c.type as conversation_type,
                   c.name as name, c.created_at as created_at, c.last_message_at as last_message_at,
                   collect({player_id: other.player_id, username: other.username}) as other_participants
            ORDER BY c.last_message_at DESC
            """
            result = await session.run(query, player_id=player_id)
            records = await result.data()
            return records
    
    # READ - Get messages in conversation
    @staticmethod
    async def get_messages(conversation_id: str, limit: int = 50, offset: int = 0) -> List[dict]:
        """Get messages in a conversation"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (c:Conversation {conversation_id: $conv_id})-[:CONTAINS]->(m:Message)
            MATCH (sender:Player)-[:SENT]->(m)
            RETURN m.message_id as message_id, $conv_id as conversation_id,
                   sender.player_id as sender_id, sender.username as sender_username,
                   m.content as content, m.timestamp as timestamp, 
                   m.edited as edited, m.edited_at as edited_at
            ORDER BY m.timestamp DESC
            SKIP $offset
            LIMIT $limit
            """
            result = await session.run(query, conv_id=conversation_id, limit=limit, offset=offset)
            records = await result.data()
            return records
    
    # UPDATE - Edit message
    @staticmethod
    async def edit_message(message_id: str, new_content: str) -> Optional[dict]:
        """Edit a message"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (m:Message {message_id: $msg_id})
            MATCH (sender:Player)-[:SENT]->(m)
            MATCH (c:Conversation)-[:CONTAINS]->(m)
            SET m.content = $content, m.edited = true, m.edited_at = datetime()
            RETURN m.message_id as message_id, c.conversation_id as conversation_id,
                   sender.player_id as sender_id, sender.username as sender_username,
                   m.content as content, m.timestamp as timestamp, 
                   m.edited as edited, m.edited_at as edited_at
            """
            result = await session.run(query, msg_id=message_id, content=new_content)
            record = await result.single()
            return dict(record) if record else None
    
    # UPDATE - Mute conversation
    @staticmethod
    async def mute_conversation(player_id: str, conversation_id: str, muted: bool = True) -> bool:
        """Mute or unmute a conversation for a player"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (p:Player {player_id: $player_id})-[m:MEMBER_OF]->(c:Conversation {conversation_id: $conv_id})
            SET m.muted = $muted
            RETURN count(m) as updated
            """
            result = await session.run(query, player_id=player_id, conv_id=conversation_id, muted=muted)
            record = await result.single()
            return record["updated"] > 0 if record else False
    
    # DELETE - Delete message
    @staticmethod
    async def delete_message(message_id: str) -> bool:
        """Delete a message"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (m:Message {message_id: $msg_id})
            DETACH DELETE m
            RETURN count(m) as deleted
            """
            result = await session.run(query, msg_id=message_id)
            record = await result.single()
            return record["deleted"] > 0 if record else False
    
    # DELETE - Leave conversation
    @staticmethod
    async def leave_conversation(player_id: str, conversation_id: str) -> bool:
        """Leave a conversation"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (p:Player {player_id: $player_id})-[m:MEMBER_OF]->(c:Conversation {conversation_id: $conv_id})
            DELETE m
            RETURN count(m) as deleted
            """
            result = await session.run(query, player_id=player_id, conv_id=conversation_id)
            record = await result.single()
            return record["deleted"] > 0 if record else False


# ==================== PARTY CRUD ====================
class PartyCRUD:
    
    # CREATE
    @staticmethod
    async def create_party(leader_id: str, game_id: str, max_size: int = 4, is_public: bool = False) -> dict:
        """Create a new party"""
        driver = get_neo4j_driver()
        party_id = generate_id()
        async with driver.session() as session:
            query = """
            MATCH (leader:Player {player_id: $leader_id})
            CREATE (party:Party {
                party_id: $party_id,
                game_id: $game_id,
                max_size: $max_size,
                is_public: $is_public,
                created_at: datetime()
            })
            CREATE (leader)-[:IN_PARTY {joined_at: datetime(), role: 'leader'}]->(party)
            RETURN party.party_id as party_id, party.game_id as game_id,
                   party.max_size as max_size, party.is_public as is_public,
                   party.created_at as created_at
            """
            result = await session.run(
                query, leader_id=leader_id, party_id=party_id, 
                game_id=game_id, max_size=max_size, is_public=is_public
            )
            record = await result.single()
            return dict(record) if record else None
    
    # CREATE - Invite to party
    @staticmethod
    async def invite_to_party(party_id: str, inviter_id: str, invitee_id: str) -> dict:
        """Invite a player to a party"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (party:Party {party_id: $party_id})
            MATCH (invitee:Player {player_id: $invitee_id})
            CREATE (invitee)-[:INVITED_TO {invited_by: $inviter_id, invited_at: datetime()}]->(party)
            RETURN party.party_id as party_id, invitee.player_id as invitee_id, 
                   invitee.username as invitee_username
            """
            result = await session.run(query, party_id=party_id, inviter_id=inviter_id, invitee_id=invitee_id)
            record = await result.single()
            return dict(record) if record else None
    
    # CREATE - Join party
    @staticmethod
    async def join_party(party_id: str, player_id: str) -> dict:
        """Join a party (accept invite or join public)"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            # Remove invite if exists and join
            query = """
            MATCH (player:Player {player_id: $player_id})
            MATCH (party:Party {party_id: $party_id})
            OPTIONAL MATCH (player)-[i:INVITED_TO]->(party)
            DELETE i
            CREATE (player)-[:IN_PARTY {joined_at: datetime(), role: 'member'}]->(party)
            RETURN party.party_id as party_id, player.player_id as player_id, 
                   player.username as username
            """
            result = await session.run(query, party_id=party_id, player_id=player_id)
            record = await result.single()
            return dict(record) if record else None
    
    # READ
    @staticmethod
    async def get_party(party_id: str) -> Optional[dict]:
        """Get party details with members"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (party:Party {party_id: $party_id})
            OPTIONAL MATCH (member:Player)-[ip:IN_PARTY]->(party)
            RETURN party.party_id as party_id, party.game_id as game_id,
                   party.max_size as max_size, party.is_public as is_public,
                   party.created_at as created_at,
                   collect({player_id: member.player_id, username: member.username, 
                           role: ip.role, joined_at: ip.joined_at}) as members
            """
            result = await session.run(query, party_id=party_id)
            record = await result.single()
            return dict(record) if record else None
    
    @staticmethod
    async def get_player_party(player_id: str) -> Optional[dict]:
        """Get the party a player is currently in"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (p:Player {player_id: $player_id})-[:IN_PARTY]->(party:Party)
            RETURN party.party_id as party_id, party.game_id as game_id,
                   party.max_size as max_size, party.is_public as is_public
            """
            result = await session.run(query, player_id=player_id)
            record = await result.single()
            return dict(record) if record else None
    
    # UPDATE
    @staticmethod
    async def update_party(party_id: str, max_size: int = None, is_public: bool = None, game_id: str = None) -> Optional[dict]:
        """Update party settings"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            set_clauses = []
            params = {"party_id": party_id}
            
            if max_size is not None:
                set_clauses.append("party.max_size = $max_size")
                params["max_size"] = max_size
            if is_public is not None:
                set_clauses.append("party.is_public = $is_public")
                params["is_public"] = is_public
            if game_id is not None:
                set_clauses.append("party.game_id = $game_id")
                params["game_id"] = game_id
            
            if not set_clauses:
                return await PartyCRUD.get_party(party_id)
            
            query = f"""
            MATCH (party:Party {{party_id: $party_id}})
            SET {", ".join(set_clauses)}
            RETURN party.party_id as party_id, party.game_id as game_id,
                   party.max_size as max_size, party.is_public as is_public
            """
            result = await session.run(query, **params)
            record = await result.single()
            return dict(record) if record else None
    
    # DELETE - Leave party
    @staticmethod
    async def leave_party(party_id: str, player_id: str) -> bool:
        """Leave a party"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (p:Player {player_id: $player_id})-[ip:IN_PARTY]->(party:Party {party_id: $party_id})
            DELETE ip
            RETURN count(ip) as deleted
            """
            result = await session.run(query, party_id=party_id, player_id=player_id)
            record = await result.single()
            return record["deleted"] > 0 if record else False
    
    # DELETE - Disband party
    @staticmethod
    async def disband_party(party_id: str) -> bool:
        """Delete a party and all memberships"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (party:Party {party_id: $party_id})
            DETACH DELETE party
            RETURN count(party) as deleted
            """
            result = await session.run(query, party_id=party_id)
            record = await result.single()
            return record["deleted"] > 0 if record else False


# ==================== CLAN CRUD ====================
class ClanCRUD:
    
    # CREATE
    @staticmethod
    async def create_clan(name: str, tag: str, owner_id: str, description: str = None) -> dict:
        """Create a new clan"""
        driver = get_neo4j_driver()
        clan_id = generate_id()
        async with driver.session() as session:
            query = """
            MATCH (owner:Player {player_id: $owner_id})
            CREATE (clan:Clan {
                clan_id: $clan_id,
                name: $name,
                tag: $tag,
                description: $description,
                created_at: datetime()
            })
            CREATE (owner)-[:BELONGS_TO {joined_at: datetime(), role: 'owner', rank: 1}]->(clan)
            RETURN clan.clan_id as clan_id, clan.name as name, clan.tag as tag,
                   clan.description as description, clan.created_at as created_at
            """
            result = await session.run(
                query, clan_id=clan_id, name=name, tag=tag, 
                owner_id=owner_id, description=description
            )
            record = await result.single()
            return dict(record) if record else None
    
    # CREATE - Join clan
    @staticmethod
    async def join_clan(clan_id: str, player_id: str) -> dict:
        """Join a clan"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            # Get current member count for rank
            count_query = """
            MATCH (clan:Clan {clan_id: $clan_id})
            OPTIONAL MATCH (m:Player)-[:BELONGS_TO]->(clan)
            RETURN count(m) as member_count
            """
            count_result = await session.run(count_query, clan_id=clan_id)
            count_record = await count_result.single()
            rank = (count_record["member_count"] or 0) + 1
            
            query = """
            MATCH (player:Player {player_id: $player_id})
            MATCH (clan:Clan {clan_id: $clan_id})
            CREATE (player)-[:BELONGS_TO {joined_at: datetime(), role: 'member', rank: $rank}]->(clan)
            RETURN clan.clan_id as clan_id, player.player_id as player_id, 
                   player.username as username
            """
            result = await session.run(query, clan_id=clan_id, player_id=player_id, rank=rank)
            record = await result.single()
            return dict(record) if record else None
    
    # READ
    @staticmethod
    async def get_clan(clan_id: str) -> Optional[dict]:
        """Get clan details with members"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (clan:Clan {clan_id: $clan_id})
            OPTIONAL MATCH (member:Player)-[bt:BELONGS_TO]->(clan)
            RETURN clan.clan_id as clan_id, clan.name as name, clan.tag as tag,
                   clan.description as description, clan.created_at as created_at,
                   count(member) as member_count,
                   collect({player_id: member.player_id, username: member.username, 
                           role: bt.role, rank: bt.rank, joined_at: bt.joined_at}) as members
            """
            result = await session.run(query, clan_id=clan_id)
            record = await result.single()
            return dict(record) if record else None
    
    @staticmethod
    async def get_player_clan(player_id: str) -> Optional[dict]:
        """Get the clan a player belongs to"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (p:Player {player_id: $player_id})-[bt:BELONGS_TO]->(clan:Clan)
            RETURN clan.clan_id as clan_id, clan.name as name, clan.tag as tag,
                   bt.role as role, bt.rank as rank
            """
            result = await session.run(query, player_id=player_id)
            record = await result.single()
            return dict(record) if record else None
    
    @staticmethod
    async def search_clans(search_term: str, limit: int = 20) -> List[dict]:
        """Search for clans by name or tag"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (clan:Clan)
            WHERE clan.name CONTAINS $search OR clan.tag CONTAINS $search
            OPTIONAL MATCH (m:Player)-[:BELONGS_TO]->(clan)
            RETURN clan.clan_id as clan_id, clan.name as name, clan.tag as tag,
                   clan.description as description, count(m) as member_count
            LIMIT $limit
            """
            result = await session.run(query, search=search_term, limit=limit)
            records = await result.data()
            return records
    
    # UPDATE
    @staticmethod
    async def update_clan(clan_id: str, name: str = None, tag: str = None, description: str = None) -> Optional[dict]:
        """Update clan details"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            set_clauses = []
            params = {"clan_id": clan_id}
            
            if name is not None:
                set_clauses.append("clan.name = $name")
                params["name"] = name
            if tag is not None:
                set_clauses.append("clan.tag = $tag")
                params["tag"] = tag
            if description is not None:
                set_clauses.append("clan.description = $description")
                params["description"] = description
            
            if not set_clauses:
                return await ClanCRUD.get_clan(clan_id)
            
            query = f"""
            MATCH (clan:Clan {{clan_id: $clan_id}})
            SET {", ".join(set_clauses)}
            RETURN clan.clan_id as clan_id, clan.name as name, clan.tag as tag,
                   clan.description as description
            """
            result = await session.run(query, **params)
            record = await result.single()
            return dict(record) if record else None
    
    @staticmethod
    async def update_member_role(clan_id: str, player_id: str, role: str, rank: int = None) -> Optional[dict]:
        """Update a member's role in the clan"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            set_clauses = ["bt.role = $role"]
            params = {"clan_id": clan_id, "player_id": player_id, "role": role}
            
            if rank is not None:
                set_clauses.append("bt.rank = $rank")
                params["rank"] = rank
            
            query = f"""
            MATCH (p:Player {{player_id: $player_id}})-[bt:BELONGS_TO]->(clan:Clan {{clan_id: $clan_id}})
            SET {", ".join(set_clauses)}
            RETURN p.player_id as player_id, p.username as username, bt.role as role, bt.rank as rank
            """
            result = await session.run(query, **params)
            record = await result.single()
            return dict(record) if record else None
    
    # DELETE - Leave clan
    @staticmethod
    async def leave_clan(clan_id: str, player_id: str) -> bool:
        """Leave a clan"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (p:Player {player_id: $player_id})-[bt:BELONGS_TO]->(clan:Clan {clan_id: $clan_id})
            DELETE bt
            RETURN count(bt) as deleted
            """
            result = await session.run(query, clan_id=clan_id, player_id=player_id)
            record = await result.single()
            return record["deleted"] > 0 if record else False
    
    # DELETE - Disband clan
    @staticmethod
    async def disband_clan(clan_id: str) -> bool:
        """Delete a clan"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (clan:Clan {clan_id: $clan_id})
            DETACH DELETE clan
            RETURN count(clan) as deleted
            """
            result = await session.run(query, clan_id=clan_id)
            record = await result.single()
            return record["deleted"] > 0 if record else False


# ==================== FOLLOW CRUD ====================
class FollowCRUD:
    
    # CREATE
    @staticmethod
    async def follow_player(follower_id: str, following_id: str) -> dict:
        """Follow a player"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (follower:Player {player_id: $follower_id})
            MATCH (following:Player {player_id: $following_id})
            CREATE (follower)-[:FOLLOWS {since: datetime()}]->(following)
            RETURN following.player_id as player_id, following.username as username
            """
            result = await session.run(query, follower_id=follower_id, following_id=following_id)
            record = await result.single()
            return dict(record) if record else None
    
    # READ
    @staticmethod
    async def get_following(player_id: str) -> List[dict]:
        """Get players that this player follows"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (p:Player {player_id: $player_id})-[f:FOLLOWS]->(following:Player)
            RETURN following.player_id as player_id, following.username as username,
                   following.status as status, f.since as following_since
            """
            result = await session.run(query, player_id=player_id)
            records = await result.data()
            return records
    
    @staticmethod
    async def get_followers(player_id: str) -> List[dict]:
        """Get players that follow this player"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (follower:Player)-[f:FOLLOWS]->(p:Player {player_id: $player_id})
            RETURN follower.player_id as player_id, follower.username as username,
                   follower.status as status, f.since as following_since
            """
            result = await session.run(query, player_id=player_id)
            records = await result.data()
            return records
    
    # DELETE
    @staticmethod
    async def unfollow_player(follower_id: str, following_id: str) -> bool:
        """Unfollow a player"""
        driver = get_neo4j_driver()
        async with driver.session() as session:
            query = """
            MATCH (follower:Player {player_id: $follower_id})-[f:FOLLOWS]->(following:Player {player_id: $following_id})
            DELETE f
            RETURN count(f) as deleted
            """
            result = await session.run(query, follower_id=follower_id, following_id=following_id)
            record = await result.single()
            return record["deleted"] > 0 if record else False
