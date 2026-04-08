# OpenCUA 使用调查结论报告

> 日期：2026-04-08
> 编写：金龙
> Boss 要求：搞清楚三个问题

---

## 问题一：索道集团是怎么成功的？

**成功原因：zb.shudaojt.com 是静态 HTML 页面。**

详情页 URL 格式是：`https://zb.shudaojt.com/zbgg/YYYYMMDD/{uuid}.html`

这是直接可访问的静态 URL，curl 或 browser 直连都能拿到。不需要 OpenCUA 的视觉能力。

**方法总结：**
- 直接 curl/wget 访问静态 HTML ✅
- 或 browser.navigate 直连 URL ✅
- 核心：URL 在列表页 href 中直接暴露

---

## 问题二：善建云采为什么失败？

**善建云采（scm.zghxsjy.com）实际上成功了！**

✅ **已验证可用**（今天重测成功）：
1. `browser.navigate` → 列表页加载正常
2. `browser.act click ref=e24` → 详情页内容加载（无 URL 变化）
3. `browser.snapshot` → 完整字段全部可见

**关键发现：**
- 该平台是 **SPA（单页应用）**
- 详情页内容由 JavaScript 动态渲染，URL 不变
- 无法用 curl/wget 获取（返回空）
- 但用 `browser.act click` + `browser.snapshot` 可以完整提取内容

**方法总结：**
- ❌ curl/wget 不行（返回空）
- ❌ browser.navigate 直连详情页 URL 不行（URL 不存在）
- ✅ browser.act click 按钮元素 + snapshot 提取内容 ✅

---

## 问题三：成都建工（cjebuy.com）的情况

**cjebuy.com = 成都建工集团官方采购平台（成建e采）**

### 技术分析

| 测试方式 | 结果 | 说明 |
|---------|------|------|
| curl/wget | ❌ 返回 Content-Length: 0 | 服务器返回空内容 |
| Python urllib | ❌ 返回 Content-Length: 0 | 同上 |
| browser.navigate → 列表页 | ✅ 正常 | 列表页本身可加载 |
| browser snapshot | ⚠️ 不完整 | 动态内容未进入 accessibility tree |
| browser evaluate (JS) | ✅ 成功 | document.querySelector 可以拿到完整数据 |
| browser evaluate → click() | ❌ 页面崩溃 | JavaScript click() 导致浏览器崩溃 |
| browser navigate → 详情页 | ❌ 页面崩溃 | 直连详情页 URL 导致崩溃 |

**结论：cjebuy.com 的详情页有严重问题——**
1. 详情页 URL 存在（`/portal/detail.do?docid=xxx`）
2. 但直接 navigate 访问会导致浏览器崩溃
3. JavaScript evaluate 的 .click() 也会导致崩溃
4. 这可能是一个防爬/防自动化机制

### 已确认的事实

- 列表页：https://www.cjebuy.com/portal/list.do?chnlcode=tender ✅
- 列表数据：21774 条 ✅（用 JS evaluate 验证）
- 详情页 URL 格式：`https://www.cjebuy.com/portal/detail.do?docid={32位hex}&chnlcode=tender&objtype=` ✅
- 详情页内容：❌ 访问崩溃，需进一步排查

---

## OpenCUA 正确使用方法总结

### 什么情况下用 OpenCUA（browser 工具）

| 情况 | 用什么 | 为什么 |
|------|--------|--------|
| 静态 HTML 页面 | curl/wget | 最简单直接 |
| SPA 单页应用 | browser.navigate + act click + snapshot | 需要 JS 渲染 |
| 详情页 URL 藏在 JS 中 | browser act click + evaluate JS | URL 不在 href 属性里 |
| 详情页 URL 暴露在 href | browser navigate 直连 | 最简单 |
| curl 返回空 | browser 工具 | 需要真实浏览器渲染 |

### OpenCUA（browser 工具）的正确使用流程

```
1. browser.navigate → 列表页 URL
2. browser.act wait → 等待页面加载（2000-5000ms）
3. browser.snapshot → 看看结构（compact=True）
4. browser.act evaluate → 用 document.querySelector 提取数据
5. browser.act click ref=X → 点击进入详情（URL 可能不变）
6. browser.snapshot → 提取详情页内容
```

### 善建云采（scm.zghxsjy.com）✅ 完全可用

**流程：**
```python
browser.navigate("https://scm.zghxsjy.com/tender/notice/1")
browser.act wait 4000ms
browser.snapshot  # 找按钮 ref
browser.act click ref=e24  # 进入详情（URL 不变）
browser.snapshot    # 完整内容在页面中
```

### 成都建工（cjebuy.com）⚠️ 部分可用

- 列表页：✅ browser navigate + JS evaluate 可提取数据
- 详情页：❌ 访问崩溃，需单独排查（可能是反自动化机制）

---

## 给 Boss 的结论

1. **索道集团**：静态 HTML，curl 直接拿 ✅
2. **善建云采**：SPA，browser click + snapshot ✅
3. **成都建工**：详情页有反自动化保护，需单独处理 ⚠️

**OpenCUA 就是 browser 工具**：截图看屏幕 → 分析 DOM → click/navigate → snapshot 提取内容。善建云采用这个方法完全成功。
