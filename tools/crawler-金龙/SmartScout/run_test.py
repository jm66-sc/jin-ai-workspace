#!/usr/bin/env python3
"""
SmartScout API 一键启动脚本
运行: python run.py
"""
import os
import sys
import subprocess
import platform
import socket
import sqlite3
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("错误: 需要Python 3.8或更高版本")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

def check_requirements():
    """检查依赖（默认只检查并提示，可通过环境变量启用自动安装）"""
    print("\n检查依赖...")

    requirements_file = "requirements_api.txt"
    if not os.path.exists(requirements_file):
        print(f"错误: 依赖文件 {requirements_file} 不存在")
        sys.exit(1)

    # 解析requirements文件
    try:
        with open(requirements_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"✗ 读取依赖文件失败: {e}")
        sys.exit(1)

    # 提取包名（简单解析，忽略注释和空行）
    packages = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        # 提取包名（去掉版本说明符）
        package = line.split('>=')[0].split('==')[0].split('[')[0].strip()
        if package:
            packages.append(package)

    print(f"需要检查 {len(packages)} 个依赖包")

    missing_packages = []
    for package in packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} (未安装)")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n⚠️  缺少 {len(missing_packages)} 个依赖包: {', '.join(missing_packages)}")
        print("  建议手动安装: pip install -r requirements_api.txt")

        # 检查是否启用自动安装
        auto_install = os.environ.get('SMARTSCOUT_AUTO_INSTALL', '').lower() in ('1', 'true', 'yes', 'y')
        if auto_install:
            print("检测到 SMARTSCOUT_AUTO_INSTALL=1，尝试自动安装...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
                print("✓ 依赖安装完成")
                # 重新检查安装结果
                print("重新检查依赖...")
                for package in missing_packages[:]:  # 复制列表以便修改
                    try:
                        __import__(package.replace('-', '_'))
                        print(f"  ✓ {package} (安装成功)")
                        missing_packages.remove(package)
                    except ImportError:
                        print(f"  ✗ {package} (安装后仍缺失)")

                if missing_packages:
                    print(f"\n❌ 仍有 {len(missing_packages)} 个包安装失败: {', '.join(missing_packages)}")
                    print("请手动检查pip安装过程")
                    sys.exit(1)
            except subprocess.CalledProcessError as e:
                print(f"✗ 自动安装失败: {e}")
                print("请手动运行: pip install -r requirements_api.txt")
                sys.exit(1)
        else:
            print("如需自动安装，请设置环境变量: export SMARTSCOUT_AUTO_INSTALL=1")
            print("或手动运行: pip install -r requirements_api.txt")
            sys.exit(1)
    else:
        print("✓ 所有依赖包已安装")

def check_port_available(port=8000):
    """检查端口是否可用（如果被占用则退出）"""
    try:
        # 尝试绑定到端口来检查是否被占用
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.bind(('0.0.0.0', port))
            # 如果绑定成功，端口可用
            print(f"✓ 端口 {port} 可用")
            return True
    except OSError as e:
        if e.errno == 48 or "Address already in use" in str(e):
            print(f"✗ 端口 {port} 已被占用")
            print(f"  请检查是否有其他进程正在使用端口 {port}")
            print(f"  可尝试: lsof -i :{port} 或 netstat -an | grep {port}")
            print(f"  或使用其他端口: export SMARTSCOUT_PORT=8001")
            sys.exit(1)
        else:
            print(f"⚠️  检查端口 {port} 时发生错误: {e}")
            print(f"  将继续启动，但可能无法绑定到端口 {port}")
            return True  # 非占用错误，继续启动

def check_directories_writable():
    """检查必要目录是否可写（如果不可写则退出）"""
    directories = ["logs", "data", "data/temp"]

    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            # 尝试写入测试文件
            test_file = os.path.join(directory, ".write_test")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            print(f"✓ 目录可写: {directory}")
        except Exception as e:
            print(f"✗ 目录不可写: {directory} - {e}")
            print(f"  请检查目录权限: chmod 755 {directory}")
            print(f"  或更改目录所有者: chown $(whoami) {directory}")
            sys.exit(1)

def check_sqlite():
    """检查SQLite可用性和数据库文件可写性"""
    try:
        # 检查sqlite3模块是否可用
        import sqlite3
        print("✓ SQLite模块可用")

        # 获取数据库路径
        sys.path.insert(0, "src")
        from config_loader import get_database_path
        db_path = get_database_path()

        # 确保目录存在
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

        # 测试数据库连接和写入
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        if result and result[0] == 1:
            print(f"✓ 数据库连接正常: {db_path}")

        # 测试写入
        cursor.execute("CREATE TABLE IF NOT EXISTS _test_table (id INTEGER)")
        cursor.execute("INSERT INTO _test_table (id) VALUES (1)")
        cursor.execute("DROP TABLE _test_table")
        conn.commit()
        conn.close()

        print("✓ 数据库可写")
        return True
    except ImportError:
        print("✗ SQLite模块不可用（Python标准库应包含sqlite3）")
        return False
    except Exception as e:
        print(f"✗ 数据库检查失败: {e}")
        print(f"  请检查数据库文件权限: {db_path if 'db_path' in locals() else '未知'}")
        return False

def setup_directories():
    """创建必要的目录"""
    directories = ["logs", "data", "data/temp"]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ 目录已创建: {directory}")

def initialize_database():
    """初始化数据库"""
    print("\n初始化数据库...")
    try:
        # 导入现有模块以初始化数据库
        sys.path.insert(0, "src")
        from sqlite_manager import SQLiteManager

        db = SQLiteManager()
        db.initialize_database()
        print("✓ 数据库表结构初始化完成")

        # 扩展表结构（tasks和feedback表）
        import sqlite3
        from config_loader import get_database_path

        db_path = get_database_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 创建tasks表（如果不存在）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                project_key TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                target_count INTEGER,
                processed_count INTEGER DEFAULT 0,
                successful_count INTEGER DEFAULT 0,
                skipped_count INTEGER DEFAULT 0,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                error_message TEXT,
                FOREIGN KEY (project_key) REFERENCES projects (url_key)
            )
        """)

        # 创建feedback表（如果不存在）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                result_id INTEGER NOT NULL,
                accuracy_rating INTEGER CHECK (accuracy_rating BETWEEN 1 AND 5),
                feedback_text TEXT,
                suggested_fields JSON,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (result_id) REFERENCES results (id)
            )
        """)

        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks (project_key)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks (status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_result ON feedback (result_id)")

        conn.commit()
        conn.close()
        print("✓ 数据库扩展表结构初始化完成")

    except Exception as e:
        print(f"⚠️ 数据库初始化警告: {e}")
        print("将继续启动，但数据库功能可能受影响")

def check_config():
    """检查配置文件存在性和必要字段"""
    config_files = ["config/settings.yaml", "config/secrets.yaml"]

    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"✓ 配置文件存在: {config_file}")
            # 检查配置文件内容
            try:
                import yaml
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}

                # 根据文件类型检查必要字段
                if config_file.endswith('settings.yaml'):
                    required_sections = ['project', 'database', 'logging']
                    for section in required_sections:
                        if section in config:
                            print(f"    ✓ 包含必要配置节: {section}")
                        else:
                            print(f"    ⚠️ 缺少配置节: {section}")

                    # 检查数据库路径
                    if 'database' in config and 'path' in config['database']:
                        db_path = config['database']['path']
                        print(f"    ✓ 数据库路径配置: {db_path}")
                    else:
                        print(f"    ⚠️ 数据库路径未配置")

                elif config_file.endswith('secrets.yaml'):
                    # 检查DeepSeek API配置
                    if 'deepseek' in config:
                        deepseek = config['deepseek']
                        if deepseek.get('api_key'):
                            masked_key = deepseek['api_key'][:8] + "..." if len(deepseek['api_key']) > 8 else "***"
                            print(f"    ✓ DeepSeek API密钥已配置: {masked_key}")
                        else:
                            print(f"    ⚠️ DeepSeek API密钥未配置")
                        if deepseek.get('base_url'):
                            print(f"    ✓ DeepSeek API地址: {deepseek['base_url']}")
                        else:
                            print(f"    ⚠️ DeepSeek API地址未配置")
                    else:
                        print(f"    ⚠️ 缺少DeepSeek配置节")

            except Exception as e:
                print(f"    ⚠️ 配置文件解析错误: {e}")
        else:
            print(f"⚠️ 配置文件不存在: {config_file}")
            # 如果是secrets.yaml，提示模板
            if config_file.endswith('secrets.yaml'):
                print("    提示: 请复制 config/secrets.yaml.template 为 secrets.yaml 并填写配置")

print("测试模式 - 跳过服务器启动")
return
def start_server():
    """启动FastAPI服务器"""
    print("\n" + "="*60)
    print("启动 SmartScout API 服务器")
    print("="*60)

    # 显示访问信息
    print("\n访问地址:")
    print("  • API文档: http://localhost:8000/docs")
    print("  • 健康检查: http://localhost:8000/health")
    print("  • 重定向文档: http://localhost:8000/redoc")

    print("\n服务器日志:")
    print("-" * 40)

    # 启动服务器
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

def main():
    """主函数"""
    print("="*60)
    print("SmartScout API 启动器")
    print("="*60)

    # 检查当前目录
    current_dir = Path(__file__).parent
    if not (current_dir / "src").exists():
        print("错误: 请在SmartScout项目根目录下运行此脚本")
        print(f"当前目录: {current_dir}")
        sys.exit(1)

    os.chdir(current_dir)
    print(f"工作目录: {current_dir}")

    # 执行启动步骤
    try:
        check_python_version()
        check_requirements()
        setup_directories()
        check_directories_writable()
        check_config()
        check_sqlite()
        check_port_available(8000)
        initialize_database()
        print("测试模式 - 跳过服务器启动")
        return
        start_server()
    except KeyboardInterrupt:
        print("\n\n服务器已停止")
    except Exception as e:
        print(f"\n启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()