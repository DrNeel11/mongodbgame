"""
Multiplayer Gaming System - Streamlit Frontend
"""

import os
from dotenv import load_dotenv
import streamlit as st
import requests
try:
    import pandas as pd
except Exception:
    pd = None
try:
    import plotly.express as px
    import plotly.graph_objects as go
except Exception:
    px = None
    go = None
from datetime import datetime
from typing import List, Dict, Optional
import json

# Configuration
load_dotenv()
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

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

# Compatibility wrappers for environments without pandas/plotly
_original_st_dataframe = st.dataframe
def _safe_dataframe(data, *args, **kwargs):
    if pd is not None:
        try:
            return _original_st_dataframe(data, *args, **kwargs)
        except Exception:
            pass
    if isinstance(data, (list, tuple)):
        st.table(data)
    else:
        try:
            st.write(data)
        except Exception:
            pass
st.dataframe = _safe_dataframe

_original_plotly_chart = st.plotly_chart
def _safe_plotly_chart(fig, *args, **kwargs):
    if px is not None and go is not None:
        try:
            return _original_plotly_chart(fig, *args, **kwargs)
        except Exception:
            pass
    st.info("Plot unavailable (plotly not installed)")
st.plotly_chart = _safe_plotly_chart

# Helper functions
def make_request(method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None, show_error: bool = True):
    """Make API request with error handling"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, params=params, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, params=params, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=data, params=params, timeout=10)
        elif method == "PATCH":
            response = requests.patch(url, json=data, params=params, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, params=params, timeout=10)
        else:
            return None
            
        response.raise_for_status()
        return response.json() if response.content else None
    except requests.exceptions.ConnectionError:
        if show_error:
            st.error("❌ Cannot connect to API. Make sure the server is running on http://localhost:8000")
        return None
    except requests.exceptions.HTTPError as e:
        if show_error:
            try:
                error_detail = e.response.json().get("detail", e.response.text)
            except:
                error_detail = e.response.text
            st.error(f"❌ API Error: {e.response.status_code} - {error_detail}")
        return None
    except Exception as e:
        if show_error:
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
            
            # Platform mapping
            platform_display = ["PC", "PlayStation", "Xbox", "Mobile", "Nintendo"]
            platform_api = ["pc", "playstation", "xbox", "mobile", "nintendo"]
            platform_map = dict(zip(platform_display, platform_api))
            
            platforms = st.multiselect(
                "Preferred Platforms",
                platform_display,
                default=["PC"]
            )
            bio = st.text_area("Bio", placeholder="Enter player bio (optional)", height=100)
            
            submitted = st.form_submit_button("Create Player", use_container_width=True)
            
            if submitted:
                if not username or not email:
                    st.error("Username and email are required!")
                else:
                    # Convert platform names to API format
                    api_platforms = [platform_map[p] for p in platforms]
                    
                    player_data = {
                        "username": username,
                        "email": email,
                        "level": level,
                        "platforms": api_platforms,
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
                        st.caption(f"Publisher: {game.get('publisher', 'N/A')}")
                    with col2:
                        st.metric("Max Players", game.get("max_players", "N/A"))
                    with col3:
                        crossplay_status = "✅ Yes" if game.get("crossplay_enabled") else "❌ No"
                        st.metric("Crossplay", crossplay_status)
                    
                    col_a, col_b = st.columns([1, 1])
                    with col_a:
                        genres = game.get("genres", [])
                        st.caption(f"Genres: {', '.join(genres) if genres else 'N/A'}")
                    with col_b:
                        platforms = game.get("platforms", [])
                        st.caption(f"Platforms: {', '.join(platforms) if platforms else 'N/A'}")
                    st.divider()
        else:
            st.warning("No games found")
    
    with tab2:
        st.subheader("Add New Game")
        
        with st.form("add_game_form"):
            title = st.text_input("Game Title", placeholder="Enter game name")
            publisher = st.text_input("Publisher", placeholder="Enter game publisher")
            
            # Genre/Genres as multiselect
            genres = st.multiselect(
                "Genres",
                ["Action", "RPG", "Strategy", "Sports", "Puzzle", "Other"],
                default=["Action"]
            )
            
            # Platform mapping
            platform_display = ["PC", "PlayStation", "Xbox", "Mobile", "Nintendo", "VR"]
            platform_api = ["pc", "playstation", "xbox", "mobile", "nintendo", "vr"]
            platform_map = dict(zip(platform_display, platform_api))
            
            platforms = st.multiselect(
                "Platforms",
                platform_display,
                default=["PC"]
            )
            
            crossplay = st.checkbox("Enable Crossplay", value=True)
            max_players = st.number_input("Max Players", min_value=1, value=4)
            
            submitted = st.form_submit_button("Add Game", use_container_width=True)
            
            if submitted:
                if not title or not publisher or not genres or not platforms:
                    st.error("Title, Publisher, Genres, and Platforms are required!")
                else:
                    # Convert platform names to API format
                    api_platforms = [platform_map[p] for p in platforms]
                    
                    game_data = {
                        "title": title,
                        "publisher": publisher,
                        "genres": genres,
                        "platforms": api_platforms,
                        "crossplay_enabled": crossplay,
                        "max_players": max_players
                    }
                    
                    result = make_request("POST", "/games", data=game_data)
                    if result:
                        st.success(f"✅ Game '{title}' added successfully!")


# ==================== LEADERBOARDS ====================
def show_leaderboards():
    """Display leaderboards"""
    st.title("🏆 Leaderboards")
    
    tab1, tab2, tab3 = st.tabs(["View Leaderboards", "Create Leaderboard", "Global Stats"])
    
    with tab1:
        st.subheader("Game Leaderboards")
        
        # Add refresh button
        col_refresh = st.columns([10, 1])[1]
        with col_refresh:
            if st.button("🔄 Refresh", use_container_width=True, key="refresh_lb"):
                st.rerun()
        
        games = make_request("GET", "/games", params={"limit": 100})
        if games:
            game_options = {g.get("title", "Unknown"): str(g.get("_id", "")) for g in games}
            selected_game = st.selectbox("Select Game", list(game_options.keys()), key="view_lb_game")
            
            if selected_game:
                game_id = game_options[selected_game]
                
                # Add type and timeframe selectors
                col1, col2 = st.columns(2)
                with col1:
                    leaderboard_type = st.selectbox(
                        "Leaderboard Type",
                        ["Wins", "Kills", "XP", "Score", "Playtime"],
                        key="view_lb_type"
                    )
                with col2:
                    timeframe = st.selectbox(
                        "Timeframe",
                        ["All Time", "Monthly", "Weekly", "Daily"],
                        key="view_lb_timeframe"
                    )
                
                # Convert to API format
                type_map = {
                    "Wins": "wins",
                    "Kills": "kills",
                    "XP": "xp",
                    "Score": "score",
                    "Playtime": "playtime"
                }
                timeframe_map = {
                    "All Time": "all_time",
                    "Monthly": "monthly",
                    "Weekly": "weekly",
                    "Daily": "daily"
                }
                
                api_type = type_map[leaderboard_type]
                api_timeframe = timeframe_map[timeframe]
                
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
                        st.info("No entries yet in this leaderboard. Create entries by promoting player scores!")
                else:
                    st.warning(f"❌ No leaderboard exists for {selected_game}")
                    st.info("💡 Go to 'Create Leaderboard' tab to create one for this game!")
        else:
            st.info("No games available yet")
    
    with tab2:
        st.subheader("Create New Leaderboard")
        
        games = make_request("GET", "/games", params={"limit": 100})
        if games:
            game_options = {g.get("title", "Unknown"): str(g.get("_id", "")) for g in games}
            selected_game = st.selectbox("Select Game for Leaderboard", list(game_options.keys()), key="create_lb_game")
            
            col1, col2 = st.columns(2)
            with col1:
                leaderboard_type = st.selectbox(
                    "Leaderboard Type",
                    ["Wins", "Kills", "XP", "Score", "Playtime"],
                    key="lb_type"
                )
            with col2:
                timeframe = st.selectbox(
                    "Timeframe",
                    ["All Time", "Monthly", "Weekly", "Daily"],
                    key="lb_timeframe"
                )
            
            if st.button("Create Leaderboard", use_container_width=True):
                if selected_game:
                    game_id = game_options[selected_game]
                    
                    # Convert friendly names to API format
                    type_map = {
                        "Wins": "wins",
                        "Kills": "kills",
                        "XP": "xp",
                        "Score": "score",
                        "Playtime": "playtime"
                    }
                    timeframe_map = {
                        "All Time": "all_time",
                        "Monthly": "monthly",
                        "Weekly": "weekly",
                        "Daily": "daily"
                    }
                    
                    lb_data = {
                        "game_id": game_id,
                        "leaderboard_type": type_map[leaderboard_type],
                        "timeframe": timeframe_map[timeframe]
                    }
                    
                    result = make_request("POST", "/leaderboards", data=lb_data)
                    if result:
                        st.success(f"✅ Leaderboard created for '{selected_game}'!")
                        st.info(f"Type: {leaderboard_type} | Timeframe: {timeframe}")
                    else:
                        st.error("Failed to create leaderboard. It might already exist.")
        else:
            st.warning("No games available yet")
    
    with tab3:
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
                        # Duration in seconds from API, convert to minutes
                        duration_minutes = match.get('duration', 0) // 60 if match.get('duration') else 0
                        
                        match_data.append({
                            "Date": match.get("timestamp", "N/A"),
                            "Game": match.get("game_id", "N/A"),
                            "Mode": match.get("game_mode", "N/A"),
                            "Map": match.get("map_name", "N/A"),
                            "Winner": match.get("winner_player_id", "N/A"),
                            "Duration": f"{duration_minutes} min"
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
                    duration_minutes = match.get('duration', 0) // 60 if match.get('duration') else 0
                    
                    match_data.append({
                        "Player": match.get("player_id", "N/A"),
                        "Date": match.get("timestamp", "N/A"),
                        "Game": match.get("game_id", "N/A"),
                        "Mode": match.get("game_mode", "N/A"),
                        "Winner": match.get("winner_player_id", "N/A"),
                        "Duration": f"{duration_minutes} min"
                    })
                
                df = pd.DataFrame(match_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No match data available yet")
    else:
        st.warning("No players available")


# ==================== SOCIAL ====================

# ==================== PLAYER STATS ====================
def show_stats():
    """Display and manage player stats"""
    st.title("📊 Player Stats")
    
    tab1, tab2, tab3 = st.tabs(["View Stats", "Create Stats", "Update Stats"])
    
    all_players = make_request("GET", "/players", params={"limit": 100})
    all_games = make_request("GET", "/games", params={"limit": 100})
    
    with tab1:
        st.subheader("View Player Stats")
        
        if all_players:
            selected_player = st.selectbox("Select Player", [p.get("username", "") for p in all_players], key="view_stats_player")
            player = next((p for p in all_players if p.get("username") == selected_player), None)
            
            if player:
                player_id = str(player.get("_id", ""))
                stats_list = make_request("GET", f"/stats/{player_id}")
                
                if stats_list:
                    st.dataframe(pd.DataFrame(stats_list), use_container_width=True)
                else:
                    st.info("No stats found for this player")
    
    with tab2:
        st.subheader("Create Player Stats")
        
        if all_players and all_games:
            col1, col2 = st.columns(2)
            with col1:
                selected_player = st.selectbox("Select Player", [p.get("username", "") for p in all_players], key="create_stats_player")
            with col2:
                selected_game = st.selectbox("Select Game", [g.get("title", "") for g in all_games], key="create_stats_game")
            
            if st.button("Create Stats", use_container_width=True):
                player = next((p for p in all_players if p.get("username") == selected_player), None)
                game = next((g for g in all_games if g.get("title") == selected_game), None)
                
                if player and game:
                    data = {
                        "player_id": str(player.get("_id", "")),
                        "game_id": str(game.get("_id", ""))
                    }
                    result = make_request("POST", "/stats", data=data)
                    if result:
                        st.success(f"✅ Stats created for {selected_player} in {selected_game}!")
                    else:
                        st.error("Failed to create stats (might already exist)")
    
    with tab3:
        st.subheader("Update Player Stats")
        
        if all_players and all_games:
            col1, col2 = st.columns(2)
            with col1:
                selected_player = st.selectbox("Select Player", [p.get("username", "") for p in all_players], key="update_stats_player")
            with col2:
                selected_game = st.selectbox("Select Game", [g.get("title", "") for g in all_games], key="update_stats_game")
            
            player = next((p for p in all_players if p.get("username") == selected_player), None)
            game = next((g for g in all_games if g.get("title") == selected_game), None)
            
            if player and game:
                st.divider()
                col_w, col_l, col_k, col_d = st.columns(4)
                with col_w:
                    wins = st.number_input("Wins to add", min_value=0, value=0)
                with col_l:
                    losses = st.number_input("Losses to add", min_value=0, value=0)
                with col_k:
                    kills = st.number_input("Kills to add", min_value=0, value=0)
                with col_d:
                    deaths = st.number_input("Deaths to add", min_value=0, value=0)
                
                col_x, col_lv = st.columns(2)
                with col_x:
                    xp = st.number_input("XP to add", min_value=0, value=0)
                with col_lv:
                    level = st.number_input("Level", min_value=1, value=1)
                
                if st.button("Update Stats", use_container_width=True):
                    player_id = str(player.get("_id", ""))
                    game_id = str(game.get("_id", ""))
                    
                    data = {
                        "wins": wins if wins > 0 else None,
                        "losses": losses if losses > 0 else None,
                        "kills": kills if kills > 0 else None,
                        "deaths": deaths if deaths > 0 else None,
                        "xp": xp if xp > 0 else None,
                        "level": level
                    }
                    data = {k: v for k, v in data.items() if v is not None}
                    
                    result = make_request("PATCH", f"/stats/{player_id}/{game_id}", data=data)
                    if result:
                        st.success(f"✅ Stats updated for {selected_player}!")


# ==================== ADMIN PANEL ====================
def show_admin_panel():
    """Admin panel with all CRUD operations"""
    st.title("⚙️ Admin Panel - CRUD Operations")
    
    st.info("🔧 Complete CRUD operations for all entities")
    
    tabs = st.tabs([
        "Players", "Games", "Achievements", "Leaderboards",
        "Matches", "Sessions", "Notifications", "Inventory"
    ])
    
    with tabs[0]:  # Players
        st.subheader("Player Management")
        sub_tabs = st.tabs(["View All", "View One", "Update", "Delete", "Login"])
        
        all_players = make_request("GET", "/players", params={"limit": 100})
        
        with sub_tabs[0]:
            if all_players:
                st.dataframe(pd.DataFrame([{
                    "Username": p.get("username"),
                    "Level": p.get("level"),
                    "Wins": p.get("total_wins"),
                    "Losses": p.get("total_losses"),
                    "Online": p.get("is_online")
                } for p in all_players]), use_container_width=True)
        
        with sub_tabs[1]:
            if all_players:
                selected = st.selectbox("Select Player", [p.get("username") for p in all_players], key="admin_view_player")
                player = next((p for p in all_players if p.get("username") == selected), None)
                if player:
                    st.json({k: v for k, v in player.items()})
        
        with sub_tabs[2]:
            if all_players:
                selected = st.selectbox("Select Player to Update", [p.get("username") for p in all_players], key="admin_update_player")
                player = next((p for p in all_players if p.get("username") == selected), None)
                
                if player:
                    col1, col2 = st.columns(2)
                    with col1:
                        new_level = st.number_input("New Level", min_value=1, max_value=100, value=player.get("level", 1))
                    with col2:
                        is_online = st.checkbox("Online Status", value=player.get("is_online", False))
                    
                    if st.button("Update Player", key="update_player_btn"):
                        data = {"level": new_level, "is_online": is_online}
                        result = make_request("PUT", f"/players/{str(player.get('_id'))}", data=data)
                        if result:
                            st.success("✅ Player updated!")
        
        with sub_tabs[3]:
            if all_players:
                selected = st.selectbox("Select Player to Delete", [p.get("username") for p in all_players], key="admin_delete_player")
                player = next((p for p in all_players if p.get("username") == selected), None)
                
                if player:
                    if st.button("🗑️ Delete Player", key="delete_player_btn", type="secondary"):
                        result = make_request("DELETE", f"/players/{str(player.get('_id'))}")
                        if result:
                            st.success("✅ Player deleted!")
                            st.rerun()
        
        with sub_tabs[4]:
            if all_players:
                selected = st.selectbox("Select Player to Login", [p.get("username") for p in all_players], key="admin_login_player")
                player = next((p for p in all_players if p.get("username") == selected), None)
                
                if player:
                    if st.button("📍 Record Login", key="login_btn"):
                        result = make_request("POST", f"/players/{str(player.get('_id'))}/login")
                        if result:
                            st.success("✅ Login recorded!")
    
    with tabs[1]:  # Games
        st.subheader("Game Management")
        sub_tabs = st.tabs(["View All", "View One", "Update", "Delete"])
        
        all_games = make_request("GET", "/games", params={"limit": 100})
        
        with sub_tabs[0]:
            if all_games:
                st.dataframe(pd.DataFrame([{
                    "Title": g.get("title"),
                    "Publisher": g.get("publisher"),
                    "Max Players": g.get("max_players"),
                    "Crossplay": g.get("crossplay_enabled"),
                    "Genres": ", ".join(g.get("genres", []))
                } for g in all_games]), use_container_width=True)
        
        with sub_tabs[1]:
            if all_games:
                selected = st.selectbox("Select Game", [g.get("title") for g in all_games], key="admin_view_game")
                game = next((g for g in all_games if g.get("title") == selected), None)
                if game:
                    st.json({k: v for k, v in game.items() if k != "_id"})
        
        with sub_tabs[2]:
            if all_games:
                selected = st.selectbox("Select Game to Update", [g.get("title") for g in all_games], key="admin_update_game")
                game = next((g for g in all_games if g.get("title") == selected), None)
                
                if game:
                    new_max_players = st.number_input("Max Players", min_value=1, value=game.get("max_players", 4))
                    crossplay = st.checkbox("Crossplay Enabled", value=game.get("crossplay_enabled", True))
                    
                    if st.button("Update Game", key="update_game_btn"):
                        data = {"max_players": new_max_players, "crossplay_enabled": crossplay}
                        result = make_request("PUT", f"/games/{str(game.get('_id'))}", data=data)
                        if result:
                            st.success("✅ Game updated!")
        
        with sub_tabs[3]:
            if all_games:
                selected = st.selectbox("Select Game to Delete", [g.get("title") for g in all_games], key="admin_delete_game")
                game = next((g for g in all_games if g.get("title") == selected), None)
                
                if game:
                    if st.button("🗑️ Delete Game", key="delete_game_btn", type="secondary"):
                        result = make_request("DELETE", f"/games/{str(game.get('_id'))}")
                        if result:
                            st.success("✅ Game deleted!")
                            st.rerun()
    
    with tabs[2]:  # Achievements
        st.subheader("Achievement Management")
        
        all_games = make_request("GET", "/games", params={"limit": 100})
        
        if all_games:
            selected_game = st.selectbox("Select Game", [g.get("title") for g in all_games], key="admin_ach_game")
            game = next((g for g in all_games if g.get("title") == selected_game), None)
            
            if game:
                game_id = str(game.get("_id"))
                
                # Achievement sub-tabs
                ach_tabs = st.tabs(["View All", "Create New", "Update", "Delete"])
                
                # View All achievements
                with ach_tabs[0]:
                    achievements = make_request("GET", f"/achievements/game/{game_id}")
                    
                    if achievements:
                        st.write(f"**Total Achievements:** {len(achievements)}")
                        
                        for ach in achievements[:20]:
                            with st.expander(f"📌 {ach.get('name')}"):
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.caption(f"**Description:** {ach.get('description', 'N/A')}")
                                with col2:
                                    st.caption(f"**XP Reward:** {ach.get('xp_reward', 0)}")
                                with col3:
                                    st.caption(f"**Rarity:** {ach.get('rarity', 'N/A')}")
                                with col4:
                                    st.caption(f"**ID:** {str(ach.get('_id', 'N/A'))[:8]}...")
                    else:
                        st.info("No achievements yet for this game")
                
                # Create new achievement
                with ach_tabs[1]:
                    st.subheader("Create New Achievement")
                    
                    with st.form("create_achievement_form"):
                        name = st.text_input("Achievement Name", placeholder="e.g., First Blood")
                        description = st.text_area("Description", placeholder="Describe the achievement", height=80)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            xp_reward = st.number_input("XP Reward", min_value=0, max_value=10000, value=100)
                        with col2:
                            rarity = st.selectbox("Rarity", ["Common", "Rare", "Epic", "Legendary"])
                        with col3:
                            unlock_condition = st.text_input("Unlock Condition", placeholder="e.g., Get 5 kills")
                        
                        submitted = st.form_submit_button("✅ Create Achievement", use_container_width=True)
                        
                        if submitted:
                            if not name or not description:
                                st.error("Name and Description are required!")
                            else:
                                ach_data = {
                                    "game_id": game_id,
                                    "name": name,
                                    "description": description,
                                    "xp_reward": xp_reward,
                                    "rarity": rarity.lower(),
                                    "unlock_condition": unlock_condition if unlock_condition else None
                                }
                                
                                result = make_request("POST", "/achievements", data=ach_data)
                                if result:
                                    st.success(f"✅ Achievement '{name}' created!")
                                    st.rerun()
                                else:
                                    st.error("Failed to create achievement")
                
                # Update achievement
                with ach_tabs[2]:
                    st.subheader("Update Achievement")
                    
                    achievements = make_request("GET", f"/achievements/game/{game_id}")
                    if achievements:
                        selected_ach = st.selectbox(
                            "Select Achievement to Update",
                            [a.get("name") for a in achievements],
                            key="update_ach_select"
                        )
                        
                        achievement = next((a for a in achievements if a.get("name") == selected_ach), None)
                        if achievement:
                            with st.form("update_achievement_form"):
                                name = st.text_input("Achievement Name", value=achievement.get("name", ""))
                                description = st.text_area("Description", value=achievement.get("description", ""), height=80)
                                
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    xp_reward = st.number_input(
                                        "XP Reward",
                                        min_value=0,
                                        max_value=10000,
                                        value=achievement.get("xp_reward", 100)
                                    )
                                with col2:
                                    current_rarity = achievement.get("rarity", "common").capitalize()
                                    rarity = st.selectbox("Rarity", ["Common", "Rare", "Epic", "Legendary"], index=["Common", "Rare", "Epic", "Legendary"].index(current_rarity) if current_rarity in ["Common", "Rare", "Epic", "Legendary"] else 0)
                                with col3:
                                    unlock_condition = st.text_input("Unlock Condition", value=achievement.get("unlock_condition", ""))
                                
                                submitted = st.form_submit_button("✅ Update Achievement", use_container_width=True)
                                
                                if submitted:
                                    ach_id = str(achievement.get("_id"))
                                    ach_data = {
                                        "name": name,
                                        "description": description,
                                        "xp_reward": xp_reward,
                                        "rarity": rarity.lower(),
                                        "unlock_condition": unlock_condition if unlock_condition else None
                                    }
                                    
                                    result = make_request("PUT", f"/achievements/{ach_id}", data=ach_data)
                                    if result:
                                        st.success(f"✅ Achievement updated!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to update achievement")
                    else:
                        st.info("No achievements to update")
                
                # Delete achievement
                with ach_tabs[3]:
                    st.subheader("Delete Achievement")
                    
                    achievements = make_request("GET", f"/achievements/game/{game_id}")
                    if achievements:
                        selected_ach = st.selectbox(
                            "Select Achievement to Delete",
                            [a.get("name") for a in achievements],
                            key="delete_ach_select"
                        )
                        
                        achievement = next((a for a in achievements if a.get("name") == selected_ach), None)
                        if achievement:
                            st.warning(f"⚠️ This will permanently delete '{selected_ach}'")
                            
                            if st.button("🗑️ Delete Achievement", type="secondary", use_container_width=True):
                                ach_id = str(achievement.get("_id"))
                                result = make_request("DELETE", f"/achievements/{ach_id}")
                                if result:
                                    st.success("✅ Achievement deleted!")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete achievement")
                    else:
                        st.info("No achievements to delete")
    
    with tabs[3]:  # Leaderboards
        st.subheader("Leaderboard Management")
        
        all_games = make_request("GET", "/games", params={"limit": 100})
        if all_games:
            selected_game = st.selectbox("Select Game", [g.get("title") for g in all_games], key="admin_lb_game")
            game = next((g for g in all_games if g.get("title") == selected_game), None)
            
            if game:
                game_id = str(game.get("_id"))
                
                # Leaderboard sub-tabs
                lb_tabs = st.tabs(["View & Filter", "Create New", "Add Entries", "Delete"])
                
                # View & Filter leaderboards
                with lb_tabs[0]:
                    st.subheader("View Leaderboard")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        view_type = st.selectbox(
                            "Leaderboard Type",
                            ["Wins", "Kills", "XP", "Score", "Playtime"],
                            key="view_lb_type"
                        )
                    with col2:
                        view_timeframe = st.selectbox(
                            "Timeframe",
                            ["All Time", "Monthly", "Weekly", "Daily"],
                            key="view_lb_timeframe"
                        )
                    
                    if st.button("🔍 View Leaderboard", use_container_width=True, key="view_lb_btn"):
                        type_map = {"Wins": "wins", "Kills": "kills", "XP": "xp", "Score": "score", "Playtime": "playtime"}
                        timeframe_map = {"All Time": "all_time", "Monthly": "monthly", "Weekly": "weekly", "Daily": "daily"}
                        
                        params = {
                            "git _type": type_map[view_type],
                            "timeframe": timeframe_map[view_timeframe]
                        }
                        
                        lb = make_request("GET", f"/leaderboards/game/{game_id}", params=params, show_error=False)
                        
                        if lb:
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Type", lb.get('leaderboard_type', 'N/A'))
                            with col2:
                                st.metric("Timeframe", lb.get('timeframe', 'N/A'))
                            with col3:
                                st.metric("Entries", len(lb.get('entries', [])))
                            
                            entries = lb.get('entries', [])
                            if entries:
                                df_lb = pd.DataFrame([{
                                    "Rank": i + 1,
                                    "Player ID": e.get("player_id", "N/A"),
                                    "Score": e.get("score", 0),
                                    "Wins": e.get("wins", 0),
                                    "Level": e.get("level", 0)
                                } for i, e in enumerate(entries[:50])])
                                st.dataframe(df_lb, use_container_width=True)
                            else:
                                st.info("No entries in this leaderboard yet")
                        else:
                            st.error(f"❌ Leaderboard not found for {view_type} ({view_timeframe}). Create it first!")
                
                # Create leaderboard
                with lb_tabs[1]:
                    st.subheader("Create New Leaderboard")
                    
                    st.info("📋 Each leaderboard has a fixed type and timeframe. Create one for each type/timeframe combination you need.")
                    
                    with st.form("create_leaderboard_form"):
                        col1, col2 = st.columns(2)
                        with col1:
                            lb_type = st.selectbox(
                                "Leaderboard Type",
                                ["Wins", "Kills", "XP", "Score", "Playtime"],
                                key="create_lb_type"
                            )
                        with col2:
                            timeframe = st.selectbox(
                                "Timeframe",
                                ["All Time", "Monthly", "Weekly", "Daily"],
                                key="create_lb_timeframe"
                            )
                        
                        submitted = st.form_submit_button("✅ Create Leaderboard", use_container_width=True)
                        
                        if submitted:
                            type_map = {"Wins": "wins", "Kills": "kills", "XP": "xp", "Score": "score", "Playtime": "playtime"}
                            timeframe_map = {"All Time": "all_time", "Monthly": "monthly", "Weekly": "weekly", "Daily": "daily"}
                            
                            lb_data = {
                                "game_id": game_id,
                                "leaderboard_type": type_map[lb_type],
                                "timeframe": timeframe_map[timeframe]
                            }
                            
                            with st.spinner("Creating leaderboard..."):
                                result = make_request("POST", "/leaderboards", data=lb_data)
                                if result:
                                    st.success(f"✅ Leaderboard created! Type: {lb_type}, Timeframe: {timeframe}")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to create leaderboard. It might already exist!")
                
                # Add/Update entries
                with lb_tabs[2]:
                    st.subheader("Add/Update Leaderboard Entry")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        entry_type = st.selectbox(
                            "Leaderboard Type",
                            ["Wins", "Kills", "XP", "Score", "Playtime"],
                            key="entry_lb_type"
                        )
                    with col2:
                        entry_timeframe = st.selectbox(
                            "Timeframe",
                            ["All Time", "Monthly", "Weekly", "Daily"],
                            key="entry_lb_timeframe"
                        )
                    
                    type_map = {"Wins": "wins", "Kills": "kills", "XP": "xp", "Score": "score", "Playtime": "playtime"}
                    timeframe_map = {"All Time": "all_time", "Monthly": "monthly", "Weekly": "weekly", "Daily": "daily"}
                    
                    params = {
                        "leaderboard_type": type_map[entry_type],
                        "timeframe": timeframe_map[entry_timeframe]
                    }
                    
                    lb = make_request("GET", f"/leaderboards/game/{game_id}", params=params, show_error=False)
                    
                    if lb:
                        lb_id = str(lb.get("_id"))
                        
                        with st.form("add_entry_form"):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                player_id = st.text_input("Player ID", placeholder="ObjectId")
                            with col2:
                                username = st.text_input("Username", placeholder="Player username")
                            with col3:
                                score = st.number_input("Score", min_value=0, value=0)
                            
                            submitted = st.form_submit_button("✅ Add/Update Entry", use_container_width=True)
                            
                            if submitted:
                                if not player_id or not username:
                                    st.error("Player ID and Username are required!")
                                else:
                                    result = make_request(
                                        "POST",
                                        f"/leaderboards/{lb_id}/entry",
                                        params={
                                            "player_id": str(player_id),
                                            "username": str(username),
                                            "score": str(score)
                                        }
                                    )
                                    if result:
                                        st.success("✅ Entry added/updated!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to add entry")
                    else:
                        st.error(f"❌ Leaderboard not found. Create it in the 'Create New' tab first!")
                
                # Delete leaderboard
                with lb_tabs[3]:
                    st.subheader("Delete Leaderboard")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        del_type = st.selectbox(
                            "Leaderboard Type",
                            ["Wins", "Kills", "XP", "Score", "Playtime"],
                            key="delete_lb_type"
                        )
                    with col2:
                        del_timeframe = st.selectbox(
                            "Timeframe",
                            ["All Time", "Monthly", "Weekly", "Daily"],
                            key="delete_lb_timeframe"
                        )
                    
                    type_map = {"Wins": "wins", "Kills": "kills", "XP": "xp", "Score": "score", "Playtime": "playtime"}
                    timeframe_map = {"All Time": "all_time", "Monthly": "monthly", "Weekly": "weekly", "Daily": "daily"}
                    
                    params = {
                        "leaderboard_type": type_map[del_type],
                        "timeframe": timeframe_map[del_timeframe]
                    }
                    
                    lb = make_request("GET", f"/leaderboards/game/{game_id}", params=params, show_error=False)
                    
                    if lb:
                        lb_id = str(lb.get("_id"))
                        
                        st.warning(f"⚠️ This will permanently delete the {del_type} ({del_timeframe}) leaderboard and all its entries")
                        
                        if st.button("🗑️ Delete Leaderboard", type="secondary", use_container_width=True):
                            result = make_request("DELETE", f"/leaderboards/{lb_id}")
                            if result:
                                st.success("✅ Leaderboard deleted!")
                                st.rerun()
                            else:
                                st.error("Failed to delete leaderboard")
                    else:
                        st.info("ℹ️ Leaderboard not found")
    
    with tabs[4]:  # Matches
        st.subheader("Match Management")
        
        all_players = make_request("GET", "/players", params={"limit": 100})
        all_games = make_request("GET", "/games", params={"limit": 100})
        
        if all_players:
            selected = st.selectbox("Select Player", [p.get("username") for p in all_players], key="admin_matches_player")
            player = next((p for p in all_players if p.get("username") == selected), None)
            
            if player:
                player_id = str(player.get('_id'))
                
                # Match sub-tabs
                match_tabs = st.tabs(["View All", "Create Match", "Delete"])
                
                # View All matches
                with match_tabs[0]:
                    matches = make_request("GET", f"/matches/player/{player_id}")
                    if matches:
                        match_data = []
                        for m in matches[:50]:
                            duration_minutes = m.get('duration', 0) // 60 if m.get('duration') else 0
                            match_data.append({
                                "Date": m.get("timestamp", "N/A"),
                                "Game": m.get("game_id", "N/A"),
                                "Mode": m.get("game_mode", "N/A"),
                                "Map": m.get("map_name", "N/A"),
                                "Winner": m.get("winner_player_id", "N/A"),
                                "Duration": f"{duration_minutes} min"
                            })
                        
                        df_matches = pd.DataFrame(match_data)
                        st.dataframe(df_matches, use_container_width=True)
                    else:
                        st.info("No matches found")
                
                # Create match
                with match_tabs[1]:
                    st.subheader("Create New Match")
                    
                    if all_games:
                        with st.form("create_match_form"):
                            col1, col2 = st.columns(2)
                            with col1:
                                selected_game = st.selectbox(
                                    "Select Game",
                                    [g.get("title", "") for g in all_games],
                                    key="create_match_game"
                                )
                            with col2:
                                game_mode = st.text_input("Game Mode", placeholder="e.g., TDM, Deathmatch")
                            
                            col3, col4 = st.columns(2)
                            with col3:
                                map_name = st.text_input("Map Name", placeholder="e.g., Nuketown")
                            with col4:
                                duration = st.number_input("Duration (seconds)", min_value=1, value=3600)
                            
                            winner_id = st.text_input("Winner Player ID (optional)", placeholder="Leave empty if no winner yet")
                            
                            submitted = st.form_submit_button("✅ Create Match", use_container_width=True)
                            
                            if submitted:
                                if not selected_game or not game_mode or not map_name:
                                    st.error("Game, Game Mode, and Map Name are required!")
                                else:
                                    game = next((g for g in all_games if g.get("title") == selected_game), None)
                                    if game:
                                        match_data = {
                                            "player_id": player_id,
                                            "game_id": str(game.get("_id")),
                                            "game_mode": game_mode,
                                            "map_name": map_name,
                                            "duration": duration,
                                            "winner_player_id": winner_id if winner_id else None
                                        }
                                        
                                        result = make_request("POST", "/matches", data=match_data)
                                        if result:
                                            st.success("✅ Match created!")
                                            st.rerun()
                                        else:
                                            st.error("Failed to create match")
                    else:
                        st.warning("No games available")
                
                # Delete match
                with match_tabs[2]:
                    st.subheader("Delete Match")
                    
                    matches = make_request("GET", f"/matches/player/{player_id}")
                    if matches:
                        match_options = {f"{m.get('timestamp', 'Unknown')} - {m.get('game_mode', 'N/A')}" : m for m in matches[:20]}
                        selected_match_key = st.selectbox(
                            "Select Match to Delete",
                            list(match_options.keys()),
                            key="delete_match_select"
                        )
                        
                        match_to_delete = match_options[selected_match_key]
                        match_id = str(match_to_delete.get("_id"))
                        
                        st.warning(f"⚠️ This will permanently delete this match record")
                        
                        if st.button("🗑️ Delete Match", type="secondary", use_container_width=True):
                            result = make_request("DELETE", f"/matches/{match_id}")
                            if result:
                                st.success("✅ Match deleted!")
                                st.rerun()
                            else:
                                st.error("Failed to delete match")
                    else:
                        st.info("No matches to delete")
    
    with tabs[5]:  # Sessions
        st.subheader("Game Session Management")
        
        all_players = make_request("GET", "/players", params={"limit": 100})
        all_games = make_request("GET", "/games", params={"limit": 100})
        
        if all_players:
            selected = st.selectbox("Select Player", [p.get("username") for p in all_players], key="admin_sessions_player")
            player = next((p for p in all_players if p.get("username") == selected), None)
            
            if player:
                player_id = str(player.get('_id'))
                
                # Session sub-tabs
                session_tabs = st.tabs(["View Active", "Create Session", "End Session"])
                
                # View Active Sessions
                with session_tabs[0]:
                    sessions = make_request("GET", f"/sessions/active/{player_id}", show_error=False)
                    if sessions:
                        session_data = []
                        for s in sessions[:50]:
                            session_data.append({
                                "Game": s.get("game_id", "N/A"),
                                "Started": s.get("started_at", "N/A"),
                                "Duration": f"{(s.get('duration', 0) // 60)}m" if s.get('duration') else "0m",
                                "Status": s.get("status", "active"),
                                "Level": s.get("level", 0)
                            })
                        
                        df_sessions = pd.DataFrame(session_data)
                        st.dataframe(df_sessions, use_container_width=True)
                    else:
                        st.info("No active sessions")
                
                # Create Session
                with session_tabs[1]:
                    st.subheader("Start New Session")
                    
                    if all_games:
                        with st.form("create_session_form"):
                            selected_game = st.selectbox(
                                "Select Game",
                                [g.get("title", "") for g in all_games],
                                key="create_session_game"
                            )
                            
                            level = st.number_input("Starting Level", min_value=1, max_value=100, value=1)
                            mode = st.text_input("Game Mode", placeholder="e.g., Campaign, Multiplayer")
                            
                            submitted = st.form_submit_button("✅ Start Session", use_container_width=True)
                            
                            if submitted:
                                if not selected_game or not mode:
                                    st.error("Game and Mode are required!")
                                else:
                                    game = next((g for g in all_games if g.get("title") == selected_game), None)
                                    if game:
                                        session_data = {
                                            "player_id": player_id,
                                            "game_id": str(game.get("_id")),
                                            "level": level,
                                            "mode": mode,
                                            "status": "active"
                                        }
                                        
                                        result = make_request("POST", "/sessions", data=session_data)
                                        if result:
                                            st.success("✅ Session started!")
                                            st.rerun()
                                        else:
                                            st.error("Failed to create session")
                    else:
                        st.warning("No games available")
                
                # End/Delete Session
                with session_tabs[2]:
                    st.subheader("End Session")
                    
                    sessions = make_request("GET", f"/sessions/active/{player_id}", show_error=False)
                    if sessions:
                        session_options = {f"{s.get('game_id', 'Unknown')} - Started: {s.get('started_at', 'N/A')[:10]}": s for s in sessions[:20]}
                        selected_session_key = st.selectbox(
                            "Select Session to End",
                            list(session_options.keys()),
                            key="delete_session_select"
                        )
                        
                        session_to_end = session_options[selected_session_key]
                        session_id = str(session_to_end.get("_id"))
                        
                        st.warning(f"⚠️ This will end the active session")
                        
                        if st.button("🛑 End Session", type="secondary", use_container_width=True):
                            result = make_request("POST", f"/sessions/{session_id}/end")
                            if result:
                                st.success("✅ Session ended!")
                                st.rerun()
                            else:
                                st.error("Failed to end session")
                    else:
                        st.info("No active sessions to end")
    
    with tabs[6]:  # Notifications
        st.subheader("Notification Management")
        
        all_players = make_request("GET", "/players", params={"limit": 100})
        if all_players:
            selected = st.selectbox("Select Player", [p.get("username") for p in all_players], key="admin_notif_player")
            player = next((p for p in all_players if p.get("username") == selected), None)
            
            if player:
                notifs = make_request("GET", f"/notifications/player/{str(player.get('_id'))}")
                if notifs:
                    for notif in notifs[:10]:
                        with st.container():
                            col1, col2 = st.columns([4, 1])
                            with col1:
                                st.write(notif.get("title", "Notification"))
                                st.caption(notif.get("message", ""))
                            with col2:
                                if st.button("🗑️", key=f"delete_notif_{notif.get('_id')}"):
                                    result = make_request("DELETE", f"/notifications/{str(notif.get('_id'))}")
                                    if result:
                                        st.rerun()
                else:
                    st.info("No notifications")
    
    with tabs[7]:  # Inventory
        st.subheader("Player Inventory Management")
        
        all_players = make_request("GET", "/players", params={"limit": 100})
        all_games = make_request("GET", "/games", params={"limit": 100})
        
        if all_players and all_games:
            col1, col2 = st.columns(2)
            with col1:
                selected_player = st.selectbox("Select Player", [p.get("username") for p in all_players], key="admin_inv_player")
            with col2:
                selected_game = st.selectbox("Select Game", [g.get("title") for g in all_games], key="admin_inv_game")
            
            player = next((p for p in all_players if p.get("username") == selected_player), None)
            game = next((g for g in all_games if g.get("title") == selected_game), None)
            
            if player and game:
                inventory = make_request("GET", f"/inventory/{str(player.get('_id'))}/{str(game.get('_id'))}")
                if inventory:
                    st.write(f"**Currency:** {inventory.get('currency', 0)}")
                    if inventory.get("items"):
                        st.dataframe(pd.DataFrame(inventory.get("items", [])))


# ==================== SOCIAL ====================
def show_social():
    
    tab1, tab2, tab3 = st.tabs(["Friends", "Messaging", "Clans"])
    
    with tab1:
        st.subheader("Friend Management")
        
        st.info("ℹ️ **Note:** Friend features require Neo4j to be running. Make sure Neo4j is connected to use this feature.")
        
        all_players = make_request("GET", "/players", params={"limit": 100})
        if all_players and len(all_players) > 1:
            col1, col2 = st.columns(2)
            with col1:
                player1 = st.selectbox(
                    "Select Player",
                    [p.get("username", "") for p in all_players],
                    key="friend_player1"
                )
            with col2:
                # Filter out player1 from the list
                other_players = [p.get("username", "") for p in all_players if p.get("username") != player1]
                if other_players:
                    player2 = st.selectbox(
                        "Add as Friend",
                        other_players,
                        key="friend_player2"
                    )
                else:
                    st.warning("No other players available to add as friends")
                    player2 = None
            
            if player2 and st.button("Add Friend", use_container_width=True):
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
                    else:
                        st.error("❌ Failed to add friend. Make sure Neo4j is running and player nodes are created.")
        elif all_players and len(all_players) == 1:
            st.warning("⚠️ Only one player exists. Create more players to add friends!")
        else:
            st.warning("No players available. Create players first!")
    
    with tab2:
        st.subheader("Send Message")
        
        st.info("ℹ️ **Note:** Messaging features require Neo4j to be running. Make sure Neo4j is connected to use this feature.")
        
        all_players = make_request("GET", "/players", params={"limit": 100})
        if all_players and len(all_players) > 1:
            col1, col2 = st.columns(2)
            with col1:
                sender = st.selectbox(
                    "From Player",
                    [p.get("username", "") for p in all_players],
                    key="msg_sender"
                )
            with col2:
                other_players = [p.get("username", "") for p in all_players if p.get("username") != sender]
                if other_players:
                    recipient = st.selectbox(
                        "To Player",
                        other_players,
                        key="msg_recipient"
                    )
                else:
                    st.warning("No other players available to message")
                    recipient = None
            
            message = st.text_area("Message", placeholder="Enter your message", height=100)
            
            if recipient and st.button("Send Message", use_container_width=True):
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
                    else:
                        st.error("❌ Failed to send message. Make sure Neo4j is running.")
        elif all_players and len(all_players) == 1:
            st.warning("⚠️ Only one player exists. Create more players to send messages!")
        else:
            st.warning("No players available. Create players first!")
    
    with tab3:
        st.subheader("Clan Management")
        st.info("🏢 **Clan Features** - Requires Neo4j\n\n"
                "Clans allow players to form organizations and guilds. "
                "Features include clan chat, member management, clan wars, and more.\n\n"
                "⚠️ Make sure Neo4j is running to use clan features.")


# ==================== MAIN APP ====================
def main():
    """Main app logic"""
    # Sidebar navigation
    st.sidebar.title("🎮 Gaming System")
    
    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Players", "Games", "Stats", "Leaderboards", "Achievements", "Matches", "Social", "Admin Panel"]
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
    elif page == "Stats":
        show_stats()
    elif page == "Leaderboards":
        show_leaderboards()
    elif page == "Achievements":
        show_achievements()
    elif page == "Matches":
        show_matches()
    elif page == "Social":
        show_social()
    elif page == "Admin Panel":
        show_admin_panel()


if __name__ == "__main__":
    main()
