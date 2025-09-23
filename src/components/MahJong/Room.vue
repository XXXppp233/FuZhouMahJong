<!-- 进入房间后展示此组件 -->

<template>
  <div class="first-half">
    <Chat :myname="status.username" />
    <div class="other-players">
      <OtherInfo v-for="(member, sid) in members" :sid="sid" />
    </div>
  </div>
  <CharacterDeck />
</template>

<script setup>
import Chat from './Chat.vue'
import CharacterDeck from './CharacterDeck.vue'
import OtherInfo from './OtherInfo.vue'
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { socket } from '@/socket'
import { statusStore } from '@/stores/status'

const status = statusStore()
const members = computed(() => status.getMembers(status.mysid)) // 其他玩家的信息

// myinfo -> {
//   id: 0 | 1 | 2 | 3
//   name: str
//   ready: bool
//   ip: str
//   decorator: { org: str, chara: str} | null
// // }
// members -> {
//   sid: {
//     id: 0 | 1 | 2 | 3
//     name: str
//     ready: bool
//     ip: str
//     decorator: { org: str, chara: str} | null
//   }
// }

onMounted(() => {
  socket.on('player_left', (data) => {
    //目前没有断线重连机制，游戏中掉线直接结束游戏。
    delete status.members[data.sid]
    console.log('Player left:', data.sid, status.members)
  })
})
onUnmounted(() => {
  socket.off('player_left')
})
</script>

<style scoped></style>
