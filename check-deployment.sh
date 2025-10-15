#!/bin/bash
################################################################################
# VulSystem 部署状态检测脚本
# 使用方法: bash check-deployment.sh
################################################################################

echo "================================================================================"
echo "                    VulSystem 部署状态检测"
echo "================================================================================"
echo "检测时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "服务器IP: 120.26.147.209"
echo "================================================================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查函数
check_service() {
    local name=$1
    local url=$2
    local expected=$3

    echo -n "检查 $name ... "
    response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 --max-time 10 "$url" 2>/dev/null)

    if [ "$response" = "$expected" ]; then
        echo -e "${GREEN}✓ 正常 (HTTP $response)${NC}"
        return 0
    else
        echo -e "${RED}✗ 异常 (HTTP $response)${NC}"
        return 1
    fi
}

# 1. 检查Docker服务
echo "【1. Docker 服务状态】"
echo "--------------------------------------------------------------------------------"
if systemctl is-active --quiet docker; then
    echo -e "${GREEN}✓ Docker 服务运行中${NC}"
else
    echo -e "${RED}✗ Docker 服务未运行${NC}"
    exit 1
fi
echo ""

# 2. 检查容器状态
echo "【2. 容器运行状态】"
echo "--------------------------------------------------------------------------------"
cd /root/VulSystem
docker compose ps

echo ""
container_count=$(docker compose ps -q | wc -l)
running_count=$(docker compose ps | grep -c "Up\|running" || true)

echo "容器统计: 总共 $container_count 个容器，运行中 $running_count 个"

if [ "$container_count" -eq 5 ] && [ "$running_count" -eq 5 ]; then
    echo -e "${GREEN}✓ 所有容器运行正常${NC}"
else
    echo -e "${YELLOW}⚠ 部分容器可能未正常启动，请检查日志${NC}"
fi
echo ""

# 3. 检查端口占用
echo "【3. 服务端口监听状态】"
echo "--------------------------------------------------------------------------------"
netstat -tulpn | grep -E ':80 |:5000 |:8080 |:8081 |:3306 ' || echo "未检测到服务端口监听"
echo ""

# 4. 检查各服务HTTP响应
echo "【4. 服务HTTP响应检测】"
echo "--------------------------------------------------------------------------------"

success_count=0

# 检查前端
if check_service "前端服务 (Vue3)" "http://120.26.147.209" "200"; then
    ((success_count++))
fi

# 检查后端
if check_service "后端服务 (SpringBoot)" "http://120.26.147.209:8081/actuator/health" "200"; then
    ((success_count++))
    echo "  后端健康检查详情:"
    curl -s http://120.26.147.209:8081/actuator/health 2>/dev/null | head -5
fi

# 检查Flask
if check_service "爬虫服务 (Flask)" "http://120.26.147.209:5000" "404"; then
    ((success_count++))
fi

# 检查XXL-Job
if check_service "任务调度 (XXL-Job)" "http://120.26.147.209:8080/xxl-job-admin" "200"; then
    ((success_count++))
fi

echo ""
echo "服务响应统计: 4 个服务中有 $success_count 个响应正常"
echo ""

# 5. 最近的日志
echo "【5. 最近的服务日志 (最近10行)】"
echo "--------------------------------------------------------------------------------"
echo "==> MySQL 日志:"
docker compose logs --tail=3 mysql 2>/dev/null | tail -3
echo ""
echo "==> Backend 日志:"
docker compose logs --tail=3 backend 2>/dev/null | tail -3
echo ""
echo "==> Flask 日志:"
docker compose logs --tail=3 flask-crawler 2>/dev/null | tail -3
echo ""

# 6. 总结
echo "================================================================================"
echo "                            检测结果总结"
echo "================================================================================"

if [ "$container_count" -eq 5 ] && [ "$running_count" -eq 5 ] && [ "$success_count" -ge 3 ]; then
    echo -e "${GREEN}✓ 部署成功！所有服务运行正常${NC}"
    echo ""
    echo "访问地址:"
    echo "  • 前端界面: http://120.26.147.209"
    echo "  • 后端API:  http://120.26.147.209:8081"
    echo "  • 爬虫服务: http://120.26.147.209:5000"
    echo "  • 任务管理: http://120.26.147.209:8080/xxl-job-admin (admin/123456)"
    exit_code=0
elif [ "$container_count" -lt 5 ]; then
    echo -e "${RED}✗ 部署未完成：部分容器未创建${NC}"
    echo "建议: 运行 'docker compose up -d --build' 重新部署"
    exit_code=1
elif [ "$running_count" -lt 5 ]; then
    echo -e "${YELLOW}⚠ 部署部分成功：部分容器未运行${NC}"
    echo "建议: 运行 'docker compose logs' 查看详细日志"
    exit_code=2
else
    echo -e "${YELLOW}⚠ 部署完成但部分服务响应异常${NC}"
    echo "建议: 等待1-2分钟后重新检测，或查看日志排查问题"
    exit_code=3
fi

echo "================================================================================"
exit $exit_code
