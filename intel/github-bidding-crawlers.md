# GitHub 招标爬虫开源项目调研报告

> 调研时间：2026-04-06
> 调研者：麦龙
> 对应：T012 · 写入 intel/github-bidding-crawlers.md

---

## 调研结论（一句话）

> GitHub 上没有 Stars 多、近期活跃的专门招标爬虫项目。
> 现有项目大多已停止维护（2018–2023年）。
> **建议：不依赖开源项目，以金龙本地浏览器自动化为主 + 麦龙云端直接爬取为辅。**

---

## 一、搜索的关键词

- `ccgp.gov.cn crawler github`
- `政府采购 爬虫 github`
- `招标 spider python github`
- `bidding crawler china github`
- `government procurement crawler github`

---

## 二、找到的开源项目汇总

| 项目 | Stars | Forks | 语言 | 最后更新 | 覆盖网站 |
|------|-------|-------|------|---------|---------|
| [OliverFoh/zhaobiao_spider](#3-oliverfohzhaobiao_spider) | ⭐24 | 11 | Python | 2020-02 | 中国政府采购网（ccgp） |
| [summerness/bid_spider](#4-summernessbid_spider) | ⭐14 | 2 | 不明 | 2022-10 | 中国政府采购网 + 辽宁政府采购网 |
| [DanielisLearning/zbspider](#5-danielislearningzbspider) | ⭐12 | 11 | Python | 2019-07 | 全国招标网（多站） |
| [xinxinxiangyin09/ZhaoBiaoSpider](#6-xinxinxiangyin09zhaobiaospider) | ⭐9 | 7 | Python | 2023-05 | 招标网多站集合 |
| [Thezkiller/ccgp_gov](#7-thezkillerccgp_gov) | ⭐8 | 5 | 不明 | 2019-07 | 中国政府采购网 |
| [handsomestWei/gxcg-spider](#8-handsomestweigxcg-spider) | ⭐7 | 2 | Python | 2023-06 | 国信招标网（gxcg） |
| [Jackjet/Crawler-ShanXiZhenFuCaiGouWang](#9-jackjetcrawler-shanxizhenfucaigouwang) | ⭐4 | 2 | Python | 2018-08 | 山西政府采购网 |
| [810230010/elevator-spider](#10-810230010elevator-spider) | ⭐3 | 3 | 不明 | — | 电梯/机电招标 |

---

## 三、详细分析

### 1. OliverFoh/zhaobiao_spider ⭐24（最高Stars）

```
GitHub: https://github.com/OliverFoh/zhaobiao_spider
Stars: 24 | Forks: 11 | 更新: 2020-02
描述: 招投标网站数据采集（多线程爬虫）
```

**优点：**
- Stars 数量最高，有一定社区认可度
- 多线程爬虫，技术相对成熟

**缺点：**
- 2020年后已停止更新（6年未维护）⚠️
- 项目描述简单，无详细文档
- 无法判断是否支持 JS 动态渲染
- 中国政府采购网结构可能已变化，代码可能失效

**结论：⚠️ 可参考架构，不建议直接安装使用**

---

### 2. summerness/bid_spider ⭐14

```
GitHub: https://github.com/summerness/bid_spider
Stars: 14 | Forks: 2 | 更新: 2022-10
描述: 招标信息爬虫，支持中国政府采购网 + 辽宁政府采购网
```

**优点：**
- 支持中国政府采购网（ccgp）
- 2022年更新，相对较新
- 已支持多网站整合

**缺点：**
- Stars 较少，社区活跃度低
- 无详细文档
- 无法确认是否支持动态渲染

**结论：⚠️ 可参考，金龙本地测试后决定是否使用**

---

### 3. DanielisLearning/zbspider ⭐12

```
GitHub: https://github.com/DanielisLearning/zbspider
Stars: 12 | Forks: 11 | 更新: 2019-07
描述: 招标爬虫，收集中国范围内招标采购信息，支持邮件通知
```

**优点：**
- 有邮件通知功能（完整的工作流）
- 全国多站覆盖
- Forks 数量高（11），社区参与度高

**缺点：**
- 2019年停止更新，7年未维护 ⚠️
- 邮件通知功能可能需要配置 SMTP
- 网站结构可能已大幅变化

**结论：⚠️ 架构可参考，不建议直接安装**

---

### 4. xinxinxiangyin09/ZhaoBiaoSpider ⭐9

```
GitHub: https://github.com/xinxinxiangyin09/ZhaoBiaoSpider
Stars: 9 | Forks: 7 | 更新: 2023-05（最新之一）
描述: 招标网的所有集合，可在线可下载到本地
```

**优点：**
- 2023年更新（最新之一）✅
- 多站集合，覆盖面广
- 有本地下载功能

**缺点：**
- Stars 较少
- 无详细文档说明
- 无法确认是否支持 JS 渲染

**结论：✅ 值得金龙本地测试，可能是最实用的参考项目**

---

### 5. Thezkiller/ccgp_gov ⭐8

```
GitHub: https://github.com/Thezkiller/ccgp_gov
Stars: 8 | Forks: 5 | 更新: 2019-07
描述: 中国政府采购网爬虫，使用 Selenium
```

**优点：**
- 专门针对中国政府采购网
- 使用 Selenium（支持 JS 渲染）✅

**缺点：**
- 2019年停止更新
- Selenium 方案较老，效率低
- ccgp.gov.cn 有严格反爬限制，Selenium 方式容易被封

**结论：⚠️ Selenium 思路可取，但 ccgp.gov.cn 已被封，参考价值有限**

---

### 6. handsomestWei/gxcg-spider ⭐7

```
GitHub: https://github.com/handsomestWei/gxcg-spider
Stars: 7 | Forks: 2 | 更新: 2023-06
描述: 国信招标网（gxcg）招投标公告爬虫，支持关键字+时间范围
```

**优点：**
- 2023年更新 ✅
- 支持关键字和时间范围查询
- 有客户端模式（Excel导出）和服务端模式

**缺点：**
- 只覆盖国信招标网一个网站
- Stars 少

**结论：📌 参考价值：★★★，国信招标网可能是我们的目标网站之一**

---

### 7. Jackjet/Crawler-ShanXiZhenFuCaiGouWang ⭐4

```
GitHub: https://github.com/Jackjet/Crawler-ShanXiZhenFuCaiGouWang
Stars: 4 | Forks: 2 | 更新: 2018-08
描述: 爬取山西政府采购网通知信息，支持邮件通知
```

**结论：❌ 停止维护（8年），Stars 少，无参考价值**

---

## 四、核心问题分析

### 为什么 GitHub 上没有好的招标爬虫？

| 问题 | 原因 |
|------|------|
| **项目普遍停止维护** | 政府网站结构经常变化，爬虫需要频繁更新，维护成本高 |
| **反爬限制** | ccgp.gov.cn 有严格 IP 限流和验证码，需要浏览器自动化 |
| **聚合平台商业化** | 招标宝、采招网等商业平台已满足市场需求，开源动力不足 |
| **JS 渲染普及** | 近年政府网站全面 SPA 化，requests/BeautifulSoup 方案失效 |

---

## 五、麦龙的推荐结论

### 推荐项目（金龙本地安装测试）

| 优先级 | 项目 | 理由 |
|--------|------|------|
| 🔴 **第一推荐** | **xinxinxiangyin09/ZhaoBiaoSpider** | 2023年更新，多站覆盖，Stars较高，架构可参考 |
| 🟡 **第二推荐** | **summerness/bid_spider** | 2022年更新，专为政府采购设计，支持ccgp.gov.cn |
| 📌 **参考** | **handsomestWei/gxcg-spider** | 国信招标网是有效来源之一，可单独参考 |

### 最终建议：不依赖开源，自建为主

> **现有开源项目的实际可用性很低（Stars少、年久失修）。**
> **建议：以金龙本地浏览器自动化（SmartScout已有思路）+ 麦龙云端直接爬取为主，开源项目仅作参考。**

---

## 六、金龙本地安装建议

如果金龙决定测试，推荐按以下顺序：

```bash
# 1. 先克隆到本地
git clone https://github.com/xinxinxiangyin09/ZhaoBiaoSpider.git
cd ZhaoBiaoSpider

# 2. 查看 requirements.txt 安装依赖
cat requirements.txt

# 3. 安装并测试（先用一个小站测试）
pip install -r requirements.txt
python main.py  # 看报错

# 4. 如有报错，定位问题：
#    - 是否需要登录？
#    - 是否是 JS 渲染页面？
#    - 是否有验证码？
```

---

_麦龙调研 | 2026-04-06_
