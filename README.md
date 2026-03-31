# Jin AI 团队协作中枢

> 这是 Colode、金龙、麦龙三个 AI 代理的任务协调仓库。

## 成员与分工

| 代理 | 身份 | 运行环境 | 主要职责 |
|------|------|----------|----------|
| **Colode** | Claude Code 终端 Agent | 本地 Mac | 战略规划、任务分配、内容审核、方案拍板 |
| **金龙** | 腾讯 CodeBuddy + OpenCUA | 本地 Mac | 桌面操作、文件下载、视频处理、员工工具 |
| **麦龙** | MiniMax 云端 Agent | 云端（微信直连）| 信息监听、定时任务、移动端接单 |

## 仓库结构

```
jin-ai-workspace/
├── TASKS.md          ← 主任务清单（Colode 写，金龙/麦龙 读）
├── STATUS.md         ← 各代理当前状态
├── PROTOCOL.md       ← 协作规则（本文件）
├── content/
│   ├── drafts/       ← 草稿（金龙/爱马 生成）
│   ├── review/       ← 待 Colode 审核
│   └── published/    ← 已发布存档
├── intel/            ← 麦龙情报监听结果
├── knowledge/        ← 金龙下载整理的资料
└── briefs/           ← 项目背景与公司信息
```

## 轮询规则

- **金龙**：每小时检查一次 TASKS.md，执行标注 `[金龙]` 的待办任务
- **麦龙**：每天 9:00 / 15:00 / 21:00 检查，或用户在微信说"看一下任务板"时立即检查
- **Colode**：Boss 交代任务后，写入 TASKS.md 并更新 STATUS.md
