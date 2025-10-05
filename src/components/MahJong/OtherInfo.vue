<template>
  <div class="box" :class="{ active: isActive }">
    <div class="playerhead">
      <button class="test-button" @click.ctrl.exact="clicktestbutton">
        <img class="characterhead" :src="`${url}`" :alt="`${charactername}`" />
      </button>
    </div>
    <div class="playerinfo">
      <h3>{{ memberinfo.name }}</h3>
      <h4>{{ charactername }}, {{ organization }}</h4>
      <div class="handstiles">
        <span
          ><b v-for="tile in locked">{{ tile }}</b></span
        >
        <span
          ><b v-for="tile in Array(handsnumber).fill('🀫')">{{ tile }}</b></span
        >
        <span><b v-if="hasnew">🀫</b></span>
      </div>
      <div class="discardedtiles">
        <b
          class="discardedtile"
          :class="{ new: index > shownnum - 1 }"
          v-for="(tile, index) in discarded"
          >{{ tile }}</b
        >
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { tilesmapStore } from '@/stores/tilesmap'
import { statusStore } from '@/stores/status'

const status = statusStore()
const tilesmap = tilesmapStore()
const props = defineProps({
  sid: {
    type: String,
    required: true,
  },
})

const memberinfo = computed(() => status.getInfoBySid(props.sid))
const playerid = computed(() =>
  status.now === 'gaming' ? status.getMemberidBySid(props.sid) : false,
)
const isActive = computed(() => status.getGameInfo().activePlayer === playerid.value)
const playerinfo = computed(() => status.getPlayerById(playerid.value))
const isGaming = computed(() => status.now === 'gaming')
// Room
const organization = computed(() =>
  memberinfo.value.decorator ? memberinfo.value.decorator.org : '',
)
const charactername = computed(() =>
  memberinfo.value.decorator ? memberinfo.value.decorator.chara : '',
)

// Gaming
// locked discarded 转换为字符后输出
const locked = computed(() =>
  playerinfo.value ? tilesmap.getTilesFont(playerinfo.value.locked) : [],
)
const handsnumber = computed(() => (playerinfo.value ? playerinfo.value.hand_count : 0))
const hasnew = computed(() => (playerinfo.value ? playerinfo.value.hasnew : false))
const discarded = computed(() =>
  playerinfo.value ? tilesmap.getTilesFont(playerinfo.value.discarded) : [],
)
const shownnum = ref(0)
watch(discarded, (newVal, oldVal) => {
  if (newVal.length === oldVal.length) {
    // 牌数没变
    return
  } else if (newVal.length >= oldVal.length) {
    // 出牌
    console.log('牌数增加')
    setTimeout(() => {
      shownnum.value = newVal.length
    }, 300) // 0.3秒后取消特写
    //shownnum.value += 1
  } else {
    // 牌被杠走
    console.log('牌数减少')
    shownnum.value = newVal.length
  }
})

const url = computed(() =>
  memberinfo.value.ready
    ? 'characters/head/' + organization.value + '/' + charactername.value + '.webp'
    : 'tilesvgs/Regular/Blank.svg',
)

//后续会改成点击头像会触发一个语音，这里为了测试改为触发特写
const emit = defineEmits(['click-head'])
const clicktestbutton = () => {
  emit('click-head', organization.value, charactername.value)
}
</script>

<style scoped>
@font-face {
  font-family: 'Segoe UI Symbol';
  src: url('/src/assets/fonts/segoe-ui-symbol.ttf') format('truetype');
}
.box {
  z-index: 1;
  caret-color: transparent; /* 隐藏光标 */
  display: flex;
  width: 26vw;
  height: 20vh;
}
.box.active {
  background-color: lightgrey;
  border-radius: 2vw;
  transition: background-color 0.2s ease-in;
}
.test-button {
  border: none;
  height: 100%;
  width: 100%;
  padding: 0;
  margin: 0;
  border-radius: 50%;
  background-color: transparent;
}
.playerhead {
  width: 10vw;
  height: 10vw;
  flex-shrink: 0; /* 防止缩小 */
}
.characterhead {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  image-rendering: optimizeQuality;
}

.playerinfo {
  margin: 0 0 0 1vw;
  width: 16vw;
  height: 20vh;
  display: grid;
  line-height: 1;
  align-content: start;
}
h3 {
  cursor: pointer;
  margin-top: 1vh;
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
.handstiles {
  height: 1vw;
  font-size: 2vh;
  display: flex;
  gap: 0.5vw;
  margin: 1vh 0;
}
.discardedtiles {
  display: flex;
  flex-wrap: wrap;
  word-wrap: break-word;
}
b {
  /* 2vh apply to 16:9 display */
  font-family: 'Segoe UI Symbol';
  font-size: 2vh;
  transform: scale(1);
  transition: 0.5s ease;
}
b:hover {
  cursor: pointer;
  color: green;
}
.discardedtile.new {
  transform: scale(10);
  transition: 0s;
}
</style>
