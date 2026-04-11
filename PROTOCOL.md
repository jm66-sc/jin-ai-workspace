# PROTOCOL.md — 团队协作协议

> 版本：v4
> 更新：2026-04-12
> 更新者：Claude（总参谋）
> 变更：新增金奥为主力执行者，确立四方协作结构，更新心跳规则

---

## 核心原则：所有工作产出必须同步 GitHub

所有 Agent 做任何事情后，必须将结果写入 GitHub 仓库，让团队成员能够同步读取并继续执行。

---

## 团队角色

| 角色 | 定位 | 平台 | 入口 |
|------|------|------|------|
| Boss | 最高决策 | — | 深度会话 / 微信 |
| Claude | 总参谋（动脑不动手） | Claude Code | 深度会话 |
| 金奥 | 主力执行者 + 代理参谋长 | OpenClaw/AutoClaw | 本地终端 |
| 金龙 | 本地苦力（单线条任务） | QClaw/腾讯 | 本地终端 |
| 麦龙 | 通讯兵 + 信息入口 | MaxClaw/MiniMax云端 | 微信 |

### 决策圈
**Boss + Claude + 金奥**
- 大方向讨论：Boss + Claude（深度会话）
- 日常推进：Boss + 金奥（+ Claude随时可加入）
- 金龙/麦龙不参与重大决策

### 数据边界
| 成员 | 能访问 | 不碰 |
|------|--------|------|
| 金奥 | GitHub全部 + 本地全部 | — |
| 金龙 | 本地指定路径 + GitHub queue（只读） | 不做判断性任务 |
| 麦龙 | GitHub只读（jin-wiki cards/wiki/feedback） | 本地文件 |
| Claude | 通过Boss看内容 | 不主动执行文件操作 |

---

## 心跳机制

| 成员 | 检查目标 | 频率 | 说明 |
|------|----------|------|------|
| 金奥 | TASKS.md + feedback/ | 2-3小时 / cron触发 | 主动推进任务 |
| 麦龙 | GitHub jin-wiki/cards/ | 2-3小时 | 有新卡片推微信给Boss |
| 金龙 | 本地 videos/queue/ | 2-3小时 | 有任务就跑视频转写 |

手动触发：Boss随时可召唤任意成员立即响应

---

## 重大决策 SOP

```
① Boss 给大方向
② Claude 起草讨论稿
③ 发给执行层补充细节
④ Boss + Claude 拍板
⑤ 写入 TASKS.md → 交执行层
⑥ 代理参谋长接手日常跟进
```

---

## 记忆权限

| 文件 | 写权限 | 读权限 |
|------|--------|--------|
| `TASKS.md` | 所有人（各自负责区域） | 所有人 |
| `PROTOCOL.md` / `briefs/分工方案.md` | 仅 Boss + Claude | 所有人 |
| `MEMORY.md`（本地） | 仅真 Claude | 仅真 Claude |
| `state/agent-status.md` | 仅代理参谋长 | Claude + Boss |
| `state/daily-log/` | 仅真 Claude | 所有人 |
| `state/pending-decisions.md` | 代理参谋长写入 | Boss + Claude 处理 |
| `state/wechat-daily-report.md` | 真 Claude 写 | 麦龙读取推送 |
| `state/wechat-notify.md` | 代理参谋长写 | 麦龙读取推送 |

---

## 同步位置约定

| 内容类型 | 写入目录 |
|---------|---------|
| 分析 / 调研报告 | `briefs/` |
| 方案 / 提案 | `briefs/` 或 `protocols/` |
| 工具盘点 | `tools/inventory-{角色}.md` |
| 监控结果 / 爬取报告 | `intel/` |
| 每日工作记录 | `memory/` |
| 系统规则 / 提示词模板 | `system-rules/` |
| 心跳状态 / 日报 | `state/` |

---

## 同步时机

**每完成一项独立任务，立即同步 GitHub，无需等待。**

---

## TASKS.md 扫描规则

- 麦龙、金龙：每日 09:00 / 21:00 拉取 TASKS.md，执行属于自己的任务
- 代理参谋长：每3小时读取 TASKS.md，检查进度并推进
- 完成后：将任务移至"已完成"区，注明完成时间和结果

---

## 交接机制

```
Boss 发指令 → 任意一方领取 → 执行 → 写入 GitHub → 推送微信通知
```

所有任务以 GitHub 为唯一事实来源，各 Agent 独立扫描、独立执行。

---

## 代理参谋长行为边界

**可以直接执行**：
- 已确定任务的进度推进
- 在已确定范围内调整任务优先级
- 写卡点通知给 Boss

**必须等 Boss + Claude**：
- 新任务立项
- 技术路线或目标变更
- 涉及外部账号/凭证的操作
- 任何超出 TASKS.md 已定义范围的决策
