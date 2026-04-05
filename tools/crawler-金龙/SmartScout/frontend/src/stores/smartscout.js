import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useSmartScoutStore = defineStore('smartscout', () => {
  // ==================== State ====================

  // 规则配置状态
  const urls = ref(['https://search.ccgp.gov.cn/bxsearch?searchtype=2&page_index=1&kw=消防'])
  const initialBlacklist = ref([])
  const initialWhitelist = ref([])
  const projectId = ref('')

  // DeepSeek推荐状态
  const recommendedBlacklist = ref([])
  const recommendedWhitelist = ref([])
  const editedBlacklist = ref([])
  const editedWhitelist = ref([])

  // 生产配置状态
  const targetCount = ref(500)
  const concurrency = ref(3)
  const maxPages = ref(50)
  const taskId = ref('')
  const productionStatus = ref('idle') // idle, pending, running, completed, failed

  // 数据验证状态
  const results = ref([])
  const totalResults = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)
  const selectedResult = ref(null)

  // 任务进度状态
  const taskProgress = ref(0)
  const processedCount = ref(0)
  const successfulCount = ref(0)
  const skippedCount = ref(0)
  const estimatedRemaining = ref('')

  // UI状态
  const activeStep = ref(0) // 0:规则确诊, 1:推荐编辑, 2:生产启动, 3:数据验证
  const autoScroll = ref(true)
  const isLoading = ref(false)

  // ==================== Computed ====================

  const stepLabels = computed(() => [
    '规则确诊',
    'DeepSeek推荐编辑',
    '生产启动',
    '数据验证'
  ])

  const stepDescriptions = computed(() => [
    '输入URL列表和初始黑白名单',
    '编辑DeepSeek推荐的规则',
    '配置生产参数并启动爬虫',
    '查看结果并提交反馈'
  ])

  const hasProject = computed(() => !!projectId.value)
  const hasTask = computed(() => !!taskId.value)
  const isProductionRunning = computed(() => productionStatus.value === 'running')

  const paginatedResults = computed(() => {
    const start = (currentPage.value - 1) * pageSize.value
    const end = start + pageSize.value
    return results.value.slice(start, end)
  })

  // ==================== Actions ====================

  // 规则确诊相关
  async function performRuleDiagnosis() {
    isLoading.value = true
    try {
      const response = await api.ruleDiagnosis({
        urls: urls.value,
        initial_blacklist: initialBlacklist.value,
        initial_whitelist: initialWhitelist.value
      })

      projectId.value = response.project_id
      recommendedBlacklist.value = response.recommended_blacklist
      recommendedWhitelist.value = response.recommended_whitelist
      editedBlacklist.value = [...response.recommended_blacklist]
      editedWhitelist.value = [...response.recommended_whitelist]

      activeStep.value = 1
      return response
    } catch (error) {
      console.error('规则确诊失败:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  async function saveRules() {
    if (!projectId.value) {
      throw new Error('请先进行规则确诊')
    }

    isLoading.value = true
    try {
      const response = await api.saveRules(projectId.value, {
        blacklist: editedBlacklist.value,
        whitelist: editedWhitelist.value,
        human_confirmed: true
      })

      activeStep.value = 2
      return response
    } catch (error) {
      console.error('保存规则失败:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // 生产相关
  async function startProduction() {
    if (!projectId.value) {
      throw new Error('请先保存规则')
    }

    isLoading.value = true
    try {
      const response = await api.startProduction(projectId.value, {
        target_count: targetCount.value,
        concurrency: concurrency.value,
        max_pages: maxPages.value
      })

      taskId.value = response.task_id
      productionStatus.value = 'running'
      activeStep.value = 3
      startProgressPolling()
      return response
    } catch (error) {
      console.error('启动生产失败:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  async function fetchTaskStatus() {
    if (!taskId.value) return

    try {
      const status = await api.getTaskStatus(taskId.value)

      taskProgress.value = status.progress
      processedCount.value = status.processed
      successfulCount.value = status.successful
      skippedCount.value = status.skipped
      estimatedRemaining.value = status.estimated_remaining
      productionStatus.value = status.status

      if (status.status === 'completed' || status.status === 'failed') {
        stopProgressPolling()
        fetchResults()
      }

      return status
    } catch (error) {
      console.error('获取任务状态失败:', error)
    }
  }

  let progressInterval = null

  function startProgressPolling() {
    if (progressInterval) clearInterval(progressInterval)
    progressInterval = setInterval(fetchTaskStatus, 3000)
  }

  function stopProgressPolling() {
    if (progressInterval) {
      clearInterval(progressInterval)
      progressInterval = null
    }
  }

  // 数据验证相关
  async function fetchResults() {
    if (!projectId.value) return

    try {
      const response = await api.getResults(projectId.value, {
        limit: 100,
        offset: 0,
        order_by: 'extraction_time DESC'
      })

      results.value = response.results
      totalResults.value = response.total
      return response
    } catch (error) {
      console.error('获取结果失败:', error)
    }
  }

  async function submitFeedback(feedbackData) {
    isLoading.value = true
    try {
      const response = await api.submitFeedback(feedbackData)
      return response
    } catch (error) {
      console.error('提交反馈失败:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // 编辑相关
  function addBlacklistTag(tag) {
    if (tag && !editedBlacklist.value.includes(tag)) {
      editedBlacklist.value.push(tag)
    }
  }

  function removeBlacklistTag(tag) {
    const index = editedBlacklist.value.indexOf(tag)
    if (index > -1) {
      editedBlacklist.value.splice(index, 1)
    }
  }

  function addWhitelistTag(tag) {
    if (tag && !editedWhitelist.value.includes(tag)) {
      editedWhitelist.value.push(tag)
    }
  }

  function removeWhitelistTag(tag) {
    const index = editedWhitelist.value.indexOf(tag)
    if (index > -1) {
      editedWhitelist.value.splice(index, 1)
    }
  }

  // UI相关
  function setActiveStep(step) {
    activeStep.value = step
  }

  function reset() {
    urls.value = ['https://search.ccgp.gov.cn/bxsearch?searchtype=2&page_index=1&kw=消防']
    initialBlacklist.value = []
    initialWhitelist.value = []
    projectId.value = ''
    recommendedBlacklist.value = []
    recommendedWhitelist.value = []
    editedBlacklist.value = []
    editedWhitelist.value = []
    targetCount.value = 500
    concurrency.value = 3
    maxPages.value = 50
    taskId.value = ''
    productionStatus.value = 'idle'
    results.value = []
    totalResults.value = 0
    currentPage.value = 1
    selectedResult.value = null
    taskProgress.value = 0
    processedCount.value = 0
    successfulCount.value = 0
    skippedCount.value = 0
    estimatedRemaining.value = ''
    activeStep.value = 0
    autoScroll.value = true
    stopProgressPolling()
  }

  return {
    // State
    urls,
    initialBlacklist,
    initialWhitelist,
    projectId,
    recommendedBlacklist,
    recommendedWhitelist,
    editedBlacklist,
    editedWhitelist,
    targetCount,
    concurrency,
    maxPages,
    taskId,
    productionStatus,
    results,
    totalResults,
    currentPage,
    pageSize,
    selectedResult,
    taskProgress,
    processedCount,
    successfulCount,
    skippedCount,
    estimatedRemaining,
    activeStep,
    autoScroll,
    isLoading,

    // Computed
    stepLabels,
    stepDescriptions,
    hasProject,
    hasTask,
    isProductionRunning,
    paginatedResults,

    // Actions
    performRuleDiagnosis,
    saveRules,
    startProduction,
    fetchTaskStatus,
    fetchResults,
    submitFeedback,
    addBlacklistTag,
    removeBlacklistTag,
    addWhitelistTag,
    removeWhitelistTag,
    setActiveStep,
    reset,
    startProgressPolling,
    stopProgressPolling
  }
})