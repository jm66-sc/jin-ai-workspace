# 给金龙的任务：下载西门子产品样本PDF

> 来源：Claude（总参谋）
> 日期：2026-04-13
> 优先级：高
> 完成后：把文件放到指定目录，回报文件名和大小清单

---

## 任务说明

从西门子官网下载以下产品的中文产品样本（Product Catalog/选型手册），PDF格式。

**下载地址**：https://support.industry.siemens.com/cs/cn/zh/ps/
（搜索产品名 + "产品样本" 或 "选型指南"）

---

## 要下载的产品清单

### PLC系列
| 产品 | 搜索关键词 |
|------|-----------|
| S7-1200 | "S7-1200 产品样本" 或 "SIMATIC S7-1200 catalog" |
| S7-1500 | "S7-1500 产品样本" |
| S7-200 SMART | "S7-200 SMART 产品样本" |

### 变频器系列
| 产品 | 搜索关键词 |
|------|-----------|
| SINAMICS G120 | "G120 产品样本" 或 "G120 catalog" |
| SINAMICS G120X | "G120X 产品样本" |
| SINAMICS V20 | "V20 产品样本" |

### I/O模块
| 产品 | 搜索关键词 |
|------|-----------|
| ET 200SP | "ET 200SP 产品样本" |
| ET 200MP | "ET 200MP 产品样本" |

### 触摸屏
| 产品 | 搜索关键词 |
|------|-----------|
| SIMATIC HMI KTP/TP系列 | "SIMATIC HMI Basic Panels 产品样本" |

### 电源
| 产品 | 搜索关键词 |
|------|-----------|
| SITOP PSU系列 | "SITOP 产品样本" 或 "SITOP catalog" |

---

## 下载步骤

1. 打开 https://support.industry.siemens.com/cs/cn/zh/
2. 搜索框输入产品关键词
3. 筛选：文件类型选"样本/Catalog"，语言选"中文"
4. 下载最新版本的PDF

备用渠道：https://www.siemens.com/cn/zh/products/automation.html → 找到产品页 → 下载文档

---

## 存放位置

下载完成后，全部放到：
```
/Users/jin/Desktop/自动化收集器/plc-wiki/raw/manuals/
```

文件命名规则：
```
<品牌>-<产品线>-<类型>-<年份>.pdf
例：siemens-s7-1200-catalog-2024.pdf
   siemens-g120-catalog-2024.pdf
```

---

## 完成后汇报

回报格式：
```
已下载：
- siemens-s7-1200-catalog-2024.pdf（5.2MB）
- siemens-g120-catalog-2023.pdf（8.1MB）
...
下载失败：
- xxx（原因：需要登录/找不到中文版）
```

---

## 注意事项

- 只下载**中文版**，没有中文就下英文版
- 只下载**产品样本/Catalog**，不需要完整技术手册（那个几百MB）
- 遇到需要登录的页面，标注一下，不强求
- 单个文件超过50MB的跳过，太大了不适合入库

---

*任务分配：Claude → 金龙执行 → 金奥瘦身入库*
