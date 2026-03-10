"""
Test script for all Neo4j endpoints
Run with: python scripts/test_neo4j_endpoints.py
"""

import requests
import json
from urllib.parse import urlencode

BASE_URL = "http://localhost:8001/api/v1/graph"

def print_result(name, response):
    status = "✓" if response.status_code < 400 else "✗"
    print(f"{status} {name}: {response.status_code}")
    try:
        data = response.json()
        print(f"   Response: {json.dumps(data, indent=2)[:300]}")
    except:
        print(f"   Response: {response.text[:300]}")
    print()

def test_player_nodes():
    print("\n" + "="*60)
    print("TESTING PLAYER NODES")
    print("="*60)
    
    # Create players
    for pid, name in [("p1", "Alice"), ("p2", "Bob"), ("p3", "Charlie"), ("p4", "Diana")]:
        r = requests.post(f"{BASE_URL}/player-nodes/", json={
            "player_id": pid, "username": name, "status": "online"
        })
        print_result(f"Create player {name}", r)
    
    # Get player
    r = requests.get(f"{BASE_URL}/player-nodes/p1")
    print_result("Get player p1", r)
    
    # Update status (URL encoded)
    r = requests.patch(f"{BASE_URL}/player-nodes/p1/status?status=in_game")
    print_result("Update p1 status", r)
    
    # Update username (URL encoded)
    r = requests.patch(f"{BASE_URL}/player-nodes/p1/username?username=Alice_Updated")
    print_result("Update p1 username", r)

def test_friendships():
    print("\n" + "="*60)
    print("TESTING FRIENDSHIPS")
    print("="*60)
    
    # Send friend request
    r = requests.post(f"{BASE_URL}/friends/request", json={
        "from_player_id": "p1", "to_player_id": "p2", "message": "Let's be friends!"
    })
    print_result("Send friend request p1->p2", r)
    
    # Get pending requests
    r = requests.get(f"{BASE_URL}/friends/requests/p2")
    print_result("Get pending requests for p2", r)
    
    # Accept friend request (URL encoded)
    r = requests.post(f"{BASE_URL}/friends/accept?from_player_id=p1&to_player_id=p2")
    print_result("Accept friend request p1->p2", r)
    
    # Create more friendships
    for from_p, to_p in [("p2", "p3"), ("p3", "p4")]:
        requests.post(f"{BASE_URL}/friends/request", json={
            "from_player_id": from_p, "to_player_id": to_p, "message": ""
        })
        requests.post(f"{BASE_URL}/friends/accept?from_player_id={from_p}&to_player_id={to_p}")
    
    # Get friends list
    r = requests.get(f"{BASE_URL}/friends/p1")
    print_result("Get friends list for p1", r)
    
    # Get friend suggestions
    r = requests.get(f"{BASE_URL}/friends/suggestions/p1?limit=5")
    print_result("Get friend suggestions for p1", r)
    
    # Get mutual friends
    r = requests.get(f"{BASE_URL}/friends/mutual/p1/p3")
    print_result("Get mutual friends p1-p3", r)
    
    # Set nickname (URL encoded)
    r = requests.patch(f"{BASE_URL}/friends/nickname?player_id=p1&friend_id=p2&nickname=Bobby")
    print_result("Set nickname for p2", r)
    
    # Send request to decline
    requests.post(f"{BASE_URL}/friends/request", json={
        "from_player_id": "p4", "to_player_id": "p1", "message": ""
    })
    # Decline (URL encoded)
    r = requests.delete(f"{BASE_URL}/friends/request?from_player_id=p4&to_player_id=p1")
    print_result("Decline friend request p4->p1", r)
    
    # Remove friend (URL encoded)
    r = requests.delete(f"{BASE_URL}/friends/?player_id=p1&friend_id=p2")
    print_result("Remove friend p2 from p1", r)

def test_blocking():
    print("\n" + "="*60)
    print("TESTING BLOCKING")
    print("="*60)
    
    # Block player
    r = requests.post(f"{BASE_URL}/block/", json={
        "blocker_id": "p1", "blocked_id": "p4", "reason": "Toxic behavior"
    })
    print_result("Block p4 by p1", r)
    
    # Get blocked players
    r = requests.get(f"{BASE_URL}/block/p1")
    print_result("Get blocked list for p1", r)
    
    # Unblock player (URL encoded)
    r = requests.delete(f"{BASE_URL}/block/?blocker_id=p1&blocked_id=p4")
    print_result("Unblock p4 by p1", r)

def test_messaging():
    print("\n" + "="*60)
    print("TESTING MESSAGING")
    print("="*60)
    
    # Create conversation
    r = requests.post(f"{BASE_URL}/messages/conversation", json={
        "conversation_type": "direct",
        "participant_ids": ["p1", "p2"],
        "name": "Alice & Bob Chat"
    })
    print_result("Create conversation", r)
    
    conv_id = None
    try:
        conv_id = r.json().get("conversation_id")
    except:
        pass
    
    if conv_id:
        # Get conversation
        r = requests.get(f"{BASE_URL}/messages/conversation/{conv_id}")
        print_result("Get conversation", r)
        
        # Send message
        r = requests.post(f"{BASE_URL}/messages/", json={
            "conversation_id": conv_id,
            "sender_id": "p1",
            "content": "Hello Bob!"
        })
        print_result("Send message", r)
        
        msg_id = None
        try:
            msg_id = r.json().get("message_id")
        except:
            pass
        
        if msg_id:
            # Edit message (PUT)
            r = requests.put(f"{BASE_URL}/messages/{msg_id}", json={
                "content": "Hello Bob! How are you?"
            })
            print_result("Edit message", r)
            
            # Delete message
            r = requests.delete(f"{BASE_URL}/messages/{msg_id}")
            print_result("Delete message", r)
        
        # Get messages
        r = requests.get(f"{BASE_URL}/messages/conversation/{conv_id}/messages")
        print_result("Get messages in conversation", r)
        
        # Get player conversations
        r = requests.get(f"{BASE_URL}/messages/player/p1/conversations")
        print_result("Get p1's conversations", r)
        
        # Mute conversation (URL encoded)
        r = requests.patch(f"{BASE_URL}/messages/conversation/{conv_id}/mute?player_id=p1&muted=true")
        print_result("Mute conversation for p1", r)
        
        # Leave conversation (URL encoded)
        r = requests.delete(f"{BASE_URL}/messages/conversation/{conv_id}/leave?player_id=p2")
        print_result("p2 leaves conversation", r)

def test_parties():
    print("\n" + "="*60)
    print("TESTING PARTIES")
    print("="*60)
    
    # Create party
    r = requests.post(f"{BASE_URL}/parties/", json={
        "leader_id": "p1",
        "game_id": "game123",
        "max_size": 4,
        "is_public": True
    })
    print_result("Create party", r)
    
    party_id = None
    try:
        party_id = r.json().get("party_id")
    except:
        pass
    
    if party_id:
        # Get party
        r = requests.get(f"{BASE_URL}/parties/{party_id}")
        print_result("Get party", r)
        
        # Invite to party
        r = requests.post(f"{BASE_URL}/parties/{party_id}/invite", json={
            "inviter_id": "p1", "invitee_id": "p2"
        })
        print_result("Invite p2 to party", r)
        
        # Join party (URL encoded)
        r = requests.post(f"{BASE_URL}/parties/{party_id}/join?player_id=p2")
        print_result("p2 joins party", r)
        
        # Update party
        r = requests.patch(f"{BASE_URL}/parties/{party_id}", json={
            "max_size": 6, "is_public": False
        })
        print_result("Update party settings", r)
        
        # Get player's party
        r = requests.get(f"{BASE_URL}/parties/player/p1")
        print_result("Get p1's party", r)
        
        # Leave party (URL encoded)
        r = requests.delete(f"{BASE_URL}/parties/{party_id}/leave?player_id=p2")
        print_result("p2 leaves party", r)
        
        # Disband party
        r = requests.delete(f"{BASE_URL}/parties/{party_id}")
        print_result("Disband party", r)

def test_clans():
    print("\n" + "="*60)
    print("TESTING CLANS")
    print("="*60)
    
    # Create clan
    r = requests.post(f"{BASE_URL}/clans/", json={
        "name": "Dragon Warriors",
        "tag": "DRW",
        "owner_id": "p1",
        "description": "Elite gaming clan"
    })
    print_result("Create clan", r)
    
    clan_id = None
    try:
        clan_id = r.json().get("clan_id")
    except:
        pass
    
    if clan_id:
        # Get clan
        r = requests.get(f"{BASE_URL}/clans/{clan_id}")
        print_result("Get clan", r)
        
        # Join clan (URL encoded)
        r = requests.post(f"{BASE_URL}/clans/{clan_id}/join?player_id=p2")
        print_result("p2 joins clan", r)
        
        # Update clan
        r = requests.patch(f"{BASE_URL}/clans/{clan_id}", json={
            "description": "Elite competitive gaming clan"
        })
        print_result("Update clan description", r)
        
        # Update member role (use valid enum value)
        r = requests.patch(f"{BASE_URL}/clans/{clan_id}/member/p2", json={
            "role": "admin", "rank": 2
        })
        print_result("Update p2 role to admin", r)
        
        # Search clans
        r = requests.get(f"{BASE_URL}/clans/search/Dragon")
        print_result("Search clans 'Dragon'", r)
        
        # Get player clan
        r = requests.get(f"{BASE_URL}/clans/player/p1")
        print_result("Get p1's clan", r)
        
        # Leave clan (URL encoded)
        r = requests.delete(f"{BASE_URL}/clans/{clan_id}/leave?player_id=p2")
        print_result("p2 leaves clan", r)
        
        # Disband clan
        r = requests.delete(f"{BASE_URL}/clans/{clan_id}")
        print_result("Disband clan", r)

def test_following():
    print("\n" + "="*60)
    print("TESTING FOLLOWING")
    print("="*60)
    
    # Follow player
    r = requests.post(f"{BASE_URL}/follow/", json={
        "follower_id": "p3", "following_id": "p1"
    })
    print_result("p3 follows p1", r)
    
    r = requests.post(f"{BASE_URL}/follow/", json={
        "follower_id": "p4", "following_id": "p1"
    })
    print_result("p4 follows p1", r)
    
    # Get followers
    r = requests.get(f"{BASE_URL}/follow/followers/p1")
    print_result("Get p1's followers", r)
    
    # Get following
    r = requests.get(f"{BASE_URL}/follow/following/p3")
    print_result("Get who p3 is following", r)
    
    # Unfollow (URL encoded)
    r = requests.delete(f"{BASE_URL}/follow/?follower_id=p4&following_id=p1")
    print_result("p4 unfollows p1", r)

def test_analytics():
    print("\n" + "="*60)
    print("TESTING ANALYTICS")
    print("="*60)
    
    # Leaderboard
    r = requests.get(f"{BASE_URL}/analytics/leaderboard?order_by=friends&limit=5")
    print_result("Leaderboard by friends", r)
    
    # Player statistics
    r = requests.get(f"{BASE_URL}/analytics/player/p1/stats")
    print_result("Player p1 statistics", r)
    
    # Global statistics
    r = requests.get(f"{BASE_URL}/analytics/global-stats")
    print_result("Global statistics", r)
    
    # Social graph
    r = requests.get(f"{BASE_URL}/analytics/player/p1/social-graph")
    print_result("p1's social graph", r)
    
    # Find influencers
    r = requests.get(f"{BASE_URL}/analytics/influencers?min_followers=1&limit=5")
    print_result("Find influencers", r)
    
    # Connection chain
    r = requests.get(f"{BASE_URL}/analytics/connection-chain?start_id=p1&end_id=p4")
    print_result("Connection chain p1->p4", r)
    
    # Shortest path
    r = requests.get(f"{BASE_URL}/analytics/shortest-path?player1_id=p1&player2_id=p3")
    print_result("Shortest path p1->p3", r)
    
    # Friend recommendations
    r = requests.get(f"{BASE_URL}/analytics/friend-recommendations/p1?limit=5")
    print_result("Friend recommendations for p1", r)
    
    # Degree centrality
    r = requests.get(f"{BASE_URL}/analytics/player/p1/degree")
    print_result("p1 degree centrality", r)
    
    # Mutual friends count
    r = requests.get(f"{BASE_URL}/analytics/mutual-friends?player1_id=p1&player2_id=p3")
    print_result("Mutual friends count p1-p3", r)
    
    # Clan rankings
    r = requests.get(f"{BASE_URL}/analytics/clan-rankings?limit=5")
    print_result("Clan rankings", r)
    
    # Activity feed
    r = requests.get(f"{BASE_URL}/analytics/player/p1/activity-feed?limit=10")
    print_result("p1 activity feed", r)

def test_delete_cleanup():
    print("\n" + "="*60)
    print("TESTING DELETE OPERATIONS (CLEANUP)")
    print("="*60)
    
    # Delete player node (DETACH DELETE)
    r = requests.delete(f"{BASE_URL}/player-nodes/p4")
    print_result("Delete player p4 (DETACH DELETE)", r)

def main():
    print("\n" + "="*60)
    print("NEO4J ENDPOINTS TEST SUITE")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print()
    
    # Check if server is running
    try:
        r = requests.get("http://localhost:8001/docs")
        print("✓ Server is running\n")
    except requests.ConnectionError:
        print("✗ Server is not running! Start with:")
        print("  python -m uvicorn app.main:app --reload --port 8001")
        return
    
    # Run tests
    test_player_nodes()
    test_friendships()
    test_blocking()
    test_messaging()
    test_parties()
    test_clans()
    test_following()
    test_analytics()
    test_delete_cleanup()
    
    print("\n" + "="*60)
    print("TEST SUITE COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
