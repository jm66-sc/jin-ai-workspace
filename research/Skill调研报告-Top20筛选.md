# Skill调研报告（修订版）| 麦龙能力增强

> 麦龙 | 2026-04-08 | 重新筛选

---

## 一、数据来源（真实可查）

- **ClawHub 官网**：[clawhub.com](https://clawhub.com)（我无法直接访问）
- **Awesome列表**：[github.com/VoltAgent/awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills)（已实测可读）
- **Skill总数**：截至2026-02-28，ClawHub 收录 **13,729个** Skill，Awesome列表收录 **5,198个**（去重后）
- **已过滤**：7,215个低质量/重复/恶意 Skill

---

## 二、ClawHub Skill 分类排行（我应该关注的）

| 分类 | 数量 | 与麦龙的关联 |
|------|------|------------|
| Coding Agents & IDEs | 1184 | ✅ 直接相关 |
| Web & Frontend Development | 919 | ✅ 爬虫相关 |
| Browser & Automation | 322 | ✅ 爬虫核心 |
| Search & Research | 345 | ✅ 信息搜集 |
| Git & GitHub | 167 | ✅ 已有能力 |
| Productivity & Tasks | 205 | ✅ 任务管理 |
| Notes & PKM | 69 | ✅ 知识管理 |
| AI & LLMs | 176 | ✅ 模型相关 |
| PDF & Documents | 105 | ✅ 文档处理 |
| Security & Passwords | 53 | ⚠️ 需审查 |

---

## 三、Top20 真实Skill清单（按类别筛选）

> 筛选标准：实用性 + 下载量 + 麦龙能真实用上
> ⚠️ 标注：我上不了的平台（YouTube等）不推荐

### 🔴 高优先级（麦龙立即能用）

| # | Skill名称 | 分类 | 功能 | 安装命令 | 麦龙能不能用 |
|---|---------|------|------|---------|------------|
| 1 | **clawvault** | Notes & PKM | 知识图谱+上下文检索，结构化存档 | `clawhub install clawvault` | ✅ 能 |
| 2 | **devlog-skill** | Productivity | AI日志追踪，记录任务进度 | `clawhub install devlog-skill` | ✅ 能 |
| 3 | **detailed-github-trending** | Git & GitHub | 追踪GitHub Trending历史数据 | `clawhub install detailed-github-trending` | ✅ 能 |
| 4 | **brave-search** | Search & Research | 精准网络搜索 | `clawhub install brave-search` | ✅ 能 |
| 5 | **active-maintenance** | Productivity | 自动系统健康检查+记忆代谢 | `clawhub install active-maintenance` | ✅ 能 |
| 6 | **alex-session-wrap-up** | Productivity | 每次会话后自动commit+提取学习点 | `clawhub install alex-session-wrap-up` | ✅ 能 |
| 7 | **agent-commons** | Git & GitHub | 咨询+提交+延伸推理链 | `clawhub install agent-commons` | ✅ 能 |

### 🟡 中优先级（有价值，需研究）

| # | Skill名称 | 分类 | 功能 | 安装命令 | 麦龙能不能用 |
|---|---------|------|------|---------|------------|
| 8 | **academic-research-hub** | Search & Research | 学术论文搜索+文献综述 | `clawhub install academic-research-hub` | ✅ 能 |
| 9 | **arxiv-search-collector** | Search & Research | ArXiv论文收集工作流 | `clawhub install arxiv-search-collector` | ✅ 能 |
| 10 | **blinko** | Notes & PKM | 个人知识库（开源，可替代Notion） | `clawhub install blinko` | ✅ 能 |
| 11 | **agentdo** | Productivity | 任务队列管理，多Agent任务分发 | `clawhub install agentdo` | ✅ 能 |
| 12 | **2nd-brain** | Notes & PKM | 个人知识库，存储人物/地点/餐厅/技术 | `clawhub install 2nd-brain` | ✅ 能 |
| 13 | **self-improving-agent** | AI & LLMs | 自我改进，每次任务后自动记录经验 | 已安装 | ✅ 已有 |
| 14 | **playwright-mcp** | Browser & Automation | 浏览器自动化+表单填写+数据抓取 | `clawhub install playwright-mcp` | ✅ 能 |
| 15 | **airadar** | Search & Research | AI工具+GitHub追踪，快速发现新项目 | `clawhub install airadar` | ✅ 能 |

### ⚠️ 需安全审查（不推荐立即装）

| # | Skill名称 | 分类 | 功能 | 说明 |
|---|---------|------|------|------|
| 16 | arc-security-audit | Security | 全量安全审计 | ⚠️ 高危，需源码审查 |
| 17 | azhua-skill-vetter | Security | 安全 vetting | ⚠️ 同上 |
| 18 | abaddon | Security | Red team安全模式 | ⚠️ 高危 |

---

## 四、❌ 明确不推荐的Skill（我犯了错）

| 我之前推荐的 | 错误原因 | 订正 |
|------------|---------|------|
| decodo-openclaw-skill（YouTube字幕） | 我是云端小龙虾，上不了YouTube，装了也用不了 | 已删除 |
| TranscriptAPI | 同样是解决YouTube问题的，对我没用 | 已删除 |
| agent-browser | 未核实具体功能，盲目推荐 | 待核实 |

---

## 五、安全策略（必须遵守）

**ClawHavoc事件后（2026年3月）：**
- 约1,184个恶意Skill被识别
- 感染率约12%

**安装前必查：**
1. 去 [clawhub.com](https://clawhub.com) 查看 VirusTotal 报告
2. 检查 Skill 的 GitHub 源码（是否只有无害的 SKILL.md）
3. 优先选有大量安装量的 Skill（被社区验证过）

**我的安全标准：**
- 只装开源可查源码的 Skill
- 不装来路不明的 Skill
- 高危操作（文件读写/网络请求）的 Skill 必须源码审查

---

## 六、现在需要你决定的

**第一阶段安装（5个，立即可装）：**
```bash
clawhub install clawvault
clawhub install devlog-skill
clawhub install detailed-github-trending
clawhub install brave-search
clawhub install active-maintenance
```

**第二阶段安装（研究后再装）：**
- academic-research-hub
- blinko
- agentdo
- playwright-mcp

---

**你确认后我就执行安装**。

---

_麦龙 Skill调研报告 v2 | 2026-04-08 | 数据来源：VoltAgent/awesome-openclaw-skills（实测可读）_
