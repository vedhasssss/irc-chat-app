import os
import random
import string
import logging
from datetime import datetime
from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

# Initialize Flask and SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key_for_terminal_chat'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# ------------------------------------------------------------------------------
# IN-MEMORY DATA STORE
# ------------------------------------------------------------------------------

# Structure: { sid: { 'nick': str, 'room': str } }
users = {}

# Structure: { room_id: { 'type': 'public'|'private', 'owner': sid (optional) } }
rooms = {}

# ------------------------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------------------------

def generate_room_code():
    """Generates a unique 10-digit numeric code."""
    while True:
        code = str(random.randint(1000000000, 9999999999))
        if code not in rooms:
            return code

def get_username(sid):
    return users.get(sid, {}).get('nick', 'Anonymous')

def cleanup_user(sid):
    """Removes user from memory and notifies their current room."""
    if sid in users:
        user_data = users[sid]
        current_room = user_data.get('room')
        nick = user_data.get('nick')
        
        if current_room:
            leave_room(current_room)
            emit('server_message', {'msg': f'<< {nick} has left the room.'}, to=current_room)
            
            # Check if room is empty and delete if private or empty public
            # (Logic: we keep public rooms in list usually, but here we clean up strictly)
            # For this exercise, we keep public rooms in the 'rooms' dict explicitly
            pass

        del users[sid]

# ------------------------------------------------------------------------------
# SOCKET EVENT HANDLERS
# ------------------------------------------------------------------------------

@socketio.on('connect')
def handle_connect():
    users[request.sid] = {'nick': None, 'room': None}
    emit('server_message', {'msg': 'Welcome! Please set a nickname using /nick <name>'})

@socketio.on('disconnect')
def handle_disconnect():
    cleanup_user(request.sid)

@socketio.on('set_nick')
def handle_set_nick(data):
    new_nick = data.get('nick').strip()
    
    # Validation
    if not new_nick:
        emit('error', {'msg': 'Nickname cannot be empty.'})
        return

    # Check uniqueness
    for uid, udata in users.items():
        if udata.get('nick') == new_nick:
            emit('error', {'msg': f'Nickname "{new_nick}" is already taken.'})
            return

    # Set nickname
    old_nick = users[request.sid].get('nick')
    users[request.sid]['nick'] = new_nick
    
    if old_nick:
        emit('server_message', {'msg': f'You changed your nickname to {new_nick}'})
    else:
        emit('server_message', {'msg': f'Nickname set to {new_nick}. You may now /join #room or /createprivate'})
        emit('nick_success', {'nick': new_nick})

@socketio.on('join_public')
def handle_join_public(data):
    room_name = data.get('room')
    sid = request.sid
    user = users[sid]

    if not user.get('nick'):
        emit('error', {'msg': 'Set a nickname first using /nick <name>'})
        return

    if not room_name.startswith('#'):
        emit('error', {'msg': 'Public rooms must start with #'})
        return

    # Leave current room
    if user.get('room'):
        leave_room(user['room'])
        emit('server_message', {'msg': f'<< {user["nick"]} left.'}, to=user['room'])

    # Join new room
    join_room(room_name)
    user['room'] = room_name
    
    # Register room if new
    if room_name not in rooms:
        rooms[room_name] = {'type': 'public'}

    emit('room_joined', {'room': room_name})
    emit('server_message', {'msg': f'>> {user["nick"]} joined {room_name}'}, to=room_name)

@socketio.on('create_private')
def handle_create_private():
    sid = request.sid
    user = users[sid]

    if not user.get('nick'):
        emit('error', {'msg': 'Set a nickname first using /nick <name>'})
        return

    # Leave current room
    if user.get('room'):
        leave_room(user['room'])
        emit('server_message', {'msg': f'<< {user["nick"]} left.'}, to=user['room'])

    # Generate Code
    room_code = generate_room_code()
    rooms[room_code] = {'type': 'private', 'owner': sid}
    
    join_room(room_code)
    user['room'] = room_code

    emit('room_joined', {'room': f'Private Room {room_code}'})
    emit('server_message', {'msg': f'Private room created. CODE: {room_code}'})
    emit('server_message', {'msg': 'Share this code with others to let them join.'})

@socketio.on('join_private')
def handle_join_private(data):
    code = data.get('code')
    sid = request.sid
    user = users[sid]

    if not user.get('nick'):
        emit('error', {'msg': 'Set a nickname first.'})
        return

    if code not in rooms:
        emit('error', {'msg': 'Invalid private room code.'})
        return
    
    if rooms[code]['type'] != 'private':
        emit('error', {'msg': 'That is not a private room.'})
        return

    # Leave current room
    if user.get('room'):
        leave_room(user['room'])
        emit('server_message', {'msg': f'<< {user["nick"]} left.'}, to=user['room'])

    join_room(code)
    user['room'] = code
    
    emit('room_joined', {'room': f'Private Room {code}'})
    emit('server_message', {'msg': f'>> {user["nick"]} joined the private room.'}, to=code)

@socketio.on('send_message')
def handle_message(data):
    sid = request.sid
    msg_content = data.get('msg')
    user = users[sid]
    room = user.get('room')

    if not user.get('nick'):
        emit('error', {'msg': 'Set a nickname first.'})
        return

    if not room:
        emit('error', {'msg': 'You are not in a room. Use /join #room or /createprivate'})
        return

    # Broadcast to room
    emit('chat_message', {
        'user': user['nick'],
        'msg': msg_content,
        'timestamp': datetime.now().isoformat()
    }, to=room)

@socketio.on('list_rooms')
def handle_list_rooms():
    public_rooms = [r for r, data in rooms.items() if data.get('type') == 'public']
    if not public_rooms:
        emit('server_message', {'msg': 'No public rooms active.'})
    else:
        emit('server_message', {'msg': f'Public Rooms: {", ".join(public_rooms)}'})

@socketio.on('list_users')
def handle_list_users():
    sid = request.sid
    user = users[sid]
    room = user.get('room')
    
    if not room:
        emit('error', {'msg': 'You must be in a room to list users.'})
        return

    # This is inefficient for millions of users but fine for a terminal app
    room_users = [u['nick'] for u in users.values() if u['room'] == room]
    emit('server_message', {'msg': f'Users in {room}: {", ".join(room_users)}'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Chat Server on 0.0.0.0:{port}...")
    socketio.run(app, host='0.0.0.0', port=port)