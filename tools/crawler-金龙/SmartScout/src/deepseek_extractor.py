"""
SmartScout DeepSeek字段提取器
从招标公告详情页提取12个关键字段
"""

import json
import logging
from typing import Dict, Any, Optional
import openai
from openai import OpenAI

# 导入配置加载器
from config_loader import get_deepseek_api_key, get_deepseek_base_url, get_deepseek_model

logger = logging.getLogger(__name__)


class DeepSeekExtractor:
    """DeepSeek字段提取器"""

    def __init__(self):
        """初始化字段提取器"""
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

        logger.info(f"DeepSeek字段提取器初始化完成，模型: {self.model}")

    def build_extraction_prompt(self, markdown_content: str) -> str:
        """
        构建字段提取提示词

        Args:
            markdown_content: Markdown格式的详情页内容

        Returns:
            完整的提示词字符串
        """
        prompt = f"""你是一个专业的政府采购公告信息提取专家。请从以下招标公告详情中提取12个关键字段。

提取字段说明：
1. 项目名称 - 招标项目的完整名称
2. 公告类型 - 招标公告类型（如：公开招标、竞争性谈判、询价等）
3. 采购单位 - 发布招标公告的采购单位名称
4. 预算金额 - 项目的预算金额（包括货币单位）
5. 中标金额 - 中标金额（如已公布）
6. 供应商 - 参与投标的供应商（如有多个用逗号分隔）
7. 中标供应商 - 中标供应商名称（如已公布）
8. 发布时间 - 公告发布时间（格式：YYYY-MM-DD HH:MM:SS）
9. 报名截止时间 - 报名截止时间（格式：YYYY-MM-DD HH:MM:SS）
10. 投标截止时间 - 投标截止时间（格式：YYYY-MM-DD HH:MM:SS）
11. 项目概况 - 项目简要描述和主要内容
12. 联系人信息 - 联系人姓名、电话、地址等信息

提取要求：
- 只提取明确出现在文本中的信息，不要猜测或推断
- 如果某个字段未找到，返回空字符串
- 保持原始文本中的格式和单位
- 时间格式尽量标准化

公告详情（Markdown格式）：
{markdown_content[:8000]}  # 限制长度，避免token超限

请返回纯JSON格式，使用以下字段名：
{{
  "project_name": "项目名称",
  "announcement_type": "公告类型",
  "purchasing_unit": "采购单位",
  "budget_amount": "预算金额",
  "winning_amount": "中标金额",
  "supplier": "供应商",
  "winning_supplier": "中标供应商",
  "publish_time": "发布时间",
  "registration_deadline": "报名截止时间",
  "bid_deadline": "投标截止时间",
  "project_overview": "项目概况",
  "contact_info": "联系人信息"
}}

只返回纯JSON格式，不要任何解释文字。"""

        logger.debug(f"提取提示词长度: {len(prompt)} 字符")
        return prompt

    def extract_fields(self, markdown_content: str) -> Dict[str, str]:
        """
        从Markdown内容中提取字段

        Args:
            markdown_content: Markdown格式的详情页内容

        Returns:
            提取的字段字典
        """
        logger.info("开始提取公告字段")

        max_retries = 3
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    logger.info(f"第 {attempt + 1} 次重试...")
                    # 等待一段时间再重试
                    import time
                    time.sleep(1 * attempt)  # 指数退避

                # 构建提示词
                prompt = self.build_extraction_prompt(markdown_content)

                # 调用DeepSeek API
                logger.info(f"调用DeepSeek API进行字段提取，模型: {self.model} (尝试 {attempt + 1}/{max_retries})")
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "你是一个专业的政府采购公告信息提取专家，只返回纯JSON格式，不要任何解释文字。"
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.1,  # 低温度确保确定性输出
                    max_tokens=1000,
                    response_format={"type": "json_object"}  # 确保JSON输出
                )

                content = response.choices[0].message.content
                logger.info(f"DeepSeek API调用成功，响应长度: {len(content)} 字符")

                # 解析响应
                extracted_fields = self.parse_extraction_response(content)
                filled_count = len([v for v in extracted_fields.values() if v])
                logger.info(f"字段提取完成，提取到 {filled_count} 个非空字段")

                # 如果提取到至少一个字段，返回结果
                if filled_count > 0:
                    # 记录提取结果
                    for field, value in extracted_fields.items():
                        if value:
                            logger.debug(f"{field}: {value[:100]}...")
                        else:
                            logger.debug(f"{field}: [空]")
                    return extracted_fields
                else:
                    logger.warning(f"第 {attempt + 1} 次尝试提取到0个字段，将重试")

            except Exception as e:
                logger.error(f"字段提取失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    logger.error("已达到最大重试次数，返回空字段")
                # 继续重试循环

        # 所有重试都失败
        logger.error("字段提取所有重试均失败，返回空字段")
        return self.get_empty_fields()

    def parse_extraction_response(self, response_text: str) -> Dict[str, str]:
        """
        解析提取响应

        Args:
            response_text: API响应文本

        Returns:
            解析后的字段字典
        """
        try:
            # 清理响应文本
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]

            # 解析JSON
            data = json.loads(cleaned_text)

            # 使用辅助方法提取字段
            return self._extract_fields_from_dict(data)

        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            logger.error(f"原始响应长度: {len(response_text)} 字符")
            logger.error(f"响应前500字符: {response_text[:500]}")
            if len(response_text) > 500:
                logger.error(f"响应后500字符: {response_text[-500:]}")

            # 尝试修复常见的JSON格式问题
            try:
                # 如果响应以```json开头，尝试移除
                if response_text.startswith("```json"):
                    fixed_text = response_text[7:]
                    if fixed_text.endswith("```"):
                        fixed_text = fixed_text[:-3]
                    data = json.loads(fixed_text.strip())
                    logger.info("通过移除```json标记修复JSON解析")
                    return self._extract_fields_from_dict(data)
            except:
                pass

            return self.get_empty_fields()
        except Exception as e:
            logger.error(f"响应解析失败: {e}")
            return self.get_empty_fields()

    def _extract_fields_from_dict(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        从字典中提取字段

        Args:
            data: 包含字段的字典

        Returns:
            提取的字段字典
        """
        extracted_fields = {}
        expected_fields = [
            "project_name", "announcement_type", "purchasing_unit",
            "budget_amount", "winning_amount", "supplier",
            "winning_supplier", "publish_time", "registration_deadline",
            "bid_deadline", "project_overview", "contact_info"
        ]

        for field in expected_fields:
            value = data.get(field, "")
            if value is None:
                value = ""
            elif not isinstance(value, str):
                value = str(value)
            extracted_fields[field] = value.strip()

        return extracted_fields

    def get_empty_fields(self) -> Dict[str, str]:
        """返回空字段字典"""
        return {
            "project_name": "",
            "announcement_type": "",
            "purchasing_unit": "",
            "budget_amount": "",
            "winning_amount": "",
            "supplier": "",
            "winning_supplier": "",
            "publish_time": "",
            "registration_deadline": "",
            "bid_deadline": "",
            "project_overview": "",
            "contact_info": ""
        }

    def validate_extraction(self, extracted_fields: Dict[str, str]) -> Dict[str, Any]:
        """
        验证提取结果

        Args:
            extracted_fields: 提取的字段字典

        Returns:
            验证结果字典
        """
        validation = {
            "has_project_name": bool(extracted_fields.get("project_name")),
            "has_purchasing_unit": bool(extracted_fields.get("purchasing_unit")),
            "has_budget_amount": bool(extracted_fields.get("budget_amount")),
            "has_contact_info": bool(extracted_fields.get("contact_info")),
            "filled_fields_count": sum(1 for v in extracted_fields.values() if v),
            "total_fields": len(extracted_fields)
        }

        validation["fill_rate"] = validation["filled_fields_count"] / validation["total_fields"] if validation["total_fields"] > 0 else 0

        return validation


def main():
    """主函数：字段提取演示"""
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
    logger.info("SmartScout DeepSeek字段提取器")
    logger.info("=" * 80)

    try:
        # 创建提取器实例
        extractor = DeepSeekExtractor()

        # 示例Markdown内容
        sample_markdown = """
# 政府采购公告

## 项目名称：XX市消防设备采购项目

### 一、采购单位
XX市消防救援支队

### 二、预算金额
人民币1,200,000.00元

### 三、公告类型
公开招标

### 四、发布时间
2026-01-15 09:00:00

### 五、投标截止时间
2026-02-15 17:00:00

### 六、项目概况
采购一批消防设备，包括灭火器、消防栓、消防水带等，用于XX市消防救援支队的装备更新。

### 七、联系人信息
联系人：张三
联系电话：13800138000
地址：XX市XX区XX路XX号
"""

        # 提取字段
        fields = extractor.extract_fields(sample_markdown)

        # 输出结果
        print("\n" + "=" * 80)
        print("字段提取结果:")
        print("=" * 80)
        for field, value in fields.items():
            print(f"{field}: {value or '[空]'}")

        # 验证结果
        validation = extractor.validate_extraction(fields)
        print(f"\n验证结果:")
        print(f"填充字段数: {validation['filled_fields_count']}/{validation['total_fields']}")
        print(f"填充率: {validation['fill_rate']:.1%}")

        logger.info("字段提取演示完成")

    except Exception as e:
        logger.error(f"字段提取失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()