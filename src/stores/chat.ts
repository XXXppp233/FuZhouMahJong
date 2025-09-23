import { ref } from 'vue'
import { defineStore } from 'pinia'

// 1. 定义消息的类型
interface ChatMessage {
  type: 'chat'
  name: string
  message: string
}

interface LogMessage {
  type: 'log'
  level: 'info' | 'warning' | 'error'
  message: string
}

type MessageEntry = ChatMessage | LogMessage
type ChatLog = {
  [key: string]: MessageEntry
} // 666 神仙语法

export const useChatStore = defineStore('chat', () => {
  const data = ref<ChatLog>({
    1754922091285: { type: 'chat', name: 'Server', message: 'F11 以全屏游玩' },
    1754922092123: { type: 'chat', name: 'Server', message: '点击 Server 以隐藏该消息。' },
    1754922093286: { type: 'log', level: 'info', message: '房间已创建' },
  })
  function addMessage(message: MessageEntry) {
    const timestamp = Date.now().toString()
    data.value[timestamp] = message
  }

  return { data, addMessage }
})
