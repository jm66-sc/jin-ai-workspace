# 港大 OpenCUA 项目调研 — 麦龙完整报告

> 调研：麦龙 | 2026-04-06
> 目标：汇报给 Boss 和 Cloud Code（参谋长）
> 背景： Boss 发现金龙用港大视觉方式操作浏览器方法不对，需调研该项目

---

## 一、项目是什么

Boss 提到的"港大 UC A"项目，实为：

| 名称 | 准确名称 | 来源 |
|------|---------|------|
| UC A / UCUCA / OpenCUA | **OpenCUA** | 香港大学 XLANG Lab（导师：余涛教授） |

**项目全称：** OpenCUA: Open Foundations for Computer-Use Agents

**官网：** https://opencua.xlang.ai/
**论文：** arXiv:2508.09123（2025年8月发布）
**GitHub：** https://github.com/xlang-ai/OpenCUA

---

## 二、核实结果

| 说法 | 实际情况 |
|------|---------|
| "港大出品" | ✅ 真实，香港大学 XLANG Lab |
| _stars_ | **727 Stars**（相当活跃的学术开源项目）|
| 2026年最新 | ✅ 2026年2月仍有更新 |
| 视觉browser自动化 | ✅ 专为 Computer-Using Agent (CUA) 设计 |

---

## 三、OpenCUA 能做什么

**核心能力：让 AI 理解屏幕内容并操作电脑**

- 接收屏幕截图
- 理解页面结构（通过视觉，而非 DOM）
- 输出操作：点击/输入/滚动/搜索
- 支持从7B到72B多种模型规模

**Benchmark 成绩：**
- OSWorld-Verified: **#1**（OpenCUA-72B）
- UI-Vision: 37.3%（SOTA）
- ScreenSpot-Pro: 60.8%

**vLLM 支持（2026年1月）：** 可以在本地高效运行，降低GPU需求

---

## 四、金龙能否使用？

### ✅ 能用的部分

- OpenCUA 框架可以**克隆研究源码**
- 有**在线 Demo**可以直接体验：https://huggingface.co/spaces/xlangai/OpenCUA-demo
- 框架是开源的，可以学习其架构

### ⚠️ 关键限制

| 要求 | 情况 |
|------|------|
| 需要强大 GPU | 72B模型需要高端GPU，金龙Mac可能不够 |
| 需要 VLM 模型 | 需要 Qwen-VL / GPT-4V 等多模态模型 |
| 配置复杂 | 对开发者经验有要求 |
| 非开箱即用 | 不是下载就能用的工具，需要部署 |

### 🔍 更适合金龙的替代方案

| 方案 | 难度 | 效果 |
|------|------|------|
| **OpenClaw 本身（browser-use）** | ⭐ 低 | 直接可用，已有browser工具 |
| **Playwright + AI Prompt** | ⭐⭐ 中 | 成熟稳定 |
| OpenCUA（本地部署） | ⭐⭐⭐⭐ 高 | Mac难以跑起来 |

---

## 五、麦龙的判断

### 金龙为什么没跑通？

**原因分析：**
1. OpenCUA 不是"下载即用"的工具，需要：
   - 配置 Python 环境 + GPU
   - 下载/配置大模型（7B–72B）
   - 本地部署 vLLM
2. 如果金龙没有强大的 Mac GPU，根本跑不动 72B 模型
3. 金龙用的"港大视觉方式"可能是指 OpenCUA 的 Demo，但 Demo 需要 API key 或强大算力

### 麦龙的评估

**OpenCUA 对金龙的实际价值：**

| 维度 | 评价 |
|------|------|
| 能力匹配度 | ⭐⭐⭐⭐ 很高（正是browser自动化需要的） |
| 本地可用性 | ⭐⭐ （Mac算力有限，可能跑不动） |
| 部署难度 | ⭐⭐⭐ 高 |
| 适合金龙吗 | **不太适合，更适合有GPU的服务器环境** |

---

## 六、建议行动（金龙现在该做什么）

### 金龙现在应该做（优先级排序）

**🔴 最高优先：先把 OpenClaw 自己的 browser 自动化跑通**

Boss 提到金龙在用"港大智能视觉"操作，但 OpenClaw 本身有内置的 browser-use 能力，这才是最直接的方案。

```
OpenClaw Browser 工具
  ↓
自然语言指令
  ↓
自动操作浏览器
```

**如果 OpenClaw 的 browser 自动化不行，再考虑 OpenCUA**

### 关于 OpenCUA 的建议

| 行动 | 建议 |
|------|------|
| 安装 | 暂不在金龙本地安装（算力不够） |
| 体验 | 可以先试在线 Demo：https://huggingface.co/spaces/xlangai/OpenCUA-demo |
| 学习 | 可以读源码了解 CUA 架构，但不要花太多时间 |
| 最终方案 | 等 Cloud Code（参谋长）评估 OpenClaw 自动化能力后再定 |

---

## 七、汇报 Cloud Code 的核心问题

> **Cloud Code（参谋长）需要决策：**
>
> 1. 金龙当前的 browser 自动化问题，是 OpenClaw 内置能力没配好，还是需要引入 OpenCUA？
> 2. OpenClaw 的 browser-use 能否完成"输入框→搜索→找列表页URL"这个操作？
> 3. 如果 OpenClaw 够用，让金龙配置好 OpenClaw；如果不够用，再考虑 OpenCUA 方案。

---

## 八、麦龙能帮什么

- 帮金龙测试 OpenClaw browser-use 的实际能力边界
- 帮调研 OpenCUA 的本地最低配置要求
- 如果 OpenClaw 不够用，麦龙可以帮金龙写 OpenCUA 的部署方案

---

_麦龙调研 | 2026-04-06_
