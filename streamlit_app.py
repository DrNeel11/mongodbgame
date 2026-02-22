"""
Multiplayer Gaming System - Streamlit Frontend
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from typing import List, Dict, Optional
import json

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

# Page configuration
st.set_page_config(
    page_title="Gaming System Dashboard",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .player-card {
        background: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Helper functions
def make_request(method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None):
    """Make API request with error handling"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, params=params, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)
        else:
            return None
            
        response.raise_for_status()
        return response.json() if response.content else None
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API. Make sure the server is running on http://localhost:8000")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ API Error: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None


# ==================== HOME / DASHBOARD ====================
def show_dashboard():
    """Display main dashboard"""
    st.title("🎮 Multiplayer Gaming System Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        players = make_request("GET", "/players", params={"limit": 100})
        if players:
            st.metric("Total Players", len(players))
        else:
            st.metric("Total Players", "N/A")
    
    with col2:
        games = make_request("GET", "/games", params={"limit": 100})
        if games:
            st.metric("Total Games", len(games))
        else:
            st.metric("Total Games", "N/A")
    
    with col3:
        st.metric("Active Leaderboards", "See Leaderboards tab")
    
    with col4:
        st.metric("Quick Stats", "Scroll below")
    
    st.divider()
    
    # Recent activity
    st.subheader("📊 Quick Stats")
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.info("ℹ️ Navigate to different sections using the sidebar menu to manage players, games, and more!")
    
    with col_right:
        st.warning("⚠️ Ensure the FastAPI server is running on http://localhost:8000")


# ==================== PLAYERS PAGE ====================
def show_players():
    """Display and manage players"""
    st.title("👥 Players Management")
    
    tab1, tab2, tab3 = st.tabs(["Browse Players", "Create Player", "Player Details"])
    
    with tab1:
        st.subheader("Browse All Players")
        
        # Filters
        col1, col2 = st.columns([3, 1])
        with col1:
            search_username = st.text_input("Search by username...", placeholder="Enter username")
        with col2:
            limit = st.number_input("Limit", min_value=10, max_value=100, value=50)
        
        players = make_request("GET", "/players", params={"limit": limit})
        
        if players:
            # Filter by search
            if search_username:
                players = [p for p in players if search_username.lower() in p.get("username", "").lower()]
            
            # Display as table
            df = pd.DataFrame([{
                "Username": p.get("username", "N/A"),
                "Level": p.get("level", 0),
                "Wins": p.get("total_wins", 0),
                "Losses": p.get("total_losses", 0),
                "Platform": ", ".join(p.get("platforms", [])),
                "Status": "🟢 Online" if p.get("is_online") else "🔴 Offline"
            } for p in players])
            
            st.dataframe(df, use_container_width=True)
            
            # Show selected player details
            selected = st.selectbox("Click to view details:", [p.get("username") for p in players], key="player_select")
            if selected:
                player = next((p for p in players if p.get("username") == selected), None)
                if player:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Level", player.get("level", 0))
                    with col2:
                        st.metric("Total Wins", player.get("total_wins", 0))
                    with col3:
                        st.metric("Total Losses", player.get("total_losses", 0))
                    
                    st.json({k: v for k, v in player.items() if k != "_id"})
        else:
            st.warning("No players found or API error")
    
    with tab2:
        st.subheader("Register New Player")
        
        with st.form("create_player_form"):
            username = st.text_input("Username", placeholder="Enter unique username")
            email = st.text_input("Email", placeholder="Enter email")
            level = st.number_input("Starting Level", min_value=1, max_value=100, value=1)
            platforms = st.multiselect(
                "Preferred Platforms",
                ["PC", "PS5", "Xbox", "Mobile", "Switch"],
                default=["PC"]
            )
            bio = st.text_area("Bio", placeholder="Enter player bio (optional)", height=100)
            
            submitted = st.form_submit_button("Create Player", use_container_width=True)
            
            if submitted:
                if not username or not email:
                    st.error("Username and email are required!")
                else:
                    player_data = {
                        "username": username,
                        "email": email,
                        "level": level,
                        "platforms": platforms,
                        "bio": bio,
                        "total_wins": 0,
                        "total_losses": 0,
                        "total_matches": 0,
                        "is_online": True
                    }
                    
                    result = make_request("POST", "/players", data=player_data)
                    if result:
                        st.success(f"✅ Player '{username}' created successfully!")
                        st.json(result)
                    else:
                        st.error("Failed to create player. Username might already exist.")
    
    with tab3:
        st.subheader("Player Details & Stats")
        
        # Get player ID
        all_players = make_request("GET", "/players", params={"limit": 100})
        if all_players:
            player_options = {p.get("username", ""): p for p in all_players}
            selected_player = st.selectbox(
                "Select Player",
                list(player_options.keys()),
                key="player_detail_select"
            )
            
            if selected_player:
                player = player_options[selected_player]
                player_id = str(player.get("_id", ""))
                
                # Display player info
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    st.metric("Level", player.get("level", 0))
                with col2:
                    wins = player.get("total_wins", 0)
                    losses = player.get("total_losses", 0)
                    wr = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
                    st.metric("Win Rate", f"{wr:.1f}%")
                with col3:
                    st.metric("Total Matches", player.get("total_matches", 0))
                
                # Detailed info
                st.json({k: v for k, v in player.items() if k != "_id"})
                
                # Get player stats
                try:
                    stats = make_request("GET", f"/stats/{player_id}")
                    if stats:
                        st.subheader("Detailed Statistics")
                        st.json(stats)
                except:
                    pass


# ==================== GAMES PAGE ====================
def show_games():
    """Display and manage games"""
    st.title("🎯 Games Catalog")
    
    tab1, tab2 = st.tabs(["Browse Games", "Add Game"])
    
    with tab1:
        st.subheader("All Available Games")
        
        search_game = st.text_input("Search games...", placeholder="Enter game name")
        games = make_request("GET", "/games", params={"limit": 100})
        
        if games:
            if search_game:
                games = [g for g in games if search_game.lower() in g.get("title", "").lower()]
            
            # Display games
            for game in games:
                with st.container():
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.subheader(game.get("title", "Unknown"))
                        st.write(game.get("description", "No description"))
                    with col2:
                        st.metric("Genre", game.get("genre", "N/A"))
                    with col3:
                        st.metric("Rating", f"{game.get('rating', 0):.1f}⭐")
                    
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.caption(f"Platforms: {', '.join(game.get('platforms', []))}")
                    with col_b:
                        st.text(f"Released: {game.get('release_date', 'N/A')}")
                    st.divider()
        else:
            st.warning("No games found")
    
    with tab2:
        st.subheader("Add New Game")
        
        with st.form("add_game_form"):
            title = st.text_input("Game Title", placeholder="Enter game name")
            description = st.text_area("Description", placeholder="Enter game description", height=100)
            genre = st.selectbox("Genre", ["Action", "RPG", "Strategy", "Sports", "Puzzle", "Other"])
            platforms = st.multiselect(
                "Platforms",
                ["PC", "PS5", "Xbox", "Mobile", "Switch", "VR"],
                default=["PC"]
            )
            rating = st.slider("Rating", 0.0, 10.0, 8.0)
            release_date = st.date_input("Release Date")
            min_players = st.number_input("Min Players", min_value=1, value=1)
            max_players = st.number_input("Max Players", min_value=1, value=4)
            
            submitted = st.form_submit_button("Add Game", use_container_width=True)
            
            if submitted:
                game_data = {
                    "title": title,
                    "description": description,
                    "genre": genre,
                    "platforms": platforms,
                    "rating": rating,
                    "release_date": release_date.isoformat(),
                    "min_players": min_players,
                    "max_players": max_players
                }
                
                result = make_request("POST", "/games", data=game_data)
                if result:
                    st.success(f"✅ Game '{title}' added successfully!")


# ==================== LEADERBOARDS ====================
def show_leaderboards():
    """Display leaderboards"""
    st.title("🏆 Leaderboards")
    
    tab1, tab2 = st.tabs(["View Leaderboards", "Global Stats"])
    
    with tab1:
        st.subheader("Game Leaderboards")
        
        games = make_request("GET", "/games", params={"limit": 100})
        if games:
            game_options = {g.get("title", "Unknown"): str(g.get("_id", "")) for g in games}
            selected_game = st.selectbox("Select Game", list(game_options.keys()))
            
            if selected_game:
                game_id = game_options[selected_game]
                leaderboard = make_request("GET", f"/leaderboards/game/{game_id}")
                
                if leaderboard:
                    entries = leaderboard.get("entries", [])
                    if entries:
                        # Convert to DataFrame
                        lb_data = []
                        for i, entry in enumerate(entries[:50], 1):
                            lb_data.append({
                                "Rank": i,
                                "Player": entry.get("player_id", "Unknown"),
                                "Score": entry.get("score", 0),
                                "Wins": entry.get("wins", 0),
                                "Level": entry.get("level", 0)
                            })
                        
                        df_lb = pd.DataFrame(lb_data)
                        st.dataframe(df_lb, use_container_width=True)
                        
                        # Visualization
                        if len(df_lb) > 0:
                            fig = px.bar(df_lb.head(20), x="Player", y="Score", title=f"Top Players in {selected_game}")
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No leaderboard entries yet for this game")
                else:
                    st.info("No leaderboard data available yet")
    
    with tab2:
        st.subheader("Global Statistics")
        
        all_players = make_request("GET", "/players", params={"limit": 100})
        if all_players:
            # Calculate stats
            total_matches = sum(p.get("total_matches", 0) for p in all_players)
            total_wins = sum(p.get("total_wins", 0) for p in all_players)
            avg_level = sum(p.get("level", 0) for p in all_players) / len(all_players) if all_players else 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Matches Played", total_matches)
            with col2:
                st.metric("Total Wins", total_wins)
            with col3:
                st.metric("Avg Player Level", f"{avg_level:.1f}")
            
            # Level distribution
            levels = [p.get("level", 0) for p in all_players]
            fig = px.histogram(levels, nbins=20, title="Player Level Distribution", labels={"value": "Level"})
            st.plotly_chart(fig, use_container_width=True)


# ==================== ACHIEVEMENTS ====================
def show_achievements():
    """Display achievements"""
    st.title("🎖️ Achievements")
    
    tab1, tab2 = st.tabs(["View Achievements", "Unlock Achievement"])
    
    with tab1:
        st.subheader("Available Achievements")
        
        games = make_request("GET", "/games", params={"limit": 100})
        
        if games:
            game_options = {g.get("title", "Unknown"): str(g.get("_id", "")) for g in games}
            selected_game = st.selectbox("Select Game", list(game_options.keys()), key="ach_game_select")
            
            if selected_game:
                game_id = game_options[selected_game]
                achievements = make_request("GET", f"/achievements/game/{game_id}")
                
                if achievements:
                    for achievement in achievements[:20]:
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.subheader(achievement.get("name", "Unknown"))
                            st.write(achievement.get("description", ""))
                        with col2:
                            st.metric("Points", achievement.get("points", 0))
                        with col3:
                            st.metric("Rarity", achievement.get("rarity", "N/A"))
                        st.divider()
                else:
                    st.info("No achievements available for this game yet")
        else:
            st.info("No games available yet")
    
    with tab2:
        st.subheader("Award Achievement to Player")
        
        all_players = make_request("GET", "/players", params={"limit": 100})
        games = make_request("GET", "/games", params={"limit": 100})
        
        if all_players and games:
            col1, col2 = st.columns([1, 1])
            with col1:
                selected_player = st.selectbox(
                    "Select Player",
                    [p.get("username", "") for p in all_players],
                    key="ach_player"
                )
            with col2:
                game_options = {g.get("title", "Unknown"): str(g.get("_id", "")) for g in games}
                selected_game = st.selectbox(
                    "Select Game",
                    list(game_options.keys()),
                    key="ach_game"
                )
            
            if selected_player and selected_game:
                game_id = game_options[selected_game]
                achievements = make_request("GET", f"/achievements/game/{game_id}")
                
                if achievements:
                    selected_achievement = st.selectbox(
                        "Select Achievement",
                        [a.get("name", "") for a in achievements],
                        key="ach_select"
                    )
                    
                    if st.button("Award Achievement", use_container_width=True):
                        player = next((p for p in all_players if p.get("username") == selected_player), None)
                        achievement = next((a for a in achievements if a.get("name") == selected_achievement), None)
                        
                        if player and achievement:
                            data = {
                                "player_id": str(player.get("_id", "")),
                                "achievement_id": str(achievement.get("_id", ""))
                            }
                            
                            result = make_request("POST", "/player-achievements", data=data)
                            if result:
                                st.success(f"✅ Achievement '{selected_achievement}' awarded to {selected_player}!")
                else:
                    st.warning("No achievements available for this game")
        else:
            st.warning("No players or games available")


# ==================== MATCHES ====================
def show_matches():
    """Display match history"""
    st.title("⚔️ Match History")
    
    st.subheader("Recent Matches")
    
    # Filter options
    all_players = make_request("GET", "/players", params={"limit": 100})
    
    if all_players:
        filter_type = st.radio("Filter by:", ["Player", "All Players"])
        
        if filter_type == "Player":
            selected_player = st.selectbox(
                "Select Player",
                [p.get("username", "") for p in all_players],
                key="match_player"
            )
            
            player = next((p for p in all_players if p.get("username") == selected_player), None)
            if player:
                player_id = str(player.get("_id", ""))
                matches = make_request("GET", f"/matches/player/{player_id}")
                
                if matches:
                    match_data = []
                    for match in matches[:20]:
                        match_data.append({
                            "Date": match.get("match_date", "N/A"),
                            "Game": match.get("game_id", "N/A"),
                            "Winner": match.get("winner_id", "N/A"),
                            "Points": match.get("winning_points", 0),
                            "Duration": f"{match.get('match_duration_seconds', 0) // 60} min"
                        })
                    
                    if match_data:
                        df = pd.DataFrame(match_data)
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.info("No match data available yet")
                else:
                    st.info(f"No matches found for {selected_player}")
        else:
            st.info("Showing all recent matches - select a player to see specific match history")
            # Get matches for multiple players
            all_matches = []
            for player in all_players[:5]:  # Limit to first 5 players
                player_id = str(player.get("_id", ""))
                matches = make_request("GET", f"/matches/player/{player_id}")
                if matches:
                    all_matches.extend(matches[:5])
            
            if all_matches:
                match_data = []
                for match in all_matches[:20]:
                    match_data.append({
                        "Player": match.get("player_id", "N/A"),
                        "Date": match.get("match_date", "N/A"),
                        "Game": match.get("game_id", "N/A"),
                        "Winner": match.get("winner_id", "N/A"),
                        "Points": match.get("winning_points", 0)
                    })
                
                df = pd.DataFrame(match_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No match data available yet")
    else:
        st.warning("No players available")


# ==================== SOCIAL ====================
def show_social():
    """Display social features"""
    st.title("👫 Social Features")
    
    tab1, tab2, tab3 = st.tabs(["Friends", "Messaging", "Clans"])
    
    with tab1:
        st.subheader("Friend Management")
        
        all_players = make_request("GET", "/players", params={"limit": 100})
        if all_players:
            col1, col2 = st.columns(2)
            with col1:
                player1 = st.selectbox(
                    "Select Player",
                    [p.get("username", "") for p in all_players],
                    key="friend_player1"
                )
            with col2:
                player2 = st.selectbox(
                    "Add as Friend",
                    [p.get("username", "") for p in all_players if p.get("username") != player1],
                    key="friend_player2"
                )
            
            if st.button("Add Friend", use_container_width=True):
                p1 = next((p for p in all_players if p.get("username") == player1), None)
                p2 = next((p for p in all_players if p.get("username") == player2), None)
                
                if p1 and p2:
                    data = {
                        "player1_id": str(p1.get("_id", "")),
                        "player2_id": str(p2.get("_id", ""))
                    }
                    
                    result = make_request("POST", "/friends", data=data)
                    if result:
                        st.success(f"✅ {player2} added as friend!")
    
    with tab2:
        st.subheader("Send Message")
        
        all_players = make_request("GET", "/players", params={"limit": 100})
        if all_players:
            col1, col2 = st.columns(2)
            with col1:
                sender = st.selectbox(
                    "From Player",
                    [p.get("username", "") for p in all_players],
                    key="msg_sender"
                )
            with col2:
                recipient = st.selectbox(
                    "To Player",
                    [p.get("username", "") for p in all_players if p.get("username") != sender],
                    key="msg_recipient"
                )
            
            message = st.text_area("Message", placeholder="Enter your message", height=100)
            
            if st.button("Send Message", use_container_width=True):
                sender_p = next((p for p in all_players if p.get("username") == sender), None)
                recipient_p = next((p for p in all_players if p.get("username") == recipient), None)
                
                if sender_p and recipient_p and message:
                    data = {
                        "sender_id": str(sender_p.get("_id", "")),
                        "receiver_id": str(recipient_p.get("_id", "")),
                        "content": message
                    }
                    
                    result = make_request("POST", "/messages", data=data)
                    if result:
                        st.success(f"✅ Message sent to {recipient}!")
    
    with tab3:
        st.subheader("Clan Management")
        st.info("Clan features will be implemented in the next update!")


# ==================== MAIN APP ====================
def main():
    """Main app logic"""
    # Sidebar navigation
    st.sidebar.title("🎮 Gaming System")
    
    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Players", "Games", "Leaderboards", "Achievements", "Matches", "Social"]
    )
    
    st.sidebar.divider()
    st.sidebar.info(
        "**Multiplayer Gaming System**\n\n"
        "A comprehensive platform for managing multiplayer games, "
        "players, achievements, and social interactions.\n\n"
        "📌 Make sure the FastAPI server is running!"
    )
    
    # Route to pages
    if page == "Dashboard":
        show_dashboard()
    elif page == "Players":
        show_players()
    elif page == "Games":
        show_games()
    elif page == "Leaderboards":
        show_leaderboards()
    elif page == "Achievements":
        show_achievements()
    elif page == "Matches":
        show_matches()
    elif page == "Social":
        show_social()


if __name__ == "__main__":
    main()
