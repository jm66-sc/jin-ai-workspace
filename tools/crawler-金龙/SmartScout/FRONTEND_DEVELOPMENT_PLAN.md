# SmartScout 前端开发计划

## 概述
基于用户设计的极简规则配置+数据验证界面，开发Vue 3单页面应用，实现完整的规则确诊→生产→验证工作流程。

## 技术栈
- **框架**: Vue 3 + Composition API
- **构建工具**: Vite（快速热重载）
- **UI组件库**: Element Plus（丰富的组件，中文支持好）
- **HTTP客户端**: Axios
- **状态管理**: Pinia（轻量级状态管理）
- **路由**: Vue Router
- **代码质量**: ESLint + Prettier
- **类型检查**: TypeScript（可选，推荐）

## 界面设计（基于用户设计）

### 4个主要区域布局
```
┌─────────────────────────────────────────────────────────────┐
│                    SmartScout 规则配置工具                    │
├─────────────────────────────────────────────────────────────┤
│ 区域1：规则配置区                                            │
│ 区域2：DeepSeek推荐区                                        │
│ 区域3：生产配置区                                            │
│ 区域4：数据验证区                                            │
└─────────────────────────────────────────────────────────────┘
```

### 详细组件设计

#### 1. 规则配置区组件 (`RuleConfig.vue`)
```vue
<template>
  <div class="rule-config-section">
    <h2>规则配置</h2>

    <!-- URL列表输入 -->
    <div class="input-group">
      <label>URL列表（每行一个URL）</label>
      <el-input
        type="textarea"
        :rows="5"
        v-model="urls"
        placeholder="示例：&#10;http://example.com/page1&#10;http://example.com/page2"
      />
    </div>

    <!-- 黑名单输入 -->
    <div class="input-group">
      <label>黑名单关键词（每行一个，用逗号分隔）</label>
      <el-input
        type="textarea"
        :rows="3"
        v-model="blacklist"
        placeholder="示例：物流,食堂,伙食..."
      />
    </div>

    <!-- 白名单输入 -->
    <div class="input-group">
      <label>白名单关键词（每行一个，用逗号分隔）</label>
      <el-input
        type="textarea"
        :rows="3"
        v-model="whitelist"
        placeholder="示例：消防设备,救援装备,灭火器..."
      />
    </div>

    <!-- 开始规则确诊按钮 -->
    <el-button
      type="primary"
      :loading="diagnosing"
      @click="startRuleDiagnosis"
    >
      开始规则确诊
    </el-button>
  </div>
</template>
```

#### 2. DeepSeek推荐区组件 (`DeepSeekRecommendation.vue`)
```vue
<template>
  <div class="recommendation-section">
    <h2>DeepSeek推荐的黑白名单</h2>

    <!-- 黑名单推荐 -->
    <div class="recommendation-list">
      <h3>黑名单：</h3>
      <div class="tag-container">
        <el-tag
          v-for="(word, index) in recommendedBlacklist"
          :key="`black-${index}`"
          type="danger"
          closable
          @close="removeBlacklistWord(index)"
        >
          {{ word }}
        </el-tag>
      </div>
    </div>

    <!-- 白名单推荐 -->
    <div class="recommendation-list">
      <h3>白名单：</h3>
      <div class="tag-container">
        <el-tag
          v-for="(word, index) in recommendedWhitelist"
          :key="`white-${index}`"
          type="success"
          closable
          @close="removeWhitelistWord(index)"
        >
          {{ word }}
        </el-tag>
      </div>
    </div>

    <!-- 添加新关键词 -->
    <div class="add-keywords">
      <el-input
        v-model="newKeyword"
        placeholder="输入要添加的关键词"
        style="width: 200px; margin-right: 10px;"
      />
      <el-radio-group v-model="newKeywordType">
        <el-radio label="blacklist">黑名单</el-radio>
        <el-radio label="whitelist">白名单</el-radio>
      </el-radio-group>
      <el-button @click="addKeyword">添加</el-button>
    </div>

    <!-- 确认规则按钮 -->
    <el-button
      type="success"
      :loading="savingRules"
      @click="confirmRules"
    >
      确认规则
    </el-button>
  </div>
</template>
```

#### 3. 生产配置区组件 (`ProductionConfig.vue`)
```vue
<template>
  <div class="production-section">
    <h2>生产配置</h2>

    <!-- 目标产值输入 -->
    <div class="input-group">
      <label>目标产值</label>
      <el-input-number
        v-model="targetCount"
        :min="1"
        :max="10000"
        placeholder="输入目标条数"
        style="width: 200px;"
      />
      <span style="margin-left: 10px;">条</span>
    </div>

    <!-- 生产状态显示 -->
    <div v-if="productionStatus" class="status-display">
      <el-alert
        :title="productionStatus.title"
        :type="productionStatus.type"
        :description="productionStatus.description"
        show-icon
      />

      <el-progress
        :percentage="productionProgress"
        :status="productionProgress === 100 ? 'success' : undefined"
        style="margin-top: 15px;"
      />

      <div class="stats">
        <span>已处理: {{ processedCount }}</span>
        <span style="margin-left: 20px;">成功: {{ successfulCount }}</span>
        <span style="margin-left: 20px;">跳过: {{ skippedCount }}</span>
      </div>
    </div>

    <!-- 开始生产按钮 -->
    <el-button
      type="warning"
      :loading="startingProduction"
      :disabled="!projectId"
      @click="startProduction"
    >
      开始生产
    </el-button>

    <!-- 暂停/继续按钮 -->
    <el-button
      v-if="productionStatus && productionStatus.status === 'running'"
      @click="pauseProduction"
    >
      暂停
    </el-button>
    <el-button
      v-if="productionStatus && productionStatus.status === 'paused'"
      @click="resumeProduction"
    >
      继续
    </el-button>
  </div>
</template>
```

#### 4. 数据验证区组件 (`DataValidation.vue`)
```vue
<template>
  <div class="validation-section">
    <h2>数据验证</h2>

    <!-- 数据滚动显示区域 -->
    <div
      class="data-scroll-container"
      :class="{ 'paused': isPaused }"
      @click="togglePause"
    >
      <div class="data-items">
        <div
          v-for="item in displayedResults"
          :key="item.id"
          class="data-item"
        >
          <div class="item-header">
            <span class="item-index">#{{ item.id }}</span>
            <span class="item-time">{{ formatTime(item.extraction_time) }}</span>
          </div>

          <div class="item-field">
            <strong>采购单位：</strong>{{ item.purchasing_unit }}
          </div>
          <div class="item-field">
            <strong>项目名称：</strong>{{ item.project_name }}
          </div>
          <div class="item-field">
            <strong>预算金额：</strong>{{ item.budget_amount }}
          </div>
          <!-- 其他9个字段... -->

          <div class="item-actions">
            <el-link
              type="primary"
              :href="item.detail_url"
              target="_blank"
              @click.stop
            >
              查看原文
            </el-link>
            <el-button
              size="small"
              @click.stop="selectItemForFeedback(item)"
            >
              反馈
            </el-button>
          </div>

          <el-divider />
        </div>
      </div>
    </div>

    <!-- 滚动控制 -->
    <div class="scroll-controls">
      <el-button @click="togglePause">
        {{ isPaused ? '继续滚动' : '暂停滚动' }}
      </el-button>
      <el-slider
        v-model="scrollSpeed"
        :min="1"
        :max="10"
        :step="1"
        style="width: 200px; margin-left: 20px;"
      >
        <template #prefix>速度</template>
      </el-slider>
    </div>

    <!-- 反馈表单 -->
    <div v-if="selectedItem" class="feedback-form">
      <h3>对记录 #{{ selectedItem.id }} 的反馈</h3>
      <el-form :model="feedbackForm" label-width="100px">
        <el-form-item label="准确性评分">
          <el-rate v-model="feedbackForm.accuracy_rating" />
        </el-form-item>

        <el-form-item label="反馈内容">
          <el-input
            type="textarea"
            :rows="4"
            v-model="feedbackForm.feedback_text"
            placeholder="请填写反馈：&#10;1. 提取是否准确？&#10;2. 原文中还有哪些重要信息未提取？&#10;3. 其他改进建议..."
          />
        </el-form-item>

        <el-form-item label="建议新增字段">
          <el-input
            v-model="feedbackForm.suggested_fields"
            placeholder="用逗号分隔，如：供应商电话,供应商邮箱"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submitFeedback">提交反馈</el-button>
          <el-button @click="cancelFeedback">取消</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>
```

## 状态管理设计 (Pinia)

### 项目状态存储 (`stores/project.ts`)
```typescript
import { defineStore } from 'pinia'

interface ProjectState {
  // 当前项目信息
  projectId: string | null
  projectName: string

  // 规则配置
  urls: string[]
  blacklist: string[]
  whitelist: string[]

  // DeepSeek推荐
  recommendedBlacklist: string[]
  recommendedWhitelist: string[]

  // 生产状态
  productionStatus: {
    status: 'idle' | 'running' | 'paused' | 'completed' | 'failed'
    taskId: string | null
    targetCount: number
    processedCount: number
    successfulCount: number
    skippedCount: number
    startTime: string | null
    estimatedRemaining: string | null
  }

  // 提取结果
  results: any[]
  totalResults: number

  // 反馈
  feedbackHistory: any[]
}

export const useProjectStore = defineStore('project', {
  state: (): ProjectState => ({
    projectId: null,
    projectName: '',
    urls: [],
    blacklist: [],
    whitelist: [],
    recommendedBlacklist: [],
    recommendedWhitelist: [],
    productionStatus: {
      status: 'idle',
      taskId: null,
      targetCount: 0,
      processedCount: 0,
      successfulCount: 0,
      skippedCount: 0,
      startTime: null,
      estimatedRemaining: null
    },
    results: [],
    totalResults: 0,
    feedbackHistory: []
  }),

  actions: {
    // 规则确诊
    async startRuleDiagnosis() {
      // 调用API /api/rule-diagnosis
    },

    // 保存规则
    async saveRules() {
      // 调用API /api/rules/{project_id}
    },

    // 开始生产
    async startProduction(targetCount: number) {
      // 调用API /api/production/{project_id}/start
    },

    // 获取结果
    async fetchResults() {
      // 调用API /api/results/{project_id}
    },

    // 提交反馈
    async submitFeedback(feedback: any) {
      // 调用API /api/feedback
    }
  }
})
```

### UI状态存储 (`stores/ui.ts`)
```typescript
import { defineStore } from 'pinia'

interface UIState {
  // 数据验证区
  isPaused: boolean
  scrollSpeed: number
  selectedItemId: number | null

  // 通知
  notifications: Array<{
    id: number
    type: 'success' | 'warning' | 'error' | 'info'
    title: string
    message: string
    timestamp: string
  }>
}

export const useUIStore = defineStore('ui', {
  state: (): UIState => ({
    isPaused: false,
    scrollSpeed: 5,
    selectedItemId: null,
    notifications: []
  }),

  actions: {
    addNotification(notification: Omit<UIState['notifications'][0], 'id' | 'timestamp'>) {
      this.notifications.unshift({
        id: Date.now(),
        ...notification,
        timestamp: new Date().toISOString()
      })

      // 自动移除旧通知
      if (this.notifications.length > 10) {
        this.notifications = this.notifications.slice(0, 10)
      }
    }
  }
})
```

## API服务层

### API客户端 (`services/api.ts`)
```typescript
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const API_KEY = import.meta.env.VITE_API_KEY

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加loading状态
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    // 统一错误处理
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// API方法
export const ruleApi = {
  // 规则确诊
  diagnose: (data: {
    urls: string[]
    initial_blacklist: string[]
    initial_whitelist: string[]
  }) => api.post('/api/rule-diagnosis', data),

  // 保存规则
  save: (projectId: string, data: {
    blacklist: string[]
    whitelist: string[]
    human_confirmed: boolean
  }) => api.post(`/api/rules/${projectId}`, data),

  // 获取项目规则
  get: (projectId: string) => api.get(`/api/rules/${projectId}`)
}

export const productionApi = {
  // 开始生产
  start: (projectId: string, data: {
    target_count: number
    concurrency?: number
    max_pages?: number
  }) => api.post(`/api/production/${projectId}/start`, data),

  // 获取任务状态
  getStatus: (taskId: string) => api.get(`/api/tasks/${taskId}`),

  // 暂停/继续/取消任务
  pause: (taskId: string) => api.post(`/api/tasks/${taskId}/pause`),
  resume: (taskId: string) => api.post(`/api/tasks/${taskId}/resume`),
  cancel: (taskId: string) => api.post(`/api/tasks/${taskId}/cancel`)
}

export const resultsApi = {
  // 获取结果
  get: (projectId: string, params?: {
    limit?: number
    offset?: number
    order_by?: string
  }) => api.get(`/api/results/${projectId}`, { params }),

  // 实时订阅（SSE）
  subscribe: (projectId: string) => {
    const eventSource = new EventSource(
      `${API_BASE_URL}/api/results/${projectId}/stream`
    )
    return eventSource
  }
}

export const feedbackApi = {
  // 提交反馈
  submit: (data: {
    result_id: number
    accuracy_rating: number
    feedback_text: string
    suggested_fields?: string[]
  }) => api.post('/api/feedback', data),

  // 获取反馈历史
  getHistory: (projectId: string) => api.get(`/api/feedback/${projectId}`)
}

export default api
```

## 目录结构

```
frontend/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── main.ts              # 应用入口
│   ├── App.vue             # 根组件
│   ├── router/
│   │   └── index.ts        # 路由配置
│   ├── stores/
│   │   ├── index.ts        # Pinia store导出
│   │   ├── project.ts      # 项目状态管理
│   │   └── ui.ts           # UI状态管理
│   ├── services/
│   │   ├── api.ts          # API客户端
│   │   └── websocket.ts    # WebSocket服务
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.vue
│   │   │   └── Layout.vue
│   │   ├── RuleConfig.vue          # 规则配置区
│   │   ├── DeepSeekRecommendation.vue # DeepSeek推荐区
│   │   ├── ProductionConfig.vue    # 生产配置区
│   │   ├── DataValidation.vue      # 数据验证区
│   │   └── common/
│   │       ├── NotificationCenter.vue
│   │       ├── LoadingSpinner.vue
│   │       └── ErrorBoundary.vue
│   ├── views/
│   │   ├── Home.vue                # 主页面（4区域布局）
│   │   └── ProjectHistory.vue      # 项目历史页面
│   ├── utils/
│   │   ├── formatters.ts           # 数据格式化
│   │   ├── validators.ts           # 表单验证
│   │   └── helpers.ts              # 工具函数
│   ├── types/
│   │   └── index.ts                # TypeScript类型定义
│   └── assets/
│       ├── styles/
│       │   ├── main.scss           # 全局样式
│       │   ├── variables.scss      # CSS变量
│       │   └── components.scss     # 组件样式
│       └── images/
├── .env.development          # 开发环境配置
├── .env.production           # 生产环境配置
├── vite.config.ts            # Vite配置
├── tsconfig.json             # TypeScript配置
├── package.json
└── README.md
```

## 实施步骤

### 第1阶段：项目搭建和基础框架（1天）
1. **创建Vue 3项目**
   ```bash
   npm create vue@latest smartscout-frontend
   # 选择：TypeScript, Pinia, Vue Router, ESLint
   ```

2. **安装依赖**
   ```bash
   cd smartscout-frontend
   npm install element-plus axios
   npm install -D sass
   ```

3. **配置Element Plus**
   ```typescript
   // main.ts
   import ElementPlus from 'element-plus'
   import 'element-plus/dist/index.css'
   import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

   app.use(ElementPlus, { locale: zhCn })
   ```

4. **配置API基础URL**
   ```env
   # .env.development
   VITE_API_BASE_URL=http://localhost:8000
   VITE_API_KEY=dev_key_123
   ```

### 第2阶段：核心组件开发（2-3天）
1. **规则配置区组件** (`RuleConfig.vue`)
   - URL列表多行输入
   - 黑白名单输入框
   - 开始规则确诊按钮

2. **DeepSeek推荐区组件** (`DeepSeekRecommendation.vue`)
   - 标签式显示推荐关键词
   - 删除和添加关键词功能
   - 确认规则按钮

3. **生产配置区组件** (`ProductionConfig.vue`)
   - 目标产值输入
   - 生产状态显示
   - 进度条和统计信息

4. **数据验证区组件** (`DataValidation.vue`)
   - 数据滚动显示
   - 暂停/继续控制
   - 反馈表单

### 第3阶段：状态管理和API集成（2天）
1. **Pinia状态管理**
   - 项目状态存储
   - UI状态存储
   - 操作和getter

2. **API服务层**
   - Axios实例配置
   - 拦截器和错误处理
   - 各个API模块

3. **组件与API集成**
   - 规则确诊流程
   - 生产控制流程
   - 结果实时获取

### 第4阶段：交互优化和实时功能（2天）
1. **实时数据更新**
   - 轮询或WebSocket获取生产进度
   - 自动刷新结果列表

2. **数据滚动效果**
   - 平滑滚动动画
   - 速度控制
   - 暂停/继续交互

3. **错误处理和用户反馈**
   - 加载状态
   - 错误提示
   - 成功通知

### 第5阶段：测试和优化（1-2天）
1. **组件测试**
   - 单元测试关键组件
   - 交互测试

2. **性能优化**
   - 虚拟滚动处理大量数据
   - 防抖和节流
   - 代码分割

3. **响应式设计**
   - 移动端适配
   - 不同屏幕尺寸优化

## 关键交互实现

### 1. 规则确诊流程
```typescript
async function startRuleDiagnosis() {
  try {
    // 1. 显示加载状态
    uiStore.showLoading('规则确诊中...')

    // 2. 调用API
    const response = await ruleApi.diagnose({
      urls: projectStore.urls,
      initial_blacklist: projectStore.blacklist,
      initial_whitelist: projectStore.whitelist
    })

    // 3. 更新推荐结果
    projectStore.recommendedBlacklist = response.recommended_blacklist
    projectStore.recommendedWhitelist = response.recommended_whitelist
    projectStore.projectId = response.project_id

    // 4. 显示成功通知
    uiStore.addNotification({
      type: 'success',
      title: '规则确诊完成',
      message: `DeepSeek推荐了${response.recommended_blacklist.length}个黑名单词和${response.recommended_whitelist.length}个白名单词`
    })

  } catch (error) {
    uiStore.addNotification({
      type: 'error',
      title: '规则确诊失败',
      message: error.message
    })
  } finally {
    uiStore.hideLoading()
  }
}
```

### 2. 实时生产进度监控
```typescript
// 使用轮询获取生产状态
function startProductionMonitoring(taskId: string) {
  const intervalId = setInterval(async () => {
    try {
      const status = await productionApi.getStatus(taskId)

      // 更新状态
      projectStore.updateProductionStatus(status)

      // 如果完成，清除定时器
      if (status.status === 'completed' || status.status === 'failed') {
        clearInterval(intervalId)
      }

      // 获取最新结果
      if (status.processed_count > projectStore.results.length) {
        await projectStore.fetchResults()
      }
    } catch (error) {
      console.error('监控生产状态失败:', error)
    }
  }, 5000) // 每5秒轮询一次

  return intervalId
}
```

### 3. 数据自动滚动
```typescript
// 使用CSS动画和JavaScript控制
function setupAutoScroll() {
  const container = document.querySelector('.data-scroll-container')
  const items = document.querySelector('.data-items')

  let scrollSpeed = uiStore.scrollSpeed // 1-10
  let isPaused = uiStore.isPaused
  let animationId: number

  function scroll() {
    if (isPaused || !container || !items) return

    // 计算滚动距离（基于速度）
    const scrollAmount = scrollSpeed * 0.5

    // 滚动
    container.scrollTop += scrollAmount

    // 如果滚动到底部，回到顶部
    if (container.scrollTop + container.clientHeight >= items.clientHeight) {
      container.scrollTop = 0
    }

    animationId = requestAnimationFrame(scroll)
  }

  // 开始滚动
  animationId = requestAnimationFrame(scroll)

  // 清理函数
  return () => {
    cancelAnimationFrame(animationId)
  }
}
```

## 样式设计

### 全局样式变量 (`src/assets/styles/variables.scss`)
```scss
// 颜色
$primary-color: #409EFF;
$success-color: #67C23A;
$warning-color: #E6A23C;
$danger-color: #F56C6C;
$info-color: #909399;

// 布局
$header-height: 60px;
$sidebar-width: 250px;
$section-spacing: 20px;

// 响应式断点
$breakpoint-xs: 480px;
$breakpoint-sm: 768px;
$breakpoint-md: 992px;
$breakpoint-lg: 1200px;
```

### 数据滚动容器样式
```scss
.data-scroll-container {
  height: 400px;
  overflow-y: auto;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 15px;
  transition: all 0.3s ease;

  &.paused {
    background-color: #f5f7fa;
    border-color: #c0c4cc;
  }

  .data-item {
    margin-bottom: 15px;
    padding-bottom: 15px;
    border-bottom: 1px dashed #e4e7ed;

    &:last-child {
      border-bottom: none;
    }

    .item-header {
      display: flex;
      justify-content: space-between;
      margin-bottom: 10px;
      color: #909399;
      font-size: 12px;
    }

    .item-field {
      margin-bottom: 8px;
      line-height: 1.5;

      strong {
        color: #303133;
        margin-right: 5px;
      }
    }

    .item-actions {
      margin-top: 10px;
      display: flex;
      gap: 10px;
    }
  }
}
```

## 测试计划

### 单元测试
```bash
# 安装测试依赖
npm install -D vitest @vue/test-utils jsdom

# 运行测试
npm run test:unit
```

### 组件测试示例
```typescript
// tests/components/RuleConfig.spec.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import RuleConfig from '@/components/RuleConfig.vue'

describe('RuleConfig.vue', () => {
  it('正确渲染URL输入框', () => {
    const wrapper = mount(RuleConfig)
    expect(wrapper.find('textarea').exists()).toBe(true)
  })

  it('点击开始按钮触发规则确诊', async () => {
    const wrapper = mount(RuleConfig)
    await wrapper.find('button').trigger('click')
    // 验证事件被触发
  })
})
```

### E2E测试（可选）
```bash
# 使用Cypress
npm install -D cypress
npm run test:e2e
```

## 部署方案

### 开发环境
```bash
npm run dev
```

### 生产构建
```bash
npm run build
```

### Nginx配置示例
```nginx
server {
    listen 80;
    server_name smartscout.example.com;

    root /var/www/smartscout-frontend/dist;
    index index.html;

    # 代理API请求到后端
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 处理前端路由（history模式）
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

### Docker部署
```dockerfile
# 构建阶段
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# 生产阶段
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 预计时间
- **项目搭建**: 1天
- **核心组件开发**: 3天
- **状态管理和API集成**: 2天
- **交互优化**: 2天
- **测试和优化**: 2天
- **总计**: 10天

## 风险与缓解

### 风险1：API接口变化
- **风险**: 后端API可能在前端开发过程中变化
- **缓解**: 使用TypeScript定义接口类型，创建API mock服务

### 风险2：大量数据性能问题
- **风险**: 数据验证区显示大量结果可能导致性能问题
- **缓解**: 实现虚拟滚动，分页加载，性能优化

### 风险3：实时更新复杂性
- **风险**: 实时生产进度和结果更新逻辑复杂
- **缓解**: 使用WebSocket或SSE简化实时通信

## 验收标准

1. ✅ 4个主要区域功能完整
2. ✅ 完整的规则确诊→生产→验证流程
3. ✅ 实时数据更新和生产进度显示
4. ✅ 良好的用户体验和交互反馈
5. ✅ 响应式设计支持不同屏幕
6. ✅ 错误处理和边界情况处理

## 后续扩展

### 短期扩展
1. **项目历史管理**: 查看和管理历史项目
2. **规则模板**: 保存和复用规则配置
3. **批量操作**: 批量导入URL和导出结果

### 长期扩展
1. **多语言支持**: 国际化
2. **主题切换**: 深色/浅色模式
3. **高级过滤**: 结果的高级搜索和过滤
4. **数据可视化**: 生产统计图表

---

**执行建议**: 建议在API封装完成或并行开发。前端开发初期可以使用mock API数据，后期切换到真实API。