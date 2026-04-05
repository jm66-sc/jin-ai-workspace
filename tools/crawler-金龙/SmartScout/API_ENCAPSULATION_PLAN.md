# SmartScout API 封装计划

## 概述
将现有的SmartScout Python爬虫后端功能封装成RESTful API，为前端界面提供数据接口。

## 技术栈
- **API框架**: FastAPI（轻量、快速、自动文档生成）
- **异步支持**: asyncio（兼容现有爬虫的异步架构）
- **数据库**: SQLite（现有数据库保持不变）
- **认证**: 简易API Key验证（可扩展）
- **跨域**: CORS支持

## 现有后端功能分析

### 已实现的核心模块
1. **规则扩展器** (`deepseek_rule_expander.py`) - DeepSeek规则扩充
2. **数据库管理器** (`sqlite_manager.py`) - 项目管理和结果存储
3. **生产者** (`producer.py`) - 列表页抓取，生成任务队列
4. **消费者** (`consumer.py`) - 详情页抓取和字段提取
5. **完整流水线** (`run_full_pipeline.py`) - 端到端工作流

### 需要封装的功能
1. **规则确诊流程**：URL列表 → 抓取样本 → DeepSeek分析 → 返回推荐规则
2. **规则保存功能**：保存人工确认后的规则到数据库
3. **生产启动功能**：根据目标产值启动爬虫生产
4. **结果查询功能**：实时获取提取结果
5. **反馈提交功能**：提交人工验证反馈

## API 接口设计

### 1. 规则确诊接口
```python
POST /api/rule-diagnosis
```
**请求体**:
```json
{
  "urls": ["http://example.com/page1", "http://example.com/page2"],
  "initial_blacklist": ["物流", "食堂", "伙食"],
  "initial_whitelist": ["消防设备", "救援装备", "灭火器"]
}
```

**响应**:
```json
{
  "project_id": "project_abc123",
  "recommended_blacklist": ["保洁", "保安", "外卖", ...],
  "recommended_whitelist": ["消防车", "呼吸器", "防护服", ...],
  "sample_count": 50,
  "status": "completed"
}
```

**后端实现**:
- 调用现有 `DeepSeekRuleExpander.expand_rules()`
- 抓取50个列表页样本（复用 `producer.py`）
- 返回DeepSeek分析结果

### 2. 保存规则接口
```python
POST /api/rules/{project_id}
```
**请求体**:
```json
{
  "blacklist": ["物流", "食堂", "伙食", "保洁", "保安"],
  "whitelist": ["消防设备", "救援装备", "灭火器", "消防车", "呼吸器"],
  "human_confirmed": true
}
```

**响应**:
```json
{
  "success": true,
  "project_id": "project_abc123",
  "rule_count": {"blacklist": 5, "whitelist": 5}
}
```

**后端实现**:
- 调用 `SQLiteManager.create_project()` 或 `update_project_rules()`
- 更新 `human_confirmed` 状态

### 3. 启动生产接口
```python
POST /api/production/{project_id}/start
```
**请求体**:
```json
{
  "target_count": 500,
  "concurrency": 3,
  "max_pages": 50
}
```

**响应**:
```json
{
  "task_id": "task_xyz789",
  "project_id": "project_abc123",
  "status": "started",
  "estimated_time": "30分钟"
}
```

**后端实现**:
- 启动异步任务（生产者+消费者流水线）
- 返回任务ID用于状态查询
- 后台运行 `FullPipeline.run()` 的修改版本

### 4. 获取结果接口
```python
GET /api/results/{project_id}
```
**查询参数**:
- `limit`: 返回结果数量（默认50）
- `offset`: 分页偏移（默认0）
- `order_by`: 排序字段（默认 `extraction_time DESC`）

**响应**:
```json
{
  "results": [
    {
      "id": 1,
      "purchasing_unit": "XX市消防救援支队",
      "project_name": "消防车辆采购",
      "budget_amount": "150.00万元",
      "announcement_type": "招标公告",
      "detail_url": "http://example.com/detail/123",
      "extraction_time": "2026-02-11 10:30:00",
      "fields": {...} // 完整的12个字段
    }
  ],
  "total": 125,
  "project_id": "project_abc123",
  "status": "in_progress"
}
```

**后端实现**:
- 调用 `SQLiteManager.get_results_by_project()`
- 实时统计生产进度

### 5. 提交反馈接口
```python
POST /api/feedback
```
**请求体**:
```json
{
  "result_id": 123,
  "accuracy_rating": 4,  // 1-5分
  "feedback_text": "提取准确，但缺少供应商联系方式字段",
  "suggested_fields": ["供应商电话", "供应商邮箱"]
}
```

**响应**:
```json
{
  "success": true,
  "feedback_id": "fb_456"
}
```

**后端实现**:
- 创建新的 `feedback` 数据库表
- 关联到具体的结果记录

### 6. 任务状态查询接口
```python
GET /api/tasks/{task_id}
```
**响应**:
```json
{
  "task_id": "task_xyz789",
  "status": "running",  // pending|running|completed|failed
  "progress": 65,       // 百分比
  "processed": 325,     // 已处理数量
  "successful": 280,    // 成功提取数量
  "skipped": 45,        // 跳过数量
  "estimated_remaining": "15分钟",
  "started_at": "2026-02-11 10:00:00",
  "updated_at": "2026-02-11 10:30:00"
}
```

## 数据库扩展

### 新增表结构

```sql
-- 任务管理表
CREATE TABLE tasks (
    task_id TEXT PRIMARY KEY,
    project_key TEXT NOT NULL,
    status TEXT DEFAULT 'pending',  -- pending|running|completed|failed
    target_count INTEGER,
    processed_count INTEGER DEFAULT 0,
    successful_count INTEGER DEFAULT 0,
    skipped_count INTEGER DEFAULT 0,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    FOREIGN KEY (project_key) REFERENCES projects (url_key)
);

-- 反馈表
CREATE TABLE feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    result_id INTEGER NOT NULL,
    accuracy_rating INTEGER CHECK (accuracy_rating BETWEEN 1 AND 5),
    feedback_text TEXT,
    suggested_fields JSON,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (result_id) REFERENCES results (id)
);
```

## 目录结构

```
smartscout_api/
├── main.py                    # FastAPI应用入口
├── api/
│   ├── __init__.py
│   ├── dependencies.py       # 依赖项（数据库连接、认证）
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── rule_diagnosis.py # 规则确诊相关端点
│   │   ├── production.py     # 生产控制相关端点
│   │   ├── results.py        # 结果查询相关端点
│   │   └── feedback.py       # 反馈相关端点
│   └── models/
│       ├── __init__.py
│       ├── schemas.py        # Pydantic模型
│       ├── database.py       # 数据库连接和会话
│       └── crud.py          # 数据库操作
├── core/
│   ├── __init__.py
│   ├── config.py            # 配置管理
│   ├── security.py          # 安全验证
│   └── exceptions.py        # 自定义异常
├── services/
│   ├── __init__.py
│   ├── rule_service.py      # 规则确诊服务
│   ├── production_service.py # 生产服务
│   └── integration.py       # 现有后端模块集成
├── utils/
│   ├── __init__.py
│   ├── logging.py           # 日志配置
│   └── helpers.py           # 工具函数
└── requirements_api.txt     # API专用依赖
```

## 与现有代码集成策略

### 1. 模块导入重用
```python
# services/integration.py
import sys
sys.path.append('../src')  # 添加现有代码路径

from src.deepseek_rule_expander import DeepSeekRuleExpander
from src.sqlite_manager import SQLiteManager
from src.producer import Producer
from src.consumer import Consumer
```

### 2. 异步任务管理
- 使用 `asyncio` 运行现有异步爬虫
- 使用 `background_tasks` 处理长时间运行的生产任务
- 实现任务状态跟踪和取消功能

### 3. 配置共享
- 重用现有的 `config/settings.yaml` 和 `config/secrets.yaml`
- 通过环境变量覆盖配置

## 实施步骤

### 第1阶段：基础框架搭建（1-2天）
1. **安装FastAPI和相关依赖**
   ```bash
   pip install fastapi uvicorn sqlalchemy pydantic python-multipart
   ```

2. **创建FastAPI应用骨架**
   - 配置CORS、中间件、异常处理
   - 设置日志和监控

3. **数据库集成**
   - 扩展现有SQLite表结构
   - 创建SQLAlchemy模型
   - 集成现有 `sqlite_manager.py`

### 第2阶段：核心API实现（2-3天）
1. **规则确诊端点**
   - 实现URL列表处理
   - 集成DeepSeek规则扩展器
   - 返回推荐规则

2. **规则管理端点**
   - 项目创建/更新
   - 规则保存和查询

3. **生产控制端点**
   - 任务启动和状态跟踪
   - 进度实时查询

### 第3阶段：数据查询和反馈（1-2天）
1. **结果查询端点**
   - 分页和过滤支持
   - 实时数据流（可选SSE）

2. **反馈系统**
   - 反馈提交端点
   - 反馈查询和统计

### 第4阶段：测试和优化（1-2天）
1. **API测试**
   - 单元测试和集成测试
   - 性能测试

2. **错误处理**
   - 完善异常处理
   - 重试机制

3. **文档生成**
   - 自动生成OpenAPI文档
   - 使用示例

## 安全考虑

### 1. API认证（简易版）
```python
# 使用API Key验证
API_KEY = os.getenv("SMART_SCOUT_API_KEY")

@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    api_key = request.headers.get("X-API-Key")
    if api_key != API_KEY:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid API Key"}
        )
    return await call_next(request)
```

### 2. 输入验证
- 使用Pydantic模型验证所有输入
- 限制URL数量和长度
- 验证黑白名单关键词

### 3. 速率限制
- 防止滥用API
- 基于IP或API Key的限制

## 部署方案

### 开发环境
```bash
uvicorn main:app --reload --port 8000
```

### 生产环境
```bash
# 使用Gunicorn + Uvicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker部署
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements_api.txt .
RUN pip install -r requirements_api.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 预计时间
- **总开发时间**: 6-9天
- **测试和调试**: 2-3天
- **文档和部署**: 1-2天

## 风险与缓解

### 风险1：现有代码异步兼容性
- **风险**: 现有爬虫代码可能不完全兼容FastAPI的异步模型
- **缓解**: 使用线程池执行同步代码，或修改现有代码为完全异步

### 风险2：数据库并发访问
- **风险**: SQLite并发写入限制
- **缓解**: 使用连接池，限制并发写入，或迁移到PostgreSQL

### 风险3：长时间运行任务管理
- **风险**: 生产任务可能运行数小时，需要可靠的状态跟踪
- **缓解**: 实现任务队列（Celery）或使用数据库状态跟踪

## 验收标准

1. ✅ 所有5个核心API端点功能正常
2. ✅ 与现有爬虫后端无缝集成
3. ✅ 支持并发用户操作
4. ✅ 完整的错误处理和日志
5. ✅ 自动生成的API文档
6. ✅ 基本的安全防护

## 后续扩展

### 短期扩展
1. **WebSocket支持**: 实时推送生产进度
2. **批量操作**: 批量URL导入和规则应用
3. **导出功能**: 结果导出为CSV/Excel

### 长期扩展
1. **用户管理系统**: 多用户支持和权限控制
2. **规则模板**: 可复用的规则模板
3. **性能监控**: 详细的爬虫性能指标
4. **分布式爬虫**: 支持多个爬虫节点

---

**执行建议**: 建议先完成API封装，再开发前端。这样前端开发时可以直接调用真实API，避免mock数据。