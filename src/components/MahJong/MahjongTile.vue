<script setup>
import { ref, onMounted, computed } from 'vue'
const props = defineProps({
  tile: {
    type: String,
    required: true,
  },
  index: {
    type: Number,
    required: false,
  },
  selected: {
    type: Boolean,
    default: false,
  },
  locked: {
    type: Boolean,
    required: false,
    default: false,
  },
})
const isPressed = ref(false)
const isDarkMode = ref(false)

const emit = defineEmits(['click'])
const ensmall = () => {
  isPressed.value = true
  if (props.locked) return
  emit('click', props.index)
}
const enlarge = () => {
  isPressed.value = false
}

// 深色模式
const checkDarkMode = () => {
  isDarkMode.value = window.matchMedia('(prefers-color-scheme: dark)').matches
}

onMounted(() => {
  checkDarkMode()
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', checkDarkMode)
})

// 计算瓦片颜色
const tileColor = computed(() => (isDarkMode.value ? 'Black' : 'Regular'))
</script>
<template>
  <div>
    <button
      @mouseup="enlarge"
      @mousedown="ensmall"
      @mouseleave="enlarge"
      :class="{ pressed: isPressed, selected: props.selected, locked: props.locked }"
      :disabled="props.locked"
    >
      <img :src="`tilesvgs/${tileColor}/${props.tile}.svg`" />
    </button>
  </div>
</template>
<style scoped>
div {
  width: 5vw;
  height: 13vh;
  margin: 0;
  align-items: flex-end;
  justify-content: center;
}
@media (prefers-color-scheme: dark) {
  button {
    border-color: #5c5c5c !important;
    background-color: rgb(59, 59, 59);
  }
  button.selected {
    border-color: green !important;
  }
}

div {
  height: 13vh;
}

button {
  width: 5vw;
  height: 13vh;
  border: 0.2vw solid #ccc;
  border-radius: 1vw;
  padding: 0;
  caret-color: transparent; /* 隐藏光标 */
  transition: transform 0.1s ease; /* 添加过渡效果 */
  transform: scale(1);
}

button.pressed {
  transform: scale(0.95);
}
button:hover {
  transform: scale(1.1);
}
button.selected {
  transform: translateY(-1vh);
  border-color: green;
}
button.selected:hover {
  transform: scale(1.1) translateY(-1vh);
}
button:hover.pressed {
  transform: scale(0.95) translateY(-1vh);
}
button.locked:hover {
  transform: scale(1.1);
}

img {
  width: 100%;
  height: 100%;
}
</style>
