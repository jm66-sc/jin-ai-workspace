# 代理参谋长（Claude 子 Agent）配置

> 撰写：Claude | 2026-04-06

---

## 一、子 Agent 定义

**代理参谋长**是 Claude 的子 agent，通过 `claude --print` 或类似方式调起的独立实例。

**定位：** 完全代理 Claude 的身份与角色，职责是读取 GitHub 状态、协调任务、推进执行。

**触发方式：** macOS launchd 每 3 小时自动调起

---

## 二、模型配置

| 配置项 | 值 |
|--------|-----|
| 模型 | `qclaw/modelroute` |
| 类型 | 通过 qclaw 路由层 |
| 超时 | 72000 秒（20 小时）|
| 并发 | 最大 3 |

---

## 三、配置来源

模型配置读取自 `~/.qclaw/openclaw.json`：

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "qclaw/modelroute"
      },
      "timeoutSeconds": 72000,
      "maxConcurrent": 3
    }
  }
}
```

---

## 四、注意事项

- `qclaw/modelroute` 是路由模型，实际会根据任务类型自动选择合适的模型
- 子 agent 与主 Agent 共享相同的模型配置
- 模型配置由 QClaw 桌面版管理

---

_Claude | 2026-04-06_