<template>
  <div class="message-wrapper" :title="fullFormattedTime">
    <div v-if="messageData.type === 'chat'" class="message-item chat-style">
      <div class="message-content">
        <span class="message-name"
          ><button @click="blur" class="blur">{{ messageData.name }}</button></span
        >
        <div class="text-wrapper">
          <span v-if="isBlurred === false">{{ messageData.message }}</span>
          <span v-if="isBlurred">{{ replace(messageData.message) }}</span>
          <span class="message-time">{{ shortTime }}</span>
        </div>
      </div>
    </div>
    <div v-else-if="messageData.type === 'log'" class="message-item log-style">
      <span class="log-text">{{ messageData.message }}</span>
    </div>
  </div>
</template>

<script setup>
// Script部分也无需任何改动
import { computed, ref } from 'vue'

const props = defineProps({
  messageData: { type: Object, required: true },
  timestamp: { type: [String, Number], required: true },
  blursymbol: { type: String, default: '*' },
})
// 🀆 🀄 🃏 🀡
const replace = (str) => {
  return Array(str.length + 1).join(props.blursymbol)
}

const pad = (num) => String(num).padStart(2, '0')

const fullFormattedTime = computed(() => {
  const date = new Date(parseInt(props.timestamp))
  return date
    .toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    })
    .replace(/\//g, '-')
})

const shortTime = computed(() => {
  const date = new Date(parseInt(props.timestamp))
  return `${pad(date.getHours())}:${pad(date.getMinutes())}`
})

// 隐藏文本
const isBlurred = ref(false)
const blur = () => {
  isBlurred.value = !isBlurred.value
}
</script>

<style scoped>
/* 定义本组件所需的所有变量 */
.message-wrapper {
  /* 浅色模式变量 */
  --bubble-bg: #fff;
  --bubble-border: #e9e9e9;
  --text-primary: #333;
  --name-color: #4caf50;
  --log-bg: #f0f0f0;
  --log-text: #888;
}

/* 同样使用 @media 查询来覆盖这些变量 */
@media (prefers-color-scheme: dark) {
  .message-wrapper {
    --bubble-bg: #2a2a2a;
    --bubble-border: #3c3c3c;
    --text-primary: #dcdcdc;
    --name-color: #3a8d3e;
    --log-bg: #252526;
    --log-text: #999;
  }
}

.message-item {
  margin-bottom: 1vh;
  max-width: 95%;
  position: relative;
}

/* 聊天气泡样式 */
.chat-style {
  position: relative;
  margin-bottom: 1vh;
  padding: 0.5vh 0.8vw;
  background: var(--bubble-bg);
  border-radius: 0.5vh;
  transition:
    background-color 0.3s,
    border-color 0.3s;
  border-left: 0.2vw solid green;
}

.message-content {
  display: grid;
  gap: 0.5vh;
}
.message-name {
  caret-color: transparent; /* 隐藏光标 */
}
.blur {
  cursor: pointer;
  margin: 0;
  border: 0;
  padding: 0;
  font-weight: bold;
  color: green;
  font-size: 1.5vh;
  background-color: inherit;
}
.text-wrapper {
  line-height: 1.2;
  font-size: 1.2vh;
  color: var(--text-primary);
  word-wrap: break-word;
  text-align: left;
}
.message-time {
  float: right;
  font-size: 1vh;
  color: #aaa;
  margin-left: 10px;
  line-height: 1.6;
  user-select: none;
  position: relative;
  bottom: -1vh;
}

/* 日志消息样式 */
.log-style {
  color: var(--log-text);
  background-color: var(--log-bg);
  font-size: 1vh;
  text-align: center;
  padding: 0.2vh 1vw;
  margin: 0 auto;
  border-radius: 1vh;
  transition:
    background-color 0.3s,
    color 0.3s;
}
.log-text {
  font-style: italic;
}
</style>
