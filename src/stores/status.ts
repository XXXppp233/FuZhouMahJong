import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

type membersType = {
  [sid: string]: {
    username: string
    ip: string
    ready: boolean
    decorator: {
      org: string
      chara: string
    }
  }
}
type playerType = {
  active: boolean
  hasnew: boolean
  id: number
  name: string
  hand_count: number
  locked: string[]
  discarded: string[]
}

type roomType = {
  id: string
  name: string
  game: string
  members: number
  max_members: number
  has_password: boolean
  status: string // waiting, gaming
}
type GameInfoType = {
  // some Public and all Private info
  init: boolean
  id: number
  activePlayer: 0 | 1 | 2 | 3 | 5 // 5 is a special value meaning no one's turn When someone can chow pong kong or hu
  wallcount: number
  hands: String[]
  locked: String[]
  new: String
  discarded: String[]
  actions: Object
}

export const statusStore = defineStore('status', () => {
  const isTyping = ref(false) // 是否在输入聊天
  const connected = ref(false) // 是否连接上服务器
  const isLogin = ref(false) // 是否登录
  const isRoom = ref(false) // 是否在房间内
  const isGaming = ref(false) // 是否在游戏中
  const username = ref('') // 用户名
  const mysid = ref('') // 用户的socket id
  const myid = ref(0) // 用户在房间内的id 0|1|2|3
  const members = ref<membersType>({}) // 房间内成员基础数据，包括自己
  const players = ref<playerType[] | undefined>(undefined) // 房间内成员游戏数据，包括自己
  const gameinfo = ref<GameInfoType>({
    init: false,
    id: 0,
    activePlayer: 0,
    wallcount: 0,
    hands: [],
    locked: [],
    new: '',
    discarded: [],
    actions: {},
  })
  const roomlist = ref<roomType[]>([]) // 对象的列表
  const roomid = ref('') // 房间号
  const now = computed(() => {
    return connected.value
      ? isLogin.value
        ? isRoom.value
          ? isGaming.value
            ? 'gaming'
            : 'room'
          : 'login'
        : 'nologin'
      : 'disconnected'
  })
  function connectToServer(sid: string) {
    connected.value = true
    mysid.value = sid
  }
  function lostConnection() {
    connected.value = false
    isLogin.value = false
    isRoom.value = false
    isGaming.value = false
    username.value = ''
    mysid.value = ''
    roomid.value = ''
    alert('Lost connection to server. Please refresh the page.')
  }
  function sucLogin(name: string) {
    username.value = name
    isLogin.value = true
    console.log('sucLogin', now.value)
  }
  function logout() {
    username.value = ''
    mysid.value = ''
    roomid.value = ''
    members.value = {}
    players.value = undefined
    myid.value = 0
    reSetGameInfo()
    isLogin.value = false
    isRoom.value = false
    isGaming.value = false
    console.log('logout', now.value)
  }
  function joinRoom(id: string) {
    roomid.value = id
    isRoom.value = true
    console.log('joinRoom', now.value)
  }
  function leaveRoom(reason: string) {
    roomid.value = ''
    players.value = undefined
    myid.value = 0
    members.value = {}
    roomlist.value = [] // 清空房间列表
    isRoom.value = false
    isGaming.value = false
    reSetGameInfo()
    alert(reason)
    console.log('leaveRoom', now.value)
  }
  function startGame() {
    isGaming.value = true
    console.log('startGame', now.value)
  }
  function endGame() {
    isGaming.value = false
    players.value = undefined
    myid.value = 0
    reSetGameInfo()
  }
  function updateRoomList(data: any) {
    roomlist.value = data
  }
  function getMembers(sid = ''): object {
    const allMembers = { ...members.value } // 创建一个副本，防止原数据被 Delete
    if (sid) {
      delete allMembers[sid] // 删除指定sid的成员信息
      return allMembers
    } else return allMembers
  }
  function getInfoBySid(sid: string): object {
    return members.value[sid]
  }
  function getMemberidBySid(sid: string): number {
    return Object.keys(members.value).indexOf(sid)
  }
  function getPlayerById(id: number): playerType | undefined {
    if (players.value) {
      return players.value[id]
    } else return undefined
  }
  function setTyping(status: boolean) {
    isTyping.value = status
    console.log('setTyping', status)
  }
  function reSetGameInfo() {
    gameinfo.value = {
      init: false,
      id: 0,
      activePlayer: 0,
      hands: [],
      locked: [],
      new: '',
      discarded: [],
      actions: {},
      wallcount: 0,
    }
  }
  function reSetActions() {
    gameinfo.value.actions = {}
  }
  function updateGameState(newState: any, isPublic: boolean) {
    if (now.value !== 'gaming') return
    if (isPublic) {
      players.value = newState.players
      if (gameinfo.value.init === false) {
        gameinfo.value.init = true
      }
      gameinfo.value.activePlayer = newState.playerindex
      gameinfo.value.wallcount = newState.wall_count
    } else {
      gameinfo.value.id = newState.id
      gameinfo.value.hands = newState.hands
      gameinfo.value.locked = newState.locked
      gameinfo.value.new = newState.new
      gameinfo.value.discarded = newState.discarded
      gameinfo.value.actions = newState.actions
    }
  }

  function getGameInfo() {
    return gameinfo.value
  }

  return {
    now,
    username,
    mysid,
    roomlist,
    roomid,
    members,
    players,
    isTyping,

    connectToServer,
    lostConnection,
    sucLogin,
    logout,
    updateRoomList,
    updateGameState,
    joinRoom,
    leaveRoom,
    startGame,
    endGame,

    getMembers,
    getInfoBySid,
    getMemberidBySid,
    getPlayerById,
    getGameInfo,
    setTyping,
  }
})
