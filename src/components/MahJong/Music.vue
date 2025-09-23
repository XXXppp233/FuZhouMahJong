<template>
  <div class="visualizer-container" :class="{ Persona: isPersona }" style="location">
    <canvas
      ref="canvas"
      :class="{ gaming: isGaming, playing: isPlaying }"
      :width="canvasSize"
      :height="canvasSize"
      @click="togglePlayback"
    ></canvas>

    <!-- 控制面板 -->
    <div class="controls-wrapper">
      <!-- 完整的控制面板 (v-show) -->
      <div v-show="controlsVisible" class="controls">
        <!-- 新增：隐藏按钮 -->

        <h3>修改主题色彩</h3>
        <div class="info">
          <p>绿 紫 蓝 金</p>
        </div>
        <div class="picker">
          <select id="musicSelect" v-model="currentUrl" @change="changeTrack">
            <option v-for="m in musicList" :key="m.url" :value="m.url">{{ m.name }}</option>
          </select>
        </div>
        <audio
          ref="audioPlayer"
          :src="currentUrl"
          controls
          autoplay
          crossorigin="anonymous"
          @play="handlePlay"
          @pause="handlePause"
        ></audio>
        <button type="button" class="toggle-btn" @click="toggleControls">隐藏</button>
      </div>

      <!-- 隐藏状态下显示的按钮 (v-else) -->
      <div v-show="!controlsVisible">
        <button type="button" class="show-btn" @click="toggleControls">
          <img :src="buttonurl(currentUrl)" alt="" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { statusStore } from '@/stores/status'

const status = statusStore()
const isGaming = computed(() => status.now === 'gaming')

// --- 新增状态 ---
const controlsVisible = ref(false) // 控制面板是否可见的状态

// --- Props Definition (All background props have been removed) ---
// style for some songs
const isPersona = computed(() => {
  return currentUrl.value.startsWith('/music/Persona')
})

// --- Configuration Constants ---
const FFT_SIZE = 2048
const DATA_USAGE_RATIO = 0.2
const INNER_RING_SCALE = 0.2
const SENSITIVITY = 1
const ROTATION_SPEED = 0.002

// --- Reactive Refs & Other Variables (All background refs have been removed) ---
const audioPlayer = ref<HTMLAudioElement | null>(null)
interface MusicItem {
  name: string
  url: string
  file: string
}
const musicList = ref<MusicItem[]>([])
const currentUrl = ref('')
const canvas = ref<HTMLCanvasElement | null>(null)
const canvasSize = ref(300)
const rotationOffset = ref(0)
const isPlaying = ref(false)
let audioContext: AudioContext | undefined
let analyser: AnalyserNode | undefined
let source: MediaElementAudioSourceNode | undefined
let dataArray: Uint8Array | undefined
let animationFrameId: number | undefined
let isAudioInitialized = false
let mql: MediaQueryList
const isDarkMode = ref(false)
const strokeColor = computed(() =>
  isPersona.value ? 'red' : isDarkMode.value ? '#ffffff' : '#000000',
)
const checkDarkMode = () => {
  if (mql) {
    isDarkMode.value = mql.matches
  } else if (typeof window !== 'undefined') {
    isDarkMode.value = window.matchMedia('(prefers-color-scheme: dark)').matches
  }
}
// --- 新增方法 ---
const toggleControls = () => {
  controlsVisible.value = !controlsVisible.value
}

// --- Core Functions ---
const initializeAudio = () => {
  /* ... (unchanged) ... */
  if (isAudioInitialized) return
  audioContext = new window.AudioContext()
  if (!audioPlayer.value) return
  source = audioContext.createMediaElementSource(audioPlayer.value)
  analyser = audioContext.createAnalyser()
  analyser.fftSize = FFT_SIZE
  source.connect(analyser)
  analyser.connect(audioContext.destination)
  dataArray = new Uint8Array(analyser.frequencyBinCount)
  isAudioInitialized = true
}

const renderFrame = () => {
  animationFrameId = requestAnimationFrame(renderFrame)

  if (!isPlaying.value) {
    return // Freeze animation when paused
  }

  rotationOffset.value += ROTATION_SPEED
  if (!analyser || !dataArray) return
  // 类型兼容性处理
  analyser.getByteFrequencyData(dataArray as unknown as Uint8Array<ArrayBuffer>)

  if (!canvas.value) return
  const canvasCtx = canvas.value.getContext('2d')!
  const { width, height } = canvas.value

  // 清除画布
  canvasCtx.clearRect(0, 0, width, height)

  // 可视化工具绘制逻辑 (unchanged)
  const centerX = width / 2
  const centerY = height / 2
  const radius = width * 0.2
  const activeDataPoints = Math.floor(analyser.frequencyBinCount * DATA_USAGE_RATIO)

  for (let i = 0; i < activeDataPoints; i++) {
    const barHeight = dataArray[i] * (width / 800) * SENSITIVITY
    const angle = rotationOffset.value + (i / activeDataPoints) * 2 * Math.PI
    const hue = (i / activeDataPoints) * 360

    canvasCtx.strokeStyle = strokeColor.value
    canvasCtx.lineWidth = Math.max(2, 4 * (width / 800))

    const startX = centerX + radius * Math.cos(angle)
    const startY = centerY + radius * Math.sin(angle)
    const endX = centerX + (radius + barHeight) * Math.cos(angle)
    const endY = centerY + (radius + barHeight) * Math.sin(angle)
    canvasCtx.beginPath()
    canvasCtx.moveTo(startX, startY)
    canvasCtx.lineTo(endX, endY)
    canvasCtx.stroke()
    const innerBarHeight = barHeight * INNER_RING_SCALE
    const endXInner = centerX + (radius - innerBarHeight) * Math.cos(angle)
    const endYInner = centerY + (radius - innerBarHeight) * Math.sin(angle)
    canvasCtx.beginPath()
    canvasCtx.moveTo(startX, startY)
    canvasCtx.lineTo(endXInner, endYInner)
    canvasCtx.stroke()
  }
}

// --- Event Handlers & Lifecycle (Unchanged) ---
const togglePlayback = () => {
  /* ... */
  if (!isAudioInitialized) initializeAudio()
  if (audioContext && audioContext.state === 'suspended') audioContext.resume().catch(() => {})
  if (!audioPlayer.value) return
  if (audioPlayer.value.paused) audioPlayer.value.play().catch(console.error)
  else audioPlayer.value.pause()
}
const handlePlay = () => {
  /* ... */
  initializeAudio()
  if (audioContext && audioContext.state === 'suspended') audioContext.resume()
  isPlaying.value = true
}
const handlePause = () => {
  isPlaying.value = false
}
const updateCanvasSize = () => {
  canvasSize.value = window.innerWidth * 0.4
  // canvasSize.value = Math.min(window.innerWidth, window.innerHeight) * 0.9
}

onMounted(() => {
  /* ... */
  mql = window.matchMedia('(prefers-color-scheme: dark)')
  checkDarkMode()
  if (mql.addEventListener) {
    mql.addEventListener('change', checkDarkMode)
  } else if (mql.addListener) {
    mql.addListener(checkDarkMode)
  }
  updateCanvasSize()
  window.addEventListener('resize', updateCanvasSize)
  // if (canvas.value && isPlaying.value === false) canvas.value.style.cursor = 'pointer'
  renderFrame()
  loadMusicList()
})
onUnmounted(() => {
  /* ... */
  if (animationFrameId) cancelAnimationFrame(animationFrameId)
  window.removeEventListener('resize', updateCanvasSize)
  if (audioContext && audioContext.state !== 'closed') audioContext.close().catch(console.error)
  if (mql.removeEventListener) {
    mql.removeEventListener('change', checkDarkMode)
  } else if (mql.removeListener) {
    mql.removeListener(checkDarkMode)
  }
})

// --- Music List Fetching (Unchanged) ---
async function loadMusicList() {
  /* ... */
  const endpoints = ['/api/music-list', '/music-list.json']
  for (const ep of endpoints) {
    try {
      const resp = await fetch(ep)
      if (!resp.ok) continue
      const data = await resp.json()
      if (Array.isArray(data) && data.length) {
        musicList.value = data
        if (!currentUrl.value) currentUrl.value = musicList.value[0].url
        return
      }
    } catch (e) {
      // ignore and try next
    }
  }
}

const emit = defineEmits(['change-Track'])

function changeTrack() {
  /* ... */
  emit('change-Track', currentUrl.value) // 可以 pop 掉 /music 作为文件名
  if (!audioPlayer.value) return
  const wasPlaying = !audioPlayer.value.paused
  audioPlayer.value.pause()
  audioPlayer.value.currentTime = 0
  const el = audioPlayer.value
  const playIfNeeded = () => {
    if (wasPlaying) {
      el.play().catch((err) => {
        console.warn('自动播放失败，等待用户交互', err)
      })
    }
    el.removeEventListener('canplay', playIfNeeded)
  }
  el.addEventListener('canplay', playIfNeeded)
}

function reloadList() {
  loadMusicList()
}

const buttonurl = (url: string) => {
  if (url.startsWith('/music/%F0%9F%90%B1')) {
    return 'icons/maodie.webp'
  } else if (url.startsWith('/music/Miku')) {
    return 'icons/Miku.jpg'
  } else if (url.startsWith('/music/%E2%99%BF')) {
    return 'icons/Otto.png'
  } else if (url.startsWith('/music/GTA')) {
    return 'icons/GTA.svg'
  } else if (url.startsWith('/music/%F0%9F%8D%AC%20')) {
    return 'icons/Anon.jpg'
  } else if (url.startsWith('/music/RDR')) {
    return 'icons/RDR2.png'
  } else return 'icons/Music.svg'
}
</script>

<style scoped>
/* Styles are mostly unchanged */
.visualizer-container {
  position: fixed;
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  z-index: 0;
  pointer-events: none;
}

canvas {
  cursor: pointer;
  pointer-events: auto;
  transition:
    transform 1s ease,
    filter 1s ease,
    opacity 1s ease;
}
canvas.gaming {
  position: fixed;
  transform: translateX(48vw);
}
canvas.playing:hover {
  cursor: url('cursor/sym57.cur'), auto;
}

@keyframes viz-orbit {
  0% {
    transform: translate(0, 0) scale(0.85) rotate(0deg);
  }
  20% {
    transform: translate(-10px, -6px) scale(0.88) rotate(72deg);
  }
  40% {
    transform: translate(0, -12px) scale(0.85) rotate(144deg);
  }
  60% {
    transform: translate(12px, 4px) scale(0.9) rotate(216deg);
  }
  80% {
    transform: translate(-6px, 8px) scale(0.87) rotate(288deg);
  }
  100% {
    transform: translate(0, 0) scale(0.85) rotate(360deg);
  }
}

/* 新增：包裹控件的容器，用于统一定位 */
.controls-wrapper {
  pointer-events: auto;
  position: fixed;
  top: 50%;
  right: 1vw;
  transform: translateY(-50%);
  transition: 0.5s ease;
  z-index: 20;
}

.controls {
  background-color: rgba(0, 0, 0, 0.7);
  padding: 1rem 1.5rem;
  border-radius: 8px;
  color: white;
  font-family: sans-serif;
  text-align: left;
  position: relative; /* 用于定位隐藏按钮 */
}
audio {
  width: 100%;
}
.picker {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  margin-bottom: 0.5rem;
}
select {
  flex: 1;
  background: #222;
  color: #fff;
  border: 1px solid #444;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}
button {
  background: #444;
  color: #fff;
  border: 1px solid #555;
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  cursor: pointer;
}
button:hover {
  background: #555;
}

/* 新增：隐藏按钮样式 */
.toggle-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 0.1rem 0.5rem;
  background-color: #555;
  border: none;
}
.toggle-btn:hover {
  background-color: #666;
}

/* 新增：显示控件按钮样式 */
.show-btn {
  caret-color: transparent;
  width: 5vh;
  height: 5vh;
  padding: 0;
  margin: 0;
  border: none;
  background: rgba(133, 133, 133, 0.8);
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  box-sizing: border-box;
  overflow: hidden;
}
.show-btn img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  display: block;
  object-fit: cover;
}
</style>
