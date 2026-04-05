"""
SmartScout 配置加载器
加载 settings.yaml 和 secrets.yaml 配置文件
"""

import os
import yaml
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class ConfigLoader:
    """配置加载器"""

    def __init__(self, config_dir: str = "../config"):
        """
        初始化配置加载器

        Args:
            config_dir: 配置文件目录，相对于当前文件
        """
        # 获取当前文件所在目录的绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_dir = os.path.join(current_dir, config_dir)

        # 配置文件路径
        self.settings_path = os.path.join(self.config_dir, "settings.yaml")
        self.secrets_path = os.path.join(self.config_dir, "secrets.yaml")

        # 配置缓存
        self._settings = None
        self._secrets = None

        logger.debug(f"配置目录: {self.config_dir}")
        logger.debug(f"设置文件: {self.settings_path}")
        logger.debug(f"密钥文件: {self.secrets_path}")

    def load_settings(self) -> Dict[str, Any]:
        """加载公开配置 settings.yaml"""
        if self._settings is not None:
            return self._settings

        try:
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                self._settings = yaml.safe_load(f) or {}
            logger.info(f"成功加载设置文件: {self.settings_path}")
            return self._settings
        except Exception as e:
            logger.error(f"加载设置文件失败: {e}")
            raise

    def load_secrets(self) -> Dict[str, Any]:
        """加载敏感配置 secrets.yaml"""
        if self._secrets is not None:
            return self._secrets

        try:
            with open(self.secrets_path, 'r', encoding='utf-8') as f:
                self._secrets = yaml.safe_load(f) or {}
            logger.info(f"成功加载密钥文件: {self.secrets_path}")
            return self._secrets
        except Exception as e:
            logger.error(f"加载密钥文件失败: {e}")
            raise

    def get_deepseek_config(self) -> Dict[str, Any]:
        """获取DeepSeek API配置"""
        secrets = self.load_secrets()
        return secrets.get("deepseek", {})

    def get_project_config(self) -> Dict[str, Any]:
        """获取项目配置"""
        settings = self.load_settings()
        return settings.get("project", {})

    def get_scout_config(self) -> Dict[str, Any]:
        """获取侦察阶段配置"""
        settings = self.load_settings()
        return settings.get("scout", {})

    def get_producer_config(self) -> Dict[str, Any]:
        """获取生产者配置"""
        settings = self.load_settings()
        return settings.get("producer", {})

    def get_consumer_config(self) -> Dict[str, Any]:
        """获取消费者配置"""
        settings = self.load_settings()
        return settings.get("consumer", {})

    def get_database_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        settings = self.load_settings()
        return settings.get("database", {})

    def get_queue_config(self) -> Dict[str, Any]:
        """获取队列配置"""
        settings = self.load_settings()
        return settings.get("queue", {})

    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        settings = self.load_settings()
        return settings.get("logging", {})

# 全局配置实例
_config_loader = None

def get_config_loader() -> ConfigLoader:
    """获取全局配置加载器实例"""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader

def get_deepseek_api_key() -> str:
    """获取DeepSeek API密钥"""
    config = get_config_loader().get_deepseek_config()
    return config.get("api_key", "")

def get_deepseek_base_url() -> str:
    """获取DeepSeek API基础URL"""
    config = get_config_loader().get_deepseek_config()
    return config.get("base_url", "https://api.deepseek.com")

def get_deepseek_model() -> str:
    """获取DeepSeek模型名称"""
    config = get_config_loader().get_deepseek_config()
    return config.get("model", "deepseek-chat")

def get_default_page_limit() -> int:
    """获取默认抓取页数"""
    config = get_config_loader().get_project_config()
    return config.get("default_page_limit", 10)

def get_database_path() -> str:
    """获取数据库路径"""
    config = get_config_loader().get_database_config()
    return config.get("path", "data/database.sqlite")

def get_queue_file_path() -> str:
    """获取队列文件路径"""
    config = get_config_loader().get_queue_config()
    return config.get("file_path", "data/temp/tasks.jsonl")

def get_scout_config() -> dict:
    """获取侦察阶段配置"""
    return get_config_loader().get_scout_config()

if __name__ == "__main__":
    # 测试配置加载
    import logging
    logging.basicConfig(level=logging.INFO)

    loader = ConfigLoader()

    print("=== 配置加载测试 ===")
    print(f"DeepSeek API密钥: {get_deepseek_api_key()[:20]}...")
    print(f"DeepSeek基础URL: {get_deepseek_base_url()}")
    print(f"默认页数限制: {get_default_page_limit()}")
    print(f"数据库路径: {get_database_path()}")
    print(f"队列文件路径: {get_queue_file_path()}")
    print("=== 测试完成 ===")