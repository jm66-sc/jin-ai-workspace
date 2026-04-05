<template>
  <div class="status-feed">
    <!-- 演示数据警告 -->
    <el-alert
      title="演示数据提示"
      type="warning"
      description="此状态反馈显示的是模拟数据，并非真实的系统事件。真实的状态监控功能尚未实现。"
      show-icon
      :closable="false"
      style="margin: 15px 20px 0 20px;"
    />

    <div class="feed-header">
      <div class="header-title">
        <el-icon><ChatLineRound /></el-icon>
        <span>状态反馈</span>
      </div>
      <div class="header-controls">
        <el-button-group size="small">
          <el-button
            :type="filter === 'all' ? 'primary' : ''"
            @click="filter = 'all'"
          >
            全部
          </el-button>
          <el-button
            :type="filter === 'system' ? 'primary' : ''"
            @click="filter = 'system'"
          >
            系统
          </el-button>
          <el-button
            :type="filter === 'api' ? 'primary' : ''"
            @click="filter = 'api'"
          >
            API
          </el-button>
          <el-button
            :type="filter === 'crawl' ? 'primary' : ''"
            @click="filter = 'crawl'"
          >
            抓取
          </el-button>
          <el-button
            :type="filter === 'user' ? 'primary' : ''"
            @click="filter = 'user'"
          >
            用户
          </el-button>
        </el-button-group>
        <el-button
          size="small"
          @click="clearMessages"
          :icon="Delete"
        >
          清空
        </el-button>
        <el-button
          size="small"
          @click="toggleAutoScroll"
          :type="autoScroll ? 'primary' : ''"
          :icon="autoScroll ? VideoPlay : VideoPause"
        >
          {{ autoScroll ? '自动滚动' : '暂停' }}
        </el-button>
      </div>
    </div>

    <div
      ref="messagesContainer"
      class="messages-container"
      @scroll="onScroll"
    >
      <div
        v-for="message in filteredMessages"
        :key="message.id"
        class="message-item"
        :class="getMessageClass(message.type)"
      >
        <div class="message-time">{{ formatTime(message.timestamp) }}</div>
        <div class="message-content">
          <div class="message-icon">
            <el-icon v-if="message.type === 'success'"><SuccessFilled /></el-icon>
            <el-icon v-else-if="message.type === 'warning'"><WarningFilled /></el-icon>
            <el-icon v-else-if="message.type === 'error'"><CircleCloseFilled /></el-icon>
            <el-icon v-else><InfoFilled /></el-icon>
          </div>
          <div class="message-text">{{ message.text }}</div>
        </div>
        <div class="message-category">
          <el-tag size="small" :type="getCategoryType(message.category)">
            {{ getCategoryLabel(message.category) }}
          </el-tag>
        </div>
      </div>
      <div v-if="filteredMessages.length === 0" class="empty-messages">
        暂无消息
      </div>
    </div>

    <div class="feed-footer">
      <div class="footer-stats">
        <span class="stat-item">总数: {{ messages.length }}</span>
        <span class="stat-item">成功: {{ stats.success }}</span>
        <span class="stat-item">警告: {{ stats.warning }}</span>
        <span class="stat-item">错误: {{ stats.error }}</span>
      </div>
      <div class="footer-input">
        <el-input
          v-model="newMessage"
          placeholder="输入自定义状态消息..."
          size="small"
          @keyup.enter="addCustomMessage"
        >
          <template #append>
            <el-button @click="addCustomMessage" :icon="Promotion" />
          </template>
        </el-input>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  ChatLineRound,
  Delete,
  VideoPlay,
  VideoPause,
  SuccessFilled,
  WarningFilled,
  CircleCloseFilled,
  InfoFilled,
  Promotion
} from '@element-plus/icons-vue'

// 消息数据
const messages = ref([])
const newMessage = ref('')
const filter = ref('all')
const autoScroll = ref(true)
const messagesContainer = ref(null)

// 消息类别定义
const messageTypes = {
  system: { label: '系统状态', type: 'info' },
  api: { label: 'API调用', type: 'primary' },
  crawl: { label: '数据抓取', type: 'success' },
  user: { label: '用户操作', type: 'warning' }
}

// 生成模拟初始消息
const generateInitialMessages = () => {
  const now = new Date()
  const initialMessages = [
    {
      id: 1,
      timestamp: new Date(now - 5000),
      type: 'success',
      category: 'system',
      text: '系统启动完成，所有服务正常运行'
    },
    {
      id: 2,
      timestamp: new Date(now - 10000),
      type: 'info',
      category: 'api',
      text: 'API健康检查通过，后端服务正常'
    },
    {
      id: 3,
      timestamp: new Date(now - 15000),
      type: 'success',
      category: 'crawl',
      text: '数据抓取任务启动，目标500条记录'
    },
    {
      id: 4,
      timestamp: new Date(now - 20000),
      type: 'warning',
      category: 'user',
      text: '用户提交了规则修改，等待确认'
    },
    {
      id: 5,
      timestamp: new Date(now - 25000),
      type: 'error',
      category: 'api',
      text: 'API请求超时，正在重试...'
    },
    {
      id: 6,
      timestamp: new Date(now - 30000),
      type: 'success',
      category: 'crawl',
      text: '已成功抓取150条记录，进度30%'
    },
    {
      id: 7,
      timestamp: new Date(now - 35000),
      type: 'info',
      category: 'system',
      text: '数据库连接正常，存储空间充足'
    },
    {
      id: 8,
      timestamp: new Date(now - 40000),
      type: 'success',
      category: 'user',
      text: '用户提交反馈，数据验证通过'
    }
  ]
  messages.value = initialMessages
}

// 计算属性
const filteredMessages = computed(() => {
  if (filter.value === 'all') {
    return messages.value
  }
  return messages.value.filter(msg => msg.category === filter.value)
})

const stats = computed(() => {
  const result = { success: 0, warning: 0, error: 0, info: 0 }
  messages.value.forEach(msg => {
    if (result[msg.type] !== undefined) {
      result[msg.type]++
    }
  })
  return result
})

// 方法
const getMessageClass = (type) => {
  return `message-${type}`
}

const getCategoryType = (category) => {
  return messageTypes[category]?.type || 'info'
}

const getCategoryLabel = (category) => {
  return messageTypes[category]?.label || '未知'
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const addMessage = (message) => {
  const newMsg = {
    id: messages.value.length + 1,
    timestamp: new Date(),
    ...message
  }
  messages.value.unshift(newMsg) // 最新消息在顶部

  // 限制消息数量
  if (messages.value.length > 50) {
    messages.value = messages.value.slice(0, 50)
  }

  // 自动滚动到最新消息
  if (autoScroll.value) {
    nextTick(() => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = 0
      }
    })
  }
}

const addCustomMessage = () => {
  if (!newMessage.value.trim()) {
    ElMessage.warning('请输入消息内容')
    return
  }

  addMessage({
    type: 'info',
    category: 'user',
    text: `[自定义] ${newMessage.value}`
  })

  newMessage.value = ''
  ElMessage.success('自定义消息已添加')
}

const clearMessages = () => {
  messages.value = []
  ElMessage.success('消息已清空')
}

const toggleAutoScroll = () => {
  autoScroll.value = !autoScroll.value
  ElMessage.info(autoScroll.value ? '自动滚动已开启' : '自动滚动已关闭')
}

const onScroll = () => {
  // 如果用户手动滚动，可以暂停自动滚动
  // 这里可以根据需要实现
}

// 模拟实时消息
let messageInterval = null
const startMessageSimulation = () => {
  if (messageInterval) clearInterval(messageInterval)

  messageInterval = setInterval(() => {
    const categories = ['system', 'api', 'crawl', 'user']
    const types = ['success', 'info', 'warning', 'error']
    const texts = [
      '系统资源使用正常，CPU占用率25%',
      'API请求处理完成，响应时间120ms',
      '数据抓取进度更新，已处理200/500条',
      '用户操作：规则配置已保存',
      '数据库备份任务执行中',
      '网络连接稳定，延迟45ms',
      '安全扫描通过，无威胁检测',
      '缓存清理完成，释放空间1.2GB'
    ]

    const randomCategory = categories[Math.floor(Math.random() * categories.length)]
    const randomType = types[Math.floor(Math.random() * types.length)]
    const randomText = texts[Math.floor(Math.random() * texts.length)]

    addMessage({
      type: randomType,
      category: randomCategory,
      text: randomText
    })
  }, 8000) // 每8秒添加一条消息
}

onMounted(() => {
  generateInitialMessages()
  startMessageSimulation()
})

onUnmounted(() => {
  if (messageInterval) {
    clearInterval(messageInterval)
  }
})
</script>

<style scoped>
.status-feed {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  overflow: hidden;
}

.feed-header {
  padding: 15px 20px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f5f7fa;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.header-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
  max-height: 400px;
  min-height: 300px;
}

.message-item {
  padding: 12px 15px;
  border-radius: 6px;
  margin-bottom: 10px;
  border-left: 4px solid #409eff;
  background-color: white;
  transition: all 0.2s;
}

.message-item:hover {
  background-color: #f5f7fa;
  transform: translateX(2px);
}

.message-item.message-success {
  border-left-color: #67c23a;
  background-color: rgba(103, 194, 58, 0.05);
}

.message-item.message-warning {
  border-left-color: #e6a23c;
  background-color: rgba(230, 162, 60, 0.05);
}

.message-item.message-error {
  border-left-color: #f56c6c;
  background-color: rgba(245, 108, 108, 0.05);
}

.message-item.message-info {
  border-left-color: #909399;
  background-color: rgba(144, 147, 153, 0.05);
}

.message-time {
  font-size: 11px;
  color: #909399;
  margin-bottom: 6px;
  text-align: right;
}

.message-content {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 8px;
}

.message-icon {
  font-size: 16px;
  margin-top: 2px;
  flex-shrink: 0;
}

.message-item.message-success .message-icon {
  color: #67c23a;
}

.message-item.message-warning .message-icon {
  color: #e6a23c;
}

.message-item.message-error .message-icon {
  color: #f56c6c;
}

.message-item.message-info .message-icon {
  color: #909399;
}

.message-text {
  flex: 1;
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
}

.message-category {
  text-align: right;
}

.empty-messages {
  text-align: center;
  padding: 40px;
  color: #909399;
  font-size: 14px;
}

.feed-footer {
  padding: 15px 20px;
  border-top: 1px solid #e4e7ed;
  background-color: #f5f7fa;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-stats {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #606266;
}

.stat-item {
  display: flex;
  align-items: center;
}

.footer-input {
  flex: 1;
  max-width: 400px;
}

@media (max-width: 768px) {
  .feed-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }

  .header-controls {
    flex-wrap: wrap;
  }

  .feed-footer {
    flex-direction: column;
    gap: 15px;
  }

  .footer-input {
    max-width: 100%;
  }

  .messages-container {
    max-height: 300px;
  }
}
</style>