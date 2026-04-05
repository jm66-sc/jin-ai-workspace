# 动态样本抓取功能说明

## 概述
本系统现已支持动态样本抓取功能。当用户通过API提供目标URL时，系统会自动从该URL抓取50个样本标题，并使用这些动态样本进行DeepSeek规则扩充，而不是使用固定的样本文件。

## 主要修改

### 1. 新增模块：`src/sample_crawler.py`
- `SampleCrawler`类：从目标URL抓取50个样本标题
- `crawl_samples_from_url_sync()`函数：同步版本的便捷函数
- 支持去重、分页抓取、错误处理

### 2. 修改模块：`src/deepseek_rule_expander.py`
- `expand_rules()`方法新增`titles`参数
- 当提供`titles`参数时，跳过文件加载，直接使用提供的标题列表
- 保持向后兼容性：当`titles`为`None`时，使用样本文件

### 3. 修改API：`main.py`
- `rule_diagnosis`接口现在支持动态样本抓取
- 使用请求中的第一个URL抓取50个样本
- 添加异常处理：动态抓取失败时回退到备用样本文件

### 4. 修改流水线：`src/run_full_pipeline.py`
- `FullPipeline`类不再使用硬编码样本文件
- `run_phase1_rule_expansion()`方法动态抓取样本
- 使用`crawl_samples_from_url_sync()`函数

### 5. 配置更新：`config/settings.yaml`
- `scout.sample_file`现在标记为"备用"
- 实际运行中优先使用动态抓取

## 工作流程

### 旧流程（静态样本）：
1. 用户提供URL列表 → 2. 使用固定样本文件 → 3. DeepSeek规则扩充

### 新流程（动态样本）：
1. 用户提供URL列表 → 2. 从第一个URL动态抓取50个样本 → 3. 使用动态样本进行DeepSeek规则扩充 → 4. （备用）如果动态抓取失败，使用固定样本文件

## API使用示例

### 请求：
```json
POST /api/rule-diagnosis
{
  "urls": ["https://search.ccgp.gov.cn/bxsearch?searchtype=2&page_index=1&kw=消防"],
  "initial_blacklist": ["物流配送", "食堂配送"],
  "initial_whitelist": ["消防设备", "消防工程"]
}
```

### 响应：
```json
{
  "project_id": "project_abc123",
  "recommended_blacklist": ["物流配送", "食堂配送", "服务咨询", ...],
  "recommended_whitelist": ["消防设备", "消防工程", "设备采购", ...],
  "sample_count": 50,
  "status": "completed"
}
```

## 测试

### 单元测试：
- `test_dynamic_sample.py`：测试模块导入和基本功能
- `test_integration.py`：测试集成功能（已移除）

### 实际测试：
1. 运行完整流水线：`python src/run_full_pipeline.py --url "https://search.ccgp.gov.cn/bxsearch?searchtype=2&page_index=1&kw=消防"`
2. 调用API规则诊断接口

## 注意事项

1. **网络要求**：动态抓取需要访问目标网站，确保网络连接正常
2. **性能考虑**：抓取50个样本可能需要1-2分钟，具体取决于网站响应速度
3. **错误处理**：系统有完善的错误处理机制，动态抓取失败时会自动回退到备用样本文件
4. **备用文件**：`simple_bids_50_20260211_032958.json`仍作为备用文件保留

## 兼容性

系统保持完全向后兼容：
- 现有代码无需修改
- API接口保持不变（行为增强）
- 配置文件保持不变（语义更新）

## 后续优化建议

1. **缓存机制**：对相同URL的抓取结果进行缓存
2. **增量抓取**：只抓取新的样本，减少重复工作
3. **质量检查**：对抓取的样本进行质量评估
4. **并发优化**：提高抓取速度

---
*更新时间：2026-02-11*
*版本：1.0.0*