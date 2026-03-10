# Interactive Command Console - Complete Guide

## Overview

The GameBD system now features a fully interactive command console where you can execute all MongoDB and Neo4j commands directly from your browser without needing external tools or cURL commands.

## Access Points

### 1. **Interactive Console** (NEW - Primary Interface)
- **URL:** `http://localhost:8001/ui/interactive`
- **Best for:** Actually executing commands and testing the system
- **Features:**
  - Form-based interface for all commands
  - Real-time command execution
  - Instant JSON response display
  - Organized by Admin/Player views
  - Separated by Database type (MongoDB vs Neo4j)

### 2. **Admin Dashboard** (Reference)
- **URL:** `http://localhost:8001/ui/dashboard`
- **Best for:** API documentation and cURL examples
- **Features:**
  - Complete endpoint reference
  - cURL command examples
  - Copy-to-clipboard functionality
  - All 70+ endpoints documented

### 3. **Home Page** (Navigation Hub)
- **URL:** `http://localhost:8001/ui/`
- **Features:**
  - Quick links to both dashboards
  - Basic data viewing
  - Navigation to all features

---

## Interactive Console Structure

### Admin View (Default)

#### 1. MongoDB Commands
This section contains all database operations for:

**Players**
- `Get All Players` - List players with pagination (skip, limit)
- `Create Player` - Register new player (username, email, level)
- `Get Player by ID` - Retrieve single player profile
- `Update Player` - Modify player stats (level, XP)
- `Delete Player` - Remove player from database

**Games**
- `Get All Games` - List all games with pagination
- `Create Game` - Add new game (title, genre, max_players)

**Player Stats**
- `Get Player Stats` - View player's game statistics
- `Create Player Stats` - Initialize stats for player

**Leaderboards**
- `Get Leaderboard` - View top players ranked by score

#### 2. Neo4j Commands
Graph database operations for social features:

**Player Nodes (Graph Identity)**
- `Create Player Node` - Initialize player in graph (player_id, username, status)
- `Get Player Node` - Retrieve player node details
- `Update Player Status` - Change online status (online/offline/away)

**Friends (Relationships)**
- `Send Friend Request` - Initiate friendship
- `Accept Friend Request` - Create friendship connection
- `Get Friends List` - View all friends
- `Get Pending Requests` - See incoming friend requests
- `Get Mutual Friends` - Find common friends between two players
- `Get Friend Suggestions` - Get recommended friends based on connections
- `Remove Friend` - Delete friendship

**Blocking (Relationship)**
- `Block Player` - Prevent another player from contacting you
- `Get Blocked Players` - View your blocklist
- `Unblock Player` - Remove from blocklist

**Messaging (Conversations & Messages)**
- `Create Conversation` - Start 1-on-1 or group chat (type: private/group)
- `Send Message` - Post message to conversation
- `Get Conversations` - List all your conversations
- `Get Messages` - Retrieve messages from conversation (with pagination)

**Parties (Temporary Groups)**
- `Create Party` - Start a party for gaming
- `Get Party` - View party details and members
- `Join Party` - Add yourself to a party

**Clans (Permanent Groups)**
- `Create Clan` - Establish clan with tag and description
- `Get Clan` - View clan info and roster
- `Join Clan` - Become clan member
- `Search Clans` - Find clans by name/tag

**Follow (Relationship)**
- `Follow Player` - Subscribe to player's activity
- `Get Following` - List players you follow
- `Get Followers` - See who follows you
- `Unfollow Player` - Stop following player

### Player View

Filtered subset designed for regular players:

**Local Player (MongoDB)**
- Get My Profile
- Get My Stats
- Browse Leaderboard

**Social Features (Neo4j)**
- Send Friend Request
- View My Friends
- Check Friend Requests
- Accept Friend Request
- Friend Suggestions
- Block Player
- Send Message
- Join Clan
- View My Clan
- Create Party
- Follow Player

---

## How to Use Commands

### Step 1: Navigate to Interactive Console
Go to `http://localhost:8001/ui/interactive`

### Step 2: Choose View
- Select "Admin View" for full system access (default)
- Select "Player View" for player-facing features

### Step 3: Choose Database
In Admin View:
- Click "MongoDB Commands" or "Neo4j Commands"
- Player View is already categorized

### Step 4: Find Your Command
Commands are organized by category (Players, Friends, Parties, etc.)

### Step 5: Fill in Parameters
Each command form displays required fields:
- Required fields must be filled
- Optional fields can be left empty
- Text inputs for IDs, names
- Select dropdowns for status (online/offline)
- Textareas for messages and bulk data

### Step 6: Execute
Click the "Execute" button to run the command

### Step 7: View Results
- **Green box with JSON:** Success response
- **Red box with error:** Error message from server
- Copy/select the response text for further use

---

## Command Examples

### Example 1: Create a Player (MongoDB)
1. Navigate to interactive console
2. Keep Admin View active
3. Click "MongoDB Commands" 
4. Find Players section
5. Locate "Create Player" card
6. Fill in:
   - Username: `john_warrior`
   - Email: `john@example.com`
   - Level: `5`
7. Click "Execute"
8. See response with generated player ID

### Example 2: Send Friend Request (Neo4j)
1. Navigate to interactive console
2. Keep Admin View active
3. Click "Neo4j Commands"
4. Find Friends section
5. Locate "Send Friend Request" card
6. Fill in:
   - From Player ID: `[your player ID from Example 1]`
   - To Player ID: `[another player ID]`
   - Message: `Hey, want to be friends?`
7. Click "Execute"
8. Relationship created in database

### Example 3: Get Top 20 on Leaderboard (MongoDB - Player View)
1. Switch to "Player View"
2. Find "Browse Leaderboard" card
3. Change limit from 50 to 20
4. Click "Get Leaderboard"
5. See top 20 players ranked by score

### Example 4: Create a Clan (Neo4j)
1. Admin View → Neo4j Commands
2. Find Clans section
3. Locate "Create Clan" card
4. Fill in:
   - Clan Name: `Dragon Slayers`
   - Clan Tag: `DRSL`
   - Owner ID: `[your player ID]`
   - Description: `Elite PvP clan`
5. Click "Execute"
6. Returns clan ID for future operations

---

## MongoDB vs Neo4j Commands

### MongoDB Commands
**Purpose:** Game data and player statistics
- Player profiles (username, level, XP, stats)
- Game definitions and metadata
- Player statistics (wins, losses, rankings)
- Match history
- Achievement tracking
- Notifications
- Inventory

**Data Structure:** Collections with documents
**Relationships:** Embedded fields, references

**Use Cases:**
- Store player profiles
- Track match results
- Maintain leaderboards
- Manage inventory items
- Track achievements

### Neo4j Commands
**Purpose:** Social relationships and graph connections
- Friendships (mutual relationships)
- Friend requests (pending connections)
- Blocking (negative relationships)
- Messaging (conversations)
- Parties (temporary groups)
- Clans (permanent organizations)
- Follow relationships

**Data Structure:** Nodes (entities) and Relationships (connections)
**Relationship Types:** FRIEND_OF, BLOCKED_BY, MEMBER_OF, FOLLOWS, etc.

**Use Cases:**
- Build friend networks
- Create party systems
- Manage clan membership
- Handle direct messaging
- Track player followers
- Implement social recommendations

---

## Key Features of Interactive Console

### 1. **Real-Time Execution**
- No need for external tools like Postman or cURL
- Instant feedback on command success/failure
- See actual API responses immediately

### 2. **Form Validation**
- Client-side validation prevents incomplete submissions
- Error messages guide you to required fields
- Real-time feedback with loading indicator

### 3. **Smart Parameter Handling**
- GET requests: Parameters added as query strings
- POST/PATCH: Parameters sent in JSON body
- DELETE requests: Parameters as query strings
- PATH parameters: Automatically replaced in URL

### 4. **Organized Layout**
- Color-coded HTTP methods (GET=Blue, POST=Green, PATCH=Cyan, DELETE=Red)
- Logical grouping by feature (Friends, Parties, Clans, etc.)
- Expandable sections for different databases
- Search-friendly structure

### 5. **Response Display**
- Pretty-formatted JSON responses
- Scrollable response boxes (max-height with overflow)
- Color-coded success (green) and error (red) boxes
- Full error details from server

### 6. **Quick Navigation**
- Tab between Admin and Player views
- Toggle between MongoDB and Neo4j sections
- Smooth scrolling to each command section

---

## Common Workflows

### Workflow 1: Set Up a New Player
```
1. Create Player (MongoDB) → Get Player ID
2. Create Player Node (Neo4j) → Initialize in graph
3. Create Player Stats (MongoDB) → Set initial stats
4. Update Player Status (Neo4j) → Set online
```

### Workflow 2: Build a Social Network
```
1. Send Friend Request (Neo4j)
2. Accept Friend Request (Neo4j)
3. Get Friends List (Neo4j)
4. Get Friend Suggestions (Neo4j)
```

### Workflow 3: Create Game Group
```
1. Create Clan (Neo4j)
2. Set clan as owner
3. Other players Join Clan (Neo4j)
4. Get Clan details (Neo4j)
5. Get Player Clan (Neo4j)
```

### Workflow 4: Direct Communication
```
1. Create Conversation (Neo4j)
2. Add participants
3. Send Message (Neo4j)
4. Get Messages (Neo4j)
```

### Workflow 5: Start Gaming Session
```
1. Create Party (Neo4j)
2. Get Party (Neo4j)
3. Other players Join Party (Neo4j)
4. Create Game Session (MongoDB)
5. Record Match results (MongoDB)
```

---

## Troubleshooting

### "Neo4j is not connected"
- Neo4j service must be running
- Server reconnects on restart
- Check Neo4j connection in logs

### "Error: Player not found"
- Verify player ID is correct from a Get All Players query
- Check spelling of player_id parameter

### "Error: Username already exists"
- When creating player, username must be unique
- Try different username or get existing player by ID

### "Conversation not found"
- Verify conversation ID from Get Conversations
- Ensure you created conversation first

### "Empty response"
- Some operations (like deletions) return empty responses
- Check the success indicator (green box = success)

### "CORS Error"
- CORS is enabled on the server
- If still seeing errors, restart server
- Clear browser cache (Ctrl+Shift+Delete)

---

## API Reference Quick Links

**MongoDB Base URL:** `http://localhost:8001/api/v1`
- `/players` - Player operations
- `/games` - Game definitions
- `/leaderboards` - Rankings

**Neo4j Base URL:** `http://localhost:8001/api/v1`
- `/player-nodes` - Graph player nodes
- `/friends` - Friend operations
- `/block` - Blocking operations
- `/messages` - Messaging/conversations
- `/parties` - Party operations
- `/clans` - Clan operations
- `/follow` - Follow operations

For detailed endpoint documentation, visit the Admin Dashboard: `/ui/dashboard`

---

## Next Steps

1. **Explore Admin Console** - Try different commands in Admin View
2. **Test Player View** - See what regular players can access
3. **Build Test Data** - Use Create commands to populate database
4. **Test Workflows** - Follow the common workflows above
5. **Review Admin Dashboard** - Check `/ui/dashboard` for cURL examples

---

## Summary

The Interactive Command Console provides a user-friendly interface to:
- ✅ Execute ALL MongoDB commands directly
- ✅ Execute ALL Neo4j commands directly
- ✅ Organize commands logically (Admin vs Player, MongoDB vs Neo4j)
- ✅ See real-time responses
- ✅ Test complete workflows without external tools
- ✅ Learn API structure through forms
- ✅ Switch between roles and databases instantly

**Access it now at:** `http://localhost:8001/ui/interactive`
