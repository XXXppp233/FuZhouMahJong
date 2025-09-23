<template>
  <div class="lobby-container">
    <!-- 左侧服务器列表面板 -->
    <aside class="server-list-panel">
      <header>
        <h3>房间列表</h3>
      </header>

      <div class="list-scroll-area">
        <!-- 列表为空时，依然显示空的容器 -->
        <ul class="room-list">
          <li
            v-for="room in status.roomlist"
            :key="room.id"
            class="room-item"
            :class="{ selected: room.id === selectedRoomId }"
            @click="selectRoom(room.id)"
          >
            <div class="room-info">
              <span class="room-name">
                <span v-if="room.has_password" class="password-icon" title="需要密码">🔒</span>
                {{ room.name }}
              </span>
              <span class="room-owner">{{ room.owner }}</span>
            </div>
            <div class="room-status">{{ room.members }} / {{ room.max_members }}</div>
          </li>
        </ul>
      </div>

      <footer>
        <button @click="handleActionButtonClick" class="action-button">
          {{ actionButtonText }}
        </button>
      </footer>
    </aside>

    <!-- 右侧内容区域 (可以展示房间详情等) -->
    <main class="room-details-panel">
      <div v-if="selectedRoom">
        <h2>{{ selectedRoom.name }}</h2>
        <p>游戏模式: {{ selectedRoom.game }}</p>
        <p>状态: {{ selectedRoom.status }}</p>
        <!-- 更多详情 -->
      </div>
      <div v-else class="placeholder-text"></div>
    </main>

    <!-- 创建房间模态框 -->
    <ModalDialog :show="showCreateModal" title="创建房间" @close="showCreateModal = false">
      <form @submit.prevent="submitCreateRoom" class="modal-form">
        <label for="room-name">房间名称</label>
        <input id="room-name" v-model="newRoomName" type="text" required />

        <label for="room-password">房间密码 (可选)</label>
        <input id="room-password" v-model="newRoomPassword" type="password" />

        <button type="submit">确认创建</button>
      </form>
    </ModalDialog>

    <!-- 加入房间模态框 -->
    <ModalDialog :show="showJoinModal" title="输入密码" @close="showJoinModal = false">
      <form @submit.prevent="submitJoinRoom" class="modal-form">
        <p>房间 "{{ selectedRoom?.name }}" 需要密码才能加入。</p>
        <label for="join-password">房间密码</label>
        <input id="join-password" v-model="joinPassword" type="password" required autofocus />

        <button type="submit">确认加入</button>
      </form>
    </ModalDialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { socket } from '@/socket' // 确保路径正确
import ModalDialog from './ModalDialog.vue'
import { statusStore } from '@/stores/status'

const status = statusStore()
// 响应式状态

const roomList = ref([])
const selectedRoomId = ref(null)

// 模态框状态
const showCreateModal = ref(false)
const showJoinModal = ref(false)

// 表单数据
const newRoomName = ref('')
const newRoomPassword = ref('')
const joinPassword = ref('')

// --- Socket.IO 通信 ---
onMounted(() => {})

onUnmounted(() => {})

// --- 计算属性 ---
const selectedRoom = computed(() => {
  if (status.roomlist) {
    return status.roomlist.find((room) => room.id === selectedRoomId.value)
  } else {
    return null
  }
})

const actionButtonText = computed(() => {
  return selectedRoomId.value ? '加入房间' : '创建房间'
})

// --- 方法 ---
function selectRoom(roomId) {
  // 点击已选中的房间则取消选中
  selectedRoomId.value = selectedRoomId.value === roomId ? null : roomId
}

function handleActionButtonClick() {
  if (selectedRoom.value) {
    // 加入房间逻辑
    if (selectedRoom.value.has_password) {
      joinPassword.value = '' // 清空上次输入的密码
      showJoinModal.value = true
    } else {
      // 无密码，直接加入
      socket.emit('join_room', { room_id: selectedRoom.value.id })
    }
    selectedRoomId.value = null
  } else {
    // 创建房间逻辑
    newRoomName.value = ''
    newRoomPassword.value = ''
    showCreateModal.value = true
  }
}

function submitCreateRoom() {
  if (!newRoomName.value.trim()) return
  socket.emit('create_room', {
    name: newRoomName.value,
    password: newRoomPassword.value,
  })
  showCreateModal.value = false
}

function submitJoinRoom() {
  console.log('try to join a room')
  if (!joinPassword.value) return
  socket.emit('join_room', {
    room_id: selectedRoom.value.id,
    password: joinPassword.value,
  })
  showJoinModal.value = false
}
</script>

<style scoped>
.lobby-container {
  display: flex;
  height: 100vh; /* 占满整个视口高度 */
  background-color: #f0f2f5;
}

/* 左侧面板 */
.server-list-panel {
  width: 320px;
  flex-shrink: 0;
  background-color: #e8e8e8;
  border-right: 1px solid #c7c7c7;
  display: flex;
  flex-direction: column;
}

.server-list-panel header {
  padding: 1rem;
  border-bottom: 1px solid #c7c7c7;
  text-align: center;
}
.server-list-panel h3 {
  margin: 0;
  color: #333;
}

/* 滚动列表区域 */
.list-scroll-area {
  flex-grow: 1;
  overflow-y: auto;
}

.room-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.room-item,
.empty-list-item {
  padding: 12px 15px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #dcdcdc;
}
.empty-list-item {
  color: #888;
  text-align: center;
  cursor: default;
  justify-content: center;
}

/* macOS 风格灰白相间 */
.room-item:nth-child(even) {
  background-color: #f5f5f5;
}
.room-item:nth-child(odd) {
  background-color: #e8e8e8;
}

.room-item.selected {
  background-color: #007aff; /* macOS 选中蓝色 */
  color: white;
}
.room-item.selected .room-owner {
  color: #d1eaff;
}
.room-item.selected .password-icon {
  color: #ffffff;
}

.room-info {
  display: flex;
  flex-direction: column;
}
.room-name {
  font-weight: 600;
}
.password-icon {
  margin-right: 5px;
  color: #777;
}
.room-owner {
  font-size: 0.8rem;
  color: #666;
}
.room-status {
  font-size: 0.9rem;
}

/* 底部操作按钮 */
.server-list-panel footer {
  padding: 1rem;
  border-top: 1px solid #c7c7c7;
}

.action-button {
  width: 100%;
  padding: 10px;
  font-size: 1rem;
  background-color: #007aff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
.action-button:hover {
  background-color: #005ecb;
}

/* 右侧详情面板 */
.room-details-panel {
  flex-grow: 1;
  padding: 2rem;
}
.placeholder-text {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #888;
  font-size: 1.2rem;
}

/* 模态框表单样式 */
.modal-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.modal-form label {
  font-weight: bold;
}
.modal-form input {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.modal-form button {
  padding: 10px;
  background-color: #007aff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>
