"""
Sample data script to populate databases with test data
Run this after starting the API server
"""

import asyncio
import httpx

BASE_URL = "http://localhost:8000/api/v1"


async def create_sample_data():
    async with httpx.AsyncClient() as client:
        print("=" * 50)
        print("Creating Sample Data for Multiplayer Gaming System")
        print("=" * 50)
        
        # ========== CREATE GAMES ==========
        print("\n📎 Creating Games...")
        games_data = [
            {
                "title": "Battle Royale X",
                "publisher": "Epic Games Studio",
                "platforms": ["xbox", "playstation", "pc", "nintendo"],
                "crossplay_enabled": True,
                "max_players": 100,
                "genres": ["battle-royale", "shooter"]
            },
            {
                "title": "Racing Thunder",
                "publisher": "Speed Studios",
                "platforms": ["xbox", "playstation", "pc"],
                "crossplay_enabled": True,
                "max_players": 20,
                "genres": ["racing", "arcade"]
            },
            {
                "title": "Fantasy Quest Online",
                "publisher": "MMORPG Inc",
                "platforms": ["pc", "mobile"],
                "crossplay_enabled": False,
                "max_players": 1000,
                "genres": ["mmorpg", "fantasy"]
            }
        ]
        
        game_ids = []
        for game in games_data:
            response = await client.post(f"{BASE_URL}/games", json=game)
            if response.status_code == 201:
                result = response.json()
                game_ids.append(result["_id"])
                print(f"  ✅ Created game: {game['title']}")
            else:
                print(f"  ❌ Failed to create game: {game['title']}")
        
        # ========== CREATE PLAYERS ==========
        print("\n👤 Creating Players...")
        players_data = [
            {"username": "ProGamer99", "email": "progamer99@email.com", "platforms": ["xbox", "pc"]},
            {"username": "NightHawk", "email": "nighthawk@email.com", "platforms": ["playstation"]},
            {"username": "ShadowStrike", "email": "shadow@email.com", "platforms": ["pc"]},
            {"username": "ThunderBolt", "email": "thunder@email.com", "platforms": ["xbox", "playstation", "pc"]},
            {"username": "CyberNinja", "email": "cyber@email.com", "platforms": ["nintendo", "mobile"]},
        ]
        
        player_ids = []
        for player in players_data:
            response = await client.post(f"{BASE_URL}/players", json=player)
            if response.status_code == 201:
                result = response.json()
                player_ids.append(result["_id"])
                print(f"  ✅ Created player: {player['username']}")
            else:
                print(f"  ❌ Failed to create player: {player['username']} - {response.text}")
        
        # ========== CREATE PLAYER NODES IN NEO4J ==========
        print("\n🔗 Creating Player Nodes in Neo4j...")
        for i, player in enumerate(players_data):
            if i < len(player_ids):
                node_data = {
                    "player_id": player_ids[i],
                    "username": player["username"],
                    "status": "online" if i < 2 else "offline"
                }
                response = await client.post(f"{BASE_URL}/player-nodes", json=node_data)
                if response.status_code == 201:
                    print(f"  ✅ Created node for: {player['username']}")
                else:
                    print(f"  ❌ Failed to create node: {player['username']}")
        
        # ========== CREATE PLAYER STATS ==========
        print("\n📊 Creating Player Stats...")
        if len(player_ids) >= 2 and len(game_ids) >= 1:
            for player_id in player_ids[:3]:
                stats_data = {"player_id": player_id, "game_id": game_ids[0]}
                response = await client.post(f"{BASE_URL}/stats", json=stats_data)
                if response.status_code == 201:
                    print(f"  ✅ Created stats for player")
                    # Update with some stats
                    await client.patch(
                        f"{BASE_URL}/stats/{player_id}/{game_ids[0]}",
                        json={"wins": 10, "losses": 5, "kills": 150, "deaths": 75, "xp": 5000}
                    )
        
        # ========== CREATE ACHIEVEMENTS ==========
        print("\n🏆 Creating Achievements...")
        if len(game_ids) >= 1:
            achievements_data = [
                {
                    "game_id": game_ids[0],
                    "name": "First Blood",
                    "description": "Get your first kill in Battle Royale X",
                    "xp_reward": 100,
                    "rarity": "common",
                    "criteria": {"kills": 1}
                },
                {
                    "game_id": game_ids[0],
                    "name": "Champion",
                    "description": "Win 10 matches",
                    "xp_reward": 1000,
                    "rarity": "epic",
                    "criteria": {"wins": 10}
                },
                {
                    "game_id": game_ids[0],
                    "name": "Legendary Warrior",
                    "description": "Get 1000 total kills",
                    "xp_reward": 5000,
                    "rarity": "legendary",
                    "criteria": {"kills": 1000}
                }
            ]
            
            achievement_ids = []
            for ach in achievements_data:
                response = await client.post(f"{BASE_URL}/achievements", json=ach)
                if response.status_code == 201:
                    result = response.json()
                    achievement_ids.append(result["_id"])
                    print(f"  ✅ Created achievement: {ach['name']}")
        
        # ========== CREATE LEADERBOARD ==========
        print("\n📈 Creating Leaderboard...")
        if len(game_ids) >= 1:
            leaderboard_data = {
                "game_id": game_ids[0],
                "leaderboard_type": "wins",
                "timeframe": "all_time"
            }
            response = await client.post(f"{BASE_URL}/leaderboards", json=leaderboard_data)
            if response.status_code == 201:
                result = response.json()
                leaderboard_id = result["_id"]
                print(f"  ✅ Created leaderboard")
                
                # Add entries
                for i, player_id in enumerate(player_ids[:3]):
                    await client.post(
                        f"{BASE_URL}/leaderboards/{leaderboard_id}/entry",
                        params={
                            "player_id": player_id,
                            "username": players_data[i]["username"],
                            "score": 100 - (i * 15)
                        }
                    )
                print("  ✅ Added leaderboard entries")
        
        # ========== CREATE FRIENDSHIPS ==========
        print("\n👥 Creating Friendships...")
        if len(player_ids) >= 3:
            # Send friend requests
            for i in range(1, min(3, len(player_ids))):
                request_data = {
                    "from_player_id": player_ids[0],
                    "to_player_id": player_ids[i],
                    "message": "Let's be friends!"
                }
                response = await client.post(f"{BASE_URL}/friends/request", json=request_data)
                if response.status_code == 201:
                    print(f"  ✅ Sent friend request: {players_data[0]['username']} -> {players_data[i]['username']}")
                    
                    # Accept the request
                    await client.post(
                        f"{BASE_URL}/friends/accept",
                        params={"from_player_id": player_ids[0], "to_player_id": player_ids[i]}
                    )
                    print(f"  ✅ Accepted friendship")
        
        # ========== CREATE CONVERSATION ==========
        print("\n💬 Creating Conversations...")
        if len(player_ids) >= 2:
            conv_data = {
                "conversation_type": "direct",
                "participant_ids": [player_ids[0], player_ids[1]],
                "name": None
            }
            response = await client.post(f"{BASE_URL}/messages/conversation", json=conv_data)
            if response.status_code == 201:
                conv = response.json()
                print(f"  ✅ Created conversation")
                
                # Send messages
                messages = [
                    {"conversation_id": conv["conversation_id"], "sender_id": player_ids[0], "content": "Hey! Want to play?"},
                    {"conversation_id": conv["conversation_id"], "sender_id": player_ids[1], "content": "Sure! Let me finish this match first."},
                    {"conversation_id": conv["conversation_id"], "sender_id": player_ids[0], "content": "Cool, invite me when ready!"},
                ]
                for msg in messages:
                    await client.post(f"{BASE_URL}/messages", json=msg)
                print(f"  ✅ Sent {len(messages)} messages")
        
        # ========== CREATE PARTY ==========
        print("\n🎮 Creating Party...")
        if len(player_ids) >= 2 and len(game_ids) >= 1:
            party_data = {
                "leader_id": player_ids[0],
                "game_id": game_ids[0],
                "max_size": 4,
                "is_public": False
            }
            response = await client.post(f"{BASE_URL}/parties", json=party_data)
            if response.status_code == 201:
                party = response.json()
                print(f"  ✅ Created party")
                
                # Invite and join
                invite_data = {
                    "party_id": party["party_id"],
                    "inviter_id": player_ids[0],
                    "invitee_id": player_ids[1]
                }
                await client.post(f"{BASE_URL}/parties/{party['party_id']}/invite", json=invite_data)
                await client.post(
                    f"{BASE_URL}/parties/{party['party_id']}/join",
                    params={"player_id": player_ids[1]}
                )
                print(f"  ✅ Player joined party")
        
        # ========== CREATE CLAN ==========
        print("\n⚔️ Creating Clan...")
        if len(player_ids) >= 3:
            clan_data = {
                "name": "Elite Gamers",
                "tag": "ELITE",
                "owner_id": player_ids[0],
                "description": "The best of the best gamers unite!"
            }
            response = await client.post(f"{BASE_URL}/clans", json=clan_data)
            if response.status_code == 201:
                clan = response.json()
                print(f"  ✅ Created clan: {clan_data['name']}")
                
                # Add members
                for player_id in player_ids[1:3]:
                    await client.post(
                        f"{BASE_URL}/clans/{clan['clan_id']}/join",
                        params={"player_id": player_id}
                    )
                print(f"  ✅ Added clan members")
        
        # ========== CREATE MATCH ==========
        print("\n🎯 Recording Match...")
        if len(player_ids) >= 4 and len(game_ids) >= 1:
            match_data = {
                "game_id": game_ids[0],
                "players": [
                    {"player_id": player_ids[0], "team": "red", "score": 1500, "kills": 12, "deaths": 5, "assists": 8},
                    {"player_id": player_ids[1], "team": "red", "score": 1200, "kills": 8, "deaths": 6, "assists": 10},
                    {"player_id": player_ids[2], "team": "blue", "score": 1100, "kills": 7, "deaths": 8, "assists": 5},
                    {"player_id": player_ids[3], "team": "blue", "score": 900, "kills": 5, "deaths": 10, "assists": 3},
                ],
                "game_mode": "team_deathmatch",
                "map_name": "Dust Valley",
                "duration": 1200,
                "winner_team": "red"
            }
            response = await client.post(f"{BASE_URL}/matches", json=match_data)
            if response.status_code == 201:
                print(f"  ✅ Recorded match")
        
        print("\n" + "=" * 50)
        print("✅ Sample data creation complete!")
        print("=" * 50)
        print("\nYou can now explore the API at:")
        print("  - Swagger UI: http://localhost:8000/docs")
        print("  - ReDoc: http://localhost:8000/redoc")


if __name__ == "__main__":
    asyncio.run(create_sample_data())
