<template>
  <div class="box">
    <img class="selectedimg" :src="headurl" alt="" v-if="isReady" />
    <div class="characters" v-if="!isReady">
      <div class="controls">
        <div class="controls-row">
          <label>
            <select class="selectlabel" v-model="selectedFolder" @change="onFolderChange">
              <option class="choices" disabled value="">请选择</option>
              <option class="choices" v-for="f in folders" :key="f" :value="f">{{ f }}</option>
            </select>
          </label>
          <div class="actions">
            <button
              type="button"
              class="selectbutton"
              :disabled="!selectedImage"
              @click="confirmSelection"
            >
              确定
            </button>
          </div>
        </div>
        <div class="grid" v-if="images.length">
          <button
            v-for="img in images"
            :key="img"
            class="thumb"
            :class="{ active: img === selectedImage }"
            @click="selectedImage = selectedImage === img ? '' : img"
            type="button"
            title="选择图片"
          >
            <div class="thumb-img">
              <img :src="img" :alt="nameFromUrl(img)" />
            </div>
            <div class="caption">{{ nameFromUrl(img) }}</div>
          </button>
        </div>
      </div>
    </div>
    <div class="myinfo" v-if="isReady">
      <h3>{{ myname }}</h3>
      <h4>{{ charactername }}, {{ orgnaization }}</h4>
    </div>
  </div>
</template>

<script setup>
import { socket } from '@/socket'
import { ref, onMounted, computed, watch } from 'vue'
import { statusStore } from '@/stores/status'

const status = statusStore()

const myinfo = computed(() => status.getInfoBySid(status.mysid))
const myname = computed(() => (myinfo.value ? myinfo.value.name : ''))
const orgnaization = computed(() => (myinfo.value.decorator ? myinfo.value.decorator.org : ''))
const charactername = computed(() => (myinfo.value.decorator ? myinfo.value.decorator.chara : ''))
const isReady = computed(() => (myinfo.value ? myinfo.value.ready : false))
const headurl = computed(() =>
  isReady.value
    ? `characters/head/${orgnaization.value}/${charactername.value}.webp`
    : 'tilesvgs/Regular/Blank.svg',
)

// New state for characters selection
const folders = ref([])
const selectedFolder = ref('')
const images = ref([])
const selectedImage = ref('')
const manifest = ref(null)
const posterurl = computed(() => null) // 不必要的

function nameFromUrl(u) {
  try {
    const file = (u || '').split('/').pop() || ''
    const decoded = decodeURIComponent(file)
    return decoded.replace(/\.[^.]+$/, '')
  } catch {
    return u
  }
}

async function fetchFolders() {
  // Try dev API first
  try {
    const r = await fetch('/api/characters/head/folders')
    if (r.ok) {
      const list = await r.json()
      folders.value = list
      if (!selectedFolder.value && list.length) selectedFolder.value = list[0]
      return
    }
  } catch {}
  // Fallback to production manifest
  try {
    const r2 = await fetch('/characters-head.json')
    if (r2.ok) {
      const data = await r2.json()
      manifest.value = data
      folders.value = data.map((x) => x.folder)
      if (!selectedFolder.value && folders.value.length) selectedFolder.value = folders.value[0]
    }
  } catch {}
}

async function fetchImages(folder) {
  images.value = []
  selectedImage.value = ''
  if (!folder) return
  // Try dev API
  try {
    const r = await fetch(`/api/characters/head/images?folder=${encodeURIComponent(folder)}`)
    if (r.ok) {
      images.value = await r.json()
      return
    }
  } catch {}
  // Fallback to manifest
  if (manifest.value) {
    const entry = manifest.value.find((x) => x.folder === folder)
    images.value = entry ? entry.images : []
  }
}

function onFolderChange() {
  fetchImages(selectedFolder.value)
}

function confirmSelection() {
  if (selectedImage.value) {
    socket.emit('player_ready', {
      ready: true,
      decorator: {
        org: selectedFolder.value,
        chara: nameFromUrl(selectedImage.value),
      },
    })
  }
}

// watch(isReady, (newval) => {
//   if (newval) {

//     })
//   }
// })

onMounted(async () => {
  await fetchFolders()
  if (selectedFolder.value) fetchImages(selectedFolder.value)
})
</script>

<style scoped>
@media (prefers-color-scheme: dark) {
  .characters {
    background-color: rgb(24, 24, 24) !important;
  }
}

.box {
  z-index: 1;
  display: flex;
  margin: 0vh 1vw;
  caret-color: transparent;
}
.selectedimg {
  width: 20vh;
  height: 20vh;
  margin-top: 5vh;
  border-radius: 50%;
  object-fit: cover;
}
.characters {
  z-index: 1;
  border: 0.5vw solid black;
  border-radius: 2vh;
  width: 50vw;
  height: 40vh;
  box-sizing: border-box;
  overflow: hidden;
  background-color: #fff;
}
.controls {
  display: flex;
  flex-direction: column;
  gap: 1vh;
  height: 100%;
}
.controls-row {
  display: flex;
  height: 3vh;
  align-items: center;
}
.controls-row label {
  flex: 1;
}
.controls-row .actions {
  margin-left: auto;
}
.selectlabel {
  font-size: 2vh;
}
.choices {
  font-size: 2vh;
}
.selectbutton {
  font-size: 2vh;
}

.grid {
  display: grid;
  grid-template-columns: repeat(4, 25%);
  /* grid-column-gap: 1vw; */
  overflow: auto;
}
.thumb {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  border: none;
  background-color: transparent;
  padding: 0;
  cursor: pointer;
  height: 30vh; /* vertical rectangle */
}
.thumb:hover {
  background-color: lightgray;
  transition: background-color 0.3s ease;
  border-radius: 1vh;
}
.thumb.active {
  background-color: green;
  border-radius: 0 !important;
}
.thumb-img {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border-radius: 1vh;
}
.thumb img {
  max-width: 100%;
  max-height: 100%;
  object-fit: fill;
  display: block;
}
.caption {
  font-size: 2vh;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.myinfo {
  z-index: 1;
  display: grid;
  line-height: 1;
  margin-top: 5vh;
  margin-left: 1vw;
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
</style>
