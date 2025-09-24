<script setup>
import MahjongTile from './MahjongTile.vue'
import ActionButton from './ActionButton.vue'
import DiscardButton from './DiscardButton.vue'
import DiscardTiles from './DiscardTiles.vue'
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { statusStore } from '@/stores/status'
import { tilesmapStore } from '@/stores/tilesmap'

const props = defineProps({})
const status = statusStore()
const tilesmap = tilesmapStore()
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

//const actionNames = ref(['吃 🀙🀚', '吃 🀚🀜', '吃 🀜🀝', '碰 🀛', '杠 🀄', '胡'])
const username = computed(() => status.username)
const myid = computed(() => status.getMemberidBySid(mysid.value))
const mysid = computed(() => status.mysid)
const isActive = computed(() => status.getGameInfo().activePlayer === myid.value) // 是否应该出牌
const myinfo = computed(() => status.getInfoBySid(mysid.value))
const mygameinfo = computed(() => status.getGameInfo())

const discarded = computed(() => tilesmap.getTilesFont(mygameinfo.value.discarded))
const hands = computed(() => tilesmap.getTilesName(mygameinfo.value.hands))
const newtile = computed(() => tilesmap.getTileName(mygameinfo.value.new))
const locked = computed(() => tilesmap.getTilesName(mygameinfo.value.locked))
const actionsName = computed(() => tilesmap.getActionsName(mygameinfo.value.actions))
const actionsData = computed(() => tilesmap.getActionData(mygameinfo.value.actions))
const actionsnumber = computed(() => actionsData.value.length)

// 游戏开始后早已初始化基本数据
const organization = computed(() => myinfo.value.decorator.org)
const charactername = computed(() => myinfo.value.decorator.chara)
// 有新牌时默认选中新牌，否则默认选中第一张牌
const selectedIndex = ref(0) // 0~15 手牌 16 新牌
// 轮到我出牌时，如果所有牌都未选中且有新牌则选中新牌，否则选中第一张牌
watch(isActive, (newval) => {
  if (newval) {
    if (selectedIndex.value >= hands.value.length && newtile.value) {
      selectedIndex.value = hands.value.length
    } else if (selectedIndex.value >= hands.value.length) {
      selectedIndex.value = 0
    }
  } else {
  }
})
const select = (index) => {
  if (index === selectedIndex.value) {
    selectedIndex.value = hands.value.length // 再次点击取消选择，选中新牌位置（如果有新牌）
  } else if (index >= hands.value.length) {
    selectedIndex.value = hands.value.length // 选中新牌位置
  } else {
    selectedIndex.value = index // 选中手牌
  }
  console.log('selectedIndex', selectedIndex.value, hands.value[index])
}
const selectAction = ref(6) // 6 为无效选择，0~5 为吃碰杠胡等操作

// 按键监听
const handleKeyPress = (event) => {
  // 只在 isTyping 为 false 时监听按键
  if (status.isTyping) return

  if (event.key.toLowerCase() === 'q') {
    console.log('Q key pressed')
    // 在这里添加 Q 键的处理逻辑
    // 例如：选择上一张牌
    if (selectedIndex.value > 0) {
      selectedIndex.value -= 1
    }
    keySounds.Play(event) // 播放 Q 键音效
  } else if (event.key.toLowerCase() === 'e') {
    console.log('E key pressed')
    // 在这里添加 E 键的处理逻辑
    // 例如：选择下一张牌
    const maxIndex = newtile.value ? hands.value.length : hands.value.length - 1
    if (selectedIndex.value < maxIndex) {
      selectedIndex.value += 1
    }
    keySounds.Play(event) // 播放 E 键音效
  }
  else if (event.keyCode >= 49 && event.keyCode <= 54) { // 49-54 是 '1'-'6' 的 keyCode
    const actionIndex = event.keyCode - 49 // 转换为 0-5 的索引
    if (actionsnumber.value === 0) return // 没有操作时不响应数字键
    if (actionIndex < actionsnumber.value) {
      if(selectAction.value === actionIndex){
        console.log('取消选择')
        selectAction.value = 6 // 再次按相同数字键取消选择
      }else{
        console.log('选择: ', actionIndex)
        selectAction.value = actionIndex
      } // 0-5 的选择
      // 在这里添加对应操作的处理逻辑
    }
    keySounds.Play(event) // 播放数字键音效
  }
}

onMounted(() => {
  loadKeySounds()
  document.addEventListener('keydown', handleKeyPress)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyPress)
})

// 测试
const emit = defineEmits(['click-head'])
const clicktestbutton = () => {
  console.log(organization.value, charactername.value)
  emit('click-head', organization.value, charactername.value)
}
</script>

<template>
  <div class="box" :class="{ active: isActive }">
    <div class="above-tiles">
      <div class="my-character">
        <button class="test-button" @click.ctrl.exact="clicktestbutton">
          <img
            class="characterhead"
            :src="`characters/head/${organization}/${charactername}.webp`"
            :alt="`${charactername}`"
          />
        </button>
      </div>
      <div id="my-actions" class="my-info">
        <!-- 吃*3碰刚胡 一共需要六个按钮  -->
        <h3>{{ username }}</h3>
        <h4>{{ charactername }}, {{ organization }}</h4>
        <DiscardTiles :discarded="discarded" />
        <div class="action-buttons">
          <ActionButton
            v-for="(action, index) in actionsName"
            :label="action"
            :actionid="index" 
            :selected="selectAction === index"
            :length="actionsnumber"
            :data="actionsData[index]"
          />
        </div>
      </div>
      <DiscardButton :selectedIndex="selectedIndex" :active="isActive" />
    </div>

    <div id="my-tiles" class="my-tiles">
      <span>
        <MahjongTile
          v-if="locked.length"
          v-for="(tile, index) in locked"
          :index="index"
          :tile="tile"
          :locked="true"
        />
      </span>
      <span>
        <MahjongTile
          v-for="(tile, index) in hands"
          :index="index"
          :tile="tile"
          :selected="selectedIndex === index"
          @click="select"
        />
      </span>
      <span>
        <MahjongTile
          v-if="newtile"
          :tile="newtile"
          :index="hands.length"
          :selected="selectedIndex === hands.length"
          @click="select"
        />
      </span>
    </div>
  </div>
</template>

<style scoped>
@font-face {
  font-family: 'Segoe UI Symbol';
  src: url('fonts/segoe-ui-symbol.ttf') format('truetype');
}
.box {
  z-index: 1;
}
.box.active {
  background-color: lightgrey;
  border-radius: 2vw;
  transition: background-color 0.5s ease-in;
}
/* span 元素目前仅对下方自己的手排生效 */
span {
  z-index: 1;
  display: flex;
  flex-wrap: nowrap;
  gap: 0.1vw;
}

.above-tiles {
  z-index: 1;
  margin-top: 5vh; /* 剩余35vh */
  display: flex;
}
.test-button {
  z-index: 1;
  border: none;
  height: 100%;
  width: 100%;
  padding: 0;
  border-radius: 10vh;
  background-color: transparent;
}

.my-character {
  z-index: 1;
  caret-color: transparent; /* 隐藏光标 */
  width: 20vh;
  height: 20vh;
  margin: 0 1vw;
}
.characterhead {
  z-index: 1;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  image-rendering: optimizeQuality;
}

.my-info {
  margin: 0 0 0 1vw;
  width: 42vw;
  height: 20vh;
  display: grid;
  line-height: 1;
  align-content: start;
}

h3 {
  z-index: 1;
  cursor: pointer;
  caret-color: transparent; /* 隐藏光标 */
  height: 4vh;
  font-size: 4vh;
  text-decoration: underline rgb(216, 216, 216);
  transition: text-decoration 0.3s ease;
}
h3:hover {
  text-decoration: underline green;
}
h4 {
  z-index: 1;
  cursor: pointer;
  caret-color: transparent; /* 隐藏光标 */
  height: 2vh;
  font-size: 2vh;
  text-decoration: underline rgb(216, 216, 216, 0);
  transition: text-decoration 0.3s ease;
}
h4:hover {
  text-decoration: underline green;
}
.action-buttons {
  z-index: 1;
  width: 42vw;
  height: 6vh;
  display: flex;
  gap: 0;
}

.my-tiles {
  z-index: 1;
  gap: 1vw;
  margin: 1vh 0;
  display: flex;
}
</style>
