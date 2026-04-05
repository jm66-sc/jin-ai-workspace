"""
SmartScout 阶段二：SQLite规则资产化
将DeepSeek规则扩充结果存入SQLite数据库
"""

import os
import json
import sqlite3
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# 导入配置加载器
from config_loader import get_database_path

logger = logging.getLogger(__name__)


class SQLiteManager:
    """SQLite数据库管理器"""

    def __init__(self, db_path: Optional[str] = None):
        """
        初始化数据库管理器

        Args:
            db_path: 数据库文件路径，如果为None则使用配置中的路径
        """
        if db_path is None:
            db_path = get_database_path()

        # 确保目录存在
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

        self.db_path = db_path
        self.connection = None

        logger.info(f"SQLite管理器初始化，数据库路径: {db_path}")

    def connect(self) -> sqlite3.Connection:
        """
        连接到数据库

        Returns:
            数据库连接对象
        """
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            # 启用外键支持和返回字典格式的行
            self.connection.execute("PRAGMA foreign_keys = ON")
            # 设置行工厂为字典格式
            self.connection.row_factory = sqlite3.Row

        return self.connection

    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.debug("数据库连接已关闭")

    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()

    def initialize_database(self):
        """
        初始化数据库表结构

        创建projects表（存储规则）和results表（存储解析结果）
        """
        conn = self.connect()
        cursor = conn.cursor()

        # 创建projects表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                url_key TEXT PRIMARY KEY,          -- 项目唯一标识（可以是哈希ID或URL）
                original_url TEXT,                 -- 原始爬取URL（从实战中复制的URL）
                white_list JSON DEFAULT '[]',      -- 白名单（包含初始和扩充）
                black_list JSON DEFAULT '[]',      -- 黑名单（包含初始和扩充）
                human_confirmed INTEGER DEFAULT 1, -- 人工确认占位（默认1=已确认）
                rule_expansions JSON,              -- DeepSeek返回的完整扩充结果
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 添加original_url列（如果表已存在且没有该列）
        try:
            cursor.execute("ALTER TABLE projects ADD COLUMN original_url TEXT")
            logger.info("已添加original_url列到projects表")
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e):
                logger.warning(f"添加original_url列失败: {e}")

        # 创建results表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_key TEXT NOT NULL,         -- 关联的项目url_key
                title TEXT,                        -- 公告标题
                announcement_type TEXT,            -- 公告类型
                purchasing_unit TEXT,              -- 采购单位
                budget_amount TEXT,                -- 预算金额
                winning_amount TEXT,               -- 中标金额
                supplier TEXT,                     -- 供应商
                winning_supplier TEXT,             -- 中标供应商
                publish_time TEXT,                 -- 发布时间
                registration_deadline TEXT,        -- 报名截止时间
                bid_deadline TEXT,                 -- 投标截止时间
                project_overview TEXT,             -- 项目概况
                contact_info TEXT,                 -- 联系人信息
                detail_url TEXT NOT NULL,          -- 详情页URL
                raw_markdown TEXT,                 -- 原始Markdown内容
                extraction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_key) REFERENCES projects (url_key)
            )
        """)

        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_results_project ON results (project_key)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_results_time ON results (extraction_time)")

        conn.commit()
        logger.info("数据库表结构初始化完成")

    def create_project(
        self,
        url_key: str,
        white_list: List[str],
        black_list: List[str],
        rule_expansions: Dict[str, List[str]],
        original_url: Optional[str] = None
    ) -> bool:
        """
        创建新项目

        Args:
            url_key: 项目唯一标识（可以是哈希ID或URL）
            white_list: 白名单关键词列表
            black_list: 黑名单关键词列表
            rule_expansions: DeepSeek返回的规则扩充结果
            original_url: 原始爬取URL（从实战中复制的URL），如果为None则使用url_key

        Returns:
            是否成功创建
        """
        conn = self.connect()
        cursor = conn.cursor()

        # 如果未提供original_url，使用url_key（向后兼容）
        if original_url is None:
            original_url = url_key

        try:
            cursor.execute("""
                INSERT INTO projects
                (url_key, original_url, white_list, black_list, rule_expansions)
                VALUES (?, ?, ?, ?, ?)
            """, (
                url_key,
                original_url,
                json.dumps(white_list, ensure_ascii=False),
                json.dumps(black_list, ensure_ascii=False),
                json.dumps(rule_expansions, ensure_ascii=False)
            ))

            conn.commit()
            logger.info(f"项目创建成功: {url_key}")
            logger.debug(f"白名单: {len(white_list)}个, 黑名单: {len(black_list)}个")
            return True

        except sqlite3.IntegrityError:
            logger.warning(f"项目已存在: {url_key}")
            return False
        except Exception as e:
            logger.error(f"创建项目失败: {e}")
            conn.rollback()
            raise

    def get_project(self, url_key: str) -> Optional[Dict[str, Any]]:
        """
        获取项目信息

        Args:
            url_key: 项目URL标识

        Returns:
            项目信息字典，如果不存在则返回None
        """
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT url_key, original_url, white_list, black_list, human_confirmed,
                   rule_expansions, created_at
            FROM projects
            WHERE url_key = ?
        """, (url_key,))

        row = cursor.fetchone()
        if row is None:
            return None

        # 将sqlite3.Row转换为字典，并解析JSON字段
        result = dict(row)
        result["white_list"] = json.loads(result["white_list"]) if result["white_list"] else []
        result["black_list"] = json.loads(result["black_list"]) if result["black_list"] else []
        result["rule_expansions"] = json.loads(result["rule_expansions"]) if result["rule_expansions"] else {}

        # 如果original_url为空，则使用url_key（向后兼容）
        if not result.get("original_url"):
            result["original_url"] = result["url_key"]

        return result

    def update_project_rules(
        self,
        url_key: str,
        white_list: List[str],
        black_list: List[str],
        rule_expansions: Dict[str, List[str]]
    ) -> bool:
        """
        更新项目规则

        Args:
            url_key: 项目URL标识
            white_list: 新的白名单
            black_list: 新的黑名单
            rule_expansions: 新的规则扩充结果

        Returns:
            是否成功更新
        """
        conn = self.connect()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE projects
                SET white_list = ?, black_list = ?, rule_expansions = ?
                WHERE url_key = ?
            """, (
                json.dumps(white_list, ensure_ascii=False),
                json.dumps(black_list, ensure_ascii=False),
                json.dumps(rule_expansions, ensure_ascii=False),
                url_key
            ))

            if cursor.rowcount == 0:
                logger.warning(f"项目不存在，无法更新: {url_key}")
                return False

            conn.commit()
            logger.info(f"项目规则更新成功: {url_key}")
            logger.debug(f"白名单: {len(white_list)}个, 黑名单: {len(black_list)}个")
            return True

        except Exception as e:
            logger.error(f"更新项目规则失败: {e}")
            conn.rollback()
            raise

    def save_extraction_result(
        self,
        project_key: str,
        title: str,
        detail_url: str,
        raw_markdown: str,
        extracted_fields: Dict[str, str]
    ) -> int:
        """
        保存提取结果

        Args:
            project_key: 项目标识
            title: 公告标题
            detail_url: 详情页URL
            raw_markdown: 原始Markdown内容
            extracted_fields: 提取的字段字典

        Returns:
            插入行的ID
        """
        conn = self.connect()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO results (
                    project_key, title, detail_url, raw_markdown,
                    announcement_type, purchasing_unit, budget_amount,
                    winning_amount, supplier, winning_supplier,
                    publish_time, registration_deadline, bid_deadline,
                    project_overview, contact_info
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_key,
                title,
                detail_url,
                raw_markdown,
                extracted_fields.get("announcement_type"),
                extracted_fields.get("purchasing_unit"),
                extracted_fields.get("budget_amount"),
                extracted_fields.get("winning_amount"),
                extracted_fields.get("supplier"),
                extracted_fields.get("winning_supplier"),
                extracted_fields.get("publish_time"),
                extracted_fields.get("registration_deadline"),
                extracted_fields.get("bid_deadline"),
                extracted_fields.get("project_overview"),
                extracted_fields.get("contact_info")
            ))

            result_id = cursor.lastrowid
            conn.commit()
            logger.debug(f"提取结果保存成功，ID: {result_id}, 标题: {title[:50]}...")
            return result_id

        except Exception as e:
            logger.error(f"保存提取结果失败: {e}")
            conn.rollback()
            raise

    def get_all_projects(self) -> List[Dict[str, Any]]:
        """
        获取所有项目

        Returns:
            项目列表
        """
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT url_key, white_list, black_list, human_confirmed,
                   rule_expansions, created_at
            FROM projects
            ORDER BY created_at DESC
        """)

        results = []
        for row in cursor.fetchall():
            result = dict(row)
            result["white_list"] = json.loads(result["white_list"]) if result["white_list"] else []
            result["black_list"] = json.loads(result["black_list"]) if result["black_list"] else []
            result["rule_expansions"] = json.loads(result["rule_expansions"]) if result["rule_expansions"] else {}
            results.append(result)

        return results

    def get_results_by_project(self, project_key: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取项目的所有解析结果

        Args:
            project_key: 项目标识
            limit: 返回结果数量限制

        Returns:
            结果列表
        """
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, title, detail_url, announcement_type, purchasing_unit,
                   budget_amount, winning_amount, supplier, winning_supplier,
                   publish_time, registration_deadline, bid_deadline,
                   project_overview, contact_info, extraction_time
            FROM results
            WHERE project_key = ?
            ORDER BY extraction_time DESC
            LIMIT ?
        """, (project_key, limit))

        return [dict(row) for row in cursor.fetchall()]

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取数据库统计信息

        Returns:
            统计信息字典
        """
        conn = self.connect()
        cursor = conn.cursor()

        stats = {}

        # 项目数量
        cursor.execute("SELECT COUNT(*) FROM projects")
        stats["project_count"] = cursor.fetchone()[0]

        # 结果数量
        cursor.execute("SELECT COUNT(*) FROM results")
        stats["result_count"] = cursor.fetchone()[0]

        # 最近的项目
        cursor.execute("SELECT COUNT(*) FROM projects WHERE created_at > datetime('now', '-7 days')")
        stats["recent_projects_7d"] = cursor.fetchone()[0]

        # 最近的结果
        cursor.execute("SELECT COUNT(*) FROM results WHERE extraction_time > datetime('now', '-7 days')")
        stats["recent_results_7d"] = cursor.fetchone()[0]

        return stats


def save_rule_expansion_to_db(
    url_key: str,
    rule_expansions: Dict[str, List[str]],
    initial_white_list: List[str] = None,
    initial_black_list: List[str] = None
) -> bool:
    """
    将规则扩充结果保存到数据库（便捷函数）

    Args:
        url_key: 项目URL标识
        rule_expansions: DeepSeek返回的规则扩充结果
        initial_white_list: 初始白名单，默认为None时使用默认值
        initial_black_list: 初始黑名单，默认为None时使用默认值

    Returns:
        是否成功保存
    """
    if initial_white_list is None:
        initial_white_list = ["消防设备", "消防工程", "设备改造", "设备采购"]

    if initial_black_list is None:
        initial_black_list = ["物流配送", "食堂配送", "服务咨询", "保安", "建筑材料"]

    # 合并初始列表和扩充列表
    white_list = initial_white_list + rule_expansions.get("white_list_additions", [])
    black_list = initial_black_list + rule_expansions.get("black_list_additions", [])

    # 创建数据库管理器并保存
    with SQLiteManager() as db:
        # 确保数据库已初始化
        db.initialize_database()

        # 创建项目
        success = db.create_project(
            url_key=url_key,
            white_list=white_list,
            black_list=black_list,
            rule_expansions=rule_expansions
        )

        if success:
            logger.info(f"规则扩充结果已保存到数据库: {url_key}")
            logger.info(f"合并后白名单: {len(white_list)}个词条")
            logger.info(f"合并后黑名单: {len(black_list)}个词条")
        else:
            logger.info(f"规则扩充结果已更新到数据库: {url_key}")

        return success


def main():
    """主函数：数据库管理演示"""
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
    logger.info("SmartScout Phase 1.3: SQLite规则资产化")
    logger.info("=" * 80)

    try:
        # 创建数据库管理器
        db_manager = SQLiteManager()

        # 初始化数据库
        db_manager.initialize_database()

        # 演示：创建示例项目
        url_key = "https://search.ccgp.gov.cn/bxsearch?searchtype=2&page_index=1&kw=消防"
        rule_expansions = {
            "black_list_additions": ["物流", "配送", "服务", "咨询"],
            "white_list_additions": ["消防", "设备", "工程", "采购"]
        }

        success = save_rule_expansion_to_db(url_key, rule_expansions)
        if success:
            logger.info("示例项目创建成功")

        # 获取并显示项目信息
        project = db_manager.get_project(url_key)
        if project:
            logger.info(f"项目信息: {project['url_key']}")
            logger.info(f"白名单: {project['white_list']}")
            logger.info(f"黑名单: {project['black_list']}")
            logger.info(f"人工确认状态: {'已确认' if project['human_confirmed'] else '未确认'}")

        # 显示统计信息
        stats = db_manager.get_statistics()
        logger.info(f"数据库统计: {stats}")

        logger.info("数据库管理演示完成")

    except Exception as e:
        logger.error(f"数据库管理失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()