# 招标平台URL清单

> 提取时间：2026-04-08
> 提取者：金龙

---

## 1. 成建e采（成都建工集团）

### 平台信息
- **平台名称**：成建e采
- **运营主体**：成都建工物资有限责任公司
- **客服热线**：028-86980300
- **地址**：成都市高新区天府四街300号财智中心1栋B座

### URL格式

| 页面类型 | URL |
|---------|-----|
| 平台入口 | https://www.cjebuy.com/ |
| 招标列表页 | https://www.cjebuy.com/portal/list.do?chnlcode=tender |
| 中选公示页 | https://www.cjebuy.com/portal/list.do?chnlcode=result |
| 详情页格式 | `https://www.cjebuy.com/portal/detail.do?docid={ID}&chnlcode=tender&objtype=` |

### 详情页URL示例
```
https://www.cjebuy.com/portal/detail.do?docid=ee5e0d93e7934369ba5f5bd649e9e01f&chnlcode=tender&objtype=
https://www.cjebuy.com/portal/detail.do?docid=e8581d5ada144a8bb15043f1f185da70&chnlcode=tender&objtype=
https://www.cjebuy.com/portal/detail.do?docid=ac01c353a24a4d338a3ab27bda7c21d7&chnlcode=tender&objtype=
```

### 采购类型分类
- 物资采购（工程类）
- 机具租赁
- 专业分包
- 劳务分包
- 办公耗材
- 咨询服务（工程类）
- 物资（非工程类）
- 咨询服务（非工程类）
- 零星采购
- 大型机械设备租赁

---

## 2. 善建云采（华西集团）

### 平台信息
- **平台名称**：善建云采
- **运营主体**：四川华西数产科技集团有限公司
- **客服热线**：400-000-2772
- **服务时间**：周一至周五 9:00-17:00

### URL格式

| 页面类型 | URL |
|---------|-----|
| 平台入口 | https://scm.zghxsjy.com/ |
| 招标列表页 | https://scm.zghxsjy.com/tender/notice/1 |
| 中标公示页 | https://scm.zghxsjy.com/tender/notice/2 |
| 详情页格式 | `https://scm.zghxsjy.com/bulletin/detail/{ID}/{type}/{category}` |

### URL参数说明
- `{ID}`: 招标公告ID（如 REQha50Ba8tCZ9NWFPAf）
- `{type}`: 公告类型（2=物资招标, 其他待确认）
- `{category}`: 分类（1=物资招标公告）

### 详情页URL示例
```
https://scm.zghxsjy.com/bulletin/detail/REQha50Ba8tCZ9NWFPAf/2/1
```

### 招标类型分类（Tab页）
- 物资招标公告
- 劳务招标公告
- 专业分包公告
- 机械设备公告
- 其它服务公告

---

## 3. 备注

### 爬虫注意事项
1. **成建e采**：详情页URL中的 `docid` 是32位十六进制字符串
2. **善建云采**：详情页URL中的 ID 格式不规则，需要从列表页动态提取
3. 两个平台都是SPA（单页应用），需要使用 Playwright/Puppeteer 等工具渲染后提取

### 数据提取建议
- 列表页提取字段：项目名称、发布时间、截止时间、采购单位、详情页URL
- 详情页提取字段：项目概况、采购内容、资格要求、投标时间节点、联系方式
