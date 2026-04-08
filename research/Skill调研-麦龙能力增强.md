# Skill调研报告：麦龙能力增强方案

> 麦龙 | 2026-04-08 | 调研报告

---

## 一、ClawHub 现状

- 截至2026年3月：ClawHub 收录 **13,729个** 社区 Skill
- 每天安装量：15,000+
- OpenClaw 官方技能注册中心（类比"AI Agent 的 npm"）

---

## 二、推荐安装的 Skill（按需求分类）

### 🟢 A类：立即可安装（我现有能力直接增强）

#### A1. Web相关能力

| Skill名称 | 功能 | 安装命令 | 适用场景 |
|---------|------|---------|---------|
| **decodo-openclaw-skill** | 通用URL抓取、Amazon解析、YouTube字幕提取、Google搜索 | `clawhub install decodo-openclaw-skill` | 抓取任意网页内容 |
| **Brave Search** | 实时网络搜索，比普通搜索更准确 | `clawhub install brave-search` | 替代普通搜索 |
| **browser-automation** | 浏览器自动化操作 | `clawhub install browser-automation` | JS动态加载网站 |

#### A2. 知识管理

| Skill名称 | 功能 | 安装命令 | 适用场景 |
|---------|------|---------|---------|
| **ClawVault** | 知识图谱+上下文检索，建立个人知识库 | `clawhub install clawvault` | 把学到的内容结构化存档 |
| **devlog-skill** | AI日志追踪，记录任务进度和项目状态 | `clawhub install devlog-skill` | 追踪T018等长期任务进度 |
| **self-improving-agent**（已有） | 自我改进，每次任务后自动记录经验教训 | 已安装 | 避免重复犯同样的错 |

#### A3. GitHub能力

| Skill名称 | 功能 | 安装命令 | 适用场景 |
|---------|------|---------|---------|
| **detailed-github-trending** | 追踪GitHub Trending历史数据，Star/Commit趋势 | `clawhub install detailed-github-trending` | 监控AI/Agent开源热点 |
| **github-actions** | GitHub Actions自动化 | `clawhub install github-actions` | 自动化GitHub工作流 |

---

### 🟡 B类：对我有价值，需要研究是否可装

#### B1. 阅读理解增强

| Skill名称 | 功能 | 适用场景 |
|---------|------|---------|
| **TranscriptAPI** | 视频内容转文字+摘要（解决B站视频无法理解的问题） | 把YouTube/B站视频转文字后阅读 |
| **Notion** | 读写Notion笔记，作为知识库 | 与Boss共享笔记 |

#### B2. 任务管理

| Skill名称 | 功能 | 适用场景 |
|---------|------|---------|
| **Mission Control** | 任务优先级分析和调度 | T018长期批处理任务管理 |
| **priority-analyzer** | 自动分析任务优先级 | TASKS.md管理 |

#### B3. 多Agent协作

| Skill名称 | 功能 | 适用场景 |
|---------|------|---------|
| **agent-teams** | 多Agent团队协作配置 | 麦龙+金龙+Cloud Code三层协作 |
| **multi-agent-communication** | 多Agent之间消息传递配置 | Agent间协作 |

---

## 三、最推荐安装的 Top 5

| 优先级 | Skill | 理由 |
|--------|-------|------|
| 🔴 第1 | **decodo-openclaw-skill** | 直接解决"抓不到内容"的问题（动态网页、YouTube字幕） |
| 🔴 第2 | **ClawVault** | 把学到的东西结构化存档，建立知识库 |
| 🔴 第3 | **detailed-github-trending** | 每天追踪GitHub热点，不需要手动搜 |
| 🟡 第4 | **devlog-skill** | 追踪T018等长期任务进度，不丢不漏 |
| 🟡 第5 | **Brave Search** | 搜索结果更精准，减少信息误判 |

---

## 四、安全警告 ⚠️

**ClawHavoc事件（2026年3月）：**
- 恶意攻击者在ClawHub上传了1,184个伪装Skill（天气助手、效率工具等）
- 感染率约12%
- **已识别的恶意Skill：约341-1,184个**

**安全策略：**
1. 只从官方推荐列表安装，不装无名Skill
2. 安装前检查Skill的GitHub源码
3. 高危Skill（涉及网络请求、文件操作）必须审查

---

## 五、安装计划建议

**第一阶段（今天可装）：**
```
clawhub install decodo-openclaw-skill
clawhub install clawvault
clawhub install devlog-skill
clawhub install detailed-github-trending
```

**第二阶段（研究后装）：**
- TranscriptAPI（解决B站视频问题）
- Mission Control（任务管理）

---

## 六、待Boss确认

1. 是否授权麦龙安装这些Skill？
2. 是否需要先审查源码再装？
3. ClawVault作为知识库，是否与IMA功能重叠？

---

_麦龙 Skill调研报告 | 2026-04-08_
