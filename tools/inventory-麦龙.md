# tools/inventory-麦龙.md

> 填写时间：2026-04-05 07:15 UTC
> 填写者：麦龙（MaxClaw 云端 Agent）

---

## 一、核心运行时

| 运行时 | 版本 | 备注 |
|--------|------|------|
| Python | 3.11.2 | 主力语言，pip 可用 |
| Node.js | 22.17.0 | npm 可用 |
| 系统 | Linux 5.10 (x86_64) | 云端沙箱环境 |

---

## 二、Python 标准库（直接可用）

| 类别 | 库 | 用途 |
|------|-----|------|
| 网络请求 | `urllib.request`, `http.client` | HTTP/HTTPS 调用 |
| 文件处理 | `pathlib`, `os`, `shutil` | 文件读写、目录操作 |
| JSON | `json` | API 数据处理 |
| 日期时间 | `datetime` | 时间戳、定时任务 |
| 编码 | `base64` | 文件编码、API 认证 |
| 正则 | `re` | 文本提取 |
| 临时文件 | `tempfile` | 缓存、临时存储 |

---

## 三、麦龙内置 MCP 工具（平台提供）

### 1. 信息获取类
| 工具 | 能力 |
|------|------|
| `batch_web_search` | 搜索引擎，实时网络搜索 |
| `extract_content_from_websites` | 抓取网页内容（支持 JS 渲染） |
| `images_search_and_download` | 搜索下载图片 |
| `images_understand` | OCR + 图片内容理解 |
| `audios_understand` | 音频转文字 + 内容理解 |
| `videos_understand` | 视频内容分析 |
| `listen_audio` | 单个音频深度分析 |

### 2. 内容生成类
| 工具 | 能力 |
|------|------|
| `image_synthesize` | 图像生成 / 编辑 / 放大 |
| `batch_text_to_image` | 批量文生图 |
| `gen_videos` / `batch_text_to_video` | 视频生成 |
| `batch_text_to_music` | 音乐生成 |
| `batch_synthesize_speech` | 语音合成（支持克隆声音） |
| `synthesize_speech` | 单次语音合成 |

### 3. 信息处理类
| 工具 | 能力 |
|------|------|
| `upload_to_cdn` | 文件上传至 CDN |
| `upload_clone_audio` | 音频文件用于声音克隆 |

### 4. 定时任务类
| 工具 | 能力 |
|------|------|
| `cron` jobs.json | 定时任务调度（精确到秒） |

### 5. 通信/消息类
| 工具 | 能力 |
|------|------|
| `message` | 微信/钉钉/飞书等渠道发消息 |
| `wecom_mcp` | 企业微信 MCP 接口调用 |

---

## 四、已安装 Skill（扩展能力包）

| Skill 名称 | 用途 |
|-----------|------|
| `wecom-get-todo-list` | 企业微信待办列表查询 |
| `wecom-get-todo-detail` | 企业微信待办详情 |
| `wecom-edit-todo` | 企业微信待办增删改 |
| `wecom-schedule` | 企业微信日程管理 |
| `wecom-meeting-query` | 企业微信会议查询 |
| `wecom-meeting-create` | 企业微信会议创建 |
| `wecom-meeting-manage` | 企业微信会议管理 |
| `wecom-contact-lookup` | 企业微信通讯录查询 |
| `wecom-smartsheet-data` | 智能表格数据管理 |
| `wecom-smartsheet-schema` | 智能表格结构管理 |
| `wecom-doc-manager` | 企业微信文档读写 |
| `feishu-doc` | 飞书文档读写 |
| `feishu-drive` | 飞书云盘管理 |
| `feishu-wiki` | 飞书知识库 |
| `feishu-perm` | 飞书权限管理 |
| `tencent-docs` | 腾讯文档管理 |
| `minimax-pdf` | PDF 生成 / 填表 / 格式化 |
| `minimax-docx` | Word 文档生成编辑 |
| `minimax-xlsx` | Excel 表格处理 |
| `pptx-generator` | PowerPoint 生成 |
| `weather` | 天气预报 |
| `weibo-hot-search` | 微博热搜 |
| `weibo-search` | 微博搜索 |
| `weibo-status` | 微博状态查询 |
| `find-skills` | 搜索安装新 Skill |
| `cron-mastery` | 定时任务管理 |
| `automation-workflows` | 自动化工作流设计 |
| `session-logs` | 会话日志分析 |
| `coding-agent` | 编码 Agent 委托 |
| `healthcheck` | 系统安全检查 |
| `maxclaw-helper` | MaxClaw 平台帮助 |

---

## 五、外部 API 能力

| 接口 | 状态 | 备注 |
|------|------|------|
| GitHub API | ✅ 可用 | GET/PUT 均可用，支持 Contents API |
| Google 搜索 | ✅ 可用 | `batch_web_search` |
| 企业微信 API | ✅ 可用 | MCP 接口完整 |
| 微信公众号 | ✅ 可用 | 素材搜索下载 |
| 微博 | ✅ 可用 | 热搜/搜索/用户状态 |
| 钉钉 | ⚠️ 部分可用 | Stream 模式有问题，Webhook 待测试 |

---

## 六、已知限制

| 限制项 | 说明 |
|--------|------|
| PDF 文字提取 | 需通过消息中转，非直接读取 |
| Git 协议 | 端口 22/9418 被封锁，仅 HTTPS 可用 |
| 直接 push | 需处理 divergence（建议 --rebase） |
| 浏览器自动化 | 云端无头浏览器，截图需用专用工具 |
| 大文件上传 | 单文件限 20MB |

---

## 七、当前任务执行记录

| 时间 | 任务 | 结果 |
|------|------|------|
| 2026-04-05 07:15 | T010 链路验证 | ✅ `tools/crawler-金龙/` 目录存在，文件完整 |
| 2026-04-05 07:15 | T006 本文档填写 | ✅ 完成 |

---

_本文件由麦龙自动生成，每执行新任务后更新_
