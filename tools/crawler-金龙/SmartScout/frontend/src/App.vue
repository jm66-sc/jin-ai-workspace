<template>
  <div id="app">
    <div class="container">
      <header>
        <h1>
          <el-icon><DataBoard /></el-icon>
          SmartScout - 智能招标爬虫系统
        </h1>
        <div class="header-subtitle">
          基于DeepSeek的智能规则扩展与数据提取平台
        </div>
      </header>

      <div class="step-indicator">
        <div
          v-for="(step, index) in store.stepLabels"
          :key="index"
          class="step-item"
          :class="{ active: store.activeStep === index, completed: store.activeStep > index }"
          @click="store.setActiveStep(index)"
        >
          <div class="step-icon">
            <el-icon v-if="store.activeStep > index">
              <Check />
            </el-icon>
            <span v-else>{{ index + 1 }}</span>
          </div>
          <div class="step-label">{{ step }}</div>
          <div class="step-description">{{ store.stepDescriptions[index] }}</div>
        </div>
      </div>

      <div class="process-guidance">
        <div class="guidance-text">
          <span>使用流程：1.输入URL → 2.确认规则 → 3.启动生产 → 4.查看结果 → 5.提交反馈</span>
          <span class="guidance-hint">提示：每个步骤完成后需点击"保存/启动"按钮进入下一步</span>
        </div>
      </div>

      <el-collapse v-model="activePanels" class="control-panel-collapse">
        <el-collapse-item title="系统控制面板" name="1">
          <ControlPanel />
        </el-collapse-item>
        <el-collapse-item title="状态反馈滚动显示" name="2">
          <StatusFeed />
        </el-collapse-item>
      </el-collapse>

      <div class="layout-grid">
        <div class="grid-item" :class="{ 'active-area': store.activeStep === 0 }">
          <RuleConfig />
        </div>
        <div class="grid-item" :class="{ 'active-area': store.activeStep === 1 }">
          <DeepSeekRecommendation />
        </div>
        <div class="grid-item" :class="{ 'active-area': store.activeStep === 2 }">
          <ProductionConfig />
        </div>
        <div class="grid-item full-width" :class="{ 'active-area': store.activeStep === 3 }">
          <DataValidation />
        </div>
      </div>

      <footer>
        <div class="footer-info">
          <span>后端状态: <el-tag size="small" type="success">已连接</el-tag></span>
          <span>API版本: 1.0.0</span>
          <span>项目ID: {{ store.projectId || '未设置' }}</span>
        </div>
        <div class="footer-actions">
          <el-button size="small" @click="resetAll" plain>
            <el-icon><Refresh /></el-icon>
            重置所有
          </el-button>
          <el-button size="small" @click="exportData" :disabled="!store.results.length">
            <el-icon><Download /></el-icon>
            导出数据
          </el-button>
          <el-button size="small" @click="viewLogs">
            <el-icon><View /></el-icon>
            查看日志
          </el-button>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useSmartScoutStore } from './stores/smartscout'
import RuleConfig from './components/RuleConfig.vue'
import DeepSeekRecommendation from './components/DeepSeekRecommendation.vue'
import ProductionConfig from './components/ProductionConfig.vue'
import DataValidation from './components/DataValidation.vue'
import ControlPanel from './components/ControlPanel.vue'
import StatusFeed from './components/StatusFeed.vue'
import { DataBoard, Check, Refresh, Download, View } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const store = useSmartScoutStore()
const activePanels = ref(['1', '2']) // 默认展开控制面板和状态反馈

const resetAll = () => {
  store.reset()
  ElMessage.success('已重置所有状态')
}

const exportData = () => {
  if (!store.results.length) {
    ElMessage.warning('没有数据可导出')
    return
  }

  const dataStr = JSON.stringify(store.results, null, 2)
  const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
  const exportFileDefaultName = `smartscout_export_${new Date().toISOString().slice(0,10)}.json`

  const linkElement = document.createElement('a')
  linkElement.setAttribute('href', dataUri)
  linkElement.setAttribute('download', exportFileDefaultName)
  linkElement.click()

  ElMessage.success('数据导出成功')
}

const viewLogs = () => {
  ElMessage.info('日志查看功能开发中...')
}
</script>

<style scoped>
header {
  text-align: center;
  margin-bottom: 30px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
}

header h1 {
  font-size: 28px;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.header-subtitle {
  font-size: 16px;
  opacity: 0.9;
}

.step-indicator {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 40px 0;
  position: relative;
}

.step-indicator::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 3px;
  background: #e4e7ed;
  z-index: 1;
  transform: translateY(-50%);
}

.step-item {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.3s;
  flex: 1;
  max-width: 200px;
}

.step-item:hover {
  transform: translateY(-2px);
}

.step-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: white;
  border: 3px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
  font-weight: 600;
  font-size: 18px;
  transition: all 0.3s;
}

.step-item.active .step-icon {
  border-color: #409eff;
  background: #409eff;
  color: white;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.step-item.completed .step-icon {
  border-color: #67c23a;
  background: #67c23a;
  color: white;
}

.step-label {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  text-align: center;
}

.step-item.active .step-label {
  color: #409eff;
}

.step-description {
  font-size: 12px;
  color: #909399;
  text-align: center;
  line-height: 1.4;
  height: 32px;
}

.grid-item.active-area {
  border-color: #409eff;
  box-shadow: 0 4px 20px rgba(64, 158, 255, 0.15);
}

footer {
  margin-top: 40px;
  padding: 20px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  border-radius: 8px;
}

.footer-info {
  display: flex;
  gap: 20px;
  align-items: center;
  font-size: 14px;
  color: #606266;
}

.footer-actions {
  display: flex;
  gap: 12px;
}

.control-panel-collapse {
  margin-bottom: 30px;
}

.control-panel-collapse :deep(.el-collapse-item__header) {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  background-color: #f5f7fa;
  padding: 0 20px;
  border-radius: 8px;
}

.control-panel-collapse :deep(.el-collapse-item__content) {
  padding: 20px 0;
  background-color: white;
}

.process-guidance {
  margin: 20px 0 30px 0;
  padding: 16px 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  border-radius: 8px;
  border: 1px solid #dcdfe6;
}

.guidance-text {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 14px;
  color: #606266;
  text-align: center;
}

.guidance-text span:first-child {
  font-weight: 600;
  color: #303133;
  font-size: 15px;
}

.guidance-hint {
  font-size: 13px;
  color: #909399;
  font-style: italic;
}
</style>