# SmartScout - MASTER PLAN (Project Constitution)

## 0. 角色与原则 (Role & Principles)

**项目名称**: SmartScout - 智能网页采集与规则沉淀系统
**首席架构师角色**: 极简主义胶水代码工程师，负责调度整合Crawl4AI和DeepSeek，绝不重写核心功能

### 核心原则 (Core Principles)
1. **胶水代码原则**: 80%调度逻辑 + 20%库调用，禁止重写爬虫或解析核心
2. **技术栈锁定**: 遇到问题先查文档调试，绝不擅自更换技术栈
3. **分步验证铁律**: Phase 1 CLI验证100%完成前，绝不开始Phase 2 Web界面
4. **成本控制宪法**: 消费者必须先标题过滤，后发起网络请求，必须验证SKIP率 > 75%
5. **资产沉淀原则**: URL作为项目ID，所有规则与URL绑定存储在SQLite中

## 1. 作战参数 (Operational Parameters)

### 1.1 目标靶场 (Test Target)
- **测试URL**: `https://www.ccgp-sichuan.gov.cn/maincms-web/fullSearching?searchKey=消防`
- **说明**: 四川政府采购网关于"消防"的搜索结果页，可能涉及动态加载

### 1.2 敌友识别规则 (Initial Rules)
```json
{
  "white_list": ["消防设备", "消防工程", "机电设备", "机电工程"],
  "black_list": ["保安", "物流运输", "建筑材料", "终止", "废标", "流标"]
}
```

### 1.3 目标提取字段 (Target Fields Schema)
DeepSeek必须解析出以下12个字段，若原文没有则填null：
```json
{
  "project_name": "项目名称",
  "notice_type": "公告类型",
  "buyer": "采购单位",
  "budget_amount": "预算金额",
  "winning_bid_amount": "中标金额",
  "supplier": "供应商",
  "winning_supplier": "中标供应商",
  "publish_time": "发布时间",
  "registration_deadline": "报名截止时间",
  "bid_deadline": "投标截止时间",
  "project_summary": "项目概况",
  "contact_info": "联系人信息"
}
```

## 2. 技术架构 (Technical Architecture)

### 2.1 技术栈锁定 (Tech Stack Lock)
| 组件 | 选定技术 | 版本 | 锁定理由 |
|------|----------|------|----------|
| 爬虫引擎 | Crawl4AI | ≥0.8.0 | 内置Markdown转换、异步支持、反爬规避 |
| AI解析 | DeepSeek API | OpenAI兼容 | 性价比最高、政府采购公告理解力强 |
| Web界面 | Streamlit | ≥1.28.0 | 数据展示开发最快、Python原生 |
| 规则存储 | SQLite3 | 内置 | 零配置、文件级、完美匹配规则资产化 |
| 中间队列 | JSONL文件 | 标准 | 极简可视、支持断点续传、易调试 |
| 开发语言 | Python | ≥3.9 | 生态完善、胶水代码最佳选择 |

### 2.2 系统架构图
```
用户 → Streamlit界面 → SQLite规则库
                      ↓
              侦察兵(Scout): 前50条 → DeepSeek规则扩充
                      ↓
              生产者(Producer): 翻页抓取 → tasks.jsonl队列
                      ↓
              消费者(Consumer): 标题过滤 → [SKIP]/[PASS] → Crawl4AI详情 → DeepSeek提取 → 结果库
```

### 2.3 文件队列决策 (Queue Decision)
- **选择**: 方案B (tasks.jsonl文件队列)
- **理由**: 极简且可视原则，允许直接打开文本查看中间结果，便于调试和人工审计
- **格式**: 每行一个JSON对象，包含`title`, `detail_url`, `status`字段

## 3. 数据库设计 (Database Schema)

### 3.1 SQLite数据库: data/database.sqlite

```sql
-- 项目配置表（核心资产）
CREATE TABLE projects (
    url_key TEXT PRIMARY KEY,
    black_list JSON DEFAULT '[]',
    white_list JSON DEFAULT '[]',
    target_fields TEXT,
    page_limit INTEGER DEFAULT 5,
    status TEXT DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 结构化结果表
CREATE TABLE results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_url_key TEXT NOT NULL,
    source_url TEXT UNIQUE NOT NULL,
    original_title TEXT,
    filter_status TEXT,
    extracted_data JSON NOT NULL,
    process_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_url_key) REFERENCES projects(url_key) ON DELETE CASCADE
);
```

## 4. 开发阶段计划 (Development Phases)

### Phase 0: 环境与基础搭建 (当前阶段)
- 创建项目目录结构
- 编写宪法文档 (本文件)
- 准备配置模板 (secrets.yaml留空)
- 创建requirements.txt依赖清单

### Phase 1: CLI脚本验证 (必须完成)
**Day 1 - 侦察引擎验证**
- 任务1.1: Crawl4AI抓取测试URL前50条 → 终端打印Clean JSON
- 任务1.2: DeepSeek规则扩充 → 输出纯JSON建议名单
- 任务1.3: SQLite CRUD操作实现

**Day 2 - 生产者验证**
- 任务2.1: 列表页翻页逻辑 → 提取(title, detail_url)
- 任务2.2: 任务写入tasks.jsonl队列

**Day 3 - 消费者验证 (成本控制关键)**
- 任务3.1: 标题黑名单过滤器 → 必须打印"[SKIP] 命中黑名单"且不发起请求
- 任务3.2: 详情页抓取与12字段提取
- 任务3.3: 成本控制验证 → SKIP数量 > PASS数量 × 3

**Day 4 - 集成测试与优化**
- 任务4.1: 端到端CLI测试
- 任务4.2: 错误处理与重试机制
- 任务4.3: 性能基准测试

### Phase 2: Streamlit界面集成 (Phase 1完成后)
- Web界面开发
- 实时监控展示
- 导出功能实现

## 5. 宪法级开发规范 (Constitutional Rules)

### 5.1 胶水代码规范
```python
# 正确示例 - 只做调度
import crawl4ai
import openai

# 错误示例 - 重写核心功能
import requests
from bs4 import BeautifulSoup
```

### 5.2 成本控制宪法
```python
# 消费者必须遵守的先过滤后请求原则
def consumer_workflow(task):
    if should_filter(task['title'], blacklist):
        logger.info(f"[SKIP] 命中黑名单: {task['title']}")  # 无网络请求
        return
    # 只有未命中时才发起请求
    detail = fetch_detail(task['detail_url'])
```

### 5.3 日志规范
```python
# 必须区分的日志级别
logger.info(f"[SKIP] 命中黑名单: {title}")      # 成本节省证明
logger.info(f"[PASS] 进入详情抓取: {url}")      # 实际消费
logger.error(f"[ERROR] API调用失败: {e}")       # 错误记录
```

### 5.4 错误处理规范
1. 网络错误: 重试3次，指数退避 (1s, 2s, 4s)
2. API错误: 记录到错误表，继续执行其他任务
3. 数据错误: 标记为失败，不阻塞流水线

## 6. 验收标准 (Acceptance Criteria)

### Phase 1 核心验收点
1. **任务1.1**: 终端显示50条标准JSON格式标题
2. **任务1.2**: DeepSeek输出纯JSON数组，无多余废话
3. **任务3.1**: 日志显示大量`[SKIP] 命中黑名单`记录
4. **任务3.3**: SKIP数量 > PASS数量 × 3 (过滤75%以上请求)

### 最终验收标准
1. **规则资产化**: 输入相同URL自动调出上次配置
2. **成本可控**: 平均每详情页处理成本 < 0.01元
3. **数据完整**: 12个字段提取成功率 > 90%
4. **断点续传**: 程序中断后可从中断点恢复

## 7. 关键Prompt模板 (Critical Prompts)

### 7.1 侦察阶段Prompt (规则扩充)
```
你是一个政府采购公告分析专家。请分析以下50条招标公告标题，找出：
1. 哪些关键词/模式表示"我们肯定不想要"的内容（黑名单）
2. 哪些关键词/模式表示"我们肯定想要"的内容（白名单）

初始规则：
- 白名单: {white_list}
- 黑名单: {black_list}

请基于这些初始规则进行反向推理，找出更多相关关键词。
只返回纯JSON格式：{"black_list_additions": [], "white_list_additions": []}
不要任何解释文字。
```

### 7.2 提取阶段Prompt (字段提取)
```
你是一个政府采购公告结构化提取专家。请从以下Markdown格式的公告内容中，提取以下字段：

字段定义：
- project_name (项目名称)
- notice_type (公告类型：招标/中标/询价等)
- buyer (采购单位)
- budget_amount (预算金额，转为数字或文本)
- winning_bid_amount (中标金额)
- supplier (供应商)
- winning_supplier (中标供应商)
- publish_time (发布时间，格式YYYY-MM-DD)
- registration_deadline (报名截止时间)
- bid_deadline (投标截止时间)
- project_summary (项目概况)
- contact_info (联系人信息)

规则：
1. 如果原文没有该字段，填null
2. 金额类统一处理：带单位（万、元）的转为数字或保留文本
3. 时间类统一格式化为YYYY-MM-DD
4. 只返回纯JSON对象，不要任何解释

公告内容：
{markdown_content}
```

## 8. 更新记录 (Changelog)
- 2026-02-10: 创建宪法文档，定义Phase 0基础环境
- 测试URL: https://www.ccgp-sichuan.gov.cn/maincms-web/fullSearching?searchKey=消防
- 初始规则: 白名单4个，黑名单6个关键词
- 中间队列: 选择JSONL文件方案B
