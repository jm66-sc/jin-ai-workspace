<template>
  <div class="control-panel">
    <!-- 演示数据警告 -->
    <el-alert
      title="演示面板提示"
      type="warning"
      description="此控制面板当前显示的是演示数据，并非真实的系统状态。系统控制功能尚未连接到后端服务。"
      show-icon
      :closable="false"
      style="margin-bottom: 20px;"
    />

    <div class="card-title">
      <el-icon><Operation /></el-icon>
      <span>系统控制面板</span>
    </div>

    <!-- 控制按钮组 -->
    <div class="control-buttons">
      <el-button-group class="main-controls">
        <el-button
          type="success"
          :icon="VideoPlay"
          @click="startSystem"
          :loading="startingSystem"
          :disabled="systemStatus.backend === 'running'"
        >
          启动系统
        </el-button>
        <el-button
          type="danger"
          :icon="VideoPause"
          @click="stopSystem"
          :loading="stoppingSystem"
          :disabled="systemStatus.backend === 'stopped'"
        >
          停止系统
        </el-button>
        <el-button
          type="warning"
          :icon="Refresh"
          @click="restartSystem"
          :loading="restartingSystem"
        >
          重启系统
        </el-button>
        <el-button
          type="info"
          :icon="Connection"
          @click="testConnections"
          :loading="testingConnections"
        >
          测试连接
        </el-button>
      </el-button-group>
    </div>

    <!-- 系统状态监控 -->
    <div class="status-monitor">
      <h3>
        <el-icon><Monitor /></el-icon>
        系统状态监控
      </h3>

      <div class="status-grid">
        <div class="status-item" :class="getStatusClass(systemStatus.backend)">
          <div class="status-icon">
            <el-icon v-if="systemStatus.backend === 'running'"><SuccessFilled /></el-icon>
            <el-icon v-else-if="systemStatus.backend === 'stopped'"><CircleCloseFilled /></el-icon>
            <el-icon v-else><WarningFilled /></el-icon>
          </div>
          <div class="status-info">
            <div class="status-label">后端服务</div>
            <div class="status-value">{{ getStatusText(systemStatus.backend) }}</div>
            <div class="status-detail">http://localhost:8000</div>
          </div>
        </div>

        <div class="status-item" :class="getStatusClass(systemStatus.frontend)">
          <div class="status-icon">
            <el-icon v-if="systemStatus.frontend === 'running'"><SuccessFilled /></el-icon>
            <el-icon v-else-if="systemStatus.frontend === 'stopped'"><CircleCloseFilled /></el-icon>
            <el-icon v-else><WarningFilled /></el-icon>
          </div>
          <div class="status-info">
            <div class="status-label">前端服务</div>
            <div class="status-value">{{ getStatusText(systemStatus.frontend) }}</div>
            <div class="status-detail">http://localhost:3001</div>
          </div>
        </div>

        <div class="status-item" :class="getStatusClass(systemStatus.database)">
          <div class="status-icon">
            <el-icon v-if="systemStatus.database === 'running'"><SuccessFilled /></el-icon>
            <el-icon v-else-if="systemStatus.database === 'stopped'"><CircleCloseFilled /></el-icon>
            <el-icon v-else><WarningFilled /></el-icon>
          </div>
          <div class="status-info">
            <div class="status-label">数据库</div>
            <div class="status-value">{{ getStatusText(systemStatus.database) }}</div>
            <div class="status-detail">SQLite (smartscout.db)</div>
          </div>
        </div>

        <div class="status-item" :class="getStatusClass(systemStatus.tasks)">
          <div class="status-icon">
            <el-icon v-if="systemStatus.tasks === 'running'"><SuccessFilled /></el-icon>
            <el-icon v-else-if="systemStatus.tasks === 'stopped'"><CircleCloseFilled /></el-icon>
            <el-icon v-else><WarningFilled /></el-icon>
          </div>
          <div class="status-info">
            <div class="status-label">任务状态</div>
            <div class="status-value">{{ getStatusText(systemStatus.tasks) }}</div>
            <div class="status-detail">{{ activeTasks }} 个活跃任务</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 系统资源监控 -->
    <div class="resource-monitor">
      <h3>
        <el-icon><TrendCharts /></el-icon>
        系统资源监控
      </h3>

      <div class="resource-grid">
        <div class="resource-item">
          <div class="resource-header">
            <span class="resource-label">CPU使用率</span>
            <span class="resource-value">{{ cpuUsage }}%</span>
          </div>
          <div class="progress-bar">
            <div
              class="progress-fill"
              :style="{ width: cpuUsage + '%', backgroundColor: getUsageColor(cpuUsage) }"
            ></div>
          </div>
          <div class="resource-detail">核心数: 8</div>
        </div>

        <div class="resource-item">
          <div class="resource-header">
            <span class="resource-label">内存使用</span>
            <span class="resource-value">{{ memoryUsage }} GB</span>
          </div>
          <div class="progress-bar">
            <div
              class="progress-fill"
              :style="{ width: memoryPercent + '%', backgroundColor: getUsageColor(memoryPercent) }"
            ></div>
          </div>
          <div class="resource-detail">总内存: 16 GB</div>
        </div>

        <div class="resource-item">
          <div class="resource-header">
            <span class="resource-label">磁盘使用</span>
            <span class="resource-value">{{ diskUsage }} GB</span>
          </div>
          <div class="progress-bar">
            <div
              class="progress-fill"
              :style="{ width: diskPercent + '%', backgroundColor: getUsageColor(diskPercent) }"
            ></div>
          </div>
          <div class="resource-detail">总容量: 100 GB</div>
        </div>

        <div class="resource-item">
          <div class="resource-header">
            <span class="resource-label">网络状态</span>
            <span class="resource-value" :class="{ 'text-success': networkStatus === 'online', 'text-warning': networkStatus === 'offline' }">
              {{ networkStatus === 'online' ? '在线' : '离线' }}
            </span>
          </div>
          <div class="progress-bar">
            <div
              class="progress-fill"
              :style="{ width: networkStatus === 'online' ? '100%' : '0%', backgroundColor: networkStatus === 'online' ? '#67c23a' : '#e6a23c' }"
            ></div>
          </div>
          <div class="resource-detail">延迟: {{ networkLatency }}ms</div>
        </div>
      </div>
    </div>

    <!-- 连接状态拓扑图（简化版） -->
    <div class="topology-section">
      <h3>
        <el-icon><Share /></el-icon>
        连接状态拓扑图
      </h3>
      <div class="topology-diagram">
        <div class="topology-node backend-node" :class="systemStatus.backend">
          <el-icon><Cpu /></el-icon>
          <div>后端服务</div>
          <div class="node-status">{{ getStatusText(systemStatus.backend) }}</div>
        </div>
        <div class="topology-connection" :class="systemStatus.backend"></div>
        <div class="topology-node database-node" :class="systemStatus.database">
          <el-icon><DataBoard /></el-icon>
          <div>数据库</div>
          <div class="node-status">{{ getStatusText(systemStatus.database) }}</div>
        </div>
        <div class="topology-connection" :class="systemStatus.frontend"></div>
        <div class="topology-node frontend-node" :class="systemStatus.frontend">
          <el-icon><Monitor /></el-icon>
          <div>前端服务</div>
          <div class="node-status">{{ getStatusText(systemStatus.frontend) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Operation,
  VideoPlay,
  VideoPause,
  Refresh,
  Connection,
  Monitor,
  SuccessFilled,
  CircleCloseFilled,
  WarningFilled,
  TrendCharts,
  Share,
  Cpu,
  DataBoard
} from '@element-plus/icons-vue'
import api from '@/services/api'

// 系统状态
const systemStatus = ref({
  backend: 'unknown',
  frontend: 'unknown',
  database: 'unknown',
  tasks: 'idle'
})

// 资源使用情况
const cpuUsage = ref(0)
const memoryUsage = ref(0)
const memoryPercent = ref(0)
const diskUsage = ref(0)
const diskPercent = ref(0)
const networkStatus = ref('online')
const networkLatency = ref(0)
const activeTasks = ref(0)

// 加载状态
const startingSystem = ref(false)
const stoppingSystem = ref(false)
const restartingSystem = ref(false)
const testingConnections = ref(false)

// 状态轮询定时器
let statusInterval = null

const getStatusClass = (status) => {
  switch (status) {
    case 'running': return 'status-running'
    case 'stopped': return 'status-stopped'
    case 'unknown': return 'status-unknown'
    default: return 'status-warning'
  }
}

const getStatusText = (status) => {
  switch (status) {
    case 'running': return '运行中'
    case 'stopped': return '已停止'
    case 'unknown': return '未知'
    default: return '异常'
  }
}

const getUsageColor = (percent) => {
  if (percent < 50) return '#67c23a' // 绿色
  if (percent < 80) return '#e6a23c' // 黄色
  return '#f56c6c' // 红色
}

// 系统控制函数
const startSystem = async () => {
  startingSystem.value = true
  try {
    // TODO: 调用后端API启动系统
    await new Promise(resolve => setTimeout(resolve, 1000)) // 模拟延迟
    ElMessage.success('系统启动命令已发送')
    systemStatus.value.backend = 'running'
    systemStatus.value.frontend = 'running'
  } catch (error) {
    ElMessage.error('启动系统失败: ' + error.message)
  } finally {
    startingSystem.value = false
  }
}

const stopSystem = async () => {
  stoppingSystem.value = true
  try {
    // TODO: 调用后端API停止系统
    await new Promise(resolve => setTimeout(resolve, 800))
    ElMessage.success('系统停止命令已发送')
    systemStatus.value.backend = 'stopped'
    systemStatus.value.frontend = 'stopped'
  } catch (error) {
    ElMessage.error('停止系统失败: ' + error.message)
  } finally {
    stoppingSystem.value = false
  }
}

const restartSystem = async () => {
  restartingSystem.value = true
  try {
    // TODO: 调用后端API重启系统
    await new Promise(resolve => setTimeout(resolve, 1500))
    ElMessage.success('系统重启命令已发送')
    systemStatus.value.backend = 'running'
    systemStatus.value.frontend = 'running'
  } catch (error) {
    ElMessage.error('重启系统失败: ' + error.message)
  } finally {
    restartingSystem.value = false
  }
}

const testConnections = async () => {
  testingConnections.value = true
  try {
    // 测试后端连接
    const health = await api.healthCheck()
    systemStatus.value.backend = 'running'
    ElMessage.success('后端连接正常')

    // 模拟前端连接测试
    await new Promise(resolve => setTimeout(resolve, 500))
    systemStatus.value.frontend = 'running'

    // 模拟数据库测试
    await new Promise(resolve => setTimeout(resolve, 300))
    systemStatus.value.database = 'running'

    ElMessage.success('所有连接测试通过')
  } catch (error) {
    ElMessage.error('连接测试失败: ' + error.message)
    systemStatus.value.backend = 'stopped'
  } finally {
    testingConnections.value = false
  }
}

// 更新资源使用情况（模拟数据）
const updateResourceUsage = () => {
  // 模拟CPU使用率
  cpuUsage.value = Math.floor(Math.random() * 30) + 20

  // 模拟内存使用
  memoryUsage.value = (Math.random() * 2 + 1).toFixed(1)
  memoryPercent.value = Math.floor((memoryUsage.value / 16) * 100)

  // 模拟磁盘使用
  diskUsage.value = (Math.random() * 20 + 30).toFixed(1)
  diskPercent.value = Math.floor((diskUsage.value / 100) * 100)

  // 模拟网络延迟
  networkLatency.value = Math.floor(Math.random() * 50) + 20

  // 模拟活跃任务数
  activeTasks.value = Math.floor(Math.random() * 5)
}

// 初始化状态检查
const checkSystemStatus = async () => {
  try {
    // 检查后端健康状态
    const health = await api.healthCheck()
    systemStatus.value.backend = 'running'

    // 模拟其他状态检查
    systemStatus.value.frontend = 'running'
    systemStatus.value.database = 'running'
    systemStatus.value.tasks = activeTasks.value > 0 ? 'running' : 'idle'
  } catch (error) {
    systemStatus.value.backend = 'stopped'
    systemStatus.value.frontend = 'unknown'
    systemStatus.value.database = 'unknown'
  }
}

onMounted(() => {
  // 初始状态检查
  checkSystemStatus()

  // 启动状态轮询
  statusInterval = setInterval(() => {
    checkSystemStatus()
    updateResourceUsage()
  }, 5000)

  // 初始资源数据
  updateResourceUsage()
})

onUnmounted(() => {
  if (statusInterval) {
    clearInterval(statusInterval)
  }
})
</script>

<style scoped>
.control-panel {
  padding: 20px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 24px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.card-title .el-icon {
  font-size: 20px;
  color: #409eff;
}

.control-buttons {
  margin-bottom: 30px;
}

.main-controls {
  display: flex;
  gap: 12px;
}

.main-controls .el-button {
  padding: 12px 24px;
  font-size: 14px;
  flex: 1;
}

.status-monitor {
  margin-bottom: 30px;
}

.status-monitor h3 {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  font-size: 16px;
  color: #303133;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.status-item {
  padding: 20px;
  border-radius: 8px;
  background: white;
  border: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  gap: 15px;
  transition: all 0.3s;
}

.status-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.status-item.status-running {
  border-color: #67c23a;
  background-color: rgba(103, 194, 58, 0.05);
}

.status-item.status-stopped {
  border-color: #f56c6c;
  background-color: rgba(245, 108, 108, 0.05);
}

.status-item.status-unknown {
  border-color: #909399;
  background-color: rgba(144, 147, 153, 0.05);
}

.status-item.status-warning {
  border-color: #e6a23c;
  background-color: rgba(230, 162, 60, 0.05);
}

.status-icon {
  font-size: 32px;
}

.status-item.status-running .status-icon {
  color: #67c23a;
}

.status-item.status-stopped .status-icon {
  color: #f56c6c;
}

.status-item.status-unknown .status-icon {
  color: #909399;
}

.status-item.status-warning .status-icon {
  color: #e6a23c;
}

.status-info {
  flex: 1;
}

.status-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 4px;
}

.status-value {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.status-detail {
  font-size: 12px;
  color: #909399;
}

.resource-monitor {
  margin-bottom: 30px;
}

.resource-monitor h3 {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  font-size: 16px;
  color: #303133;
}

.resource-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.resource-item {
  padding: 20px;
  border-radius: 8px;
  background: white;
  border: 1px solid #e4e7ed;
}

.resource-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.resource-label {
  font-size: 14px;
  color: #606266;
}

.resource-value {
  font-size: 18px;
  font-weight: 600;
  color: #409eff;
}

.resource-value.text-success {
  color: #67c23a;
}

.resource-value.text-warning {
  color: #e6a23c;
}

.progress-bar {
  height: 8px;
  background-color: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.resource-detail {
  font-size: 12px;
  color: #909399;
}

.topology-section {
  margin-bottom: 20px;
}

.topology-section h3 {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  font-size: 16px;
  color: #303133;
}

.topology-diagram {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  position: relative;
}

.topology-node {
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  min-width: 120px;
  border: 2px solid #e4e7ed;
  background: white;
  z-index: 2;
}

.topology-node .el-icon {
  font-size: 32px;
  margin-bottom: 8px;
  color: #409eff;
}

.topology-node.running {
  border-color: #67c23a;
  background-color: rgba(103, 194, 58, 0.1);
}

.topology-node.stopped {
  border-color: #f56c6c;
  background-color: rgba(245, 108, 108, 0.1);
}

.topology-node.unknown {
  border-color: #909399;
  background-color: rgba(144, 147, 153, 0.1);
}

.node-status {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.topology-connection {
  flex: 1;
  height: 3px;
  background-color: #e4e7ed;
  position: relative;
}

.topology-connection.running {
  background-color: #67c23a;
}

.topology-connection.stopped {
  background-color: #f56c6c;
}

.topology-connection.unknown {
  background-color: #909399;
}

.topology-connection::before {
  content: '';
  position: absolute;
  top: -4px;
  right: -4px;
  width: 11px;
  height: 11px;
  border-radius: 50%;
  background-color: inherit;
}

@media (max-width: 1200px) {
  .status-grid,
  .resource-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .topology-diagram {
    flex-direction: column;
    gap: 20px;
  }

  .topology-connection {
    width: 3px;
    height: 40px;
  }

  .topology-connection::before {
    top: auto;
    bottom: -4px;
    right: -4px;
  }
}

@media (max-width: 768px) {
  .status-grid,
  .resource-grid {
    grid-template-columns: 1fr;
  }

  .main-controls {
    flex-direction: column;
  }
}
</style>