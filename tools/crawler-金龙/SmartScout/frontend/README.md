# SmartScout 前端项目

基于Vue 3 + Element Plus的智能招标爬虫系统前端界面。

## 技术栈
- Vue 3.3.0
- Element Plus 2.3.8
- Pinia 2.1.6
- Axios 1.6.0
- Vite 5.0.0

## 项目结构
```
frontend/
├── public/
├── src/
│   ├── components/          # 4个核心组件
│   │   ├── RuleConfig.vue           # 规则配置区
│   │   ├── DeepSeekRecommendation.vue # DeepSeek推荐区
│   │   ├── ProductionConfig.vue     # 生产配置区
│   │   └── DataValidation.vue       # 数据验证区
│   ├── stores/             # Pinia状态管理
│   │   └── smartscout.js   # 全局状态管理
│   ├── services/           # API服务层
│   │   └── api.js          # Axios API封装
│   ├── assets/             # 静态资源
│   │   └── styles/
│   │       └── main.css    # 全局样式
│   ├── App.vue             # 根组件
│   └── main.js             # 应用入口
├── index.html              # HTML模板
├── package.json            # 依赖配置
└── vite.config.js          # Vite配置
```

## 安装和运行

### 1. 安装依赖
```bash
npm install
```

### 2. 启动开发服务器
```bash
npm run dev
```

### 3. 访问地址
- 前端界面: http://localhost:3000
- 后端API: http://localhost:8000 (需先启动阶段一的后端服务)

## 核心功能

### 1. 规则确诊流程
- 输入URL列表和初始黑白名单
- 调用DeepSeek规则扩展器
- 获取推荐的规则列表

### 2. DeepSeek推荐编辑
- 显示DeepSeek推荐的黑白名单
- 支持标签编辑（添加/删除）
- 保存规则到数据库

### 3. 生产配置与监控
- 配置目标产值、并发数、最大页数
- 启动爬虫生产任务
- 实时进度监控和统计

### 4. 数据验证与反馈
- 滚动显示提取结果
- 支持自动滚动和暂停
- 提交人工验证反馈
- 统计和数据分析

## API集成
前端通过Axios调用阶段一实现的所有5个API端点：
1. `POST /api/rule-diagnosis` - 规则确诊
2. `POST /api/rules/{project_id}` - 保存规则
3. `POST /api/production/{project_id}/start` - 启动生产
4. `GET /api/results/{project_id}` - 获取结果
5. `POST /api/feedback` - 提交反馈
6. `GET /api/tasks/{task_id}` - 任务状态查询

## 状态管理
使用Pinia进行全局状态管理，包含：
- 规则配置状态
- DeepSeek推荐状态
- 生产配置状态
- 数据验证状态
- UI状态管理

## 组件说明

### RuleConfig.vue
规则配置区域，包含：
- URL列表输入（文本域）
- 初始黑名单标签输入和管理
- 初始白名单标签输入和管理
- 规则确诊按钮

### DeepSeekRecommendation.vue
DeepSeek推荐编辑区域，包含：
- 推荐的黑名单标签显示和编辑
- 推荐的白名单标签显示和编辑
- 标签添加、删除、清空功能
- 保存规则按钮

### ProductionConfig.vue
生产配置区域，包含：
- 目标产值配置（滑块）
- 并发数配置（滑块）
- 最大翻页数配置（滑块）
- 生产进度监控（进度条）
- 实时统计信息
- 生产控制按钮

### DataValidation.vue
数据验证区域，包含：
- 数据滚动显示区域（自动滚动）
- 分页控制
- 数据项选择和反馈提交
- 反馈表单（评分、意见、建议字段）
- 数据统计面板

## 交互流程
完整的4步工作流程：
1. **规则确诊** → 2. **推荐编辑** → 3. **生产启动** → 4. **数据验证**

## 配置说明

### 代理配置
Vite配置了代理，将`/api`请求转发到`http://localhost:8000`，确保前后端分离开发。

### 环境要求
- Node.js 16+
- 阶段一后端服务已启动
- 现代浏览器（Chrome 90+, Firefox 88+, Edge 90+）

## 开发说明

### 添加新组件
```bash
# 在components目录下创建新组件
src/components/NewComponent.vue
```

### 状态管理扩展
```javascript
// 在stores/smartscout.js中添加新的state和actions
const newState = ref('')
const newAction = () => { /* ... */ }
```

### API扩展
```javascript
// 在services/api.js中添加新的API方法
export const apiService = {
  newApiMethod(data) {
    return api.post('/new-endpoint', data)
  }
}
```

## 构建部署
```bash
# 构建生产版本
npm run build

# 预览构建结果
npm run preview
```

构建结果将生成在`dist/`目录中，可直接部署到静态文件服务器。

## 注意事项
1. 确保后端API服务已启动并运行在端口8000
2. 配置文件中包含代理设置，如需更改端口请修改`vite.config.js`
3. 生产环境中需要配置正确的API地址
4. 数据验证区域的自动滚动功能可手动暂停