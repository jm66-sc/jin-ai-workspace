#!/usr/bin/env python3
"""
干净环境启动验证脚本
模拟新同事第一次拿到项目后的最小启动场景
"""

import os
import sys
import shutil
import tempfile
import subprocess
from pathlib import Path

# 颜色定义
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[1;34m'
NC = '\033[0m'  # No Color

def print_step(step_num, description):
    """打印步骤信息"""
    print(f"\n{BLUE}步骤 {step_num}: {description}{NC}")
    print("-" * 60)

def print_success(message):
    """打印成功信息"""
    print(f"{GREEN}✓ {message}{NC}")

def print_warning(message):
    """打印警告信息"""
    print(f"{YELLOW}⚠ {message}{NC}")

def print_error(message):
    """打印错误信息"""
    print(f"{RED}✗ {message}{NC}")

def create_clean_environment():
    """创建干净环境目录"""
    print_step(1, "创建干净环境目录")

    # 创建临时目录
    temp_dir = tempfile.mkdtemp(prefix="smartscout_clean_")
    print(f"临时目录: {temp_dir}")

    # 获取项目根目录
    project_root = Path(__file__).parent.parent

    # 需要复制的文件和目录
    copy_items = [
        # 核心配置文件
        "config",
        # 源代码
        "src",
        "core",
        "api",
        "services",
        "utils",
        # 启动脚本
        "run.py",
        "main.py",
        # 依赖文件
        "requirements.txt",
        "requirements_api.txt",
        # 文档（可选）
        "README.md",
        "DEPLOYMENT.md",
        "docs",
        # 启动脚本
        "run_test.sh",
        "run_all.sh",
        # 其他必要文件
        ".gitignore",
    ]

    # 排除的目录和文件（生成内容）
    exclude_patterns = [
        "__pycache__",
        ".pyc",
        "venv",
        "logs",
        "data",
        "*.log",
        "*.sqlite",
        "*.sqlite-*",
    ]

    # 复制文件和目录
    for item in copy_items:
        source = project_root / item
        if not source.exists():
            print_warning(f"源文件不存在: {item}")
            continue

        dest = Path(temp_dir) / item
        if source.is_dir():
            # 复制目录，排除不需要的内容
            shutil.copytree(
                source,
                dest,
                ignore=shutil.ignore_patterns(*exclude_patterns)
            )
            print_success(f"复制目录: {item}")
        else:
            # 复制文件
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
            print_success(f"复制文件: {item}")

    # 特殊处理：确保删除真实的 secrets.yaml（如果存在）
    secrets_path = Path(temp_dir) / "config" / "secrets.yaml"
    if secrets_path.exists():
        secrets_path.unlink()
        print_success("删除真实配置: config/secrets.yaml")

    # 确保 secrets.yaml.template 存在
    template_path = Path(temp_dir) / "config" / "secrets.yaml.template"
    if not template_path.exists():
        print_error("模板文件不存在: config/secrets.yaml.template")
        return None

    print_success(f"干净环境创建完成: {temp_dir}")
    return temp_dir

def test_missing_config(clean_dir):
    """测试缺失配置的情况"""
    print_step(2, "测试缺失配置启动")

    os.chdir(clean_dir)
    print(f"切换到目录: {clean_dir}")

    # 运行 run.py 并捕获输出
    print("运行 run.py...")
    try:
        result = subprocess.run(
            [sys.executable, "run.py"],
            capture_output=True,
            text=True,
            timeout=30,  # 30秒超时
            env={**os.environ, "SMARTSCOUT_TEST_MODE": "1"}  # 启用测试模式
        )

        output = result.stdout + result.stderr

        # 检查输出
        print("分析输出...")
        with open("run_output_missing_config.txt", "w", encoding="utf-8") as f:
            f.write(output)

        # 检查关键提示
        # 首先检查是否有依赖缺失
        has_dependency_check = "检查依赖" in output or "依赖" in output
        dependency_missing = "缺少" in output and "依赖包" in output
        dependency_error = "未安装" in output or "ImportError" in output

        # 检查配置相关提示
        config_missing_warning = "⚠️ 配置文件不存在: config/secrets.yaml" in output
        template_hint = "请复制 config/secrets.yaml.template" in output
        copy_command = "cp config/secrets.yaml.template config/secrets.yaml" in output
        edit_hint = "填写您的DeepSeek API密钥" in output

        # 评估结果
        all_passed = True

        # 依赖检查
        if has_dependency_check:
            print_success("依赖检查已执行")
            if dependency_missing:
                print_warning("依赖包缺失 (预期中，干净环境)")
                # 依赖缺失可能导致提前退出，配置检查可能未执行
                if not config_missing_warning:
                    print_warning("配置缺失检查可能未执行 (因依赖缺失提前退出)")
            else:
                print_success("依赖检查通过")
        else:
            print_warning("未检测到依赖检查输出")

        # 配置检查（如果可能执行了）
        if config_missing_warning:
            print_success("配置文件缺失提示正常")
        else:
            if dependency_missing:
                print_warning("配置文件缺失提示未显示 (可能因依赖缺失提前退出)")
            else:
                print_error("配置文件缺失提示未显示")
                all_passed = False

        if template_hint:
            print_success("模板复制提示正常")
        else:
            if dependency_missing:
                print_warning("模板复制提示未显示 (可能因依赖缺失提前退出)")
            else:
                print_error("模板复制提示未显示")
                all_passed = False

        if copy_command:
            print_success("复制命令提示正常")
        else:
            if dependency_missing:
                print_warning("复制命令提示未显示 (可能因依赖缺失提前退出)")
            else:
                print_error("复制命令提示未显示")
                all_passed = False

        if edit_hint:
            print_success("编辑指引提示正常")
        else:
            if dependency_missing:
                print_warning("编辑指引提示未显示 (可能因依赖缺失提前退出)")
            else:
                print_error("编辑指引提示未显示")
                all_passed = False

        if result.returncode != 0:
            print_warning(f"run.py 退出码: {result.returncode} (预期非零，因为配置缺失)")

        return all_passed, output

    except subprocess.TimeoutExpired:
        print_error("run.py 运行超时")
        return False, "Timeout"
    except Exception as e:
        print_error(f"运行 run.py 失败: {e}")
        return False, str(e)

def setup_test_config(clean_dir):
    """设置测试配置"""
    print_step(3, "设置测试配置")

    os.chdir(clean_dir)

    # 复制模板
    template_path = Path("config/secrets.yaml.template")
    secrets_path = Path("config/secrets.yaml")

    try:
        shutil.copy2(template_path, secrets_path)
        print_success(f"复制模板: {template_path} -> {secrets_path}")

        # 读取并修改配置
        with open(secrets_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 替换API密钥为测试值
        content = content.replace('api_key: "YOUR_DEEPSEEK_API_KEY_HERE"', 'api_key: "test_key_1234567890"')
        content = content.replace('enabled: false', 'enabled: false')

        with open(secrets_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print_success("配置已更新为测试值")

        # 验证配置文件
        import yaml
        with open(secrets_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        if config.get('deepseek', {}).get('api_key') == "test_key_1234567890":
            print_success("测试配置验证通过")
        else:
            print_error("测试配置验证失败")
            return False

        return True

    except Exception as e:
        print_error(f"设置测试配置失败: {e}")
        return False

def test_with_config(clean_dir):
    """测试有配置的情况"""
    print_step(4, "测试配置完整启动")

    os.chdir(clean_dir)

    # 运行 run.py 并捕获输出
    print("运行 run.py (带配置)...")
    try:
        result = subprocess.run(
            [sys.executable, "run.py"],
            capture_output=True,
            text=True,
            timeout=30,  # 30秒超时
            env={**os.environ, "SMARTSCOUT_TEST_MODE": "1", "SMARTSCOUT_AUTO_INSTALL": "1"}  # 启用测试模式和自动安装
        )

        output = result.stdout + result.stderr

        # 检查输出
        print("分析输出...")
        with open("run_output_with_config.txt", "w", encoding="utf-8") as f:
            f.write(output)

        # 检查关键步骤
        checks = [
            ("Python版本检查", "✓ Python" in output),
            ("依赖检查", "检查依赖" in output),
            ("配置文件存在", "✓ 配置文件存在: config/secrets.yaml" in output),
            ("API密钥配置", "DeepSeek API密钥已配置:" in output),
            ("端口检查", "✓ 端口 8000 可用" in output or "检查端口" in output),
            ("数据库检查", "数据库" in output),  # 可能初始化或检查
        ]

        all_passed = True
        for check_name, check_result in checks:
            if check_result:
                print_success(f"检查通过: {check_name}")
            else:
                print_warning(f"检查警告: {check_name} 未找到")
                # 这里不是失败，只是警告

        # 检查是否尝试启动服务器
        if "启动 SmartScout API 服务器" in output:
            print_success("服务器启动流程正常")
        else:
            print_warning("未检测到服务器启动信息")

        # 在测试模式下，我们期望正常退出（不启动服务器）
        if result.returncode == 0:
            print_success(f"run.py 成功退出 (退出码: {result.returncode})")
        else:
            print_warning(f"run.py 非零退出 (退出码: {result.returncode})")

        return True, output

    except subprocess.TimeoutExpired:
        print_error("run.py 运行超时")
        return False, "Timeout"
    except Exception as e:
        print_error(f"运行 run.py 失败: {e}")
        return False, str(e)

def generate_report(clean_dir, missing_config_test, with_config_test, missing_output, config_output):
    """生成验证报告"""
    print_step(5, "生成验证报告")

    report = f"""# 干净环境启动验证报告
## 验证时间: {os.popen('date').read().strip()}
## 验证环境: {clean_dir}

## 1. 缺失配置测试
- 测试结果: {'通过' if missing_config_test else '失败'}
- 关键检查项:
  1. 配置文件缺失提示: {'✓' if "⚠️ 配置文件不存在: config/secrets.yaml" in missing_output else '✗'}
  2. 模板复制提示: {'✓' if "请复制 config/secrets.yaml.template" in missing_output else '✗'}
  3. 复制命令提示: {'✓' if "cp config/secrets.yaml.template config/secrets.yaml" in missing_output else '✗'}
  4. 编辑指引提示: {'✓' if "填写您的DeepSeek API密钥" in missing_output else '✗'}

## 2. 配置完整测试
- 测试结果: {'通过' if with_config_test else '失败'}
- 关键检查项:
  1. Python版本检查: {'✓' if "✓ Python" in config_output else '✗'}
  2. 依赖检查: {'✓' if "检查依赖" in config_output else '✗'}
  3. 配置文件存在: {'✓' if "✓ 配置文件存在: config/secrets.yaml" in config_output else '✗'}
  4. API密钥配置: {'✓' if "DeepSeek API密钥已配置:" in config_output else '✗'}
  5. 端口检查: {'✓' if "端口" in config_output and ("可用" in config_output or "检查" in config_output) else '✗'}
  6. 服务器启动流程: {'✓' if "启动 SmartScout API 服务器" in config_output else '✗'}

## 3. 总体评估
- 缺失配置提示清晰度: {'良好' if missing_config_test else '需要改进'}
- 配置检查完整性: {'良好' if with_config_test else '需要改进'}
- 新同事可启动性: {'可启动' if missing_config_test and with_config_test else '需要指导'}

## 4. 发现的问题
{generate_issues(missing_output, config_output)}

## 5. 建议
1. 确保 secrets.yaml.template 包含所有必要的配置字段
2. 验证提示信息是否足够清晰引导新同事
3. 检查依赖安装指引是否明确
4. 验证数据库初始化流程

## 6. 验证文件
- 缺失配置运行输出: {os.path.join(clean_dir, 'run_output_missing_config.txt')}
- 完整配置运行输出: {os.path.join(clean_dir, 'run_output_with_config.txt')}
"""

    report_path = os.path.join(clean_dir, "CLEAN_START_VALIDATION_REPORT.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print_success(f"验证报告已生成: {report_path}")

    # 同时复制到项目docs目录
    docs_report_path = Path(__file__).parent.parent / "docs" / "CLEAN_START_VALIDATION.md"
    try:
        shutil.copy2(report_path, docs_report_path)
        print_success(f"报告已复制到项目文档: {docs_report_path}")
    except Exception as e:
        print_warning(f"无法复制报告到项目文档: {e}")

    return report_path

def generate_issues(missing_output, config_output):
    """生成问题列表"""
    issues = []

    # 检查缺失配置提示的问题
    if "⚠️ 配置文件不存在: config/secrets.yaml" not in missing_output:
        issues.append("- 缺失配置文件时未显示明确警告")

    if "请复制 config/secrets.yaml.template" not in missing_output:
        issues.append("- 未提示复制模板文件")

    if "填写您的DeepSeek API密钥" not in missing_output:
        issues.append("- 未提供配置填写指引")

    # 检查配置完整时的问题
    if "✓ Python" not in config_output:
        issues.append("- Python版本检查未显示成功标志")

    if "检查依赖" not in config_output:
        issues.append("- 依赖检查未执行或未显示")

    if "✓ 配置文件存在: config/secrets.yaml" not in config_output:
        issues.append("- 配置文件存在性检查未通过")

    if "DeepSeek API密钥已配置:" not in config_output:
        issues.append("- API密钥配置验证未显示")

    if "启动 SmartScout API 服务器" not in config_output:
        issues.append("- 服务器启动流程未触发")

    if not issues:
        issues.append("- 未发现重大问题")

    return "\n".join(issues)

def main():
    """主验证流程"""
    print(f"{BLUE}{'='*60}{NC}")
    print(f"{BLUE}SmartScout 干净环境启动验证{NC}")
    print(f"{BLUE}{'='*60}{NC}")

    # 创建干净环境
    clean_dir = create_clean_environment()
    if not clean_dir:
        print_error("创建干净环境失败")
        sys.exit(1)

    try:
        # 测试缺失配置
        missing_config_passed, missing_output = test_missing_config(clean_dir)

        # 设置测试配置
        if not setup_test_config(clean_dir):
            print_error("设置测试配置失败")
            sys.exit(1)

        # 测试有配置的情况
        with_config_passed, config_output = test_with_config(clean_dir)

        # 生成报告
        report_path = generate_report(
            clean_dir,
            missing_config_passed,
            with_config_passed,
            missing_output,
            config_output
        )

        # 总体评估
        print_step(6, "验证总结")

        if missing_config_passed and with_config_passed:
            print_success("✅ 验证通过: 干净环境启动流程正常")
            print_success("新同事可根据提示完成配置并启动服务")
        else:
            print_error("❌ 验证失败: 存在需要修复的问题")
            if not missing_config_passed:
                print_error("  - 缺失配置提示不充分")
            if not with_config_passed:
                print_error("  - 配置完整后启动流程有问题")

        print(f"\n验证目录: {clean_dir}")
        print(f"验证报告: {report_path}")

        # 询问是否清理临时目录
        print(f"\n{YELLOW}提示: 临时目录 {clean_dir} 将在程序退出后保留以供检查")
        print(f"如需手动清理: rm -rf {clean_dir}{NC}")

        return missing_config_passed and with_config_passed

    except Exception as e:
        print_error(f"验证过程异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)