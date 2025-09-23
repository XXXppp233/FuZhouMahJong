<script setup>
import { ref, computed } from 'vue'
import Music from './Music.vue'

// 初始背景图
const imgurl = ref('')

// 将传入的音乐 URL：/music/xxx.mp3 -> musicimg/xxx.jpg
// 规则：
// 1. 仅替换路径中第一个 "music" 为 "musicimg"
// 2. 末尾 .mp3（忽略大小写）改为 .jpg
// 3. 去掉开头的 / 以保持与现有相对路径一致
const changeimg = (url) => {
  if (!url || typeof url !== 'string') return
  let result = url
    // 替换第一个分段名 music (可选前导 /)
    .replace(/^\/?music(?=\/)/, (m) => m.replace('music', 'musicimg'))
    // 结尾 mp3 扩展换成 jpg（忽略大小写，保留可能的查询参数）
    .replace(/\.mp3(\?.*)?$/i, '.jpg')

  // 去掉开头的 /
  if (result.startsWith('/')) result = result.slice(1)
  imgurl.value = result
}

// 动态背景样式，响应 imgurl 变化
const bgStyle = computed(() => ({
  backgroundImage: `linear-gradient(rgba(255,255,255,0.3), rgba(255,255,255,0.9)), url('${imgurl.value}')`,
}))
</script>

<template>
  <div class="background" :style="bgStyle">
    <Music @change-Track="changeimg" />
  </div>
</template>

<style>
.background {
  z-index: -1;
  width: 100vw;
  height: 100vh;
  /* 背景图片由内联 style 动态提供 */

  /* 2. 设置背景图尺寸为 cover */
  background-size: cover;

  /* 3. 背景图居中显示 */
  background-position: center center;

  /* 4. 固定背景，滚动时不移动，效果更佳 */
  background-attachment: fixed;

  /* 5. 防止背景图重复 */
  background-repeat: no-repeat;

  /* 6. 设置一个备用背景色，以防图片加载失败 */
  background-color: #1a1a1a;

  /* 基础页面样式 */
  margin: 0;
  color: white;
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  text-align: center;
}
</style>
