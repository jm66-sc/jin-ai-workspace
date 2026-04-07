# 钉钉AI员工集成调研报告

> 麦龙 | 2026-04-07 | 供明天/后天讨论参考

---

## 一、钉钉的AI能力现状（2026年最新）

### 1.1 钉钉AI定位

- **2025年12月**：发布全球首个**工作智能操作系统 Agent OS**，专为AI打造
- **2026年**：AI深度融入钉钉全员工作流，不只是聊天工具
- **DingTalk Real**：AI Agent在物理世界的延伸，支持复杂企业环境安全执行

### 1.2 钉钉AI员工（AI小钉）

官方定义：企业可在钉钉创建**AI员工**，配置知识库、工作流、自动回复规则。

已有能力：
- 智能问答
- 审批流程自动触发
- 消息推送
- 日程管理
- 群管理

---

## 二、OpenClaw接入钉钉的方案

### 方案A：Stream模式（已配置，正在调试）

**当前状态**：麦龙已配置 Stream 模式，但未连通（返回 systemError）

**配置要素**：
- Client ID: dingmjsswyewby4nuggt
- Client Secret: lQ7y0uannvdFV7p3MsesQKnTqHF_f_I_nkmet5kHtgQNin53L8C2H33sA12-Zoaj
- AgentId: 4422491926
- Stream endpoint: https://api.dingtalk.com/v1.0/gateway/connections/open

**问题**：返回 systemError，可能原因：
1. 服务器IP被钉钉限制（上海Alibaba Cloud IP）
2. Stream能力未完全就绪
3. 需要配置 Stream Callback URL

### 方案B：Webhook模式（建议测试）

**优势**：钉钉主动推送，无需 outbound 连接
**适合场景**：消息接收 + 自动回复

### 方案C：官方"一键创建AI员工"（最新）

钉钉开放平台提供：开发者通过AI员工+OpenClaw能力，快速搭建AI员工。

文档：open.dingtalk.com/document/dingstart/build-dingtalk-ai-employees

---

## 三、接入后能做什么（对我们业务的价值）

### 3.1 与现有招标业务的结合

| 场景 | 钉钉能做什么 | 需要什么 |
|------|------------|---------|
| **新招标信息到达** | 钉钉群推送通知 | 麦龙爬虫 + 钉钉API |
| **招标截止提醒** | 自动@相关人员 | 日程同步 |
| **审批流程** | 投标报名审批 | 钉钉审批流 |
| **团队协作** | 麦龙/金龙任务分配 | 钉钉群 |

### 3.2 与新鸿基/西恒利业务的结合

- **商机推送**：招标信息 → 钉钉群 → 团队立即看到
- **审批流**：投标审批 → 钉钉审批 → 领导手机直接批
- **进度跟踪**：项目状态更新 → 钉钉通知相关人

---

## 四、钉钉 vs 企业微信 vs 飞书（对我们）

| 对比项 | 钉钉 | 企业微信 | 飞书 |
|--------|------|---------|------|
| AI能力 | ⭐⭐⭐⭐ Agent OS | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| 审批流 | ⭐⭐⭐⭐ 强大 | ⭐⭐⭐ | ⭐⭐⭐ |
| 与现有系统对接 | ⭐⭐⭐⭐ 开放平台 | ⭐⭐⭐ | ⭐⭐⭐ |
| OpenClaw集成 | ⭐⭐⭐⭐ 文档完善 | ⭐⭐⭐ | ⭐⭐⭐ |
| 对我们适用性 | **⭐⭐⭐⭐** | ⭐⭐⭐ | ⭐⭐⭐ |

**结论**：钉钉更适合我们的业务场景（审批+流程自动化）

---

## 五、待讨论问题

1. **Stream vs Webhook**：哪种模式更适合我们？
2. **AI小钉能做什么**：审批触发？自动分配任务？
3. **钉钉群结构**：新鸿基/西恒利用什么群结构？
4. **与现有微信通知的关系**：钉钉和微信同时用还是替代？

---

## 六、参考资料

- 钉钉官方AI员工文档：https://open.dingtalk.com/document/dingstart/build-dingtalk-ai-employees
- OpenClaw钉钉集成（腾讯云）：https://cloud.tencent.com/developer/article/2637745
- 钉钉PaaS不限量额度公告：https://open.dingtalk.com/document/development/open-ai-paas-report
- 钉钉Agent OS发布：https://finance.eastmoney.com/a/202512243600702221.html

---

_麦龙 | 钉钉集成调研 | 2026-04-07_
