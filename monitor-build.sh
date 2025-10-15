#!/bin/bash
################################################################################
# VulSystem 构建进度监控脚本
################################################################################

echo "开始监控 Docker 构建进度..."
echo "监控时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "================================================================================"
echo ""

# 循环监控
MAX_WAIT=1200  # 最长等待20分钟
INTERVAL=30    # 每30秒检查一次
elapsed=0

while [ $elapsed -lt $MAX_WAIT ]; do
    echo "[$(date '+%H:%M:%S')] 检查构建状态 (已等待 $((elapsed/60)) 分钟)..."

    # 检查容器数量
    container_count=$(docker compose ps -q 2>/dev/null | wc -l)
    running_count=$(docker compose ps 2>/dev/null | grep -c "Up\|running" || echo "0")

    if [ "$container_count" -eq 0 ]; then
        echo "  状态: 构建中... (还未创建容器)"
        echo "  提示: Maven 正在下载依赖包，这个过程需要较长时间"
    elif [ "$container_count" -lt 5 ]; then
        echo "  状态: 部分容器已创建 ($container_count/5)"
        docker compose ps --format "table {{.Service}}\t{{.Status}}" 2>/dev/null
    elif [ "$running_count" -eq 5 ]; then
        echo "  ✓ 成功! 所有容器已启动 ($running_count/5)"
        echo ""
        docker compose ps
        echo ""
        echo "================================================================================"
        echo "构建完成！现在可以运行检测脚本验证部署:"
        echo "  bash /root/VulSystem/check-deployment.sh"
        echo "================================================================================"
        exit 0
    else
        echo "  状态: 所有容器已创建，等待启动完成 ($running_count/5 运行中)"
        docker compose ps --format "table {{.Service}}\t{{.Status}}" 2>/dev/null
    fi

    echo ""
    sleep $INTERVAL
    elapsed=$((elapsed + INTERVAL))
done

echo ""
echo "================================================================================"
echo "⚠ 构建超时 (超过 $((MAX_WAIT/60)) 分钟)"
echo "请检查构建日志:"
echo "  docker compose logs"
echo "================================================================================"
exit 1
