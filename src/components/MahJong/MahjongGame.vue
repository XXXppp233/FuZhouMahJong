<!-- 游戏开始后展示此页面 -->
// eslint-disable-next-line vue/block-lang
<script setup>
import Chat from './Chat.vue'
import OtherInfo from './OtherInfo.vue'
import MyTiles from './MyTiles.vue'
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { socket } from '@/socket'
import { statusStore } from '@/stores/status'

const status = statusStore()

const showVideo = ref(false)
const videoPlayer = ref(null)
const focusurl = ref('')

const onVideoEnded = () => {
  showVideo.value = false
}
// 测试
const FocusAni = async (organization, charactername) => {
  focusurl.value = `characters/focus/${organization}/${charactername}.webm`
  try {
    const response = await fetch(focusurl.value, { method: 'HEAD' })
    const contentType = response.headers.get('Content-Type')
    if (response.ok && contentType && contentType.startsWith('video')) {
      console.log('video exists:', focusurl.value)
      showVideo.value = true
      await nextTick()
      videoPlayer.value?.play()
    } else {
      console.error(
        'Video not found or incorrect content type:',
        focusurl.value,
        'Content-Type:',
        contentType,
      )
    }
  } catch (error) {
    console.error('Error checking video existence:', error)
  }
}

const props = defineProps({})
const mysid = status.mysid // 不应该被修改

const members = computed(() => {
  const originalMembers = status.getMembers()
  const sidlist = Object.keys(originalMembers)
  const myIndex = sidlist.indexOf(mysid)

  if (myIndex === -1) {
    // 如果找不到我的 sid，直接返回原数据
    return originalMembers
  }

  // 重新排列：从我的位置开始，按顺序排列
  const reorderedSids = [
    ...sidlist.slice(myIndex), // 从我的位置到末尾
    ...sidlist.slice(0, myIndex), // 从开头到我的位置之前
  ]

  // 删除我的 sid（现在在第一个位置）
  const otherSids = reorderedSids.slice(1)

  // 根据重新排序的 sid 列表构建新的 members 对象
  const reorderedMembers = {}
  otherSids.forEach((sid) => {
    reorderedMembers[sid] = originalMembers[sid]
  })

  return reorderedMembers
})
// initdata = {
//   mysid: str,
//   myname: str,
//   decorators: { str: { org: str, chara: str } },
// }

// // PrivateState
// const hands = ref([])
// const locked = ref([])
// const discarded = ref([])
// const newtile = ref('')
// const actions = ref({}) // 可执行的操作
// if can_hu:
//     player.actions['hu'] = True
// if can_kong_val:
//     player.actions['kong'] = True
// if can_pong_val:
//     player.actions['pong'] = True
// if possible_chows:
//     player.actions['chow'] = possible_chows # 存入可行的吃牌组合

// 判断组件需要的数据是否完成初始化
const allowOtherInfo = computed(() => (status.players ? true : false))
console.log('init status.players.value', status.players)
const allowMytiles = computed(() => status.getGameInfo().init)

onMounted(() => {
  socket.on('game_action_result', game_action_res)
})
onUnmounted(() => {
  socket.off('game_action_result', game_action_res)
})

const game_action_res = (data) => {
  if (data.success) {
    if (data.type === 'discard') {
      console.log(data.message)
    } else {
      // type === chow pong kong hu
      console.log('Game Action Success:', data.message)
      for (const sid in status.members) {
        if (status.members[sid].name === data.name) {
          FocusAni(status.members[sid].decorator.org, status.members[sid].decorator.chara)
          break
        }
      }
    }
  } else {
    alert('Game Action Failed: ' + data.message)
  }
}
</script>

<template>
  <div class="first-half">
    <Chat />
    <div class="other-players">
      <OtherInfo
        @click-head="FocusAni"
        v-for="(member, sid) in members"
        v-if="allowOtherInfo"
        :sid="sid"
      />
    </div>
  </div>
  <MyTiles @click-head="FocusAni" v-if="allowMytiles" />
  <video
    v-if="showVideo"
    ref="videoPlayer"
    :src="`${focusurl}`"
    @ended="onVideoEnded"
    autoplay
  ></video>
</template>
<style>
video {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100vw;
  height: 100vh;
  object-fit: cover;
  z-index: 9999;
}
.first-half {
  display: flex;
}
.other-players {
  display: flex;
  margin: 0 1vw;
  gap: 1vw;
}
</style>
