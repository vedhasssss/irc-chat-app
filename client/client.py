import sys
import curses
import threading
import time
import socketio
from datetime import datetime

# ------------------------------------------------------------------------------
# CONFIGURATION & STATE
# ------------------------------------------------------------------------------

SERVER_URL = 'http://localhost:5000'
sio = socketio.Client()

# Global State
messages = []
input_buffer = ""
running = True
current_nick = None
current_room = "Lobby"
error_msg = ""

# Synchronization
lock = threading.Lock()

# ------------------------------------------------------------------------------
# SOCKET.IO CALLBACKS
# ------------------------------------------------------------------------------

@sio.event
def connect():
    add_system_message("Connected to server.")

@sio.event
def connect_error(data):
    add_system_message(f"Connection failed: {data}")

@sio.event
def disconnect():
    add_system_message("Disconnected from server.")

@sio.event
def server_message(data):
    add_system_message(data['msg'])

@sio.event
def error(data):
    add_system_message(f"ERROR: {data['msg']}")

@sio.event
def chat_message(data):
    timestamp_str = data.get('timestamp', '')
    if timestamp_str:
        # Parse ISO format timestamp and format it
        try:
            dt = datetime.fromisoformat(timestamp_str)
            formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            formatted_time = timestamp_str
    else:
        formatted_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with lock:
        messages.append(f"{formatted_time} | {data['user']} | {data['msg']}")

@sio.event
def room_joined(data):
    global current_room
    current_room = data['room']
    add_system_message(f"Joined: {current_room}")

@sio.event
def nick_success(data):
    global current_nick
    current_nick = data['nick']

def add_system_message(msg):
    with lock:
        messages.append(f"* {msg}")

# ------------------------------------------------------------------------------
# UI RENDERING (CURSES)
# ------------------------------------------------------------------------------

def draw_ui(stdscr):
    global input_buffer, running

    # Colors
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)  # System/Status
    curses.init_pair(2, curses.COLOR_CYAN, -1)   # Header
    curses.init_pair(3, curses.COLOR_WHITE, -1)  # Normal Text

    stdscr.nodelay(True) # Non-blocking input
    stdscr.timeout(100)  # Refresh every 100ms

    rows, cols = stdscr.getmaxyx()
    
    # Setup windows
    # Top: Chat History (rows - 2)
    # Bottom: Input Line (1 row)
    
    while running:
        rows, cols = stdscr.getmaxyx()
        stdscr.clear()

        # --- HEADER ---
        header_text = f" Terminal Chat | Nick: {current_nick or 'None'} | Room: {current_room} "
        stdscr.attron(curses.color_pair(2) | curses.A_REVERSE)
        try:
            stdscr.addstr(0, 0, header_text + " " * (cols - len(header_text)))
        except curses.error:
            pass # Ignore if terminal too small
        stdscr.attroff(curses.color_pair(2) | curses.A_REVERSE)

        # --- CHAT HISTORY ---
        # Display as many messages as fit in the area between header and input
        chat_height = rows - 2
        with lock:
            msgs_to_show = messages[-(chat_height):]
        
        for idx, msg in enumerate(msgs_to_show):
            y = idx + 1
            if y < rows - 1:
                try:
                    # Simple wrapping logic or truncation
                    display_msg = msg[:cols-1]
                    # Colorize system messages differently
                    if msg.startswith('*') or msg.startswith('ERROR') or msg.startswith('>>') or msg.startswith('<<'):
                        stdscr.attron(curses.color_pair(1))
                        stdscr.addstr(y, 0, display_msg)
                        stdscr.attroff(curses.color_pair(1))
                    else:
                        stdscr.addstr(y, 0, display_msg)
                except curses.error:
                    pass

        # --- SEPARATOR ---
        try:
            stdscr.hline(rows - 2, 0, '-', cols)
        except curses.error:
            pass

        # --- INPUT AREA ---
        input_prompt = f"[{current_nick or '?'}]> "
        try:
            stdscr.addstr(rows - 1, 0, input_prompt, curses.color_pair(2))
            stdscr.addstr(rows - 1, len(input_prompt), input_buffer)
        except curses.error:
            pass

        stdscr.refresh()

        # --- INPUT HANDLING ---
        try:
            key = stdscr.getch()
            if key != -1:
                if key == 10: # Enter
                    process_input(input_buffer)
                    input_buffer = ""
                elif key == 27: # ESC or special keys handling could go here
                    pass
                elif key in (curses.KEY_BACKSPACE, 127, 8):
                    input_buffer = input_buffer[:-1]
                elif 32 <= key <= 126:
                    input_buffer += chr(key)
        except KeyboardInterrupt:
            running = False

# ------------------------------------------------------------------------------
# INPUT LOGIC
# ------------------------------------------------------------------------------

def process_input(text):
    global running, messages
    text = text.strip()
    if not text:
        return

    if text.startswith('/'):
        parts = text.split()
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd == '/quit':
            running = False
        elif cmd == '/nick':
            if args:
                sio.emit('set_nick', {'nick': args[0]})
            else:
                add_system_message("Usage: /nick <name>")
        elif cmd == '/join':
            if args:
                sio.emit('join_public', {'room': args[0]})
            else:
                add_system_message("Usage: /join #roomname")
        elif cmd == '/createprivate':
            sio.emit('create_private')
        elif cmd == '/joinprivate':
            if args:
                sio.emit('join_private', {'code': args[0]})
            else:
                add_system_message("Usage: /joinprivate <10-digit-code>")
        elif cmd == '/rooms':
            sio.emit('list_rooms')
        elif cmd == '/users':
            sio.emit('list_users')
        else:
            add_system_message(f"Unknown command: {cmd}")
    else:
        # Standard chat message
        if current_nick:
            sio.emit('send_message', {'msg': text})
        else:
            add_system_message("Please set a nickname first with /nick <name>")

# ------------------------------------------------------------------------------
# MAIN ENTRY
# ------------------------------------------------------------------------------

def main(stdscr):
    # Connect to server in background
    try:
        sio.connect(SERVER_URL)
    except Exception as e:
        # Wait a bit then print error to UI loop
        messages.append(f"Could not connect to server: {e}")
        messages.append("Ensure server is running on localhost:5000")

    draw_ui(stdscr)
    
    # Cleanup
    sio.disconnect()

if __name__ == '__main__':
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("\nExited.")
    except Exception as e:
        print(f"\nFatal Error: {e}")