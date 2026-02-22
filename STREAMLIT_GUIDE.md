## 🎮 Streamlit Frontend Setup & Usage

### Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the FastAPI backend server** (in one terminal):
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Run the Streamlit frontend** (in another terminal):
   ```bash
   streamlit run streamlit_app.py
   ```

   The app will automatically open in your browser at `http://localhost:8501`

### Features

#### 📊 **Dashboard**
- Quick overview of total players, games, and statistics
- Key metrics at a glance

#### 👥 **Players**
- Browse all players with search functionality
- Create new players with custom profiles
- View detailed player statistics and match history
- See win rates, levels, and platforms

#### 🎯 **Games**
- Browse the complete game catalog
- Search games by name
- Add new games with details (genre, platforms, rating, etc.)
- View game descriptions and metadata

#### 🏆 **Leaderboards**
- View player rankings by score
- Global statistics (total matches, wins, average level)
- Level distribution visualization
- Top players by score

#### 🎖️ **Achievements**
- Browse available achievements
- Award achievements to players
- View achievement details and rarity

#### ⚔️ **Match History**
- View recent matches
- See match duration, date, and results
- Track winning points

#### 👫 **Social Features**
- Add friends between players
- Send messages between players
- Clan management (coming soon!)

### How to Use

1. **Create Players**: Go to Players → Create Player tab
2. **Add Games**: Go to Games → Add Game tab
3. **Track Achievements**: Go to Achievements → Unlock Achievement tab
4. **Send Messages**: Go to Social → Messaging tab
5. **Check Leaderboards**: Go to Leaderboards for rankings

### API Integration

The Streamlit app communicates with your FastAPI backend on:
- **Base URL**: `http://localhost:8000`
- **Endpoints Used**:
  - `/players` - Player management
  - `/games` - Game catalog
  - `/leaderboards` - Rankings
  - `/achievements` - Achievement system
  - `/matches` - Match history
  - `/stats` - Player statistics
  - `/friends` - Friend management
  - `/messages` - Messaging system

### Troubleshooting

- **"Cannot connect to API"**: Make sure your FastAPI server is running on port 8000
- **No data showing**: Ensure you've seeded some data using `scripts/seed_data.py`
- **Port already in use**: Change Streamlit port with: `streamlit run streamlit_app.py --server.port 8502`

### File Structure
```
mongodbgame/
├── streamlit_app.py      # Main Streamlit frontend
├── requirements.txt      # Updated with Streamlit dependencies
├── app/                  # FastAPI backend
│   ├── main.py          # API server
│   ├── routes/          # API endpoints
│   ├── models/          # Data models
│   ├── crud/            # Database operations
│   └── database/        # DB connections
└── scripts/
    └── seed_data.py     # Populate sample data
```

### Performance Tips

- Use the search/filter features to reduce data loaded
- Limit is set to 50-100 records by default for better performance
- Refresh the page if data seems stale
