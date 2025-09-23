<template>
  <!-- 1. 用一个 div 包裹组件，并在这个 div 上添加点击事件 -->
  <div @click="togglePlayback" class="visualizer-container">
    <!-- 2. 给 av-line 组件添加一个 ref -->
    <av-line
      ref="visualizer"
      :src="props.audiourl"
      :controls="false"
      :line-width="2"
      line-color="lime"
      :fft-size="256"
    ></av-line>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  audiourl: {
    type: String,
    default: '/music/月牙灣.mp3', // 请确保这个路径是正确的
  },
})

// 3. 创建一个模板引用来访问 av-line 组件实例
const visualizer = ref(null)

// 4. 定义点击时触发的函数
const togglePlayback = () => {
  // 确保组件已经被挂载，并且可以访问到内部的 audio 元素
  if (visualizer.value && visualizer.value.audio) {
    const audio = visualizer.value.audio

    // 检查音频当前是暂停还是播放状态，并执行相反操作
    if (audio.paused) {
      audio.play()
    } else {
      audio.pause()
    }
  }
}
</script>

<style scoped>
/* 5. 添加一个样式，让用户知道这个区域是可以点击的 */
.visualizer-container {
  cursor: pointer;
}
</style>
