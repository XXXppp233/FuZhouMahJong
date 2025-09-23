<template>
  <div class="chat-container">
    <div class="chat-header">
      <h3>聊天</h3>
    </div>

    <div class="chat-messages" ref="messagesContainer">
      <Message v-for="(item, id) in chatLog.data" :key="id" :messageData="item" :timestamp="id" />
    </div>

    <div class="chat-input">
      <input
        v-model="newMessage"
        @keyup.enter="sendMessage"
        @focus="onInputFocus"
        @blur="onInputBlur"
        placeholder="What can I say ?"
        class="message-input"
      />
      <button @click="sendMessage" class="send-button">发送</button>
    </div>
  </div>
</template>

<script setup>
// Script部分无需任何改动
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { socket } from '@/socket'
import { useChatStore } from '@/stores/chat'
import { statusStore } from '@/stores/status'
import Message from './Message.vue'
const props = defineProps({
  myname: { type: String, default: 'me' },
  inheritedlog: { type: Object, default: () => ({}) },
})
const messagesContainer = ref(null)
const newMessage = ref('')
const chatLog = useChatStore()
const status = statusStore()
const isTyping = status.isTyping

const onInputFocus = () => {
  status.setTyping(true)
}

const onInputBlur = () => {
  status.setTyping(false)
}

const sendMessage = () => {
  if (newMessage.value.trim() === '') return
  console.log('Sending message:', newMessage.value)
  socket.emit('chat_message', {
    message: newMessage.value,
  })
  newMessage.value = ''
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

watch(
  chatLog.data,
  () => {
    nextTick(scrollToBottom)
  },
  { deep: true },
)
onMounted(() => {
  scrollToBottom()
  socket.on('chat_message', onChatUpdate)
})

onUnmounted(() => {
  socket.off('chat_message', onChatUpdate)
})

const onChatUpdate = (data) => {
  console.log('Received chat message:', data)
  chatLog.addMessage(data)
}
</script>

<style scoped>
/* 核心变更：变量现在定义在 .chat-container 上，而不是 :root */
.chat-container {
  /* 浅色模式变量 */
  --bg-main: #fff;
  --bg-secondary: #fafafa;
  --bg-header: #f7f7f7;
  --text-primary: #333;
  --text-header: #333;
  --border-color: #ddd;
  --input-bg: #fff;
  --input-text: #333;
  --scrollbar-thumb: #ccc;
  --scrollbar-thumb-hover: #999;
  --btn-primary-bg: #4caf50;
  --btn-primary-hover: #45a049;

  /* 布局样式 */
  z-index: 1;
  width: 18vw;
  height: 60vh;
  border: 0.1vh solid var(--border-color);
  background: var(--bg-main);
  transition:
    background-color 0.3s,
    border-color 0.3s;
  border-radius: 1vw;
  display: flex;
  flex-direction: column;
  box-shadow: 0 0.5vw 1vw rgba(0, 0, 0, 0.1);
  font-family: 'Microsoft YaHei', sans-serif;
}

/* 使用 @media 查询来覆盖 .chat-container 上的变量 */
@media (prefers-color-scheme: dark) {
  .chat-container {
    --bg-main: #1e1e1e;
    --bg-secondary: #181818;
    --bg-header: #252526;
    --text-primary: #dcdcdc;
    --text-header: #ccc;
    --border-color: #3a3a3a;
    --input-bg: #3c3c3c;
    --input-text: #ddd;
    --scrollbar-thumb: #555;
    --scrollbar-thumb-hover: #666;
    --btn-primary-bg: #3a8d3e;
    --btn-primary-hover: #45a049;
  }
}

/* 以下样式使用var()，它们会自动适应主题 */
.chat-header {
  /* ... 省略未改变的样式 ... */
  height: 4vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0.5vw;
  background: var(--bg-header);
  border-bottom: 0.1vh solid var(--border-color);
  transition:
    background-color 0.3s,
    border-color 0.3s;
  border-radius: 0.5vw 0.5vw 0 0;
  flex-shrink: 0;
}

.chat-header h3 {
  margin: 0; /* color: var(--text-header) */
  font-size: 2vh;
}
.chat-messages {
  flex: 1;
  padding: 0.1vw;
  overflow-y: auto;
  background: var(--bg-secondary);
  transition: background-color 0.3s;
}
.chat-input {
  height: 5vh;
  display: flex;
  padding: 0.5vw;
  border-top: 0.1vh solid var(--border-color);
  background: var(--bg-main);
  transition:
    background-color 0.3s,
    border-color 0.3s;
  border-radius: 0 0 0.5vh 0.5vh;
  flex-shrink: 0;
}
.message-input {
  height: 3vh;
  width: 9vw;
  font-size: 1.5vh;
  flex: 1;
  padding: 1vh 1vw;
  border: 0.1vh solid var(--border-color);
  background-color: var(--input-bg);
  color: var(--input-text);
  border-radius: 1.5vh;
  margin-right: 0.5vw;
  outline: none;
  transition: border-color 0.2s;
}
.message-input:focus {
  border-color: var(--btn-primary-bg);
}
.send-button {
  font-size: 1.5vh;
  height: 3vh;
  width: 3vw;
  background: green /* var(--btn-primary-bg) */;
  color: white;
  border: none;
  border-radius: 1.5vh;
  cursor: pointer;
  transition: background-color 0.2s ease;
}
.send-button:hover {
  background: var(--btn-primary-hover);
}
.chat-messages::-webkit-scrollbar {
  width: 6px;
}
.chat-messages::-webkit-scrollbar-track {
  background: transparent;
}
.chat-messages::-webkit-scrollbar-thumb {
  background: var(--scrollbar-thumb);
  border-radius: 3px;
}
.chat-messages::-webkit-scrollbar-thumb:hover {
  background: var(--scrollbar-thumb-hover);
}
</style>
