#!/bin/bash

# VulSystem 启动脚本
# ==========================================

set -e

echo "======================================"
echo "  VulSystem Docker 部署启动脚本"
echo "======================================"
echo ""

# 检查 Docker 和 Docker Compose
echo "[1/5] 检查 Docker 环境..."
if ! command -v docker &> /dev/null; then
    echo "❌ 错误：Docker 未安装"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ 错误：Docker 服务未运行"
    exit 1
fi

echo "✅ Docker 环境正常"
echo ""

# 检查环境变量文件
echo "[2/5] 检查环境配置..."
if [ ! -f ".env" ]; then
    echo "❌ 错误：.env 文件不存在"
    echo "   请创建 .env 文件或从 .env.example 复制"
    exit 1
fi
echo "✅ 环境配置正常"
echo ""

# 创建日志目录
echo "[3/5] 创建日志目录..."
mkdir -p logs/backend logs/flask
echo "✅ 日志目录创建完成"
echo ""

# 停止旧容器（如果存在）
echo "[4/5] 停止旧容器（如果存在）..."
docker compose down 2>/dev/null || true
echo "✅ 旧容器已停止"
echo ""

# 启动所有服务
echo "[5/5] 启动所有服务..."
echo "   这可能需要 10-15 分钟（首次构建）..."
docker compose up -d --build

echo ""
echo "======================================"
echo "  部署完成！"
echo "======================================"
echo ""
echo "服务启动中，请等待 2-3 分钟..."
echo ""
echo "访问地址："
echo "  - 前端界面: http://120.26.147.209"
echo "  - 后端 API: http://120.26.147.209:8081"
echo "  - Flask 爬虫: http://120.26.147.209:5000"
echo "  - XXL-Job: http://120.26.147.209:8080/xxl-job-admin"
echo "    (默认账号: admin / 密码: 123456)"
echo ""
echo "查看日志："
echo "  docker compose logs -f"
echo ""
echo "查看服务状态："
echo "  docker compose ps"
echo ""
