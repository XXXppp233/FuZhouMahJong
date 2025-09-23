// src/socket.js
import { reactive } from 'vue'
import { io } from 'socket.io-client'

// 创建一个响应式对象来存储 socket 的状态
export const state = reactive({
  connected: false,
})

// 替换为你的服务器 URL
const URL = 'http://10.22.72.227:5000'

export const socket = io(URL, {
  autoConnect: false, // 手动连接
  reconnection: false, // 禁用自动重连
})

// 不监听连接成功事件
