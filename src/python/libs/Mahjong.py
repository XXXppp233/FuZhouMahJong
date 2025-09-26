import random
from collections import Counter
import logging

# (MahjongPlayer 类和自定义异常基本不变，这里为了简洁省略，仅展示 MahjongServer 的变化)
class NotAcceptTime(Exception): pass
class AlreadyActed(Exception): pass

class MahjongPlayer:
    # ... (这个类的内容保持不变) ...
    def __init__(self, id, name):
        """玩家实例拥有 id 和名字，以及手牌、锁牌、新牌、已经打出的牌，开始游戏后才使用这里的玩家实例"""
        self.id = id
        self.sid = None
        self.decorator = None # 未来会添加个性化支持
        self.name = name
        self.hands = []  # 玩家手牌
        self.locked = []  # 已经碰杠吃的牌
        self.new = ''
        self.discarded = []  # 已经打出的牌
        self.actions = None
        self.active = False

    def can_chow(self, tile, sort_rules):  # tile is list or tuple
        """判断能否吃牌, tile 是要吃的牌，sort_rules 由 MahjongServer 提供"""
        if 'joker' in tile or tile[0] in 'eswnbfz': return []
        possible_chows = []; tile_val = sort_rules.get(tile); tile_suit = tile[-1]
        if tile_val is None: return []
        # (t-2, t-1), t
        c1 = next((t for t, v in sort_rules.items() if v == tile_val - 2 and t[-1] == tile_suit), None)
        c2 = next((t for t, v in sort_rules.items() if v == tile_val - 1 and t[-1] == tile_suit), None)
        if c1 in self.hands and c2 in self.hands: possible_chows.append(tuple(sorted([c1, c2], key=lambda t: sort_rules.get(t))))
        # (t-1, t+1), t
        c1 = next((t for t, v in sort_rules.items() if v == tile_val - 1 and t[-1] == tile_suit), None)
        c2 = next((t for t, v in sort_rules.items() if v == tile_val + 1 and t[-1] == tile_suit), None)
        if c1 in self.hands and c2 in self.hands: possible_chows.append(tuple(sorted([c1, c2], key=lambda t: sort_rules.get(t))))
        # t, (t+1, t+2)
        c1 = next((t for t, v in sort_rules.items() if v == tile_val + 1 and t[-1] == tile_suit), None)
        c2 = next((t for t, v in sort_rules.items() if v == tile_val + 2 and t[-1] == tile_suit), None)
        if c1 in self.hands and c2 in self.hands: possible_chows.append(tuple(sorted([c1, c2], key=lambda t: sort_rules.get(t))))
        logging.info(f"Player {self.name} can chow with tile {tile}: {possible_chows}") # 仅在服务端可见，不会广播给客户端
        return list(set(possible_chows))
    
    def can_hu(self, tile=None, sort_rules=None, gamerule=None):
        """tile 为其他人打出的牌或者新摸的牌, 检查玩家是否可以胡牌"""
        hands = self.hands.copy()
        if tile:
            hands.append(tile)  # 将要胡的牌加入手牌
        counts = Counter(hands)
        joker_count = counts.pop('joker', 0)

        if gamerule.get('three golden win', True) and joker_count >= 3:
            logging.info(f"Player {self.name} can hu with three jokers")
            return True
        if gamerule.get('allow seven pairs', False) and self.can_seven_pairs(counts, joker_count):
            logging.info(f"Player {self.name} can hu with seven pairs")
            return True
         # 规则3: 标准胡牌 (n * ABC/AAA + DD)
        # 找出所有可能的对子（将牌）
        possible_pairs = [t for t, c in counts.items() if c >= 2]
        # 如果牌不够凑成对子，可以用金来凑
        if joker_count > 0:
            possible_pairs.extend([t for t, c in counts.items() if c == 1])
        # 甚至可以用两张金自成一对
        if joker_count >= 2:
            possible_pairs.append('joker_pair')

        # 遍历每一种可能的对子
        for pair_tile in set(possible_pairs):
            temp_counts = counts.copy()
            temp_joker_count = joker_count
            
            if pair_tile == 'joker_pair':
                temp_joker_count -= 2
            elif temp_counts[pair_tile] == 1:
                temp_counts.pop(pair_tile)
                temp_joker_count -= 1
            else:
                temp_counts[pair_tile] -= 2
                if temp_counts[pair_tile] == 0:
                    temp_counts.pop(pair_tile)
            
            # 检查剩下的牌能否组成顺子或刻子
            if self._can_form_melds(temp_counts, temp_joker_count, sort_rules):
                logging.info(f"Player {self.name} can hu with standard melds.")
                return True
        return False
    def _can_form_melds(self, counts, joker_count, sort_rules):
        """递归辅助函数，检查手牌能否组成顺子或刻子"""
        if not counts:
            return True # 所有牌都已组成面子

        # 从最小的牌开始尝试
        tile = min(counts.keys(), key=lambda t: sort_rules.get(t, 99))
        
        # 尝试组成刻子 (AAA)
        if counts[tile] >= 3:
            new_counts = counts.copy()
            new_counts[tile] -= 3
            if new_counts[tile] == 0:
                del new_counts[tile]
            if self._can_form_melds(new_counts, joker_count, sort_rules):
                return True
        # 尝试用金补刻子
        if counts[tile] == 2 and joker_count >= 1:
            new_counts = counts.copy()
            del new_counts[tile]
            if self._can_form_melds(new_counts, joker_count - 1, sort_rules):
                return True
        if counts[tile] == 1 and joker_count >= 2:
            new_counts = counts.copy()
            del new_counts[tile]
            if self._can_form_melds(new_counts, joker_count - 2, sort_rules):
                return True

        # 尝试组成顺子 (ABC)，仅对万、条、筒有效
        tile_val = sort_rules.get(tile)
        if tile_val and tile[0] not in 'eswnbfzjapoc':  # 排除风牌和花牌
            tile_suit = tile[-1]
            c2_val = tile_val + 1
            c3_val = tile_val + 2
            c2 = next((t for t, v in sort_rules.items() if v == c2_val and t[-1] == tile_suit), None)
            c3 = next((t for t, v in sort_rules.items() if v == c3_val and t[-1] == tile_suit), None)

            if c2 and c3:
                # 尝试不同的组合方式，优先使用手上的牌
                # 1. 手上有 c2, c3
                if c2 in counts and c3 in counts:
                    new_counts = counts.copy()
                    new_counts[tile] -= 1; new_counts[c2] -= 1; new_counts[c3] -= 1
                    # 清理数量为0的牌
                    new_counts = {k: v for k, v in new_counts.items() if v > 0}
                    if self._can_form_melds(new_counts, joker_count, sort_rules):
                        return True
                # 2. 手上有 c2, 缺 c3 (用金补)
                if c2 in counts and c3 not in counts and joker_count >= 1:
                    new_counts = counts.copy()
                    new_counts[tile] -= 1; new_counts[c2] -= 1
                    new_counts = {k: v for k, v in new_counts.items() if v > 0}
                    if self._can_form_melds(new_counts, joker_count - 1, sort_rules):
                        return True
                # 3. 手上有 c3, 缺 c2 (用金补)
                if c3 in counts and c2 not in counts and joker_count >= 1:
                    new_counts = counts.copy()
                    new_counts[tile] -= 1; new_counts[c3] -= 1
                    new_counts = {k: v for k, v in new_counts.items() if v > 0}
                    if self._can_form_melds(new_counts, joker_count - 1, sort_rules):
                        return True
                # 4. 缺 c2, c3 (用两金补)
                if c2 not in counts and c3 not in counts and joker_count >= 2:
                    new_counts = counts.copy()
                    new_counts[tile] -= 1
                    new_counts = {k: v for k, v in new_counts.items() if v > 0}
                    if self._can_form_melds(new_counts, joker_count - 2, sort_rules):
                        return True

        return False # 如果所有组合都失败 

    def can_kong(self, tile):
        """检查玩家是否由三张相同牌"""
        if tile == 'joker': return False
        return self.hands.count(tile) == 3
    def _can_kong(self):
        """检查玩家是否有四张相同牌"""
        counts = Counter(self.hands)
        for tile, count in counts.items():
            if tile != 'joker' and count == 4:
                return tile
        return None
    def can_pong(self, tile):
        """检查玩家是否有两张相同牌"""
        if tile == 'joker': return False
        return self.hands.count(tile) >= 2
    def can_seven_pairs(self, counts, joker_count):
        """辅助函数，手牌数不为 13 时，服务端自动设定 allow seven pairs 为 False"""
        """检查金牌能否填补七对的空缺"""
        holes = sum(count % 2 for count in counts.values())
        return joker_count >= holes and (joker_count - holes) % 2 == 0
    def drawtile(self,tile = None):     # 摸牌
        if tile and self.new == '':
            """设置新牌, tile 是新摸的牌"""
            self.new = tile
            logging.info(f"Player {self.name} has a new tile: {tile}")
        return self.new    

    def integrate_new_tile(self):
        """将新摸的牌 self.new 正式放入手牌，并清空 self.new"""
        if self.new:
            self.hands.append(self.new)
            self.new = ''

    def discard(self, tile_index = None):
        """
        出牌。如果指定 tile_index，则从手牌打出；否则打出刚摸的牌 self.new。
        """
        if tile_index is not None and tile_index in range(len(self.hands)):
            # 从手牌中打出一张
            tile = self.hands.pop(tile_index)
        elif self.new:
            # 打出新摸的牌
            tile = self.new
            self.new = ''
        else:
            # 索引无效或无新牌，为防止崩溃，打出最后一张牌
            logging.warning(f"Invalid discard index or no new tile, discarding last tile.")
            tile = self.hands.pop(-1)

        self.discarded.append(tile)
        logging.info(f"Player {self.name} discarded tile: {tile}")
        return tile
    
    def sort_hands(self, sort_rule):
        """对手牌进行排序, 规则在 MahjongServer 中定义"""
        self.hands.sort(key=lambda x: sort_rule.get(x, -1))

    def chow(self, tile, chow_pair, sort_rule):
        """吃牌, tile 是要吃的牌，chow_pair 是吃的牌对"""
        melds = sorted([tile] + list(chow_pair), key=lambda t: sort_rule.get(t, -1))
        for meld in melds:
            self.locked.append(meld)
        for t in chow_pair:
            self.hands.remove(t)
    def kong(self, tile):
        """杠牌, tile 是要杠的牌"""
        for _ in range(4):
            self.locked.append(tile)
        # 杠牌后需要补一张牌，这个逻辑由服务端处理
        for _ in range(3):
            self.hands.remove(tile)
    def dark_kong(self, tile=None):
        """暗杠不会记录到 locked 上"""
        if self.new and self.hands.count(self.new) == 3: # 摸到的新牌能杠
            for _ in range(3):
                self.hands.remove(self.new)
            self.new = ''
        elif self.hands.count(tile) == 4: # 手上有四张能杠
            for _ in range(4):
                self.hands.remove(tile)



    def pong(self, tile):
        """碰牌, tile 是要碰的牌"""
        for _ in range(3):
            self.locked.append(tile)
        for _ in range(2):
            self.hands.remove(tile)      


class MahjongServer:
    def __init__(self, playersnames=None):
        # ... (原有属性不变) ...
        self.players = [MahjongPlayer(i, name) for i, name in enumerate(playersnames or ['Player1', 'Player2', 'Player3', 'Player4'])]
        self.playerindex = 0
        # 新增: 存储当前回合的临时状态
        self.pending_claims = {}
        self.submitted_claims = {}
        self.last_discarded_tile = None
        self.status = 'waiting' # waiting, playing, finished
        self.winner_id = None   # 记录胜利者ID
        self.winner_hands = []  # 胜利者的手牌
        self.acceptspecialactions = False
        self.golden_tile = None  # 金牌
        self.sort_rule = {
            '1o': 2, '2o': 3, '3o': 4, '4o': 5, '5o': 6, '6o': 7, '7o': 8, '8o': 9, '9o': 10,
            '1t': 12, '2t': 13, '3t': 14, '4t': 15, '5t': 16, '6t': 17, '7t': 18, '8t': 19, '9t': 20,
            '1w': 22, '2w': 23, '3w': 24, '4w': 25, '5w': 26, '6w': 27, '7w': 28, '8w': 29, '9w': 30,
            'e': 32, 's': 34, 'w': 36, 'n': 38, 'b': 42, 'f': 44, 'z': 46, 'joker': 0,
            'spring': 50, 'summer': 53, 'autumn': 56, 'winter': 59,
            'plum': 62, 'orchid': 65, 'bamboo': 68, 'chrysanthemum': 71
            }
        self.wall = []  # 剩余牌堆
        self.gamerule = {
            "rules": "classic",
            "max players": 4,
            "tiles number": 16,
            "golden tile": True,
            "golden tile number": 4,
            "three golden win": True,
            "allow seven pairs": False,
            "items to remove": ["spring", "summer", "autumn", "winter", "plum", "orchid", "bamboo", "chrysanthemum", "joker"]
        }


    # ... (getgamestate, getgamerule, shuffle, deal, new_tile, turntonext 不变) ...
    def getgamestate(self, playerid=None):
        """
        获取游戏状态的核心方法 (已修改)
        现在返回一个更结构化的 "players" 列表
        """
        if playerid is not None:
            return {
                "hands": self.players[playerid].hands,
                "locked": self.players[playerid].locked,
                "new": self.players[playerid].new,
                "discarded": self.players[playerid].discarded,
                "id":self.players[playerid].id,
                "actions": self.players[playerid].actions,
                "active": self.players[playerid].active # 由客户端计算是否 Active
            }
        else:
            return {
                "playerindex": self.playerindex,
                "wall_count": len(self.wall),
                "players": [
                    {
                        "active": p.active, # true or false
                        "hasnew": bool(p.new),
                        "id": p.id,
                        "name": p.name,
                        "hand_count": len(p.hands),
                        "locked": p.locked,
                        "discarded": p.discarded
                    } for p in self.players
                ],
            }
    def getgamerule(self):
        return self.gamerule
    def shuffle(self, dice = 2):
        """洗牌"""
        tileswall = [item for item in self.sort_rule if item not in self.gamerule.get("items to remove", [])]
        logging.info(f"Tiles removed: {self.gamerule['items to remove']}")  
        
        self.wall = [name for name in tileswall for _ in range(4)]
        random.shuffle(self.wall)
        jokertile = self.wall[-dice]
        self.golden_tile = jokertile
        if self.gamerule.get("golden tile", True):
            logging.info(f"{jokertile} is the golden tile")
            self.wall = ['joker' if tile == jokertile else tile for tile in self.wall]
        if self.gamerule['golden tile number'] == 3:
            self.wall.pop(-dice)
        logging.info(f"完成洗牌")

    def deal(self):
        """发牌"""
        tilesnumber = self.gamerule['tiles number']
        for player in self.players:
            player.hands = self.wall[:tilesnumber]
            self.wall = self.wall[tilesnumber:]
            player.sort_hands(self.sort_rule)
            logging.info(f"Player {player.name} dealt hands: {player.hands}")  
    def new_tile(self):
        """摸牌"""
        if not self.wall:
            logging.warning("No more tiles in the wall")
            return None
        tile = self.wall.pop(0)
        self.players[self.playerindex].drawtile(tile)
        return tile
    def turntonext(self, actor_id=None): # 提供 id 则以 id 为准，不提供则按顺序推进
        """轮转到下一个玩家"""
        if actor_id is not None:
            self.playerindex = actor_id
        else:
            self.playerindex = (self.playerindex + 1) % len(self.players)
        logging.info(f"Turn is now on player index: {self.playerindex}")


    def checkactions(self, tile):
        # ... (此方法逻辑不变) ...
        """
        检查其他玩家对打出的牌 `tile` 是否可以执行 吃/碰/杠/胡 操作。
        此方法会调用 Player 的 can 系列函数，并将所有可行操作统计到每个 player 实例的 
        self.actions 属性中，然后填充服务端的 self.pending_claims 以便进行优先级裁决。
        """
        # 1. 先清空所有玩家的 actions，准备重新计算
        for p in self.players:
            p.actions = {}

        indexmap = { 0: [1,2,3], 1: [2,3,0], 2: [3,0,1], 3: [0,1,2] }
        server_actions = { 'hu': {}, 'kong': {}, 'pong': {}, 'chow': {} }
        checkpoint = False

        # 2. 遍历除了出牌玩家之外的所有玩家
        for player in self.players:
            if player.id == self.playerindex:
                continue

            # 3. 调用 can 系列函数检查各种可能性
            can_hu = player.can_hu(tile, self.sort_rule, self.gamerule)
            can_kong_val = player.can_kong(tile)
            can_pong_val = player.can_pong(tile)
            
            # 只有下家能吃
            possible_chows = []
            if player.id == (self.playerindex + 1) % len(self.players):
                possible_chows = player.can_chow(tile, self.sort_rule)

            # 4. 将可行操作统计到 player.actions
            if can_hu:
                player.actions['hu'] = tile
            if can_kong_val:
                player.actions['kong'] = tile
            if can_pong_val:
                player.actions['pong'] = tile
            if possible_chows:
                player.actions['chow'] = possible_chows

            # 5. 如果玩家有任何可行操作，填充服务端的 server_actions 用于后续优先级处理
            if player.actions:
                # 'hu' 的优先级根据出牌顺序决定
                priority = indexmap[self.playerindex].index(player.id)
                if 'hu' in player.actions:
                    server_actions['hu'][player.id] = priority
                    checkpoint = True
                # 碰和杠的优先级固定，低于胡
                if 'kong' in player.actions:
                    server_actions['kong'][player.id] = 5
                    checkpoint = True
                if 'pong' in player.actions:
                    server_actions['pong'][player.id] = 6
                    checkpoint = True
                # 吃的优先级最低
                if 'chow' in player.actions:
                    server_actions['chow'][player.id] = 7
                    checkpoint = True

        # 更新服务端的 pending_claims，只保留有玩家可以执行的动作类型
        self.pending_claims = {k: v for k, v in server_actions.items() if v}

        if checkpoint:
            logging.info(f"Actions available for tile {tile}: {self.pending_claims}")
            # 额外打印出每个玩家的具体可行操作
            for p in self.players:
                if p.actions:
                    logging.info(f"Player {p.name} (ID: {p.id}) can perform: {p.actions}")
            return True        
        else:
            logging.info(f"No actions available for tile {tile}")
            return False

    def endgame(self, winner_id=None, reason="unknown", win_tile=None):
        if self.status == 'finished':
            logging.warning("游戏已经结束。")
            return
        
        self.status = 'finished'
        self.winner_id = winner_id
        

        if reason == 'hu' and winner_id is not None and win_tile is not None:
            winner_name = self.players[winner_id].name
            self.winner_hands = self.players[winner_id].hands.copy() + [win_tile]
            self.winner_hands.sort(key=lambda x: self.sort_rule.get(x, -1))
            logging.info(f"🎉 游戏结束！玩家 {winner_name} 点炮胡牌，胡的牌是: {win_tile}")
        elif reason == 'self_drawn_hu' and winner_id is not None:
            winner_name = self.players[winner_id].name
            logging.info(f"🎉 游戏结束！玩家 {winner_name} 自摸胡牌！")
            self.winner_hands = self.players[winner_id].hands.copy() + [self.players[winner_id].new]
            self.winner_hands.sort(key=lambda x: self.sort_rule.get(x, -1))
        elif reason == 'draw':
            logging.info("牌墙已空，游戏荒庄。")
        else:
            logging.info(f"游戏因 '{reason}' 结束")
        
        return self.getgamestate()

    def start(self, dice=2):
        """开始游戏"""
        if self.status == 'playing':
            logging.warning("Game already started")
            return None
        self.shuffle(dice)
        self.deal()
        # 庄家是ID 0的玩家
        self.playerindex = 0
        self.status = 'playing'
        logging.info("Game started")
        return self.getgamestate()


    # --- 新增/重构的公共方法 ---

    def perform_discard(self, player_id, tile_index):
        """
        处理玩家的出牌动作，包含所有验证逻辑。
        :return: 包含出牌结果的字典。
        """
        if player_id != self.playerindex:
            raise NotAcceptTime("现在不是你的出牌回合。")

        player = self.players[player_id]
        discarded_tile = player.discard(tile_index)
        if player.new:
            player.integrate_new_tile()
        player.sort_hands(self.sort_rule)
        
        self.last_discarded_tile = discarded_tile
        isPending =  self.checkactions(discarded_tile)
        

        return {
            "tile": discarded_tile,
            "claims_pending": isPending
        }

    def submit_claim(self, player_id, data):
        """
        接收并验证玩家的宣告动作（吃碰杠胡）。
        :raises: NotAcceptTime, AlreadyActed, ValueError
        """
        action_type = data['action']
        if not self.pending_claims or action_type not in self.pending_claims or player_id not in self.pending_claims[action_type]:
            logging.info(f"Player {self.players[player_id].name} cannot perform action '{action_type}' now.")
            return
        if player_id in self.submitted_claims:
            logging.info(f"Player {self.players[player_id].name} has already submitted an action this round.")
            return

        claim_data = action_type
        if action_type == 'chow':
            chow_pair = tuple(sorted(data.get('tiles', [])))
            possible_chows = self.players[player_id].can_chow(self.last_discarded_tile, self.sort_rule)
            if chow_pair not in possible_chows:
                print(f"Invalid chow pair {chow_pair} for player {player_id}, possible: {possible_chows}")
                return
            claim_data = ('chow', chow_pair)

        self.submitted_claims[player_id] = claim_data
        logging.info(f"玩家 {self.players[player_id].name} 提交了操作: {claim_data}")

    def process_submitted_claims(self):
        """
        处理并执行优先级最高的玩家动作。
        现在此方法直接使用内部的 self.submitted_claims。
        :return: 执行了动作的玩家 ID，如果没有动作被执行则返回 None。
        """
        best_action = None
        best_priority = 10
        actor_id = None

        for pid, action_data in self.submitted_claims.items():
            action_type = action_data[0] if isinstance(action_data, tuple) else action_data
            if pid in self.pending_claims.get(action_type, {}):
                priority = self.pending_claims[action_type][pid]
                if priority < best_priority:
                    best_priority = priority
                    best_action = action_data
                    actor_id = pid
        
        # 清空本轮的临时状态
        self.pending_claims = {}
        self.submitted_claims = {}
        info = None

        if actor_id is not None:
            action_type = best_action[0] if isinstance(best_action, tuple) else best_action
            actor = self.players[actor_id]
            
            # 从出牌者的弃牌堆中移除这张牌，因为它被响应了
            discarding_player = self.players[self.playerindex]
            discarded_tile = discarding_player.discarded.pop(-1)
            
            logging.info(f"Player {actor.name} performs action '{action_type}' on tile {discarded_tile}")

            if action_type == 'hu':
                self.endgame(actor_id, 'hu', discarded_tile)
                info =  {'id': actor_id, 'action': 'hu'}
            elif action_type == 'kong':
                actor.kong(discarded_tile)
                info = {'id': actor_id, 'action': 'kong'}
            elif action_type == 'pong':
                actor.pong(discarded_tile)
                info = {'id': actor_id, 'action': 'pong'}
            elif action_type == 'chow':
                chow_pair = best_action[1]
                actor.chow(discarded_tile, chow_pair, self.sort_rule)
                info = {'id': actor_id, 'action': 'chow'}
            for p in self.players:
                p.actions = None # 重置玩家可执行操作。
        return info