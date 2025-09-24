import uuid
from datetime import datetime
import time
from . import Mahjong
import random
import logging

# ... (_replacements, NotAcceptTime, AlreadyActed 定义不变) ...
_replacements = {
    '1o': '🀙', '2o': '🀚', '3o': '🀛', '4o': '🀜', '5o': '🀝', '6o': '🀞', '7o': '🀟', '8o': '🀠', '9o': '🀡',
    '1t': '🀐', '2t': '🀑', '3t': '🀒', '4t': '🀓', '5t': '🀔', '6t': '🀕', '7t': '🀖', '8t': '🀗', '9t': '🀘',
    '1w': '🀇', '2w': '🀈', '3w': '🀉', '4w': '🀊', '5w': '🀋', '6w': '🀌', '7w': '🀍', '8w': '🀎', '9w': '🀏',
    'e': '🀀', 's': '🀁', 'w': '🀂', 'n': '🀃', 'b': '🀆', 'f': '🀅', 'z': '🀄', 'joker': '🃏', 'back': '🀫',
    'spring': '🀦', 'summer': '🀧', 'autumn': '🀨', 'winter': '🀩',
    'plum': '🀢', 'orchid': '🀣', 'bamboo': '🀤', 'chrysanthemum': '🀥'
}

class NotAcceptTime(Exception):
    """自定义异常，表示在错误的时间执行了操作。"""
    pass

class AlreadyActed(Exception):
    """自定义异常，表示玩家在本回合已经执行过操作。"""
    pass


class MahjongRoom:
    # ... (__init__, 房间管理方法, 状态广播方法等保持不变) ...
    def __init__(self, name, password, sio_server, owner_sid, owner_name, id=None):
        """
        初始化一个麻将房间。

        :param name: 房间名称。
        :param password: 房间密码 (可以是None)。
        :param sio_server: Socket.IO服务器实例。
        :param owner_sid: 创建者的 session ID。
        :param owner_name: 创建者的名称。
        :param id: 房间的唯一ID, 如果为None则自动生成。
        """
        self.sio = sio_server
        self.name = name
        self.game = 'mahjong'
        self.log = ''
        self.id = id if id else str(uuid.uuid4())
        self.password = password
        self.owner = owner_name
        self.winner = None
        self.members = {}  # {sid: {'name': str, 'ready': bool, 'ip': str}}
        self.spectators = {}
        self.status = 'waiting'  # 'waiting', 'playing', 'finished'
        self.game_instance = None
        self.created_time = datetime.now().isoformat()
        self.tmp_discarder = None  # 临时存储刚出牌的玩家ID，确保此时谁都无法出牌
        self.action_history = {} # 检测有无执行， time.time() 作为 key, value 为 boolean
        
        # 默认游戏规则
        self.rules = {
            "rules": "classic",
            "max players": 4,
            "tiles number": 16,
            "golden tile": True,
            "golden tile number": 4,
            "three golden win": True,
            "allow seven pairs": False,
            "stand delay": 10,
            "special delay": 5,
            "items_to_remove": ['spring', 'summer', 'autumn', 'winter', 'plum', 'orchid', 'bamboo', 'chrysanthemum']
        }

        # 游戏流程控制属性
        self.sid_to_player_id = {}
        self.player_id_to_sid = {}
        # 注意: pending_claims 和 submitted_claims 的主要逻辑移到 game_instance 中
        # self.pending_claims = {}
        # self.submitted_claims = {}

    # --- 房间管理方法 ---
    def add_member(self, sid, name, ip_address):
        """添加一个新成员到房间。"""
        
        if sid in self.members:
            return
        # print(f"🆕 {name} ({sid}) 加入房间 {self.name}   ")
        # members 为游戏前，Players 为游戏中
        self.sio.enter_room(sid, self.id)
        self.members[sid] = {'name': name, 'ready': False, 'ip': ip_address, 'decorator': None}
        self.update_clients(f"{name} 加入房间")
 

    def remove_member(self, sid):
        """从房间移除一个成员。"""
        if sid in self.members:
            name = self.members[sid]['name']
            del self.members[sid]
            self.sio.leave_room(sid, self.id)
            self.update_clients(f"{name} 离开房间")
            return name
        return None

    def get_member_count(self):
        """返回当前房间人数。"""
        return len(self.members)

    def is_full(self):
        """检查房间是否已满。"""
        return self.get_member_count() >= self.rules['max players']

    def modify_rules(self, new_rules, sid):
        """修改房间规则。"""
        self.rules.update(new_rules)
        self.log = f"{datetime.now().isoformat()} {self.members[sid]['name']} 修改了房间规则"
        logging.info(f"✅ 房间 {self.name} 的规则已更新: {self.rules}")
        self.update_clients("房间规则已更新")

    def set_player_ready(self, sid, is_ready):
        """设置玩家的准备状态。"""
        if sid in self.members:
            self.members[sid]['ready'] = is_ready
            log_msg = f"{self.members[sid]['name']} {'准备' if is_ready else '取消准备'}"
            self.update_clients(log_msg)
            self.check_all_ready_to_start()

    def check_all_ready_to_start(self):
        """检查是否所有玩家都已准备好，如果是，则开始游戏倒计时。"""
        if self.status != 'waiting':
            return
        if self.get_member_count() == self.rules['max players'] and all(m['ready'] for m in self.members.values()):
            self.sio.start_background_task(self._start_game_countdown)

    # --- 状态广播 ---
    def get_room_state(self):
        """获取房间的当前状态字典。"""
        return {
            'game': self.game,
            'name': self.name,
            'id': self.id,
            'owner': self.owner,
            'members': self.members,
            'rules': self.rules,
            'status': self.status,
            'log': self.log
        }

    def update_clients(self, log_message=None):
        """
        根据游戏状态，向客户端广播房间或游戏的最新状态。
        """
        logging.info(f"142 update_clients 广播房间/游戏状态更新, log_message: {log_message}")
        # --- 情况1: 游戏正在进行中 ---
        if self.status == 'playing' and self.game_instance:
            # 获取公共游戏状态
            public_state = self.game_instance.getgamestate()
            if log_message:
                public_state['report'] = log_message
            
            # 广播公共游戏状态
            self.sio.emit('game_state_update', public_state, room=self.id)

            # 向每个玩家分别发送其私有游戏状态
            for p in self.game_instance.players:
                private_state = self.game_instance.getgamestate(playerid=p.id)
                player_sid = self.player_id_to_sid.get(p.id)
                if player_sid:
                    self.sio.emit('private_state_update', private_state, room=player_sid)
        
        # --- 情况2: 游戏处于等待或结束状态 ---
        elif self.status == 'finished' and self.game_instance: # 这段代码现阶段不会执行
            # 游戏已结束，暴露所有玩家的手牌
            hands = {p.id: p.hands for p in self.game_instance.players}
            self.sio.emit('expose_hands', hands, room=self.id)
        else:
            # 如果提供了日志消息，更新房间的日志
            if log_message:
                self.log = f"{datetime.now().isoformat()} {log_message}"
            
            # 广播房间大厅的状态
            self.sio.emit('room_info_update', {"success": True,"message": "获取成功", "members": self.members}, room=self.id)

    # --- 游戏核心逻辑 ---
    def handle_player_action(self, sid, data):
        """处理来自客户端的游戏内动作，充当控制器角色。"""
        logging.info('179 handle_player_action 收到玩家动作请求')
        action_type = data.get('action')
        player_id = self.sid_to_player_id.get(sid)
        if player_id is None: return
        print('Player: ', player_id, 'Action: ', action_type, data)  # --- IGNORE ---

        try:
            if self.status != 'playing':
                raise NotAcceptTime("游戏当前未在进行中。")
            
            # --- 新增分支：处理自摸胡 ---
            # 检查这是否是一个对摸牌的响应 (而不是对别人出牌的响应)
            is_self_draw_action = (self.game_instance.playerindex == player_id and self.game_instance.pending_claims.get('hu') is not None)
            # is_self_dark_kong_action = (self.game_instance.playerindex == player_id and self.game_instance.pending_claims.get('kong') is not None)
            if action_type == 'discard':
                self._handle_discard(player_id, data)
            elif action_type == 'hu' and is_self_draw_action:
                logging.info('_handle_self_drawn_hu 处理自摸胡请求')
                self._handle_self_drawn_hu(player_id)
            # elif action_type == 'kong' and is_self_dark_kong_action:
            #     logging.info('_handle_self_dark_kong 处理自摸暗杠请求')
            #     self._handle_self_dark_kong(player_id)
            # --- 结束新增分支 ---
            elif action_type in ['hu', 'pong', 'kong', 'chow']:
                self._handle_claim(sid, player_id, data)
            else:
                raise ValueError("未知的游戏操作")
                
        except (ValueError, NotAcceptTime, AlreadyActed) as e:
            player_name = self.members.get(sid, {}).get('name', '未知玩家')
            logging.warning(f"玩家 {player_id} ({player_name}) 操作无效: {e}")
            self.sio.emit('game_action_result', {'success': False, 'message': str(e)}, room=sid)

    # --- 新增函数：处理自摸胡 ---
    def _handle_self_drawn_hu(self, player_id):
        """立即处理玩家的自摸胡动作。"""
        logging.info('_handle_self_drawn_hu')
        player = self.game_instance.players[player_id]
        # 再次验证是否真的能胡
        if player.can_hu(player.new, self.game_instance.sort_rule, self.game_instance.gamerule):
            logging.info(f"玩家 {player.name} 确认自摸胡牌。")
            # 直接调用游戏结束逻辑
            self.game_instance.endgame(winner_id=player_id, reason='self_drawn_hu')
            self.end_game(f"玩家 {player.name} 自摸胡牌！")
        else:
            # 如果因为某些原因客户端发送了错误的请求，记录日志并忽略
            logging.warning(f"玩家 {player.name} 尝试自摸胡牌，但验证失败。")
            self.sio.emit('game_action_result', {'success': False, 'message': '无效的胡牌操作'}, room=self.player_id_to_sid.get(player_id))
    def _handle_self_dark_kong(self, player_id):
        logging.info('_handle_self_dark_kong')
        player = self.game_instance.players[player_id]
        self.game_instance.new_tile()
        self.sio.emit('game_action_result', {'success': True, 'name': player.name, 'type': 'kong', 'message': f'玩家 {player.name} 完成了 暗杠'}, room=self.id)
        self.update_clients(f"玩家 {player.name} 执行了 暗杠 操作。")
        logging.info(f"玩家 {player.name} 确认暗杠。")


    def _handle_discard(self, player_id, data):
        """处理出牌动作，调用游戏引擎并处理结果。"""
        logging.info('224 _handle_discard')
        tile_index = data.get('tileindex')
        result = self.game_instance.perform_discard(player_id, tile_index)
        
        player_name = self.game_instance.players[player_id].name
        discarded_char = _replacements.get(result['tile'], result['tile'])
        self.update_clients(f"玩家 {player_name} 打出了: {discarded_char}")
        self.sio.emit('game_action_result', {'success': True, 'type': 'discard', 'name': player_name, 'message': f'{player_name} 打出了 {discarded_char}'}, room=self.id)

        if result['claims_pending']:
            action_time = time.time()
            self.action_history[action_time] = False # 标记当前有玩家可以响应
            print('有玩家可以响应，等待响应...') 
            self.tmp_discarder = self.game_instance.playerindex
            self.game_instance.playerindex = 5
            self.update_clients(f"玩家 {player_name} 出牌后，等待其他玩家响应...")
            self.sio.start_background_task(self._process_claims_after_delay, action_time, True)
        else:
            print('没有玩家可以响应，直接下一个')
            self.sio.start_background_task(self._transition_to_next_turn)

    def _handle_claim(self, sid, player_id, data):
        """处理宣告动作，调用游戏引擎并通知客户端。"""
        logging.info('244 _handle_claim')
        if self.game_instance.playerindex == 5:
            self.game_instance.submit_claim(player_id, data) # 以后可以添加返回值以确认是否是最高优先级的动作，如果是则直接执行一个 delay 为 false 的 process_claims_after_delay
            self.sio.emit('game_action_result', {'success': True, 'message': '操作已提交，等待其他玩家...'}, room=sid)
        else: 
            logging.warning(f"玩家 {player_id} 试图在非响应时间宣告。")    

    def _process_claims_after_delay(self, action_time, delay: bool):
        """在延迟后处理所有已提交的宣告。"""
        logging.info("249 _process_claims_after_delay 处理玩家宣告前的延迟...")
        delay = self.rules.get('special delay', 5)
        if delay:
            self.sio.sleep(delay)
        game = self.game_instance
        
        if self.tmp_discarder is not None:
            game.playerindex = self.tmp_discarder
            self.tmp_discarder = None

        # 游戏引擎现在自己处理提交的动作
        result = game.process_submitted_claims()
        for p in game.players:
            p.actions = None    

        # 如果游戏因胡牌而结束
        if game.status == 'finished':
            # endgame 方法会在内部被调用，这里只需确保客户端更新
            self.end_game(f"玩家 {game.players[game.winner_id].name} 胡牌")
            return

        if result:
            actor_id = result['id']
            action_type = result['action']
            actor_player = game.players[actor_id]

            
            game.turntonext(actor_id=actor_id)
            if action_type == 'kong':
                game.new_tile()
            self.sio.emit('game_action_result', {'success': True, 'name': actor_player.name, 'type': action_type, 'message': f'玩家 {actor_player.name} 完成了 {action_type}'}, room=self.id)
            self.update_clients(f"玩家 {actor_player.name} 执行了 {action_type} 操作。")
            if not actor_player.hands:
                self.end_game("荒庄(有玩家无牌可打)")
                return
            self.action_history[action_time] = True # 标记此轮有玩家执行了动作, 以后可以添加更纤细的记录
        else: # 没有人执行动作
            if game.status == 'playing':
                 self._transition_to_next_turn()
                 del self.action_history[action_time] # 清理记录


    def _transition_to_next_turn(self):
        """轮到下一位玩家。"""
        logging.info("289 _transition_to_next_turn 轮到下一位玩家...")
        game = self.game_instance
        if not game.wall:
            self.end_game("牌墙已空，游戏荒庄！")
            return

        game.turntonext()
        next_player_id = game.playerindex
        next_player = game.players[next_player_id]
        newly_drawn_tile = game.new_tile()
        
        if not newly_drawn_tile:
            self.end_game("牌墙已空，游戏荒庄！")
            return
            
        logging.info(f"玩家 {next_player.name} 摸到了: {newly_drawn_tile}")
        
        # 检查自摸
        if next_player.can_hu(newly_drawn_tile, game.sort_rule, game.gamerule):
            game.pending_claims = {'hu': {next_player_id: 0}}
            # 确保 actions 是一个字典，然后再赋值
            if next_player.actions is None:
                next_player.actions = {}
            next_player.actions['hu'] = True
            logging.info(f"玩家 {next_player.name} 可以自摸胡牌。")
            self.update_clients(f"轮到玩家 {next_player.name} 摸牌。")
            return
        # if next_player.can_kong(newly_drawn_tile):
        #     game.pending_claims = {'kong': {next_player_id: 5}}
        #     if next_player.actions is None:
        #         next_player.actions = {}
        #     next_player.actions['kong'] = newly_drawn_tile
        #     logging.info(f"玩家 {next_player.name} 可以杠牌。")

        # elif next_player._can_kong():
        #     game.pending_claims = {'kong': {next_player_id: 5}}
        #     if next_player.actions is None:
        #         next_player.actions = {}
        #     next_player.actions['kong'] = True
        #     logging.info(f"玩家 {next_player.name} 可以杠牌。")

        self.update_clients(f"轮到玩家 {next_player.name} 摸牌。")


    def end_game(self, reason):
        """结束当前游戏。"""
        if self.status == 'finished':
            return
        
        logging.info(f"320 end_game 游戏结束: {reason}")
        
        winner_name = "荒庄"
        if self.game_instance and self.game_instance.winner_id is not None:
            winner_name = self.game_instance.players[self.game_instance.winner_id].name
        
        # 确保游戏引擎状态也设置为 'finished'
        if self.game_instance and self.game_instance.status != 'finished':
            self.game_instance.endgame(reason=reason)
            
        self.status = 'finished'
        self.sio.emit('game_over', {'success': True, 'reason': reason, 'winner': winner_name}, room=self.id)
        self.sio.sleep(3)
        self.status = 'waiting'
        for p in self.members.values():
            p['ready'] = False
        logging.info(f"取消玩家的准备状态, {self.members}")
        self.sio.emit('chat_message', {'type': 'log', 'level': 'info', 'message': f'游戏结束！{reason}。胜利者: {winner_name}'}, room=self.id) 
        self.update_clients(f"游戏结束！{reason}。胜利者: {winner_name}")

    def _start_game_countdown(self):
        """游戏开始倒计时。"""
        logging.info(f"341 _start_game_countdown 房间 {self.name} 准备开始倒计时...")
        self.game_instance = None # 重置游戏实例

        for i in range(3, 0, -1):
            self.sio.emit('chat_message', {
                'type': 'log',
                'level': 'info',
                'message': f"游戏将在 {i} 秒后开始..."
                }, room=self.id)
            self.sio.sleep(1)

        # 倒计时结束后再次检查状态，防止有玩家退出
        if self.get_member_count() != self.rules['max players'] or not all(m['ready'] for m in self.members.values()):
            self.update_clients("有玩家取消准备或离开，游戏开始已取消")
            return
        
        self.start_game()
        self.update_clients("游戏开始！")

    def start_game(self):
        """初始化并开始麻将游戏。"""
        if self.status == 'playing':
            return

        player_sids = list(self.members.keys())
        player_names = [self.members[sid]['name'] for sid in player_sids]
        
        self.game_instance = Mahjong.MahjongServer(playersnames=player_names)
        self.status = 'playing'
        self.sid_to_player_id = {sid: i for i, sid in enumerate(player_sids)}
        self.player_id_to_sid = {i: sid for sid, i in self.sid_to_player_id.items()}

        # 1. 初始化游戏引擎
        self.game_instance.start(dice=random.randint(2, 12))
        
        # 2. 庄家摸开局第一张牌
        dealer = self.game_instance.players[self.game_instance.playerindex]
        self.game_instance.new_tile()

        # 3. 为每个玩家单独发送初始化信息
        golden_tile = self.game_instance.golden_tile
        self.sio.emit('chat_message', {'type': 'log', 'level': 'info', 'message': f'本局游戏金牌是 {_replacements.get(golden_tile, golden_tile)}'}, room=self.id)
        for p in self.game_instance.players:
            player_sid = self.player_id_to_sid.get(p.id)
            if player_sid:
                self.sio.emit('game_initialized', {
                    'my_id': p.id
                }, room=player_sid)

        # 4. 广播公共状态并通知庄家出牌
        golden_tile_char = _replacements.get(golden_tile, golden_tile)
        self.update_clients(f"游戏开始！金牌是 {golden_tile_char}。")
        # self._notify_player_to_discard(dealer.id)