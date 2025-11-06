#!/bin/bash

# 部署进度检查脚本

echo "======================================"
echo "  VulSystem 部署进度检查"
echo "======================================"
echo ""

# 检查镜像构建状态
echo "[1/3] 镜像构建状态:"
echo "-----------------------------------"
IMAGES=$(docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" | grep -E "vulsystem|mysql|xxl-job|nginx|python|node")

if echo "$IMAGES" | grep -q "vulsystem-backend"; then
    echo "✅ Backend 镜像: 已构建"
else
    echo "⏳ Backend 镜像: 构建中..."
fi

if echo "$IMAGES" | grep -q "vulsystem-flask"; then
    echo "✅ Flask 镜像: 已构建"
else
    echo "⏳ Flask 镜像: 构建中..."
fi

if echo "$IMAGES" | grep -q "vulsystem-frontend"; then
    echo "✅ Frontend 镜像: 已构建"
else
    echo "⏳ Frontend 镜像: 构建中..."
fi

if echo "$IMAGES" | grep -q "mysql"; then
    echo "✅ MySQL 镜像: 已就绪"
else
    echo "⏳ MySQL 镜像: 下载中..."
fi

if echo "$IMAGES" | grep -q "xxl-job"; then
    echo "✅ XXL-Job 镜像: 已就绪"
else
    echo "⏳ XXL-Job 镜像: 下载中..."
fi

echo ""

# 检查容器状态
echo "[2/3] 容器运行状态:"
echo "-----------------------------------"
CONTAINERS=$(docker compose ps -a 2>/dev/null)

if [ -z "$CONTAINERS" ] || [ "$(echo "$CONTAINERS" | wc -l)" -le 2 ]; then
    echo "⏳ 容器尚未创建，镜像构建中..."
    PROGRESS="20%"
else
    RUNNING=$(docker compose ps --filter "status=running" 2>/dev/null | grep -v "NAME" | wc -l)
    TOTAL=5

    echo "运行中的容器: $RUNNING / $TOTAL"

    docker compose ps 2>/dev/null | grep -v "NAME" | while read line; do
        if echo "$line" | grep -q "running"; then
            echo "  ✅ $(echo $line | awk '{print $4}')"
        else
            echo "  ⏳ $(echo $line | awk '{print $4}')"
        fi
    done

    PROGRESS=$((RUNNING * 100 / TOTAL))
    PROGRESS="${PROGRESS}%"
fi

echo ""

# 检查构建进程
echo "[3/3] 构建进程:"
echo "-----------------------------------"
BUILD_PROCESS=$(ps aux | grep "docker compose up" | grep -v grep | wc -l)
if [ "$BUILD_PROCESS" -gt 0 ]; then
    echo "🔨 Docker Compose 正在运行 ($BUILD_PROCESS 个进程)"
    echo "⏳ 预计还需要 5-10 分钟..."
else
    echo "✅ 构建进程已完成"
fi

echo ""
echo "======================================"
echo "  总体进度: $PROGRESS"
echo "======================================"
echo ""

# 如果所有容器都在运行，显示访问信息
if [ "$RUNNING" -eq 5 ] 2>/dev/null; then
    echo "🎉 部署完成！"
    echo ""
    echo "访问地址:"
    echo "  - 前端界面: http://120.26.147.209"
    echo "  - 后端 API: http://120.26.147.209:8081"
    echo "  - Flask 爬虫: http://120.26.147.209:5000"
    echo "  - XXL-Job: http://120.26.147.209:8080/xxl-job-admin"
    echo ""
    echo "下一步: 配置 XXL-Job 定时任务"
    echo "请查看: XXL-JOB-SETUP-GUIDE.md"
else
    echo "💡 提示: 再次运行此脚本查看最新进度"
    echo "   ./check_deployment.sh"
fi
echo ""
