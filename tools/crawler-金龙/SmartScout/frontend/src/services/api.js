import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 可以在这里添加认证token等
    console.log(`API请求: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    console.log(`API响应: ${response.status} ${response.config.url}`)
    return response.data
  },
  error => {
    console.error(`API错误: ${error.message}`, error.response?.data || error)
    return Promise.reject(error.response?.data || error)
  }
)

// API端点定义
const apiService = {
  // 1. 规则确诊接口
  ruleDiagnosis(data) {
    return api.post('/rule-diagnosis', data)
  },

  // 2. 保存规则接口
  saveRules(projectId, data) {
    return api.post(`/rules/${projectId}`, data)
  },

  // 3. 启动生产接口
  startProduction(projectId, data) {
    return api.post(`/production/${projectId}/start`, data)
  },

  // 4. 获取结果接口
  getResults(projectId, params = {}) {
    const { limit = 50, offset = 0, order_by = 'extraction_time DESC' } = params
    return api.get(`/results/${projectId}`, {
      params: { limit, offset, order_by }
    })
  },

  // 5. 提交反馈接口
  submitFeedback(data) {
    return api.post('/feedback', data)
  },

  // 6. 任务状态查询接口
  getTaskStatus(taskId) {
    return api.get(`/tasks/${taskId}`)
  },

  // 健康检查
  healthCheck() {
    return api.get('/health')
  }
}

export default apiService