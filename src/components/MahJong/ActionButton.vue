<template>
  <span>
    <button
      v-if="props.label"
      :class="{ pressed: ispressed, left: isleft, right: isright, selected: props.selected }"
      @mousedown="ispressed = true"
      @mouseup="ispressed = false"
      @click="handleAction"
    >
      {{ props.label }}
    </button>
  </span>
</template>
<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { socket } from '@/socket'

const props = defineProps({
  label: {
    //操作提示，给玩家看
    type: String,
    required: true,
  },
  actionid: {
    //操作 id 用于判断是否是第一个或最后一个
    type: Number,
    required: true,
  },
  selected: {
    // 是否被选中
    type: Boolean,
    default: false,
  },
  length: {
    //总操作数 用于判断是否是第一个或最后一个
    type: Number,
    required: true,
  },
  data: {   // true false ['1o', '2o'] 之类的附加数据
    type: [Array, Boolean],
    default: null,
  }
})
const emit = defineEmits(['click'])
const ispressed = ref(false)

const handleAction = () => {
  console.log('handleAction', props.actionid, props.label)
  if (props.label.startsWith('胡')) {
    socket.emit('game_action', { action: 'hu' })
  } else if (props.label.startsWith('杠')) {
    socket.emit('game_action', { action: 'kong' })
  } else if (props.label.startsWith('碰')) {
    socket.emit('game_action', { action: 'pong' })
  } else if (props.label.startsWith('吃')) {
    socket.emit('game_action', { action: 'chow', tiles: props.data })
  } else {
    console.log('未知操作')
  }
}
const isleft = ref(props.actionid === 0)
const isright = ref(props.actionid === props.length - 1)
console.log(props.actionid, props.label)

const handleKeyDown = (event) => {
  if (props.selected){
    if (event.keyCode === 87) { // W 键
    ispressed.value = true
  }
  }
  else return
  
}
const handleKeyUp = (event) => {
  if (props.selected){
    if (event.keyCode === 87) { // W 键
    ispressed.value = false
    handleAction()
  }
  }
  else return
}


onMounted(() => {
  addEventListener('keydown', handleKeyDown)
  addEventListener('keyup', handleKeyUp)
})
onUnmounted(() => {
  removeEventListener('keydown', handleKeyDown)
  removeEventListener('keyup', handleKeyUp)
})


</script>
<style scoped>
@media (prefers-color-scheme: dark) {
  button {
    background-color: #333;
    color: white;
  }
}

span {
  z-index: 1;
  caret-color: transparent; /* 隐藏光标 */
  width: 7vw;
  height: 6vh;
  display: inline-block;
}
button {
  border: 0.1vh solid #000000;
  width: 7vw;
  height: 6vh;
  font-size: 2vw;
  font-family: 'Segoe UI Symbol';
  transition:
    background-color 0.3s ease,
    color 0.3s ease; /* 添加过渡效果 */
  transition: 0.1s ease;
}
button:hover {
  background-color: green;
  color: white;
}
button.pressed {
  transform: scale(0.9);
}
button.selected {
  background-color: green;
  color: white;
}
button.left {
  border-top-left-radius: 2vw;
  border-bottom-left-radius: 2vw;
}
button.right {
  border-top-right-radius: 2vw;
  border-bottom-right-radius: 2vw;
}
</style>
