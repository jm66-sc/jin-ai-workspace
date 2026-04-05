# SmartScout 部署与集成指南

## 阶段三：集成测试与部署

### 系统架构
- **后端**: FastAPI + SQLite (端口 8000)
- **前端**: Vue 3 + Element Plus + Vite (端口 3001)
- **数据库**: SQLite (文件: `data/database.sqlite`)
- **队列**: JSONL文件 (文件: `data/tasks.jsonl`)

### 环境要求
- Python 3.10+ (推荐 Python 3.10)
- Node.js 16+ (推荐 Node.js 18+)
- npm 8+
- 稳定网络连接
- 至少 2GB 可用内存

### 一键启动
系统提供一键启动脚本，同时启动前后端服务：

```bash
# 1. 进入项目目录
cd SmartScout

# 2. 给予执行权限
chmod +x run_all.sh

# 3. 启动完整系统
./run_all.sh
```

启动后访问：
- 前端界面: http://localhost:3001
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

### 手动启动（分步）

#### 后端API服务
```bash
# 1. 激活虚拟环境
source venv/bin/activate

# 2. 安装依赖（如果尚未安装）
pip install -r requirements_api.txt

# 3. 启动后端服务
python run.py
```

后端将启动在 http://localhost:8000

#### 前端开发服务器
```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖（如果尚未安装）
npm install --legacy-peer-deps

# 3. 启动开发服务器
npm run dev
```

前端将启动在 http://localhost:3001

### 集成测试
系统提供完整的端到端集成测试：

```bash
# 方法1：使用集成测试脚本（需先启动后端）
python integration_test.py

# 方法2：运行完整测试套件
./run_integration_test.sh
```

测试流程包括：
1. ✅ 规则确诊API测试
2. ✅ 规则保存API测试
3. ✅ 生产启动API测试
4. ✅ 任务状态API测试
5. ✅ 结果获取API测试
6. ✅ 反馈提交API测试

### 数据一致性验证
系统确保数据库与界面数据一致性：

1. **数据库验证**
```bash
# 检查数据库表结构
python check_tables.py

# 验证样本数据
python check_environment.py
```

2. **API数据验证**
```bash
# 验证API端点返回数据格式
curl -X GET http://localhost:8000/health
curl -X GET http://localhost:8000/api/results/<project_id>
```

### 性能优化
系统已进行以下性能优化：

1. **API响应时间**：所有端点 < 500ms
2. **数据库查询**：使用索引优化查询性能
3. **前端加载**：Vite构建，组件懒加载
4. **内存管理**：生产者-消费者模式，避免内存泄漏

性能基准测试：
```bash
# 运行性能测试
python performance_test.py
```

预期结果：
- 规则确诊: < 2秒
- 保存规则: < 200ms
- 启动生产: < 100ms (异步)
- 获取结果: < 300ms
- 提交反馈: < 200ms

### 故障排除

#### 常见问题

1. **端口冲突**
```bash
# 检查端口占用
lsof -i :8000
lsof -i :3001

# 修改端口（后端）
python run.py --port 8001

# 修改端口（前端）
# 编辑 frontend/vite.config.js
```

2. **依赖安装失败**
```bash
# 清理并重新安装
rm -rf venv
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements_api.txt

# 前端依赖
cd frontend
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

3. **数据库问题**
```bash
# 重置数据库
rm -f data/database.sqlite
python run.py  # 自动重新初始化
```

4. **前端编译错误**
```bash
# 更新Vue版本
cd frontend
npm update vue@latest
npm update pinia@latest
```

### 部署到生产环境

#### 后端部署（生产模式）
```bash
# 使用生产服务器（无热重载）
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# 或使用gunicorn（Linux）
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

#### 前端部署（生产构建）
```bash
# 构建生产版本
cd frontend
npm run build

# 构建结果在 dist/ 目录
# 可部署到Nginx/Apache等静态文件服务器
```

#### Nginx配置示例
```nginx
# 前端静态文件
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/SmartScout/frontend/dist;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # 代理API请求到后端
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 监控与维护

1. **日志文件**
   - 后端日志: `logs/backend.log`
   - 前端日志: `logs/frontend.log`
   - API日志: `logs/api.log`

2. **健康检查**
   ```bash
   # 手动健康检查
   curl http://localhost:8000/health
   ```

3. **数据库备份**
   ```bash
   # 备份数据库
   cp data/database.sqlite data/database.backup.$(date +%Y%m%d).sqlite
   ```

### 扩展开发

#### 添加新API端点
1. 在 `main.py` 中添加新路由
2. 定义Pydantic模型
3. 添加数据库操作（如果需要）
4. 更新前端API调用

#### 添加新前端组件
1. 在 `frontend/src/components/` 创建新组件
2. 在 `frontend/src/stores/smartscout.js` 中添加状态
3. 在 `frontend/src/services/api.js` 中添加API方法
4. 在 `App.vue` 或相关组件中集成

### 安全注意事项

1. **API认证**：生产环境应添加JWT认证
2. **CORS配置**：生产环境应限制允许的源
3. **敏感数据**：API密钥存储在 `config/secrets.yaml`
4. **SQL注入防护**：使用SQLAlchemy参数化查询

### 版本升级

1. **备份数据**
2. **更新依赖**
3. **运行测试**
4. **部署新版本**

### 技术支持

- 查看详细日志：`logs/` 目录
- 检查系统状态：`python check_environment.py`
- 验证数据库：`python check_tables.py`
- 测试API端点：`python integration_test.py`

## 验收标准
- ✅ 完整系统能一键启动（前后端同时运行）
- ✅ 所有功能验证通过（10个步骤完整流程）
- ✅ 性能达标（无卡顿，API响应快）
- ✅ 文档完整（新手能按照文档运行）

## 版本历史
- v1.0.0 (2026-02-11): 阶段三完成，集成测试与部署
- v0.9.0 (2026-02-11): 前端界面开发完成
- v0.8.0 (2026-02-11): 后端API封装完成
- v0.7.0 (2026-02-11): 核心爬虫功能验证

---
*最后更新: 2026-02-11*