"""
SmartScout 阶段一：DeepSeek规则扩充
基于50个样本进行黑白名单规则扩充
"""

import os
import json
import logging
from typing import List, Dict, Any
import openai
from openai import OpenAI

# 导入配置加载器
from config_loader import get_deepseek_api_key, get_deepseek_base_url, get_deepseek_model, get_scout_config

logger = logging.getLogger(__name__)

class DeepSeekRuleExpander:
    """DeepSeek规则扩充器"""

    def __init__(self):
        """初始化规则扩充器"""
        # 加载DeepSeek配置
        self.api_key = get_deepseek_api_key()
        self.base_url = get_deepseek_base_url()
        self.model = get_deepseek_model()

        if not self.api_key:
            raise ValueError("DeepSeek API密钥未配置，请检查config/secrets.yaml")

        # 初始化OpenAI客户端（DeepSeek兼容OpenAI API）
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        logger.info(f"DeepSeek规则扩充器初始化完成，模型: {self.model}")

    def load_sample_data(self, sample_file: str = None) -> List[str]:
        """
        加载样本数据

        Args:
            sample_file: 样本文件路径，相对于当前文件，如果为None则使用配置中的默认路径

        Returns:
            标题列表
        """
        # 处理默认样本文件路径
        if sample_file is None:
            scout_config = get_scout_config()
            sample_file = scout_config.get("sample_file", "../simple_bids_50_20260211_032958.json")
            logger.info(f"使用配置中的样本文件: {sample_file}")

        # 构建绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, sample_file)

        logger.info(f"加载样本数据: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 提取标题（visible_text字段）
            titles = []
            for item in data:
                if isinstance(item, dict) and 'visible_text' in item:
                    # 清理标题文本（移除多余空白和换行）
                    title = item['visible_text'].strip()
                    title = ' '.join(title.split())  # 合并多个空白
                    if title:
                        titles.append(title)

            logger.info(f"成功加载 {len(titles)} 个标题")
            if titles:
                logger.debug(f"样本标题示例（前3个）: {titles[:3]}")

            return titles

        except Exception as e:
            logger.error(f"加载样本数据失败: {e}")
            raise

    def build_prompt(self, titles: List[str], initial_white_list: List[str], initial_black_list: List[str]) -> str:
        """
        构建DeepSeek提示词

        Args:
            titles: 标题列表
            initial_white_list: 初始白名单关键词列表
            initial_black_list: 初始黑名单关键词列表

        Returns:
            完整的提示词字符串
        """
        # 构建标题文本（每行一个标题）
        titles_text = "\n".join([f"- {title}" for title in titles[:50]])  # 限制50个

        # 动态生成领域描述基于初始列表
        white_domain_desc = "、".join(initial_white_list[:3]) + "等" if initial_white_list else "设备、工程、采购"
        black_domain_desc = "、".join(initial_black_list[:3]) + "等" if initial_black_list else "服务、物流、配送"

        prompt = f"""你是一个招标公告信息分析专家。请分析以下50条招标公告标题，找出：
1. 哪些关键词/模式表示"我们不关心"的内容（黑名单）
2. 哪些关键词/模式表示"我们关心"的内容（白名单）

核心关注领域：
- {white_domain_desc}类相关公告
- 我们关心的：偏设备、工程、采购类的公告

不关心的领域：
- {black_domain_desc}类相关公告
- 非核心领域的其他公告

初始参考词：
- 白名单参考：{', '.join(initial_white_list) if initial_white_list else '无'}
- 黑名单参考：{', '.join(initial_black_list) if initial_black_list else '无'}

请基于这50个样本的个体特性，进行相关性分析：
1. 首先分析样本中出现的实际关键词和模式
2. 扩充充实黑白名单，特别是黑名单的解决性
3. 优先考虑高频出现的实际词条
4. 每个列表最多返回20个最相关的关键词，避免冗余

样本标题：
{titles_text}

只返回纯JSON格式：{{"black_list_additions": [], "white_list_additions": []}}
不要任何解释文字。"""

        logger.debug(f"提示词长度: {len(prompt)} 字符")
        logger.debug(f"初始白名单: {initial_white_list}")
        logger.debug(f"初始黑名单: {initial_black_list}")
        return prompt

    def call_deepseek_api(self, prompt: str) -> str:
        """
        调用DeepSeek API

        Args:
            prompt: 提示词

        Returns:
            API响应文本
        """
        logger.info(f"调用DeepSeek API，模型: {self.model}")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个招标公告信息分析专家，只返回纯JSON格式，不要任何解释文字。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0,  # 零温度确保确定性输出
                max_tokens=4000,
                response_format={"type": "json_object"}  # 确保JSON输出
            )

            content = response.choices[0].message.content
            logger.info(f"DeepSeek API调用成功，响应长度: {len(content)} 字符")
            logger.debug(f"API响应内容: {content}")

            return content

        except Exception as e:
            logger.error(f"DeepSeek API调用失败: {e}")
            raise

    def parse_response(self, response_text: str) -> Dict[str, List[str]]:
        """
        解析DeepSeek响应

        Args:
            response_text: API响应文本

        Returns:
            解析后的规则扩充字典
        """
        logger.info("解析DeepSeek响应")

        try:
            # 清理响应文本（移除可能的markdown代码块）
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]

            # 解析JSON
            data = json.loads(cleaned_text)

            # 验证数据结构
            if not isinstance(data, dict):
                raise ValueError("响应不是JSON对象")

            if "black_list_additions" not in data or "white_list_additions" not in data:
                raise ValueError("响应缺少必要的字段")

            # 确保列表类型
            black_additions = data.get("black_list_additions", [])
            white_additions = data.get("white_list_additions", [])

            if not isinstance(black_additions, list):
                black_additions = []
            if not isinstance(white_additions, list):
                white_additions = []

            result = {
                "black_list_additions": black_additions,
                "white_list_additions": white_additions
            }

            logger.info(f"规则扩充结果: 黑名单+{len(black_additions)}个, 白名单+{len(white_additions)}个")
            if black_additions:
                logger.debug(f"黑名单扩充: {black_additions}")
            if white_additions:
                logger.debug(f"白名单扩充: {white_additions}")

            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            logger.error(f"原始响应: {response_text}")
            raise
        except Exception as e:
            logger.error(f"响应解析失败: {e}")
            raise

    def expand_rules(self, sample_file: str = None,
                    initial_white_list: List[str] = None, initial_black_list: List[str] = None,
                    titles: List[str] = None) -> Dict[str, List[str]]:
        """
        执行规则扩充

        Args:
            sample_file: 样本文件路径，如果为None则使用配置中的默认路径（当titles为None时使用）
            initial_white_list: 初始白名单关键词列表
            initial_black_list: 初始黑名单关键词列表
            titles: 直接提供的标题列表，如果提供则优先使用，忽略sample_file

        Returns:
            规则扩充结果
        """
        logger.info("开始规则扩充流程")

        # 处理默认参数
        if initial_white_list is None:
            initial_white_list = []
        if initial_black_list is None:
            initial_black_list = []

        try:
            # 1. 加载样本数据
            if titles is not None:
                logger.info(f"使用提供的标题列表，数量: {len(titles)}")
                if not titles:
                    raise ValueError("提供的标题列表为空")
            else:
                titles = self.load_sample_data(sample_file)
                if not titles:
                    raise ValueError("样本数据为空")

            # 2. 构建提示词（传入初始黑白名单）
            prompt = self.build_prompt(titles, initial_white_list, initial_black_list)

            # 3. 调用DeepSeek API
            response = self.call_deepseek_api(prompt)

            # 4. 解析响应
            result = self.parse_response(response)

            logger.info("规则扩充流程完成")
            return result

        except Exception as e:
            logger.error(f"规则扩充流程失败: {e}")
            raise

def main():
    """主函数：规则扩充演示"""
    import sys
    import logging

    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger.info("=" * 80)
    logger.info("SmartScout Phase 1.2: DeepSeek规则扩充")
    logger.info("=" * 80)

    try:
        # 创建规则扩充器
        expander = DeepSeekRuleExpander()

        # 执行规则扩充
        result = expander.expand_rules()

        # 输出结果（纯JSON格式，无多余内容）
        print("\n" + "=" * 80)
        print("规则扩充结果（纯JSON格式）:")
        print("=" * 80)
        print(json.dumps(result, ensure_ascii=False, indent=2))

        logger.info("规则扩充演示完成")

    except Exception as e:
        logger.error(f"规则扩充失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()