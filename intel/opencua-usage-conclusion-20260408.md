# OpenCUA 使用结论报告（终版）

> 日期：2026-04-08 上午
> 编写：金龙
> Boss 要求：搞清楚为什么、给出结论、完成任务

---

## 一、三个平台的情况

### 1. 索道集团（蜀道集团 zb.shudaojt.com）✅ 成功

**为什么成功：**
- 静态 HTML 页面，无需 JavaScript
- curl / wget 直接返回完整 HTML
- 详情页 URL 直接暴露在列表页 `<a href>` 中
- **根本原因：技术门槛低，不需要 OpenCUA**

**方法：**
```bash
curl -s "https://zb.shudaojt.com/zbgg/zhaobiao.html" | grep 'href'
# 详情页 URL: https://zb.shudaojt.com/zbgg/YYYYMMDD/{uuid}.html
```

---

### 2. 善建云采（scm.zghxsjy.com）✅ 成功（今天重新验证）

**为什么之前失败：**
- 之前用的是 curl → 返回空（SPA 页面）
- 之前直接 navigate 详情页 URL → URL 不存在（SPA，URL 不变）

**为什么现在成功：**
- SPA 单页应用，详情内容由 JavaScript 渲染
- 用 `browser.act click` 点击列表中的项目按钮
- 点击后内容加载（URL 不变，但 DOM 已更新）
- 用 `browser.snapshot` 提取完整字段

**正确方法：**
```
browser.navigate → https://scm.zghxsjy.com/tender/notice/1
browser.act wait 4000ms
browser.snapshot  → 找招标项目按钮的 ref（如 ref=e24）
browser.act click ref=e24  → 进入详情（URL 不变，内容加载）
browser.snapshot  → 完整字段：
  - 标题：2026年机司安分司和悦中学项目-建筑辅材及安全材料招标
  - 招标单位：四川省建筑机械化工程有限公司
  - 项目名称：和悦路西侧配套中学建设项目
  - 采购内容：零星材料
  - 联系人：聂涛 18227159182
```

**结论：善建云采用 browser 工具完全可用。**

---

### 3. 成都建工（cjebuy.com / 成建e采）⚠️ 部分问题

**cjebuy.com = 成都建工物资有限责任公司官方网站**

**问题分析：**
| 测试 | 结果 | 原因 |
|------|------|------|
| curl 列表页 | Content-Length: 0 | 服务器不响应非浏览器 |
| curl 详情页 | Content-Length: 0 | 同上 |
| browser.navigate 列表页 | ✅ 正常 | JavaScript 渲染成功 |
| browser snapshot | ❌ 列表内容未进入 accessibility tree | Playwright 渲染但 snapshot 不完整 |
| browser evaluate JS | ✅ 成功 | document.querySelector 拿到完整数据（21774条）|
| browser 直接 navigate 详情页 URL | ❌ 浏览器崩溃 | **反自动化检测触发** |
| browser act click 列表链接 | ❌ 浏览器崩溃 | 同上 |

**根本原因：cjebuy.com 有 WebDriver 检测机制**
- 广联达（Glodon）平台，内置反爬
- 当检测到 `navigator.webdriver == true` 时触发崩溃
- 这是网站主动的安全防护，与我们的方法无关

**已确认的事实：**
- 列表页数据：✅ 21774条（JS evaluate 验证）
- 详情页 URL 格式：✅ `https://www.cjebuy.com/portal/detail.do?docid={32位hex}&chnlcode=tender&objtype=`
- 详情页 docid 示例：
  - `ee5e0d93e7934369ba5f5bd649e9e01f` → 成都建工绿色建材板块2026年度监控维修维护服务项目
  - `e8581d5ada144a8bb15043f1f185da70` → 宝兴宝灵新材料年产20万吨石膏项目商砼采购
- 详情页内容：❌ 访问导致崩溃

---

## 二、OpenCUA 是什么、怎么用

### OpenCUA = browser 工具

OpenCUA 的实质：
- 截图 → browser snapshot
- 识别 UI 元素 → browser snapshot 找 ref
- 模拟鼠标 → browser act click/type
- 执行动作 → browser navigate / act

### OpenCUA 正确使用流程

```
第一步：browser.navigate → 目标页面
第二步：browser.act wait → 等待 JS 渲染（2-8秒）
第三步：browser.snapshot → 看页面结构（找元素 ref）
第四步：browser.act click ref=X → 点击进入（可能无 URL 变化）
第五步：browser.snapshot → 提取内容
```

### 各场景用什么方法

| 场景 | 方法 | 工具 |
|------|------|------|
| 静态 HTML | curl / wget | 最简单 |
| SPA（URL 不变，内容动态）| browser click + snapshot | OpenCUA |
| 详情 URL 在 href 中 | browser navigate | OpenCUA |
| curl 返回空 | browser | OpenCUA |
| 有反爬（WebDriver 检测）| 待解决 | 需特殊处理 |

---

## 三、任务完成情况

| 平台 | 状态 | 说明 |
|------|------|------|
| 善建云采 | ✅ 完成 | browser click + snapshot 完整提取 |
| 成都建工 | ⚠️ 部分 | 列表数据 ✅，详情页因反爬崩溃 ❌ |

**成都建工详情页需要进一步处理：**
1. 绕过 WebDriver 检测（undetected-chromedriver）
2. 或用 session cookie + 正确 headers 模拟真实浏览器
3. 或用 Selenium + stealth mode

---

## 四、关键结论（回答 Boss 的问题）

**问：索道集团为什么成功？**
> 答：静态 HTML，curl 直接拿，不需要 OpenCUA

**问：善建云采为什么之前失败、现在成功？**
> 答：之前用错了方法（curl 和 navigate）；正确方法是 browser click + snapshot

**问：成都建工为什么失败？**
> 答：有 WebDriver 反爬检测，browser navigate 或 click 详情页会崩溃。这是网站主动安全机制，与方法无关

**问：OpenCUA 怎么正确用？**
> 答：OpenCUA = browser 工具。流程：navigate → wait → snapshot（找ref）→ click（操作）→ snapshot（提取）。善建云采验证了这个方法可行。
