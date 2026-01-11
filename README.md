# Terminal IRC Chat

A production-quality, terminal-based chat application using Python, Flask-SocketIO, and Curses.

## Features
- **Real-time:** Instant messaging via WebSockets with timestamps
- **TUI:** Split-screen terminal interface (Message history / Input)
- **Public Rooms:** Join any room starting with `#` (e.g., `#python`)
- **Private Rooms:** Secure, random 10-digit code access
- **Commands:** IRC-style commands (`/nick`, `/join`, etc.)
- **Timestamps:** Messages displayed in "Date | Name | Message" format
- **Windows Support:** Works on Windows with `windows-curses`

## Quick Start (Windows)

### Option 1: Double-Click Launch (Easiest!)
Just double-click one of these batch files:

- **`start_chat.bat`** - Starts server + 1 client
- **`start_chat_multi.bat`** - Starts server + 2 clients (for testing)

That's it! The chat application will open automatically.

### Option 2: Manual Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the server:**
   ```bash
   cd server
   python app.py
   ```

3. **Start the client (in new terminal):**
   ```bash
   cd client
   python client.py
   ```

## How to Use

### Basic Commands

1. **Set your nickname:**
   ```
   /nick YourName
   ```

2. **Join a public room:**
   ```
   /join #general
   ```

3. **Send a message:**
   Just type and press Enter!

### All Available Commands

- `/nick <name>` - Set your nickname
- `/join #roomname` - Join a public room
- `/createprivate` - Create a private room (get a 10-digit code)
- `/joinprivate <code>` - Join a private room using code
- `/rooms` - List all public rooms
- `/users` - List users in current room
- `/quit` - Exit the application

### Private Rooms Example

**User 1:**
```
/nick Alice
/createprivate
→ Server: Private room created. CODE: 1234567890
```

**User 2:**
```
/nick Bob
/joinprivate 1234567890
→ Joined the private room!
```

## Message Format

All chat messages are displayed with timestamps:
```
2026-01-09 20:35:15 | Alice | Hello everyone!
2026-01-09 20:35:22 | Bob | Hi Alice!
```

## Technical Details

- **Server:** Flask + Flask-SocketIO + Eventlet
- **Client:** Python-SocketIO + Curses (windows-curses on Windows)
- **Protocol:** WebSocket (Socket.IO)
- **Port:** 5000 (localhost)

## Prerequisites
- Python 3.10+
- Windows, Linux, or macOS

## Troubleshooting

**Q: "ModuleNotFoundError: No module named '_curses'"**  
A: Install windows-curses:
```bash
pip install windows-curses
```

**Q: "Address already in use"**  
A: Another server is running. Find and kill it:
```bash
netstat -ano | findstr :5000
taskkill /F /PID <PID>
```

**Q: Can't connect to server**  
A: Make sure the server is running first before starting clients.

## License
MIT License