<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { ref, onMounted, computed, onUnmounted, watch } from 'vue'
import { socket } from '@/socket'
import { statusStore } from '@/stores/status'
import { tilesmapStore } from '@/stores/tilesmap'
import MahjongGame from './components/MahJong/MahjongGame.vue'
import Music from './components/MahJong/Music.vue'
import Intro from './components/MahJong/Intro.vue'
import Fail from './components/MahJong/Fail.vue'
import RoomList from './components/MahJong/RoomList.vue'
import Room from './components/MahJong/Room.vue'

const status = statusStore() // status.now = 'nologin' | 'login' | 'room' | 'gaming' | 'fail'
const tilesmap = tilesmapStore()
const now = computed(() => status.now)

onMounted(() => {
  socket.connect() // 初始时连接一次。
  socket.on('connect_res', connect_res)
  socket.on('disconnect', lost_connection)
  socket.on('join_server_result', login_res)
  socket.on('room_list_update', room_list_update)
  socket.on('create_room_result', create_res)
  socket.on('join_room_result', join_room_res)
  socket.on('room_deleted', room_deleted)
  socket.on('leave_room_result', leave_room_res)
  socket.on('room_info_update', room_info_update)
  socket.on('game_initialized', gameini)
  socket.on('game_state_update', GameStateUpdate)
  socket.on('private_state_update', PrivateStateUpdate)
  socket.on('game_over', game_over)
  socket.on('*', (event, ...args) => {
    console.log('Socket event:', event, args)
  })
  console.log(status.now)
})

onUnmounted(() => {
  socket.off('join_server_result', login_res)
  socket.off('room_deleted', room_deleted)
  socket.off('leave_room_result', leave_room_res)
  socket.off('game_initialized', gameini)
  socket.off('game_state_update', GameStateUpdate)
  socket.off('private_state_update', PrivateStateUpdate)
  socket.off('disconnect', lost_connection)
  socket.off('room_list_update', room_list_update)
  socket.off('create_room_result', create_res)
  socket.off('join_room_result', join_room_res)
  socket.off('room_info_update', room_info_update)
  socket.off('game_over', game_over)
  socket.off('connect_res', connect_res)
  socket.off('*')
})

const lost_connection = () => {
  status.lostConnection()
}
const connect_res = (data) => {
  if (data.success) {
    status.connectToServer(data.clientsid)
    console.log(data.message, 'My socket id:', status.mysid)
  } else {
    socket.disconnect()
  }
}
const login_res = (data) => {
  if (data.success) {
    status.sucLogin(data.username)
    status.updateRoomList(data.room_list)
  } else {
    alert(data.message)
  }
}
const room_list_update = (data) => {
  if (data.success) {
    status.updateRoomList(data.room_list)
  } else {
    alert(data.message)
  }
}
const create_res = (data) => {
  if (data.success) {
    // 创建成功
    console.log(data.message)
  } else {
    // 创建失败
    alert(data.message)
  }
}
const join_room_res = (data) => {
  if (data.success) {
    status.joinRoom(data.id)
    socket.emit('get_room_info', status.roomid)
  } else {
    alert(data.message)
  }
}
const room_deleted = (data) => {
  console.log('room_deleted', data)
  if (data.success) {
    status.leaveRoom('房间已解散')
    status.updateRoomList(data.room_list)
  } else {
    alert(data.message)
  }
}
const leave_room_res = (data) => {
  if (data.success) {
    status.leaveRoom('You have left the room')
  } else {
    alert(data.message)
  }
}
const room_info_update = (data) => {
  if (data.success) {
    status.members = data.members
  } else {
    console.log('Failed to get room info:', data.message)
  }
}
const gameini = (data) => {
  status.startGame()
}

const game_over = (data) => {
  if (data.success) {
    const gameinfo = status.getGameInfo()
    socket.emit('chat_message', {
      type: 'log',
      level: 'info',
      message:
        status.username +
        ': ' +
        tilesmap.getTilesFont(gameinfo.locked) +
        ' ' +
        tilesmap.getTilesFont(gameinfo.hands),
    })
    console.log('Game Over:')
    status.endGame()
  } else {
    return
  }
}
const GameStateUpdate = (newState) => {
  // Public game state update
  status.updateGameState(newState, true)
}
const PrivateStateUpdate = (newState) => {
  // Private game state update
  status.updateGameState(newState, false)
}
</script>
<template>
  <!-- <Room :roomid="room_id" /> -->
  <!-- <Music :status="status" /> -->
  <Music v-if="!['nologin', 'disconnected'].includes(now)" />
  <Intro v-if="now === 'nologin'" />
  <RoomList v-if="now === 'login'" />
  <Room v-if="now === 'room'" />
  <MahjongGame v-if="now === 'gaming'" />

  <!-- <BackGround /> -->
  <!-- <MahjongGame /> -->
  <!-- <Test /> -->
  <Fail v-if="now === 'disconnected'" />
</template>

<style></style>
