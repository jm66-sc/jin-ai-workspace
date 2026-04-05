# SmartScout - 技术规格文档

## 1. Crawl4AI 配置规格

### 1.1 基本爬取配置
```python
crawl4ai_config = {
    "url": target_url,
    "word_count_threshold": 50,  # 最小字数阈值
    "include_raw_html": False,   # 不包含原始HTML以节省空间
    "verbose": False,            # 关闭详细日志
    "wait_for": "div.search-result-item",  # 等待搜索结果项加载
    "timeout": 30000,            # 超时时间30秒
}
```

### 1.2 动态页面处理
对于四川政府采购网的可能动态加载：
```python
dynamic_config = {
    "strategy": "dynamic",       # 动态页面策略
    "scroll_delay": 2000,        # 滚动延迟2秒
    "max_scrolls": 5,            # 最大滚动次数
    "remove_popups": True,       # 移除弹窗
}
```

### 1.3 Markdown转换配置
```python
markdown_config = {
    "include_links": True,       # 包含链接
    "include_images": False,     # 不包含图片
    "include_tables": True,      # 包含表格
    "summary": False,            # 不生成摘要
}
```

## 2. DeepSeek API 调用规格

### 2.1 API参数
```python
deepseek_params = {
    "model": "deepseek-chat",
    "temperature": 0.1,          # 低随机性保证一致性
    "max_tokens": 2000,          # 最大输出token
    "response_format": {"type": "json_object"},  # 强制JSON输出
}
```

### 2.2 成本估算
- 输入token: 平均每详情页 3000 tokens
- 输出token: 平均每响应 500 tokens
- 估算成本: 0.14元/百万输入token + 0.28元/百万输出token
- 目标: 通过标题过滤减少75%详情页请求

## 3. 文件队列格式 (tasks.jsonl)

### 3.1 任务格式
```json
{
  "task_id": "uuid或序号",
  "project_url_key": "基础URL",
  "title": "公告标题原文",
  "detail_url": "完整详情页URL",
  "list_page": 1,
  "position": 25,
  "status": "pending",  // pending/processing/completed/failed
  "created_at": "2026-02-10T10:30:00"
}
```

### 3.2 状态流转
```
pending → processing → completed
          ↓
         failed → (重试) → completed
```

## 4. 日志格式规范

### 4.1 日志级别定义
- INFO: 正常流程记录 (`[SKIP]`, `[PASS]`)
- WARNING: 可恢复的错误 (网络超时、API限流)
- ERROR: 不可恢复的错误 (配置错误、数据损坏)
- DEBUG: 详细调试信息 (仅在开发时启用)

### 4.2 标准日志格式
```python
# 成本控制日志
logger.info(f"[SKIP] 命中黑名单: {title} (过滤器: {matched_keyword})")

# 正常处理日志
logger.info(f"[PASS] 进入详情抓取: {url}")

# 错误日志
logger.error(f"[ERROR] 详情页抓取失败: {url} - {error_message}")
```

## 5. 错误处理规格

### 5.1 重试策略
```python
retry_config = {
    "max_retries": 3,
    "backoff_factor": 1.0,      # 指数退避基数
    "retry_on": [               # 重试的错误类型
        "TimeoutError",
        "ConnectionError",
        "RateLimitError",
    ]
}
```

### 5.2 错误分类
1. **网络错误** (重试): 超时、连接断开
2. **API错误** (重试/跳过): 限流、认证失败
3. **数据错误** (跳过): HTML解析失败、字段缺失
4. **配置错误** (终止): API Key无效、URL格式错误

## 6. 性能指标规格

### 6.1 关键性能指标 (KPI)
| 指标 | 目标值 | 测量方式 |
|------|--------|----------|
| 标题过滤率 | >75% | SKIP数量 / 总任务数 |
| 平均详情页处理时间 | <30秒 | 端到端计时 |
| 字段提取成功率 | >90% | 非null字段数 / 总字段数 |
| 内存使用峰值 | <500MB | 内存监控 |

### 6.2 监控点
1. **生产者**: 每页抓取时间、URL提取成功率
2. **消费者**: 过滤决策时间、详情页抓取时间、DeepSeek处理时间
3. **系统**: 队列积压量、内存使用、错误率

## 7. 测试数据规格

### 7.1 测试URL
- 主测试URL: `https://www.ccgp-sichuan.gov.cn/maincms-web/fullSearching?searchKey=消防`
- 备用测试URL: 需要时可提供其他政府采购网站

### 7.2 验证数据集
- 侦察阶段: 50条标题样本
- 生产阶段: 5页列表数据 (约100-150条)
- 消费阶段: 按75%过滤率，实际处理25-38条详情

## 8. 部署规格

### 8.1 本地开发环境
- Python 3.9+
- 至少4GB可用内存
- 稳定网络连接

### 8.2 生产环境要求
- Linux服务器 (Ubuntu 20.04+)
- Python虚拟环境
- SQLite数据库文件备份机制
- 日志轮转配置