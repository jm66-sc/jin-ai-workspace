# SmartScout 最终实施计划
**最后更新**: 2026-02-11
**状态**: 待用户确认后进入Bypass模式

## 🎯 核心目标
完成Phase 1 CLI验证：侦察→规则扩充→生产者→消费者完整流水线

## 🔗 测试URL（确认）
```
https://search.ccgp.gov.cn/bxsearch?searchtype=2&page_index=1&kw=消防
```
**说明**: 中国政府招标网搜索"消防"，已验证成功（2-3秒获取50条数据）

## 📝 DeepSeek提示词（已修改）

### 侦察阶段Prompt（规则扩充）
```
你是一个招标公告信息分析专家。请分析以下50条招标公告标题，找出：
1. 哪些关键词/模式表示"我们不关心"的内容（黑名单）
2. 哪些关键词/模式表示"我们关心"的内容（白名单）

核心关注领域：
- 设备类：消防设备、消防工程、设备改造、设备采购
- 我们关心的：偏设备、工程、采购类的公告

不关心的领域：
- 服务类：物流配送、食堂配送、服务咨询
- 非设备类：保安、建筑材料、运输等

初始参考词：
- 白名单参考：消防设备、消防工程、设备改造、设备采购
- 黑名单参考：物流配送、食堂配送、服务咨询、保安、建筑材料

请基于这50个样本的个体特性，进行相关性分析：
1. 首先分析样本中出现的实际关键词和模式
2. 扩充充实黑白名单，特别是黑名单的解决性
3. 优先考虑高频出现的实际词条

只返回纯JSON格式：{"black_list_additions": [], "white_list_additions": []}
不要任何解释文字。
```

### 提取阶段Prompt（字段提取）
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

## 📊 数据量规划
| 阶段 | 数据量 | 说明 |
|------|--------|------|
| 侦察阶段 | 50个样本 | `simple_bids_50_20260211_032958.json` |
| 生产者阶段 | 10页约200个任务 | `tasks.jsonl`队列文件 |
| 消费者阶段 | >50个详情页解析 | 最终验收标准 |

## 🗺️ 实施阶段

### 阶段一：DeepSeek规则扩充（任务1.2）
**文件**: `src/deepseek_rule_expander.py`
**输入**: 50个样本JSON
**输出**: 纯JSON格式规则扩充
**验收**: 终端输出纯JSON，无多余废话

### 阶段二：SQLite规则资产化（任务1.3）
**文件**: `src/sqlite_manager.py`
**数据库增强**:
```sql
-- projects表新增字段
url_key TEXT PRIMARY KEY,
white_list JSON DEFAULT '[]',
black_list JSON DEFAULT '[]',
human_confirmed INTEGER DEFAULT 1,  -- 人工确认占位（默认1=已确认）
rule_expansions JSON,               -- DeepSeek完整扩充结果
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```
**功能**: CRUD操作，URL绑定，人工确认占位
**验收**: 相同URL可自动调出配置，数据库可查看

### 阶段三：生产者流水线（任务2.1/2.2）
**文件**: `src/producer.py`
**配置**: 复用`config/success_template.py`的`GOV_CRAWL_CONFIG`
**翻页**: 10页（`default_page_limit=10`）
**队列**: `data/temp/tasks.jsonl`，每行`{"title": "...", "detail_url": "...", "status": "pending"}`
**验收**: 文件可文本查看，包含约200个任务

### 阶段四：消费者流水线（任务3.1/3.2）
**文件**: `src/consumer.py`
**规则过滤**: 标题比对黑白名单，`[SKIP]`不发起请求，`[PASS]`进入详情抓取
**详情解析**: Crawl4AI抓取→Markdown→DeepSeek提取12个字段→存入数据库
**验收**: 日志显示`[SKIP]`/`[PASS]`，>50个详情页解析成功

### 阶段五：端到端测试
**文件**: `src/run_full_pipeline.py`
**流程**: 侦察→规则扩充→生产者→消费者完整执行
**验收**: 完整流程无错误，>50个详情页入库，包含原文URL

## 📁 文件结构
```
SmartScout/src/
├── config_loader.py           # 配置加载（secrets.yaml, settings.yaml）
├── deepseek_rule_expander.py  # 阶段一：规则扩充
├── sqlite_manager.py          # 阶段二：数据库CRUD
├── producer.py                # 阶段三：生产者流水线
├── consumer.py                # 阶段四：消费者流水线
└── run_full_pipeline.py       # 阶段五：端到端测试入口
```

## ✅ 验收标准（简化版）
1. ✅ DeepSeek返回纯JSON规则扩充
2. ✅ SQLite数据库包含`human_confirmed=1`占位字段
3. ✅ `tasks.jsonl`包含约200个任务
4. ✅ 消费者日志显示`[SKIP]`和`[PASS]`记录
5. ✅ 详情页解析>50个，12个字段存入数据库
6. ✅ 完整流程跑通，无错误中断

## 🔧 配置确认
- **DeepSeek API**: 已配置在`config/secrets.yaml`
- **代理信息**: 已存储但禁用（`enabled: false`）
- **默认页数**: 10页（`project.default_page_limit=10`）
- **爬取配置**: 使用`config/success_template.py`的`GOV_CRAWL_CONFIG`

## 🚀 Bypass模式准备
**状态**: 等待用户确认后进入Bypass模式
**行为**: 进入后自主开发，不再提问，直至完成所有阶段
**输出**: 每个阶段完成后在终端显示进度

## 📋 最终检查清单
- [ ] 确认测试URL正确
- [ ] 确认DeepSeek提示词符合意图
- [ ] 确认数据量规划可接受
- [ ] 确认人工确认占位机制合理
- [ ] 用户启用Bypass模式

---
**下一步**: 用户确认后，启用Bypass模式，开始实施阶段一。