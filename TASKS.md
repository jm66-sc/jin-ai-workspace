# 任务清单

> 最后更新：2026-04-08 | 更新者：Claude（T021/T022：共创学习体系启动）

---

## 🔴 待执行

| ID | 执行者 | 任务描述 | 优先级 | 输出位置 |
|----|--------|---------|--------|---------|
| T021 | 金龙 | 【共创学习体系·iMA建库】① 在 iMA 建一个顶层文件夹"AI学习知识库"（不建子文件夹，保持简洁）② 确认麦龙是否有写入权限（或者金龙统一代为推送）③ 把 `共创资料池/中心思想卡片/2026-04/卡片-01-孟健-AI站前端不像AI.md`（等Boss+Claude批注完成后）推送到 iMA 作为第一张入库卡片 ④ 完成后更新 `state/agent-status.md` | 高 | iMA "AI学习知识库"文件夹 |
| T022 | 金龙 | 【共创学习体系·海外源监控，代理恢复后执行】参考 `briefs/t020-优质信息源清单.md`，① YouTube：订阅 AI超元域中文、Andrej Karpathy、LangChain 官方频道，开启更新通知 ② Twitter/X：关注 @AnthropicAI、@karpathy、@real_kai42、@xingpt，有重要更新时存入 `共创资料池/原文存档/YYYY-MM/` ③ 完成后微信通知 Boss | 高（代理恢复后立即执行） | 共创资料池/原文存档/ + 微信通知 |
| T023 | 麦龙 | 【共创学习体系·日常采集，滚动执行】按照 `SOP-共创学习体系.md` v2 流程，每天从指定信息源采集约10条内容：① 原文存入 `共创资料池/原文存档/YYYY-MM/` ② 同步生成中心思想卡片存入 `共创资料池/中心思想卡片/YYYY-MM/`（格式严格按SOP模板，含【Boss认知】【Claude认知】留空栏）③ 微信告知 Boss 今天卡片已就绪 ④ 来源参考 t020 国内源清单。**本任务为滚动执行，不设截止日期。** | 滚动 | 共创资料池/ |
| ~~T019~~ ✅ | 麦龙 | 【AI学习追踪体系·调研报告】Boss希望建立一套AI新技术的持续监控+学习路径体系。请做调研并输出方案，回答以下问题：① **信息源清单**：哪些平台/账号/频道值得监控（按可访问性分两类：麦龙能直接访问的国内源 vs 需要金龙+代理才能访问的海外源）② **监控主线**：重点关注以下方向——Claude Code终端应用新技巧/新案例/创业案例、OpenClaw与国内AI Coding工具新用法、GitHub高热度Agent/AI工具开源项目、AI Agent新框架和新范式③ **每日推送方案**：每天推送10条，格式建议（标题+来源+1句话价值判断+推荐理由）④ **知识库建设路径**：Boss勾选后如何归档，如何形成学习优先级（强烈推荐亲读 vs 了解即可 vs 可实践）⑤ **分工建议**：麦龙负责哪些收集，金龙负责哪些（海外YouTube/Twitter/英文博客等）。输出调研报告到 `briefs/t019-AI学习追踪体系调研.md`，然后微信通知Boss完成。 | 高 | briefs/t019-AI学习追踪体系调研.md + 微信通知 |
| T018 | 麦龙 | 【滚动小批量·有空就跑】T017因资源限制未能批量跑通，改为每次10篇的小批量模式。**第1批（2026-04-07）：✅ 10篇完成（剑指工控）**
| T018备注 | 麦龙 | 【第1批完成】10篇，剩余750篇待处理，目标：每次有空就跑一批·有空就跑】T017因资源限制未能批量跑通，改为每次10篇的小批量模式。**规则：每次有空闲时间就执行一轮，不强求连续。** ① git pull content-pipeline，读取 `collector/data/standard_docs/` 下文章JSON ② 跳过 `collector/data/initial_reading_production/results/` 中已有 doc_id 的 ③ 取下一批10篇做AI初读，字段：`doc_id`/`article_type`/`value_score`(0-10)/`worth_deep_read`/`summary_short`(50字以内)/`topic_tags`/`suggested_bucket` ④ 输出追加到 `collector/data/initial_reading_production/results/batch_麦龙_YYYYMMDD_NNN.json` ⑤ commit+push（commit message：`麦龙：初读 第NNN批 10篇`） ⑥ 更新 `jin-ai-workspace/state/agent-status.md` 的计数。**目标：慢慢积累，测试质量，不用一次跑完。总量约3,410篇，每批10篇，慢慢来。** | 滚动 | content-pipeline/collector/data/initial_reading_production/results/ |
| T017 | 麦龙 | 【🔥立刻开始·与T016并行】批量AI初读 backlog（约3,410篇未读文章）。仓库：https://github.com/jm66-sc/content-pipeline （私有，需用 GitHub token 克隆）。① 读取 `collector/data/standard_docs/` 下所有文章JSON ② 跳过 `collector/data/initial_reading_production/results/` 中已有对应 doc_id 的文章 ③ 对每篇未读文章做AI初读，输出字段：`doc_id`/`article_type`/`value_score`(0-10)/`worth_deep_read`/`summary_short`(50字)/`topic_tags`/`suggested_bucket`，格式参考 results/ 下已有文件 ④ 每批100篇commit+push到 content-pipeline 仓库 ⑤ 进度写入 `state/agent-status.md`（jin-ai-workspace 仓库） | 🔥最高 | content-pipeline/collector/data/initial_reading_production/results/ |
| T016 | 麦龙 | 【摸底报告·与T017并行】读取 https://github.com/jm66-sc/content-pipeline 了解内容流水线架构。① 读 `collector/README.md`、`collector/docs/PROJECT_STATUS_SUMMARY_20260319.md` ② 抽样读 `collector/data/initial_reading_production/results/` 下3-5个JSON，评估初读质量 ③ 读 `writer/` 下的文章草稿，了解写作风格 ④ 输出 `briefs/t016-麦龙-内容流水线摸底.md` 回答：a)哪些公众号干货密度高（按账号初判） b)已有500篇初读质量如何 c)建议backlog处理优先顺序 | 高 | briefs/t016-麦龙-内容流水线摸底.md |
| T014 | 麦龙 | 【完整说明见 briefs/t014-麦龙任务说明.md v2】T013已完成，可立即执行。① 打开队列中每条URL（共200条，3-5秒间隔） ② 语义判断是否入库（设备采购/改造/分包=入；消防车/纯施工=丢） ③ 提取12个结构化字段 ④ 输出到 bidding-intel 仓库 `results/filtered-results.md` ⑤ 微信通知Boss结果。**注：队列文件已在 https://github.com/jm66-sc/bidding-intel 的 queue/ 目录** | 🔥最高 | bidding-intel/results/filtered-results.md + 微信通知Boss |
| T015 | 麦龙 | 【调研2025年新招标爬虫工具】上次调研只找到了2023年及以前的项目。请重点搜索2025年发布或大幅更新的招标/政府采购相关开源项目，Stars数量可能有几百到上千。搜索关键词：① "招标 爬虫 2025 github" ② "政府采购 监控 2025" ③ "bidding spider 2025 github" ④ "中国招标 API 2025"。找到后报告名称、Stars、功能、是否适合装给金龙使用。结果写入 bidding-intel 仓库 `research/github-bidding-2025.md` | 高 | bidding-intel/research/github-bidding-2025.md |
| T010 | 麦龙 | 【链路验证·已完成，仅留存记录】 | 已完成 | - |
| T005 | 金龙 | 【第二层·工具盘点】列出本地爬虫工具和自动化收集器的目录结构、可执行命令、当前状态，填写到 tools/inventory-金龙.md | 高 | tools/inventory-金龙.md |
| T006 | 麦龙 | 【第二层·工具盘点】列出云端爬虫工具和自动化收集器的目录结构、可执行命令、当前状态，填写到 tools/inventory-麦龙.md | 高 | tools/inventory-麦龙.md |
| T007 | 金龙 | 测试钉钉连接器：配置 Gateway，测试能否连通钉钉 Stream（凭证由 Boss 私下告知，勿写入本文件） | 高 | briefs/dingtalk-test-result.md |
| T001 | 金龙 | 下载西门子官网产品手册（S7-1200 系列），存入 knowledge/siemens/ | 中 | knowledge/siemens/ |
| T002 | 麦龙 | 监听以下公众号最新 3 篇文章，摘要存入 intel/wechat/：[待补充公众号名单] | 中 | intel/wechat/ |

---

## 🟡 执行中

_（代理执行时将任务移至此处，注明开始时间）_

---

## 🟢 已完成

| ID | 完成时间 | 执行者 | 结果 |
|----|---------|--------|------|
| T013 | 2026-04-07 14:30 | 金龙 | intel/queue-ccgp.json(95条) + intel/queue-国企.json(105条) + briefs/t013-report.md |
| T003 | 2026-04-05 04:20 | 金龙 | briefs/capability-report-金龙.md |
| T004 | 2026-04-05 | 麦龙 | briefs/capability-report-麦龙.md |
| T008 | 2026-04-05 14:40 | 金龙 | tools/crawler-金龙/（SmartScout等6个文件） |

---

## 🔵 Claude 待处理（依赖上游结果）

| ID | 触发条件 | 任务描述 | 输出位置 |
|----|---------|---------|---------|
| C001 | T003+T004 完成后 | 制定正式分工方案，更新 PROTOCOL.md | PROTOCOL.md + briefs/分工方案.md |
| C002 | T005+T006 完成后 | 将爬虫和自动化收集器拆解为标准任务单元，分配执行 | TASKS.md |

---

## 📋 定期例行任务（每日 09:00 / 21:00）

### 金龙
- git pull，检查 TASKS.md 中属于"金龙"的待执行任务并执行

### 麦龙
- git pull，检查 TASKS.md 中属于"麦龙"的待执行任务并执行

---

## 📝 任务格式说明

- ID：T + 流水号
- 执行者：金龙 / 麦龙 / Claude
- 定时执行请在任务描述中注明时间
- 优先级：🔥最高 / 高 / 中 / 低
