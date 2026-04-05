"""
SmartScout FastAPI 服务入口
基于现有爬虫代码提供RESTful API
"""
import os
import sys
import logging
from pathlib import Path

# 添加现有src目录到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import sqlite3
import json
import uuid
import asyncio
from datetime import datetime, timedelta
import time

# 导入现有模块
try:
    from deepseek_rule_expander import DeepSeekRuleExpander
    from sqlite_manager import SQLiteManager, save_rule_expansion_to_db
    from producer import Producer
    from consumer import Consumer
    from config_loader import get_database_path, get_queue_file_path, get_default_page_limit
except ImportError as e:
    print(f"导入现有模块失败: {e}")
    print("请确保在SmartScout目录下运行")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/api.log", encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="SmartScout API",
    description="SmartScout爬虫后端RESTful API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件托管 (前端构建结果)

# 数据库路径
DB_PATH = get_database_path()
QUEUE_FILE = get_queue_file_path()

# Pydantic模型（请求/响应）
class RuleDiagnosisRequest(BaseModel):
    urls: List[str] = Field(..., description="URL列表")
    initial_blacklist: List[str] = Field(default=[], description="初始黑名单")
    initial_whitelist: List[str] = Field(default=[], description="初始白名单")

class RuleDiagnosisResponse(BaseModel):
    project_id: str = Field(..., description="项目ID")
    recommended_blacklist: List[str] = Field(..., description="推荐黑名单")
    recommended_whitelist: List[str] = Field(..., description="推荐白名单")
    sample_count: int = Field(..., description="样本数量")
    status: str = Field(..., description="状态")

class SaveRuleRequest(BaseModel):
    blacklist: List[str] = Field(..., description="黑名单")
    whitelist: List[str] = Field(..., description="白名单")
    human_confirmed: bool = Field(default=True, description="人工确认")

class SaveRuleResponse(BaseModel):
    success: bool = Field(..., description="是否成功")
    project_id: str = Field(..., description="项目ID")
    rule_count: Dict[str, int] = Field(..., description="规则数量")

class StartProductionRequest(BaseModel):
    target_count: int = Field(default=500, description="目标数量")
    concurrency: int = Field(default=3, description="并发数")
    max_pages: int = Field(default=50, description="最大页数")

class StartProductionResponse(BaseModel):
    task_id: str = Field(..., description="任务ID")
    project_id: str = Field(..., description="项目ID")
    status: str = Field(..., description="状态")
    estimated_time: str = Field(..., description="预计时间")

class ResultItem(BaseModel):
    id: int = Field(..., description="结果ID")
    purchasing_unit: str = Field(..., description="采购单位")
    project_name: str = Field(..., description="项目名称")
    budget_amount: str = Field(..., description="预算金额")
    announcement_type: str = Field(..., description="公告类型")
    detail_url: str = Field(..., description="详情页URL")
    extraction_time: str = Field(..., description="提取时间")
    fields: Dict[str, Any] = Field(..., description="完整字段")

class GetResultsResponse(BaseModel):
    results: List[ResultItem] = Field(..., description="结果列表")
    total: int = Field(..., description="总数")
    project_id: str = Field(..., description="项目ID")
    status: str = Field(..., description="状态")

class FeedbackRequest(BaseModel):
    result_id: int = Field(..., description="结果ID")
    accuracy_rating: int = Field(..., ge=1, le=5, description="准确度评分1-5")
    feedback_text: str = Field(..., description="反馈文本")
    suggested_fields: List[str] = Field(default=[], description="建议字段")

class FeedbackResponse(BaseModel):
    success: bool = Field(..., description="是否成功")
    feedback_id: str = Field(..., description="反馈ID")

class TaskStatusResponse(BaseModel):
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="状态")
    progress: int = Field(..., description="进度百分比")
    processed: int = Field(..., description="已处理数量")
    successful: int = Field(..., description="成功提取数量")
    skipped: int = Field(..., description="跳过数量")
    estimated_remaining: str = Field(..., description="预计剩余时间")
    started_at: str = Field(..., description="开始时间")
    updated_at: str = Field(..., description="更新时间")

# 数据库扩展函数
def extend_database_tables():
    """扩展数据库表结构（tasks和feedback表）"""
    conn = sqlite3.connect(DB_PATH)
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
    logger.info("数据库表结构扩展完成")

# 初始化时扩展数据库表
@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    logger.info("SmartScout API 启动中...")

    # 确保日志目录存在
    os.makedirs("logs", exist_ok=True)

    # 扩展数据库表
    extend_database_tables()

    logger.info("SmartScout API 启动完成")

# API端点
@app.post("/api/rule-diagnosis", response_model=RuleDiagnosisResponse)
async def rule_diagnosis(request: RuleDiagnosisRequest):
    """
    规则确诊接口
    基于提供的URL列表进行规则确诊
    """
    logger.info(f"规则确诊请求: {len(request.urls)}个URL")

    try:
        # 使用第一个URL的哈希值作为项目ID，避免URL中的斜杠导致路径问题
        import hashlib
        if request.urls:
            url_hash = hashlib.md5(request.urls[0].encode()).hexdigest()[:8]
            project_id = f"project_{url_hash}"
        else:
            project_id = str(uuid.uuid4())

        # 调用DeepSeek规则扩展器
        expander = DeepSeekRuleExpander()

        # 动态抓取样本标题（使用第一个URL）
        try:
            logger.info(f"开始从URL动态抓取50个样本: {request.urls[0] if request.urls else '无URL'}")

            if not request.urls:
                raise ValueError("URL列表不能为空")

            # 导入样本抓取器（异步版本，因为我们在async函数中）
            from sample_crawler import crawl_samples_from_url

            # 抓取50个样本标题（异步调用）
            sample_titles = await crawl_samples_from_url(request.urls[0])
            logger.info(f"动态抓取完成：获取 {len(sample_titles)} 个样本标题")

        except Exception as e:
            logger.error(f"动态样本抓取失败，使用备用样本文件: {e}")
            # 如果动态抓取失败，使用备用样本文件
            sample_file = os.path.join(os.path.dirname(__file__), "simple_bids_50_20260211_032958.json")
            logger.info(f"使用备用样本文件: {sample_file}")
            rule_expansions = expander.expand_rules(
                sample_file=sample_file,
                initial_white_list=request.initial_whitelist,
                initial_black_list=request.initial_blacklist
            )
        else:
            # 使用动态抓取的标题进行规则扩充
            logger.info(f"使用动态抓取的 {len(sample_titles)} 个标题进行规则扩充")
            if not sample_titles:
                logger.warning("动态抓取返回空标题列表，使用备用样本文件")
                sample_file = os.path.join(os.path.dirname(__file__), "simple_bids_50_20260211_032958.json")
                logger.info(f"使用备用样本文件: {sample_file}")
                rule_expansions = expander.expand_rules(
                    sample_file=sample_file,
                    initial_white_list=request.initial_whitelist,
                    initial_black_list=request.initial_blacklist
                )
            else:
                rule_expansions = expander.expand_rules(
                    titles=sample_titles,
                    initial_white_list=request.initial_whitelist,
                    initial_black_list=request.initial_blacklist
                )

        # 提取扩充列表
        black_list_additions = rule_expansions.get("black_list_additions", [])
        white_list_additions = rule_expansions.get("white_list_additions", [])

        # 合并初始列表和扩充列表
        recommended_blacklist = request.initial_blacklist + black_list_additions
        recommended_whitelist = request.initial_whitelist + white_list_additions

        # 保存规则到数据库
        with SQLiteManager() as db:
            # 合并初始列表和扩充列表
            white_list = request.initial_whitelist + white_list_additions
            black_list = request.initial_blacklist + black_list_additions

            success = db.create_project(
                url_key=project_id,
                white_list=white_list,
                black_list=black_list,
                rule_expansions=rule_expansions,
                original_url=request.urls[0] if request.urls else None
            )

            if not success:
                # 如果项目已存在，更新规则
                db.update_project_rules(
                    url_key=project_id,
                    white_list=white_list,
                    black_list=black_list,
                    rule_expansions=rule_expansions
                )

        return RuleDiagnosisResponse(
            project_id=project_id,
            recommended_blacklist=recommended_blacklist,
            recommended_whitelist=recommended_whitelist,
            sample_count=50,
            status="completed"
        )

    except Exception as e:
        logger.error(f"规则确诊失败: {e}")
        raise HTTPException(status_code=500, detail=f"规则确诊失败: {str(e)}")

@app.post("/api/rules/{project_id}", response_model=SaveRuleResponse)
async def save_rules(project_id: str, request: SaveRuleRequest):
    """
    保存规则接口
    保存人工确认后的规则到数据库
    """
    logger.info(f"保存规则请求: {project_id}")

    try:
        with SQLiteManager() as db:
            # 获取现有项目
            project = db.get_project(project_id)
            if not project:
                raise HTTPException(status_code=404, detail="项目不存在")

            # 更新项目规则
            success = db.update_project_rules(
                url_key=project_id,
                white_list=request.whitelist,
                black_list=request.blacklist,
                rule_expansions={
                    "black_list_additions": request.blacklist,
                    "white_list_additions": request.whitelist
                }
            )

            if not success:
                raise HTTPException(status_code=500, detail="更新规则失败")

        return SaveRuleResponse(
            success=True,
            project_id=project_id,
            rule_count={"blacklist": len(request.blacklist), "whitelist": len(request.whitelist)}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"保存规则失败: {e}")
        raise HTTPException(status_code=500, detail=f"保存规则失败: {str(e)}")

# 任务状态跟踪
active_tasks = {}

async def run_production_task(task_id: str, project_id: str, target_count: int, concurrency: int, max_pages: int):
    """运行生产任务的背景任务"""
    logger.info(f"开始生产任务 {task_id} for project {project_id}")

    try:
        # 更新任务状态为运行中
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tasks SET status = 'running', started_at = CURRENT_TIMESTAMP WHERE task_id = ?",
            (task_id,)
        )
        conn.commit()

        # 获取项目的原始URL
        with SQLiteManager() as db:
            project = db.get_project(project_id)
            if not project:
                raise ValueError(f"项目不存在: {project_id}")

            # 使用original_url，如果为空则使用project_id（向后兼容）
            target_url = project.get("original_url", project_id)
            logger.info(f"使用目标URL进行生产: {target_url}")

        # 运行生产者（使用原始URL）
        producer = Producer(target_url, max_pages=max_pages)
        items = await producer.run(clear_existing=True)

        # 运行消费者
        consumer = Consumer(project_id, max_workers=concurrency)
        await consumer.run(task_limit=target_count, batch_size=concurrency)

        # 更新任务状态为完成
        cursor.execute(
            "UPDATE tasks SET status = 'completed', completed_at = CURRENT_TIMESTAMP, "
            "processed_count = ?, successful_count = ?, skipped_count = ? WHERE task_id = ?",
            (consumer.stats["detail_crawled"], consumer.stats["extraction_success"],
             consumer.stats["skipped_blacklist"] + consumer.stats["skipped_no_rule"], task_id)
        )
        conn.commit()

        logger.info(f"生产任务 {task_id} 完成")

    except Exception as e:
        logger.error(f"生产任务 {task_id} 失败: {e}")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tasks SET status = 'failed', error_message = ? WHERE task_id = ?",
            (str(e), task_id)
        )
        conn.commit()
    finally:
        # 从活动任务中移除
        if task_id in active_tasks:
            del active_tasks[task_id]

@app.post("/api/production/{project_id}/start", response_model=StartProductionResponse)
async def start_production(
    project_id: str,
    request: StartProductionRequest,
    background_tasks: BackgroundTasks
):
    """
    启动生产接口
    根据目标产值启动爬虫生产
    """
    logger.info(f"启动生产请求: {project_id}, 目标: {request.target_count}")

    try:
        # 验证项目存在
        with SQLiteManager() as db:
            project = db.get_project(project_id)
            if not project:
                raise HTTPException(status_code=404, detail="项目不存在")

        # 生成任务ID
        task_id = f"task_{uuid.uuid4().hex[:8]}"

        # 创建任务记录
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (task_id, project_key, status, target_count) VALUES (?, ?, 'pending', ?)",
            (task_id, project_id, request.target_count)
        )
        conn.commit()
        conn.close()

        # 在后台运行生产任务
        background_tasks.add_task(
            run_production_task,
            task_id, project_id,
            request.target_count, request.concurrency, request.max_pages
        )

        # 存储任务引用
        active_tasks[task_id] = {
            "status": "pending",
            "project_id": project_id,
            "started_at": datetime.now().isoformat()
        }

        return StartProductionResponse(
            task_id=task_id,
            project_id=project_id,
            status="started",
            estimated_time="30分钟"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"启动生产失败: {e}")
        raise HTTPException(status_code=500, detail=f"启动生产失败: {str(e)}")

@app.get("/api/results/{project_id}", response_model=GetResultsResponse)
async def get_results(
    project_id: str,
    limit: int = 50,
    offset: int = 0,
    order_by: str = "extraction_time DESC"
):
    """
    获取结果接口
    实时获取提取结果
    """
    logger.info(f"获取结果请求: {project_id}, limit={limit}, offset={offset}")

    try:
        with SQLiteManager() as db:
            # 获取项目
            project = db.get_project(project_id)
            if not project:
                raise HTTPException(status_code=404, detail="项目不存在")

            # 获取结果
            results = db.get_results_by_project(project_id, limit=limit + offset)

            # 应用分页
            paginated_results = results[offset:offset + limit]

            # 转换为响应格式
            result_items = []
            for row in paginated_results:
                # 构建字段字典
                fields = {
                    "announcement_type": row.get("announcement_type"),
                    "purchasing_unit": row.get("purchasing_unit"),
                    "budget_amount": row.get("budget_amount"),
                    "winning_amount": row.get("winning_amount"),
                    "supplier": row.get("supplier"),
                    "winning_supplier": row.get("winning_supplier"),
                    "publish_time": row.get("publish_time"),
                    "registration_deadline": row.get("registration_deadline"),
                    "bid_deadline": row.get("bid_deadline"),
                    "project_overview": row.get("project_overview"),
                    "contact_info": row.get("contact_info")
                }

                result_items.append(ResultItem(
                    id=row.get("id"),
                    purchasing_unit=row.get("purchasing_unit", ""),
                    project_name=row.get("title", ""),
                    budget_amount=row.get("budget_amount", ""),
                    announcement_type=row.get("announcement_type", ""),
                    detail_url=row.get("detail_url", ""),
                    extraction_time=row.get("extraction_time", ""),
                    fields=fields
                ))

            # 获取总数（需要单独查询）
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM results WHERE project_key = ?", (project_id,))
            total = cursor.fetchone()[0]
            conn.close()

            return GetResultsResponse(
                results=result_items,
                total=total,
                project_id=project_id,
                status="completed" if len(results) > 0 else "no_results"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取结果失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取结果失败: {str(e)}")

@app.post("/api/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """
    提交反馈接口
    提交人工验证反馈
    """
    logger.info(f"提交反馈请求: result_id={request.result_id}")

    try:
        # 验证结果存在
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM results WHERE id = ?", (request.result_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="结果不存在")

        # 插入反馈
        cursor.execute(
            "INSERT INTO feedback (result_id, accuracy_rating, feedback_text, suggested_fields) "
            "VALUES (?, ?, ?, ?)",
            (request.result_id, request.accuracy_rating, request.feedback_text,
             json.dumps(request.suggested_fields, ensure_ascii=False))
        )

        feedback_id = f"fb_{cursor.lastrowid}"
        conn.commit()
        conn.close()

        return FeedbackResponse(
            success=True,
            feedback_id=feedback_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"提交反馈失败: {e}")
        raise HTTPException(status_code=500, detail=f"提交反馈失败: {str(e)}")

@app.get("/api/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    任务状态查询接口
    获取生产任务状态
    """
    logger.info(f"查询任务状态: {task_id}")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT task_id, project_key, status, target_count, processed_count, "
            "successful_count, skipped_count, started_at, completed_at FROM tasks WHERE task_id = ?",
            (task_id,)
        )

        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="任务不存在")

        # 计算进度
        target_count = row[3] or 1
        processed_count = row[4] or 0
        progress = int((processed_count / target_count) * 100) if target_count > 0 else 0

        # 计算预计剩余时间
        estimated_remaining = "未知"
        if row[7]:  # started_at
            started_at = datetime.fromisoformat(row[7])
            if row[8]:  # completed_at
                estimated_remaining = "已完成"
            elif processed_count > 0:
                elapsed = (datetime.now() - started_at).total_seconds()
                if elapsed > 0 and processed_count > 0:
                    items_per_second = processed_count / elapsed
                    remaining_items = target_count - processed_count
                    if items_per_second > 0:
                        remaining_seconds = remaining_items / items_per_second
                        if remaining_seconds < 60:
                            estimated_remaining = f"{int(remaining_seconds)}秒"
                        elif remaining_seconds < 3600:
                            estimated_remaining = f"{int(remaining_seconds/60)}分钟"
                        else:
                            estimated_remaining = f"{int(remaining_seconds/3600)}小时"

        return TaskStatusResponse(
            task_id=row[0],
            status=row[2],
            progress=progress,
            processed=processed_count,
            successful=row[5] or 0,
            skipped=row[6] or 0,
            estimated_remaining=estimated_remaining,
            started_at=row[7] or "",
            updated_at=row[8] or datetime.now().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询任务状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询任务状态失败: {str(e)}")

@app.get("/health")
@app.get("/api/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)