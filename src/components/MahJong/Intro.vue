<template>
  <div class="intro" @mouseup="focusNameInput" @wheel="mouseWheel">
    <h3 class="inputprompt" :class="{ active: !isMahjor }" v-show="username.length === 0">
      Enter your name and press the
      <button
        class="enter"
        @mousedown="pressEnter"
        @mouseup="unPressEnter"
        @mouseleave="isPressed = false"
        :class="{ active: !isMahjor, pressed: isPressed }"
      >
        Enter↵
      </button>
    </h3>
    <input
      autofocus
      id="nameinput"
      class="nameinput"
      type="text"
      v-model="username"
      @keydown="handleKeyDown"
      @keyup="handleKeyUP"
      ref="inputRef"
    />
  </div>
  <div class="mahjor" @wheel="mouseWheel">
    <h1 class="mahjor-h" :class="{ active: isMahjor }" title="Mahjor">特级锦标赛</h1>
    <div class="mahjor-content" :class="{ active: isMahjor }"></div>
  </div>
  <div class="ranking" @wheel="mouseWheel">
    <h1 class="ranking-h" :class="{ active: isRanking }" title="天下英雄如过江之鲫">排行榜</h1>
    <div class="ranking-content" :class="{ active: isRanking }">
      <ul class="ranking-list">
        <li
          v-for="(data, index) in rankingData"
          class="ranking-item"
          :class="{ Odd: index % 2, first: index === 0 }"
        >
          <span class="ranking-index">{{ index ? index : ' ' }}</span>
          <span class="ranking-name" :title="data.name">{{ data.name }}</span>
          <span class="ranking-freq" :title="`Frequency`">{{ data.frequency }}</span>
          <span class="ranking-rate" :title="`1st`">{{ data.rate1 }}</span>
          <span class="ranking-rate" :title="`2nd`">{{ data.rate2 }}</span>
          <span class="ranking-rate" :title="`3rd`">{{ data.rate3 }}</span>
          <span class="ranking-rate" :title="`4nd`">{{ data.rate4 }}</span>
          <span class="ranking-perf" :title="`Performances`">{{ data.performances }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { socket } from '@/socket'

const rankingData = [
  {
    name: 'Name',
    frequency: 'Freq',
    rate1: '1st Rate',
    rate2: '2nd Rate',
    rate3: '3rd Rate',
    rate4: '4th Rate',
    performances: 'Perf',
  },
  {
    name: 'ChenMLD',
    frequency: 1500,
    rate1: 100,
    rate2: 0,
    rate3: 0,
    rate4: 0,
    performances: 'S+',
  },
  {
    name: 'Player1',
    frequency: 1300,
    rate1: 70,
    rate2: 20,
    rate3: 10,
    rate4: 0,
    performances: 'A+',
  },
  {
    name: 'Player2',
    frequency: 1200,
    rate1: 50,
    rate2: 30,
    rate3: 10,
    rate4: 10,
    performances: 'A',
  },
  {
    name: 'Player3',
    frequency: 1100,
    rate1: 30,
    rate2: 40,
    rate3: 20,
    rate4: 10,
    performances: 'B',
  },
  {
    name: 'Player4',
    frequency: 900,
    rate1: 20,
    rate2: 30,
    rate3: 30,
    rate4: 20,
    performances: 'C',
  },
  {
    name: 'Player5',
    frequency: 800,
    rate1: 10,
    rate2: 20,
    rate3: 40,
    rate4: 30,
    performances: 'D',
  },
  { name: 'Player6', frequency: 700, rate1: 5, rate2: 15, rate3: 30, rate4: 50, performances: 'E' },
  {
    name: 'Player1145141919810',
    frequency: 600,
    rate1: 0,
    rate2: 10,
    rate3: 20,
    rate4: 70,
    performances: 'F',
  },
]

const allowScroll = ref(true)
const scrollheight = ref(0)
const isMahjor = computed(
  () => scrollheight.value >= window.innerHeight && scrollheight.value < window.innerHeight * 2,
)
const isRanking = computed(() => scrollheight.value >= window.innerHeight * 2)

const username = ref('')
watch(username, (newVal) => {
  username.value = newVal.trimStart()
})
const inputRef = ref(null)
const isPressed = ref(false)
const pressEnter = () => {
  isPressed.value = true
  keySounds.Play({ key: 'enter', keyCode: 13 })
}
const unPressEnter = () => {
  isPressed.value = false
  keySounds.Play({ key: 'enter', keyCode: 14 })
}
const focusNameInput = () => {
  if (inputRef.value) {
    inputRef.value.focus({ preventScroll: true })
  }
}
const unfocusNameInput = () => {
  if (inputRef.value) {
    inputRef.value.blur()
  }
}

const keySoundType = ref('MikuTap') // 默认键盘音效类型
const url = computed(() => `../../keyboardsounds/${keySoundType.value}/main.js`)
let keySounds = null
const loadKeySounds = async () => {
  try {
    const soundsModule = await import(/* @vite-ignore */ url.value)
    keySounds = soundsModule.default
  } catch (error) {
    console.error('Error loading key sounds:', error)
  }
}
const handleKeyUP = (event) => {
  if (event.key === 'Enter') {
    login()
  }
}
const handleKeyDown = (event) => {
  keySounds.Play(event) // 调用导入的Play函数
}

function login() {
  if (username.value.trim() === '') {
    return
  } else {
    const data = {
      name: username.value.trim(),
    }
    socket.emit('join_server', data)
  }
}

const mouseWheel = (event) => {
  event.preventDefault() // 阻止默认滚动行为
  if (event.deltaY < 0) {
    // 向上滚动
    scrollheight.value -= window.innerHeight
    if (scrollheight.value < 0) scrollheight.value = 0

    window.scrollTo({ top: scrollheight.value, behavior: 'smooth' }) // 向上滚动一页
  } else if (event.deltaY > 0) {
    // 向下滚动
    scrollheight.value += window.innerHeight
    const maxScrollHeight = document.documentElement.scrollHeight - window.innerHeight
    if (scrollheight.value > maxScrollHeight) scrollheight.value = maxScrollHeight

    window.scrollTo({ top: scrollheight.value, behavior: 'smooth' }) // 向下滚动一页
  }
}

onMounted(() => {
  loadKeySounds()
})
onUnmounted(() => {})
</script>

<style scoped>
.intro {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
}
.inputprompt {
  color: transparent;
  text-align: center;
  font-size: 5vh;
  margin-bottom: 2vh;
  transform: scale(0.8);
  transition: 0.5s ease;
}
.inputprompt.active {
  color: lightgray;
  transform: scale(1);
}
.enter {
  font-size: inherit;
  color: transparent;
  background-color: transparent;
  border-radius: 1vh;
  border: 0.3vh solid gray;
  transition: 0.2s ease;
  transform: scale(1);
}
.enter.active {
  color: black;
}
.enter:hover {
  cursor: pointer;
  color: inherit;
}
.enter.pressed {
  transform: scale(0.9);
}
.nameinput {
  caret-color: transparent;
  color: inherit;
  background-color: transparent;
  text-align: center;
  font-size: 10vh;
  width: 80vw;
  border: 0;
}
.nameinput:focus {
  outline: none;
}
.mahjor {
  text-align: center;
  height: 100vh;
}
.mahjor-h {
  line-height: 14vh;
  color: transparent;
  -webkit-text-stroke: 0.3vh inherit;
  font-size: 10vh;
  transition: 0.5s;
}
.mahjor-h.active {
  color: inherit;
  -webkit-text-stroke: 0.3vh inherit;
}
.mahjor-content {
  background-color: antiquewhite;
  border-radius: 3vh;
  margin: 3vh 10vw 3vh 10vw;
  height: 80vh;
  width: 80vw;
  transform: translateY(20vh);
  transform: scale(0.9);
  transition: 0.2s;
}
.mahjor-content.active {
  transform: translateY(0) scale(1);
}
.ranking {
  text-align: center;
  height: 100vh;
}
.ranking-h {
  line-height: 14vh;
  color: transparent;
  -webkit-text-stroke: 0.3vh inherit;
  font-size: 10vh;
  transition: 0.5s;
}
.ranking-h.active {
  color: inherit;
  -webkit-text-stroke: 0.3vh inherit;
}
.ranking-content {
  background-color: whitesmoke;
  border-radius: 3vh;
  margin: 3vh 10vw 3vh 10vw;
  height: 80vh;
  width: 80vw;
  transform: translateY(20vh);
  transform: scale(0.9);
  transition: 0.2s;
}
.ranking-content.active {
  transform: translateY(0) scale(1);
}
.ranking-list {
  padding: 0;
}

.ranking-item {
  background-color: unset;
  display: flex;
  list-style-type: none;
  font-size: 3vh;
  line-height: 4vh;
  background-color: inherit;
}
.ranking-item.first {
  font: bold;
  font-size: 4vh;
  line-height: 6vh;
  border-radius: 3vh 3vh 0 0;
}
.ranking-item.first:hover {
  background-color: inherit;
  cursor: default;
}
.ranking-item.Odd {
  background-color: snow;
}
.ranking-item:hover {
  background-color: white;
  cursor: pointer;
}
.ranking-index {
  width: 5%;
  text-align: center;
}
.ranking-name {
  width: 10%;
  text-align: left;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}
.ranking-freq {
  width: 10%;
  text-align: right;
}
.ranking-rate {
  width: 14%;
  text-align: right;
}
.ranking-perf {
  width: 19%;
  text-align: center;
}

@media (prefers-color-scheme: dark) {
  .enter.active {
    color: white;
  }
  .mahjor-content {
    background-color: darkslategray;
  }
  .ranking-content {
    background-color: dimgray;
  }
  .ranking-item.Odd {
    background-color: gray;
  }
  .ranking-item:hover {
    background-color: rgb(24, 24, 24);
    cursor: pointer;
  }
}
</style>
