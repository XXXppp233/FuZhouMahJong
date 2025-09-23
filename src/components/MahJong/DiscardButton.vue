<template>
  <div :class="{ pressed: ispressed }">
    <button
      :class="{ pressed: ispressed }"
      @mousedown="handleMouseDown"
      @mouseup="ispressed = false"
    ></button>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { socket } from '@/socket'
import { statusStore } from '@/stores/status'

const keySoundType = ref('MikuTap') // default value
const keyboardsoundsurl = computed(() => `../../keyboardsounds/${keySoundType.value}/main.js`)
let keySounds = null
const loadKeySounds = async () => {
  try {
    const soundsModule = await import(/* @vite-ignore */ keyboardsoundsurl.value)
    keySounds = soundsModule.default
  } catch (error) {
    console.error('Error loading key sounds:', error)
  }
}


const props = defineProps({
  selectedIndex: {
    //要打出的牌
    type: Number,
    default: 0,
  },
  active: {
    //是否轮到自己出牌
    type: Boolean,
    default: false,
  },
})

const ispressed = ref(false)

const handleMouseDown = () => {
  ispressed.value = true
  submitDiscard()
}
const handleSpaceDown = (event) => {
  if (statusStore().isTyping) return
  if (event.code === 'Space') {
    ispressed.value = true
    keySounds.Play(event)
    submitDiscard()
  }
}
const handleSpaceUp = (event) => {
  if (event.code === 'Space') {
    ispressed.value = false
  }
}

const submitDiscard = () => {
  if (props.active) {
    socket.emit('game_action', {
      action: 'discard',
      tileindex: props.selectedIndex,
    })
  } else {
    console.log('你现在不能出牌')
  }
}

onMounted(() => {
  loadKeySounds()
  addEventListener('keydown', handleSpaceDown)
  addEventListener('keyup', handleSpaceUp)
})
onUnmounted(() => {
  removeEventListener('keydown', handleSpaceDown)
  removeEventListener('keyup', handleSpaceUp)
})
</script>

<style scoped>
div {
  z-index: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 20vh;
  height: 20vh;
  border-radius: 10vh;
  margin: 0 1vw;
  background-image: linear-gradient(
    120deg,
    rgba(0, 255, 55, 0),
    rgba(0, 255, 55, 1),
    rgba(0, 255, 55, 0)
  );
  /* background: radial-gradient(circle, green, white, green, white, green); */
  transition: background-color 0.5s ease-in;
}
button {
  caret-color: transparent; /* 隐藏光标 */
  border: 0;
  width: 16vh;
  height: 16vh;
  border-radius: 8vh;
  transition: 0.1s;
}
button:hover {
  background-color: #f0f0f0;
  transform: scale(1.25);
}
button.pressed {
  transform: scale(0.9);
}

div.pressed {
  transform: scale(1.05);
}
</style>
