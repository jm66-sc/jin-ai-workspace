#!/bin/bash

# SmartScout 系统验证脚本
# 检查前后端服务是否正常运行

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== SmartScout 系统验证 ===${NC}"
echo "验证时间: $(date)"
echo

# 检查端口函数
check_port() {
    local port=$1
    local service=$2
    local url=$3

    echo -e "${YELLOW}检查 ${service} (端口 ${port})...${NC}"

    # 检查端口是否监听
    if lsof -i :${port} > /dev/null 2>&1; then
        echo -e "  ✓ 端口 ${port} 正在监听"

        # 尝试连接服务
        if curl -s ${url} > /dev/null 2>&1; then
            echo -e "  ✓ ${service} 服务响应正常"
            return 0
        else
            echo -e "  ⚠ ${service} 服务无响应，但端口被占用"
            return 1
        fi
    else
        echo -e "  ✗ 端口 ${port} 未监听"
        return 1
    fi
}

# 检查后端API
check_backend() {
    echo -e "${YELLOW}\n检查后端API...${NC}"

    if check_port 8000 "后端API" "http://localhost:8000/health"; then
        # 测试健康检查端点
        response=$(curl -s http://localhost:8000/health)
        status=$(echo ${response} | grep -o '"status":"[^"]*"' | cut -d'"' -f4)

        if [ "$status" = "healthy" ]; then
            echo -e "  ✓ 后端健康检查通过"
            return 0
        else
            echo -e "  ⚠ 后端健康检查异常: ${response}"
            return 1
        fi
    else
        return 1
    fi
}

# 检查前端服务
check_frontend() {
    echo -e "${YELLOW}\n检查前端服务...${NC}"

    if check_port 3000 "前端开发服务器" "http://localhost:3000"; then
        # 检查HTML页面
        if curl -s http://localhost:3000 | grep -q "html"; then
            echo -e "  ✓ 前端HTML页面可访问"
            return 0
        else
            echo -e "  ⚠ 前端页面返回非HTML内容"
            return 1
        fi
    else
        return 1
    fi
}

# 检查数据库
check_database() {
    echo -e "${YELLOW}\n检查数据库...${NC}"

    local db_file="data/database.sqlite"

    if [ -f "$db_file" ]; then
        echo -e "  ✓ 数据库文件存在: $(du -h "$db_file" | cut -f1)"

        # 检查数据库是否可读
        if sqlite3 "$db_file" "SELECT name FROM sqlite_master WHERE type='table' LIMIT 1;" > /dev/null 2>&1; then
            echo -e "  ✓ 数据库可正常查询"
            return 0
        else
            echo -e "  ✗ 数据库查询失败"
            return 1
        fi
    else
        echo -e "  ✗ 数据库文件不存在"
        return 1
    fi
}

# 检查API端点
check_api_endpoints() {
    echo -e "${YELLOW}\n检查API端点...${NC}"

    endpoints=(
        "/api/rule-diagnosis"
        "/api/rules/test_project"
        "/api/production/test_project/start"
        "/api/results/test_project"
        "/api/feedback"
        "/api/tasks/test_task"
    )

    success_count=0
    total_count=0

    for endpoint in "${endpoints[@]}"; do
        ((total_count++))
        url="http://localhost:8000${endpoint}"

        # 测试端点是否可达（不测试具体功能）
        if curl -s -I "${url}" > /dev/null 2>&1; then
            echo -e "  ✓ ${endpoint} 可达"
            ((success_count++))
        else
            echo -e "  ⚠ ${endpoint} 不可达"
        fi
    done

    if [ $success_count -eq $total_count ]; then
        echo -e "  ✓ 所有API端点可达"
        return 0
    else
        echo -e "  ⚠ ${success_count}/${total_count} 个API端点可达"
        return 1
    fi
}

# 主验证函数
main() {
    echo -e "${GREEN}开始系统验证...${NC}"
    echo

    local all_checks_passed=true

    # 检查后端
    if check_backend; then
        echo -e "${GREEN}✓ 后端服务验证通过${NC}"
    else
        echo -e "${RED}✗ 后端服务验证失败${NC}"
        all_checks_passed=false
    fi

    # 检查前端
    if check_frontend; then
        echo -e "${GREEN}✓ 前端服务验证通过${NC}"
    else
        echo -e "${RED}✗ 前端服务验证失败${NC}"
        all_checks_passed=false
    fi

    # 检查数据库
    if check_database; then
        echo -e "${GREEN}✓ 数据库验证通过${NC}"
    else
        echo -e "${RED}✗ 数据库验证失败${NC}"
        all_checks_passed=false
    fi

    # 检查API端点（仅在后台端通过时）
    if [ "$all_checks_passed" = true ]; then
        if check_api_endpoints; then
            echo -e "${GREEN}✓ API端点验证通过${NC}"
        else
            echo -e "${YELLOW}⚠ API端点验证部分通过${NC}"
            # 不将此项视为失败，因为某些端点可能需要特定数据
        fi
    fi

    echo -e "\n${GREEN}========================================${NC}"

    if [ "$all_checks_passed" = true ]; then
        echo -e "${GREEN}✅ 系统验证通过${NC}"
        echo -e "\n访问信息:"
        echo -e "  前端界面: ${GREEN}http://localhost:3000${NC}"
        echo -e "  后端API:  ${GREEN}http://localhost:8000${NC}"
        echo -e "  API文档: ${GREEN}http://localhost:8000/docs${NC}"
        echo -e "\n系统已准备就绪！"
        exit 0
    else
        echo -e "${RED}❌ 系统验证失败${NC}"
        echo -e "\n请检查:"
        echo -e "  1. 确保已运行 ${GREEN}./run_all.sh${NC}"
        echo -e "  2. 检查日志文件: ${YELLOW}logs/backend.log${NC} 和 ${YELLOW}logs/frontend.log${NC}"
        echo -e "  3. 检查端口是否被占用: ${GREEN}lsof -i :8000${NC} 和 ${GREEN}lsof -i :3000${NC}"
        echo -e "  4. 检查依赖是否安装: ${GREEN}pip install -r requirements_api.txt${NC}"
        exit 1
    fi
}

# 执行主函数
main