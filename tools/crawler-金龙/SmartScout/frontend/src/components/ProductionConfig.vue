<template>
  <div class="production-config">
    <div class="card-title">
      <el-icon><TrendCharts /></el-icon>
      <span>生产配置</span>
    </div>

    <div v-if="!store.projectId" class="empty-state">
      <el-empty description="请先完成规则确诊和编辑" />
    </div>

    <div v-else>
      <div class="production-info">
        <el-alert
          :title="`项目: ${store.projectId}`"
          type="info"
          :closable="false"
          show-icon
        >
          <template #default>
            <div v-if="store.hasTask" class="task-info">
              任务ID: {{ store.taskId }}
              <el-button
                size="small"
                type="text"
                @click="copyTaskId"
                :icon="DocumentCopy"
              >
                复制
              </el-button>
            </div>
          </template>
        </el-alert>
      </div>

      <div v-if="!store.hasTask" class="config-section">
        <div class="form-row">
          <div class="form-label">目标产值</div>
          <el-slider
            v-model="store.targetCount"
            :min="100"
            :max="1000"
            :step="50"
            show-stops
            show-input
            :marks="{
              100: '100',
              500: '500',
              1000: '1000'
            }"
          />
          <div class="slider-value">
            目标数量: <strong>{{ store.targetCount }}</strong> 条结果
          </div>
        </div>

        <div class="form-row">
          <div class="form-label">并发数</div>
          <el-slider
            v-model="store.concurrency"
            :min="1"
            :max="10"
            :step="1"
            show-stops
            show-input
          />
          <div class="slider-value">
            并发数量: <strong>{{ store.concurrency }}</strong> 个任务同时执行
          </div>
        </div>

        <div class="form-row">
          <div class="form-label">最大翻页数</div>
          <el-slider
            v-model="store.maxPages"
            :min="10"
            :max="100"
            :step="10"
            show-stops
            show-input
          />
          <div class="slider-value">
            爬取页数: <strong>{{ store.maxPages }}</strong> 页
          </div>
        </div>

        <div class="estimate-section">
          <h4>预计信息</h4>
          <div class="estimate-grid">
            <div class="estimate-item">
              <div class="estimate-label">预计时间</div>
              <div class="estimate-value">约30分钟</div>
            </div>
            <div class="estimate-item">
              <div class="estimate-label">预计成功率</div>
              <div class="estimate-value">70-80%</div>
            </div>
            <div class="estimate-item">
              <div class="estimate-label">预计跳过率</div>
              <div class="estimate-value">约75%</div>
            </div>
          </div>
        </div>

        <div class="button-group">
          <el-button
            type="primary"
            :loading="store.isLoading"
            @click="handleStartProduction"
            size="large"
          >
            <el-icon><VideoPlay /></el-icon>
            启动生产
          </el-button>
          <el-button @click="resetConfig" size="large">
            <el-icon><Refresh /></el-icon>
            重置配置
          </el-button>
        </div>
      </div>

      <div v-else class="progress-section">
        <div class="progress-header">
          <h3>生产进度监控</h3>
          <el-tag :type="getStatusType(store.productionStatus)">
            {{ getStatusText(store.productionStatus) }}
          </el-tag>
        </div>

        <div class="progress-main">
          <el-progress
            :percentage="store.taskProgress"
            :stroke-width="16"
            :color="customColors"
            striped
            striped-flow
            :duration="10"
          />
          <div class="progress-info">
            <span>{{ store.taskProgress }}%</span>
            <span>预计剩余: {{ store.estimatedRemaining || '计算中...' }}</span>
          </div>
        </div>

        <div class="progress-stats">
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-label">已处理</div>
              <div class="stat-value">{{ store.processedCount }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">成功提取</div>
              <div class="stat-value" style="color: #67c23a">
                {{ store.successfulCount }}
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-label">跳过</div>
              <div class="stat-value" style="color: #e6a23c">
                {{ store.skippedCount }}
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-label">成功率</div>
              <div class="stat-value">
                {{
                  store.processedCount > 0
                    ? Math.round((store.successfulCount / store.processedCount) * 100) + '%'
                    : '0%'
                }}
              </div>
            </div>
          </div>
        </div>

        <div class="progress-actions">
          <el-button
            v-if="store.isProductionRunning"
            type="warning"
            @click="handleStopProduction"
            plain
          >
            <el-icon><VideoPause /></el-icon>
            暂停生产
          </el-button>
          <el-button
            v-if="store.productionStatus === 'completed'"
            type="success"
            @click="handleViewResults"
          >
            <el-icon><View /></el-icon>
            查看结果
          </el-button>
          <el-button
            v-if="store.productionStatus === 'failed'"
            type="danger"
            @click="handleRetry"
          >
            <el-icon><RefreshRight /></el-icon>
            重试
          </el-button>
          <el-button @click="handleNewTask" plain>
            <el-icon><Plus /></el-icon>
            新建任务
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useSmartScoutStore } from '@/stores/smartscout'
import {
  TrendCharts,
  VideoPlay,
  Refresh,
  VideoPause,
  View,
  RefreshRight,
  Plus,
  DocumentCopy
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const store = useSmartScoutStore()

const customColors = [
  { color: '#f56c6c', percentage: 20 },
  { color: '#e6a23c', percentage: 40 },
  { color: '#5cb87a', percentage: 60 },
  { color: '#1989fa', percentage: 80 },
  { color: '#6f7af3', percentage: 100 }
]

const getStatusType = (status) => {
  switch (status) {
    case 'running': return 'primary'
    case 'completed': return 'success'
    case 'failed': return 'danger'
    default: return 'info'
  }
}

const getStatusText = (status) => {
  switch (status) {
    case 'pending': return '等待中'
    case 'running': return '进行中'
    case 'completed': return '已完成'
    case 'failed': return '已失败'
    default: return '未知'
  }
}

const handleStartProduction = async () => {
  try {
    await store.startProduction()
    ElMessage.success('生产任务已启动！系统将自动进入"数据验证"步骤查看结果')
  } catch (error) {
    ElMessage.error('启动生产失败：' + (error.detail || error.message))
  }
}

const handleStopProduction = () => {
  ElMessage.info('暂停功能开发中...')
}

const handleViewResults = () => {
  store.setActiveStep(3)
  store.fetchResults()
}

const handleRetry = () => {
  store.taskId = ''
  store.productionStatus = 'idle'
  store.taskProgress = 0
}

const handleNewTask = () => {
  store.taskId = ''
  store.productionStatus = 'idle'
  store.taskProgress = 0
  store.processedCount = 0
  store.successfulCount = 0
  store.skippedCount = 0
}

const resetConfig = () => {
  store.targetCount = 500
  store.concurrency = 3
  store.maxPages = 50
  ElMessage.success('配置已重置为默认值')
}

const copyTaskId = () => {
  navigator.clipboard.writeText(store.taskId)
  ElMessage.success('任务ID已复制到剪贴板')
}
</script>

<style scoped>
.production-config {
  height: 100%;
}

.empty-state {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.production-info {
  margin-bottom: 20px;
}

.task-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  font-family: monospace;
  font-size: 12px;
}

.config-section {
  margin-top: 20px;
}

.slider-value {
  margin-top: 8px;
  font-size: 14px;
  color: #606266;
}

.slider-value strong {
  color: #409eff;
}

.estimate-section {
  margin-top: 30px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.estimate-section h4 {
  margin-bottom: 16px;
  color: #303133;
  font-size: 16px;
}

.estimate-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.estimate-item {
  text-align: center;
}

.estimate-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.estimate-value {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.progress-section {
  margin-top: 20px;
}

.progress-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.progress-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.progress-main {
  margin-bottom: 20px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 14px;
  color: #606266;
}

.progress-stats {
  margin-bottom: 24px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #409eff;
}

.progress-actions {
  display: flex;
  gap: 12px;
}
</style>