# config/gov_basic_config.py
GOV_BASIC_CONFIG = {
    # 基础URL和参数
    "base_url": "https://search.ccgp.gov.cn/bxsearch",
    "search_params": {
        "searchtype": "2",      # 固定参数
        "page_index": "1",      # 页码（动态）
        "kw": "消防"            # 关键词（动态）
    },

    # Crawl4AI配置
    "crawler_config": {
        "browser_mode": "undetected",
        "enable_stealth": True,
        "headless": True,       # 生产环境用headless
        "timeout": 30000,       # 30秒超时
        "verbose": False        # 关闭详细日志（除非调试）
    },

    # 解析配置
    "parser_config": {
        "metadata_pattern": r'(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}) \| 采购人：([^|]+) \| 代理机构：([^|]+)\s*([^|]*)\s*\| ([^|]+)',
        "time_format": "%Y.%m.%d %H:%M:%S",
        "output_time_format": "%Y-%m-%d %H:%M:%S"
    },

    # 运行参数
    "runtime_config": {
        "max_pages": 3,         # 最大爬取页数（每页20条）
        "delay_between_pages": 2,  # 页间延迟（秒）
        "retry_times": 3        # 失败重试次数
    }
}