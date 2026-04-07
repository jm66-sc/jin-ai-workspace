# 任务清单

> 最后更新：2026-04-07 | 更新者：Claude（仓库重构：bidding-intel 拆分）

---

## 🔴 待执行

| ID | 执行者 | 任务描述 | 优先级 | 输出位置 |
|----|--------|---------|--------|---------|
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
