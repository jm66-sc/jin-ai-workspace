# Claude → 金奥 交接指令
> 时间：2026-04-12 凌晨 | Boss已去休息，由金奥接手执行
> 读完后执行，按优先级顺序。

---

## 一、Claude今晚完成的事（你接手前的状态）

| 内容 | 状态 |
|------|------|
| `/Users/jin/Documents/jin-wiki/CLAUDE.md` — Schema规则v1.0（打分标准/卡片模板/Lint清单） | ✅ 已写完并push |
| `PROTOCOL.md` v4 — 加入金奥四方协作结构，更新心跳规则 | ✅ 已push |
| jin-ai-workspace 全部积压文件（TASKS.md/agent-status/战队重构记录等） | ✅ 已commit+push |
| jin-wiki 仓库结构 | ✅ 在线，空壳，等你填充 |

两个仓库均干净，无未提交内容。

---

## 二、你现在要做的事（按优先级）

### 🔴 P1：更新 cron 提示词（今晚或明早必须完成）

**背景**：你的 Task A（02:00文章）和 Task B（02:20视频）只完成了"抓取"，还没有"打分→生成卡片→push jin-wiki"这一步。Boss今天晚上等的就是第一张真实卡片。

**要加的步骤**（在每次抓取结束后串联执行）：

1. 对每篇文章按 `/Users/jin/Documents/jin-wiki/CLAUDE.md` §一 打分标准打分（1-10，四维加权）
2. 评分 ≥ 7.0 的文章生成 frontmatter，写入 `wiki/<方向>/YYYY-MM-DD-<来源>-<标题>.md`
3. 按 §三 卡片模板生成当天 `cards/YYYY-MM-DD.md`（必读/精品/入库列表）
4. 追加记录到 `wiki/index.md`（一行一篇）
5. `git add . && git commit -m "金奥：YYYY-MM-DD 内容入库 X篇" && git push`
6. 推送完后，把 `cards/YYYY-MM-DD.md` 移到 `cards/archive/YYYY-MM-DD.md`
7. 写入 `wiki/log.md`（操作记录）

**jin-wiki 本地路径**：`/Users/jin/Documents/jin-wiki/`
**GitHub 远端**：已配置，直接 push 即可（代理 127.0.0.1:8118 已全局生效）

---

### 🟡 P2：确认 T024/T026 自动化状态

- T024（招标情报，08:00）：脚本框架已建，确认明天早上能正常输出并 push 到 `bidding-intel/daily-reports/YYYYMMDD.md`
- T026（内容源监控，07:00）：确认明天早上报告能正常输出

两份报告 Boss 醒来要看，输出路径要对。

---

### 🟡 P3：卡片-01 仍差 Claude 认知（不是你的任务，记录一下）

`共创资料池/中心思想卡片/2026-04/卡片-01-孟健-AI站前端不像AI.md`

Claude认知栏为空，等下次Boss召唤Claude时由Claude填写。**你不要填这个。**

---

### 🔵 P4：历史文章迁移（不急，有空做）

25,160篇标准化文章还没进 jin-wiki。三步计划：
1. 第一批：500篇（评分≥7.0的）做试点入库
2. 第二批：剩余有打分结果的文章（~28K条）批量入库
3. raw 数据原地保留，不迁移

先把 cron 跑通，这批再慢慢消化。

---

## 三、你不需要管的事

- PROTOCOL.md / CLAUDE.md 修改 → 只有 Boss+Claude 改
- TASKS.md 新任务立项 → 只有 Boss+Claude 批准
- 卡片-01 Claude认知 → Claude 的事

---

## 四、麦龙通知

如果你完成了 P1（cron更新），请写一条到 `state/wechat-notify.md`，格式：

```
【金奥完成】cron已更新，打分+卡片+push已串联，jin-wiki第一张卡片将在明天凌晨自动生成。
```

麦龙会在它的心跳周期推给Boss微信。

---

*交接人：Claude（总参谋）| 接手人：金奥（主力执行者）*
