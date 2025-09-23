import socketio
import eventlet
import logging
from datetime import datetime

from libs import MahjongRoom as mr

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- 服务器和全局数据存储初始化 ---

# 创建Socket.IO服务器
sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio)

# 全局数据存储
# users 存储所有连接到服务器的用户信息
# rooms 存储所有 MahjongRoom 对象的实例
users = {}  # {sid: {'ip': str, 'name': str, 'room_id': str, 'status': str}}
rooms = {}  # {room_id: MahjongRoom_instance}
namelist = []


# --- 辅助函数 ---

def authenticate(name, password):
    pass  # 这里可以实现认证逻辑:

def get_room_list():
    """生成并返回一个对客户端友好的房间列表。"""
    room_list = []
    for room in rooms.values():
        room_list.append({
            'id': room.id,
            'name': room.name,
            'game': room.game,
            'owner': room.owner,
            'members': room.get_member_count(),
            'max_members': room.rules['max players'],
            'has_password': bool(room.password),
            'status': room.status
        })
    return room_list

def handle_leave_room(sid, room_id):
    """处理用户离开房间的通用逻辑，无论是主动离开还是断线。"""
    if room_id not in rooms:
        return

    room = rooms[room_id]
    user_name = users[sid]['name']
    
    # 从房间实例中移除成员
    room.remove_member(sid)
    
    # 更新用户的状态
    users[sid]['room_id'] = None
    users[sid]['status'] = 'online'

    # 如果离开的是房主，则解散房间
    if room.owner == user_name:
        membersids = list(room.members.keys())
        for member_sid in membersids:
            sio.emit('room_deleted', {'success': True, 'message': '房主离开，房间已解散'}, room=member_sid)
        del rooms[room_id]
        logging.info(f"🏠 房间 {room.name} 因房主离开而已解散。")
    # 如果房间变空了，也解散它
    elif room.get_member_count() == 0:
        del rooms[room_id]
        logging.info(f"🏠 房间 {room.name} 因无人而自动解散。")
    else: # 在房间没有解散的情况下通知有玩家离开房间。
        sio.emit('player_left', {'sid': sid}, room=room_id)
        sio.emit('chat_message', {'type': 'log', 'level': 'info', 'message': f'玩家 {user_name} 离开了房间。'}, room=room_id) 
        
    # 向所有客户端广播最新的房间列表
    sio.emit('room_list_update', 
    {
        'success': True,
        'message': f'房间 {room.name} 解散',
        'room_list': get_room_list()
    })


# --- Socket.IO 服务器事件处理器 ---

@sio.event
def connect(sid, environ):
    """当一个新客户端连接时触发。"""
    client_ip = environ.get('REMOTE_ADDR', 'unknown')
    logging.info(f"🔗 客户端连接: {sid} from {client_ip}")
    users[sid] = {'ip': client_ip, 'name': '', 'room_id': None, 'status': 'offline'}
    sio.emit('connect_res', {'success': True, 'message': '连接成功', 'clientsid': sid}, room=sid)

@sio.event
def disconnect(sid):
    """当一个客户端断开连接时触发。"""
    logging.info(f"🔌 客户端断开: {sid}")
    if sid in users:
        # 如果用户在房间里，则处理离开逻辑
        if users[sid].get('room_id'):
            handle_leave_room(sid, users[sid]['room_id'])
    # Safely remove user
        if users[sid]['name'] in namelist:
            namelist.remove(users[sid]['name'])
        del users[sid]
@sio.event
def join_server(sid, data):
    """处理用户登录到服务器大厅的请求。"""
    name = data.get('name', '').strip()
    if not name:
        sio.emit('join_server_result', {'success': False, 'message': '用户名不能为空'}, room=sid)
        return
    if name in namelist:
        sio.emit('join_server_result', {'success': False, 'message': '用户名已被占用'}, room=sid)
        return
    
    users[sid]['name'] = name
    users[sid]['status'] = 'online'
    namelist.append(name)
    sio.emit('join_server_result', {'success': True, 'message': '登陆成功', 'username': name, 'room_list': get_room_list()}, room=sid)
    logging.info(f"✅ 用户 {name} ({sid}) 成功加入服务器")

@sio.event
def get_rooms(sid):
    """向客户端发送当前的房间列表。"""
    logging.info(f'{users[sid]['name']} 尝试获取房间列表')
    data = {
        'success': True,
        'message': '获取成功',
        'room_list': get_room_list()
    }
    if sid in users:
        sio.emit('room_list_update', data, room=sid)
    else: return
@sio.event
def get_room_info(sid,room_id):
    if users[sid]['room_id']!=room_id:
        logging.info(f'{users[sid]['name']} 尝试获取不属于自己的房间信息')
        sio.emit('room_info_update', {'success': False, 'message': '你不在该房间内'}, room=sid)
        return
    
    if room_id not in rooms:
        return
    room = rooms[room_id]
    data = {
        'success': True,
        'message': '获取成功',
        'members': room.members,
    }
    sio.emit('room_info_update', data, room=room_id)
    logging.info(f'当前房间成员 {room.members}')  



@sio.event
def create_room(sid, data):
    """处理用户创建新房间的请求。"""
    room_name = data.get('name', '').strip()
    logging.info(f"{users[sid]['name']} 尝试创建房间 {room_name}")
    if not room_name:
        sio.emit('create_room_result', {'success': False, 'message': '房间名不能为空'}, room=sid)
        return
    
    # 实例化来自 MahjongRoom 库的 MahjongRoom 类
    # 将 sio 服务器实例传递给了它，以便它能自行通信
    room = mr.MahjongRoom(
        name=room_name,
        password=data.get('password', ''),
        sio_server=sio,
        owner_sid=sid,
        owner_name=users[sid]['name']
    )
    rooms[room.id] = room
    
    sio.emit('create_room_result', {'success': True, 'message': '房间创建成功', 'room_id': room.id}, room=sid)
    
    sio.emit('room_list_update', {
        'success': True,
        'message': f'{users[sid]["name"]} 创建了新房间',
        'room_list': get_room_list()
    }) # 向所有客户端广播房间列表更新
    logging.info(f"🏠 用户 {users[sid]['name']} 创建了房间: {room_name} (ID: {room.id})")
    join_room(sid, {'room_id': room.id, 'password': room.password})  # 自动加入新创建的房间

@sio.event
def join_room(sid, data):
    """处理用户加入已存在房间的请求。"""
    room_id = data.get('room_id')
    password = data.get('password', '')
    
    if room_id not in rooms:
        sio.emit('join_room_result', {'success': False, 'message': '房间不存在'}, room=sid)
        return
    
    room = rooms[room_id]
    if room.is_full():
        sio.emit('join_room_result', {'success': False, 'message': '房间已满'}, room=sid)
        return
    if room.password and room.password != password:
        sio.emit('join_room_result', {'success': False, 'message': '密码错误'}, room=sid)
        return

    # 调用房间实例的方法来添加成员
    room.add_member(sid, users[sid]['name'], users[sid]['ip'])
    
    # 更新用户状态
    users[sid]['room_id'] = room_id
    users[sid]['status'] = 'in_room'
    
    sio.emit('join_room_result', {'success': True, 'message': '成功加入房间', 'id': room_id}, room=sid)
    sio.emit('room_list_update', {
        'success': True,
        'message': f'{room.name} 有新成员加入',
        'room_list': get_room_list()
    })
    logging.info(f"🚪 用户 {users[sid]['name']} 加入了房间: {room.name}: {room_id}")

@sio.event
def leave_room(sid, data):
    """处理用户主动离开房间的请求。"""
    if sid in users and users[sid].get('room_id'):
        handle_leave_room(sid, users[sid]['room_id'])
        sio.emit('leave_room_result', {'success': True, 'message': '已离开房间'}, room=sid)

@sio.event
def player_ready(sid, data):
    """处理玩家准备/取消准备的动作。"""
    room_id = users[sid].get('room_id')
    if not room_id or room_id not in rooms:
        return
    logging.info(f"{users[sid]['name']} 在房间 {room_id} 设置准备状态为 {data.get('ready', False)}")
    room = rooms[room_id]
    room.set_player_ready(sid, data.get('ready', False))
    room.members[sid]['decorator'] = data.get('decorator', None)
    get_room_info(sid,room_id)
    

@sio.event
def game_action(sid, data):
    """游戏操作的统一入口，将所有游戏内动作转发给对应的房间实例处理。"""
    print('Received Game Action signal from sid: ', sid, 'Data: ', data)  # --- IGNORE ---
    if sid not in users:
        return
    
    room_id = users[sid].get('room_id')
    if not room_id or room_id not in rooms:
        return
        
    room = rooms[room_id]
    if room.status != 'playing':
        sio.emit('game_action_result', {'success': False, 'message': '游戏未开始'}, room=sid)
        return
        
    # 将动作全权委托给房间实例处理
    room.handle_player_action(sid, data)

@sio.event
def chat_message(sid, data):
    """处理房间内的聊天消息。"""
    room_id = users[sid].get('room_id')
    message = data.get('message', '').strip()
    if not room_id or not message:
        return
    
    chat_data = {
        'type': 'chat',
        'name': users[sid]['name'],
        'message': message
    }
    sio.emit('chat_message', chat_data, room=room_id)
#   1754922093286: { type: 'log', level: 'info', message: '玩家 1 摸了一张牌。' },
#   1754922094551: { type: 'chat', name: '玩家 1', messages: 'Man!' },


# --- 启动服务器 ---

if __name__ == '__main__':
    print("🚀 Socket.IO 服务器启动中...")
    print("📡 监听地址: http://127.0.0.1:5000")
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)