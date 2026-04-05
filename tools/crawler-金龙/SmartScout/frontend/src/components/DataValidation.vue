<template>
  <div class="data-validation">
    <div class="card-title">
      <el-icon><DataAnalysis /></el-icon>
      <span>数据验证</span>
    </div>

    <div v-if="!store.results.length" class="empty-state">
      <el-empty description="暂无数据，请先启动生产任务" />
    </div>

    <div v-else>
      <div class="data-header">
        <div class="data-stats">
          <span class="stat-item">
            总结果数: <strong>{{ store.totalResults }}</strong>
          </span>
          <span class="stat-item">
            当前页: <strong>{{ store.currentPage }}</strong> / {{ Math.ceil(store.totalResults / store.pageSize) }}
          </span>
          <span class="stat-item">
            显示: <strong>{{ store.paginatedResults.length }}</strong> 条
          </span>
        </div>
        <div class="data-controls">
          <div class="auto-scroll-control">
            <span>自动滚动:</span>
            <el-switch
              v-model="store.autoScroll"
              size="small"
              active-text="开"
              inactive-text="关"
            />
          </div>
          <el-button-group>
            <el-button
              size="small"
              @click="prevPage"
              :disabled="store.currentPage <= 1"
            >
              上一页
            </el-button>
            <el-button
              size="small"
              @click="nextPage"
              :disabled="store.currentPage >= Math.ceil(store.totalResults / store.pageSize)"
            >
              下一页
            </el-button>
          </el-button-group>
          <el-button
            size="small"
            @click="refreshData"
            :loading="store.isLoading"
          >
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </div>

      <div
        ref="scrollContainer"
        class="scrollable-data"
        @mouseenter="pauseScroll"
        @mouseleave="resumeScroll"
      >
        <div
          v-for="item in store.paginatedResults"
          :key="item.id"
          class="data-item"
          :class="{ selected: selectedId === item.id }"
          @click="selectItem(item)"
        >
          <div class="item-header">
            <div class="item-title">
              <el-icon><Document /></el-icon>
              <span class="title-text">{{ item.project_name || '未命名项目' }}</span>
            </div>
            <div class="item-meta">
              <el-tag size="small">{{ item.announcement_type || '未知类型' }}</el-tag>
              <span class="item-time">{{ formatTime(item.extraction_time) }}</span>
            </div>
          </div>
          <div class="item-details">
            <!-- 基础信息 -->
            <div class="detail-row">
              <span class="detail-label">项目名称:</span>
              <span class="detail-value highlight">{{ item.project_name || '未知' }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">公告类型:</span>
              <span class="detail-value">{{ item.announcement_type || '未知' }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">项目编号:</span>
              <span class="detail-value">{{ item.id || '未知' }}</span>
            </div>

            <!-- 金额信息 -->
            <div class="detail-row">
              <span class="detail-label">预算金额:</span>
              <span class="detail-value highlight">{{ item.budget_amount || '未知' }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">中标金额:</span>
              <span class="detail-value highlight">{{ item.fields?.winning_amount || '未知' }}</span>
            </div>

            <!-- 时间信息 -->
            <div class="detail-row">
              <span class="detail-label">发布时间:</span>
              <span class="detail-value">{{ formatDateTime(item.fields?.publish_time) || '未知' }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">截止时间:</span>
              <span class="detail-value">{{ formatDateTime(item.fields?.bid_deadline || item.fields?.registration_deadline) || '未知' }}</span>
            </div>

            <!-- 参与方信息 -->
            <div class="detail-row">
              <span class="detail-label">采购单位:</span>
              <span class="detail-value">{{ item.purchasing_unit || '未知' }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">采购人:</span>
              <span class="detail-value">{{ item.purchasing_unit || '未知' }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">代理机构:</span>
              <span class="detail-value">{{ item.fields?.contact_info?.split('代理机构：')[1]?.split('\n')[0] || '未知' }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">中标人:</span>
              <span class="detail-value highlight">{{ item.fields?.winning_supplier || '未知' }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">采购方式:</span>
              <span class="detail-value">{{ extractPurchaseMethod(item.fields?.project_overview) || '未知' }}</span>
            </div>

            <!-- 原文链接 -->
            <div class="detail-row">
              <span class="detail-label">原文链接:</span>
              <span class="detail-value">
                <a
                  :href="item.detail_url"
                  target="_blank"
                  @click.stop="openOriginalUrl(item.detail_url)"
                  class="original-url"
                  title="点击打开原始公告页面"
                >
                  {{ formatUrl(item.detail_url) || '未知' }}
                </a>
                <el-button
                  size="small"
                  type="text"
                  @click.stop="copyUrl(item.detail_url)"
                  title="复制链接"
                  style="margin-left: 8px;"
                >
                  <el-icon><CopyDocument /></el-icon>
                </el-button>
              </span>
            </div>

            <div class="detail-actions">
              <el-button
                size="small"
                type="primary"
                text
                @click.stop="printItem(item)"
              >
                <el-icon><Printer /></el-icon>
                打印
              </el-button>
              <el-button
                size="small"
                type="primary"
                text
                @click.stop="viewDetails(item)"
              >
                <el-icon><View /></el-icon>
                查看详情
              </el-button>
              <el-button
                size="small"
                type="success"
                text
                @click.stop="submitFeedbackForItem(item)"
              >
                <el-icon><Edit /></el-icon>
                提交反馈
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="selectedItem" class="feedback-form">
        <div class="feedback-header">
          <h3>提交反馈 - ID: {{ selectedId }}</h3>
          <el-button
            size="small"
            type="text"
            @click="clearSelection"
            :icon="Close"
          />
        </div>
        <div class="feedback-body">
          <div class="form-row">
            <div class="form-label">准确度评分</div>
            <el-rate
              v-model="feedback.accuracy_rating"
              :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
              show-text
              text-color="#606266"
              :texts="['非常差', '差', '一般', '好', '非常好']"
            />
          </div>
          <div class="form-row">
            <div class="form-label">反馈意见</div>
            <el-input
              v-model="feedback.feedback_text"
              type="textarea"
              :rows="3"
              placeholder="请输入具体的反馈意见..."
              resize="none"
            />
          </div>
          <div class="form-row">
            <div class="form-label">建议新增字段（可选）</div>
            <el-input
              v-model="newSuggestedField"
              placeholder="输入字段名称后按Enter添加"
              @keyup.enter="addSuggestedField"
              clearable
            >
              <template #append>
                <el-button @click="addSuggestedField">
                  <el-icon><Plus /></el-icon>
                </el-button>
              </template>
            </el-input>
            <div class="tag-container">
              <el-tag
                v-for="field in feedback.suggested_fields"
                :key="field"
                closable
                type="info"
                @close="removeSuggestedField(field)"
              >
                {{ field }}
              </el-tag>
            </div>
          </div>
          <div class="button-group">
            <el-button
              type="primary"
              :loading="submittingFeedback"
              @click="submitFeedback"
            >
              <el-icon><Check /></el-icon>
              提交反馈
            </el-button>
            <el-button @click="clearFeedbackForm">
              <el-icon><Delete /></el-icon>
              清空
            </el-button>
          </div>
        </div>
      </div>

      <div v-else class="no-selection">
        <el-alert
          title="点击上方数据项以提交反馈"
          type="info"
          :closable="false"
          show-icon
        />
      </div>

      <div class="summary-section">
        <h3>数据统计</h3>
        <div class="summary-grid">
          <div class="summary-item">
            <div class="summary-label">平均评分</div>
            <div class="summary-value">4.2</div>
            <div class="summary-sub">基于23条反馈</div>
          </div>
          <div class="summary-item">
            <div class="summary-label">反馈率</div>
            <div class="summary-value">15%</div>
            <div class="summary-sub">23/150条结果</div>
          </div>
          <div class="summary-item">
            <div class="summary-label">建议字段</div>
            <div class="summary-value">8个</div>
            <div class="summary-sub">待处理</div>
          </div>
          <div class="summary-item">
            <div class="summary-label">验证进度</div>
            <div class="summary-value">45%</div>
            <div class="summary-sub">67/150条</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useSmartScoutStore } from '@/stores/smartscout'
import {
  DataAnalysis,
  Refresh,
  Document,
  Close,
  Plus,
  Check,
  Delete,
  CopyDocument,
  Printer,
  View,
  Edit
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const store = useSmartScoutStore()
const scrollContainer = ref(null)
const selectedId = ref(null)
const selectedItem = ref(null)
const submittingFeedback = ref(false)
const newSuggestedField = ref('')
const scrollInterval = ref(null)

const feedback = ref({
  result_id: null,
  accuracy_rating: 3,
  feedback_text: '',
  suggested_fields: []
})

const formatTime = (timeStr) => {
  if (!timeStr) return '未知时间'
  try {
    return new Date(timeStr).toLocaleString('zh-CN')
  } catch {
    return timeStr
  }
}

const formatDateTime = (timeStr) => {
  if (!timeStr) return ''
  try {
    const date = new Date(timeStr)
    return date.toLocaleString('zh-CN')
  } catch {
    return timeStr
  }
}

const extractPurchaseMethod = (overview) => {
  if (!overview) return ''

  const methods = ['公开招标', '邀请招标', '竞争性谈判', '竞争性磋商', '单一来源采购', '询价', '电子招投标']
  for (const method of methods) {
    if (overview.includes(method)) {
      return method
    }
  }
  return ''
}

const copyUrl = (url) => {
  if (!url) {
    ElMessage.warning('URL为空')
    return
  }

  navigator.clipboard.writeText(url).then(() => {
    ElMessage.success('链接已复制到剪贴板')
  }).catch(err => {
    console.error('复制失败:', err)
    ElMessage.error('复制失败')
  })
}

const printItem = (item) => {
  if (!item) {
    ElMessage.warning('请选择要打印的数据项')
    return
  }

  const printWindow = window.open('', '_blank')
  if (!printWindow) {
    ElMessage.error('无法打开打印窗口，请检查浏览器弹窗设置')
    return
  }

  const printContent = generatePrintHtml(item)
  printWindow.document.write(printContent)
  printWindow.document.close()
  printWindow.focus()

  // 延迟打印，确保内容加载
  setTimeout(() => {
    printWindow.print()
    // 不立即关闭，让用户选择是否保存
  }, 500)
}

const generatePrintHtml = (item) => {
  const fields = item.fields || {}

  return `
  <!DOCTYPE html>
  <html lang="zh-CN">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>采购公告详情 - ${item.project_name || '未知项目'}</title>
    <style>
      body { font-family: 'Microsoft YaHei', sans-serif; margin: 20px; color: #333; }
      .print-container { max-width: 800px; margin: 0 auto; }
      .header { text-align: center; border-bottom: 2px solid #409eff; padding-bottom: 15px; margin-bottom: 25px; }
      .header h1 { color: #409eff; margin: 0; }
      .print-time { text-align: right; font-size: 14px; color: #666; margin-bottom: 20px; }
      .field-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
      .field-table th, .field-table td { border: 1px solid #ddd; padding: 12px 15px; text-align: left; }
      .field-table th { background-color: #f5f7fa; font-weight: 600; width: 150px; }
      .field-table tr:nth-child(even) { background-color: #f9f9f9; }
      .section-title { background-color: #409eff; color: white; padding: 10px 15px; margin: 25px 0 15px 0; border-radius: 4px; }
      .url-link { word-break: break-all; color: #409eff; }
      .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; color: #666; font-size: 14px; }
      @media print {
        body { margin: 0; }
        .no-print { display: none; }
      }
    </style>
  </head>
  <body>
    <div class="print-container">
      <div class="header">
        <h1>政府采购公告详情</h1>
        <p>SmartScout 智能数据提取系统</p>
      </div>

      <div class="print-time">
        打印时间：${new Date().toLocaleString('zh-CN')}
      </div>

      <h2 class="section-title">基础信息</h2>
      <table class="field-table">
        <tr>
          <th>项目名称</th>
          <td>${item.project_name || '未知'}</td>
        </tr>
        <tr>
          <th>项目编号</th>
          <td>${item.id || '未知'}</td>
        </tr>
        <tr>
          <th>公告类型</th>
          <td>${item.announcement_type || '未知'}</td>
        </tr>
        <tr>
          <th>采购方式</th>
          <td>${extractPurchaseMethod(fields.project_overview) || '未知'}</td>
        </tr>
      </table>

      <h2 class="section-title">金额信息</h2>
      <table class="field-table">
        <tr>
          <th>预算金额</th>
          <td>${item.budget_amount || '未知'}</td>
        </tr>
        <tr>
          <th>中标金额</th>
          <td>${fields.winning_amount || '未知'}</td>
        </tr>
      </table>

      <h2 class="section-title">时间信息</h2>
      <table class="field-table">
        <tr>
          <th>发布时间</th>
          <td>${formatDateTime(fields.publish_time) || '未知'}</td>
        </tr>
        <tr>
          <th>截止时间</th>
          <td>${formatDateTime(fields.bid_deadline || fields.registration_deadline) || '未知'}</td>
        </tr>
        <tr>
          <th>提取时间</th>
          <td>${formatTime(item.extraction_time) || '未知'}</td>
        </tr>
      </table>

      <h2 class="section-title">参与方信息</h2>
      <table class="field-table">
        <tr>
          <th>采购单位</th>
          <td>${item.purchasing_unit || '未知'}</td>
        </tr>
        <tr>
          <th>采购人</th>
          <td>${item.purchasing_unit || '未知'}</td>
        </tr>
        <tr>
          <th>代理机构</th>
          <td>${fields.contact_info?.split('代理机构：')[1]?.split('\\n')[0] || '未知'}</td>
        </tr>
        <tr>
          <th>中标人</th>
          <td>${fields.winning_supplier || '未知'}</td>
        </tr>
      </table>

      <h2 class="section-title">其他信息</h2>
      <table class="field-table">
        <tr>
          <th>项目概况</th>
          <td>${fields.project_overview || '未知'}</td>
        </tr>
        <tr>
          <th>联系人信息</th>
          <td>${fields.contact_info || '未知'}</td>
        </tr>
        <tr>
          <th>原文链接</th>
          <td><a href="${item.detail_url}" class="url-link">${item.detail_url || '未知'}</a></td>
        </tr>
      </table>

      <div class="footer">
        <p>本报告由 SmartScout 智能数据提取系统生成</p>
        <p>生成时间：${new Date().toLocaleString('zh-CN')}</p>
        <p class="no-print">请按 Ctrl+P 打印本页，或使用浏览器的打印功能</p>
      </div>
    </div>
  </body>
  </html>
  `
}

const selectItem = (item) => {
  selectedId.value = item.id
  selectedItem.value = item
  feedback.value.result_id = item.id
  feedback.value.accuracy_rating = 3
  feedback.value.feedback_text = ''
  feedback.value.suggested_fields = []
}

const clearSelection = () => {
  selectedId.value = null
  selectedItem.value = null
  clearFeedbackForm()
}

const viewDetails = (item) => {
  if (item.detail_url) {
    openOriginalUrl(item.detail_url)
  } else {
    ElMessage.warning('该条目没有原文链接')
    console.log('查看详情:', item)
  }
}

const formatUrl = (url) => {
  if (!url) return ''
  try {
    const urlObj = new URL(url)
    return urlObj.hostname + urlObj.pathname.substring(0, 30) + (urlObj.pathname.length > 30 ? '...' : '')
  } catch {
    return url.substring(0, 40) + (url.length > 40 ? '...' : '')
  }
}

const openOriginalUrl = (url) => {
  if (!url) {
    ElMessage.warning('URL为空')
    return
  }
  window.open(url, '_blank', 'noopener,noreferrer')
  ElMessage.success('已在新的标签页打开原文')
}

const submitFeedbackForItem = (item) => {
  selectItem(item)
}

const addSuggestedField = () => {
  if (newSuggestedField.value.trim() &&
      !feedback.value.suggested_fields.includes(newSuggestedField.value.trim())) {
    feedback.value.suggested_fields.push(newSuggestedField.value.trim())
    newSuggestedField.value = ''
  }
}

const removeSuggestedField = (field) => {
  const index = feedback.value.suggested_fields.indexOf(field)
  if (index > -1) {
    feedback.value.suggested_fields.splice(index, 1)
  }
}

const clearFeedbackForm = () => {
  feedback.value = {
    result_id: null,
    accuracy_rating: 3,
    feedback_text: '',
    suggested_fields: []
  }
  newSuggestedField.value = ''
}

const submitFeedback = async () => {
  if (!feedback.value.result_id) {
    ElMessage.warning('请选择一个数据项')
    return
  }

  if (!feedback.value.feedback_text.trim()) {
    ElMessage.warning('请输入反馈意见')
    return
  }

  submittingFeedback.value = true
  try {
    await store.submitFeedback(feedback.value)
    ElMessage.success('反馈提交成功！')
    clearFeedbackForm()
    clearSelection()
  } catch (error) {
    ElMessage.error('提交反馈失败：' + (error.detail || error.message))
  } finally {
    submittingFeedback.value = false
  }
}

const prevPage = () => {
  if (store.currentPage > 1) {
    store.currentPage--
    scrollToTop()
  }
}

const nextPage = () => {
  if (store.currentPage < Math.ceil(store.totalResults / store.pageSize)) {
    store.currentPage++
    scrollToTop()
  }
}

const refreshData = () => {
  store.fetchResults()
  ElMessage.success('数据已刷新')
}

const scrollToTop = () => {
  if (scrollContainer.value) {
    scrollContainer.value.scrollTop = 0
  }
}

const pauseScroll = () => {
  if (scrollInterval.value) {
    clearInterval(scrollInterval.value)
    scrollInterval.value = null
  }
}

const resumeScroll = () => {
  if (store.autoScroll && !scrollInterval.value) {
    startAutoScroll()
  }
}

const startAutoScroll = () => {
  if (!store.autoScroll) return

  pauseScroll()
  scrollInterval.value = setInterval(() => {
    if (scrollContainer.value) {
      const container = scrollContainer.value
      const scrollHeight = container.scrollHeight
      const clientHeight = container.clientHeight

      if (container.scrollTop + clientHeight >= scrollHeight - 10) {
        container.scrollTop = 0
      } else {
        container.scrollTop += 1
      }
    }
  }, 50)
}

onMounted(() => {
  if (store.projectId) {
    store.fetchResults()
  }
  startAutoScroll()
})

onUnmounted(() => {
  pauseScroll()
})

watch(() => store.autoScroll, (newVal) => {
  if (newVal) {
    startAutoScroll()
  } else {
    pauseScroll()
  }
})
</script>

<style scoped>
.data-validation {
  height: 100%;
}

.empty-state {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.data-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.data-stats {
  display: flex;
  gap: 20px;
}

.stat-item {
  font-size: 14px;
  color: #606266;
}

.stat-item strong {
  color: #409eff;
  margin-left: 4px;
}

.data-controls {
  display: flex;
  gap: 16px;
  align-items: center;
}

.scrollable-data {
  height: 350px;
  overflow-y: auto;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  padding: 0;
  background: white;
}

.data-item {
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: all 0.2s;
}

.data-item:hover {
  background-color: #f5f7fa;
}

.data-item.selected {
  background-color: #f0f9ff;
  border-left: 4px solid #409eff;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.item-title {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.title-text {
  font-weight: 600;
  color: #303133;
  font-size: 15px;
}

.item-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.item-time {
  font-size: 12px;
  color: #909399;
}

.item-details {
  padding-left: 28px;
}

.detail-row {
  display: flex;
  margin-bottom: 6px;
  font-size: 13px;
}

.detail-label {
  width: 80px;
  color: #909399;
  flex-shrink: 0;
}

.detail-value {
  color: #606266;
  flex: 1;
}

.detail-value.highlight {
  color: #409eff;
  font-weight: 500;
}

.detail-actions {
  margin-top: 10px;
  display: flex;
  gap: 8px;
}

.feedback-form {
  margin-top: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #dcdfe6;
}

.feedback-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.feedback-header h3 {
  margin: 0;
  color: #303133;
  font-size: 16px;
}

.no-selection {
  margin-top: 20px;
}

.summary-section {
  margin-top: 24px;
}

.summary-section h3 {
  margin-bottom: 16px;
  color: #303133;
  font-size: 16px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.summary-item {
  text-align: center;
  padding: 16px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.summary-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.summary-value {
  font-size: 24px;
  font-weight: 700;
  color: #409eff;
  margin-bottom: 4px;
}

.summary-sub {
  font-size: 12px;
  color: #909399;
}

.original-url {
  color: #409eff;
  text-decoration: none;
  cursor: pointer;
}

.original-url:hover {
  text-decoration: underline;
  color: #66b1ff;
}
</style>