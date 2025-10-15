# VulSystem 完整部署指南

## 📋 系统架构

VulSystem 是一个完整的漏洞管理系统，包含以下组件：

```
┌─────────────────────────────────────────────────────┐
│                   用户浏览器                          │
└────────────────────┬────────────────────────────────┘
                     │ HTTP :80
         ┌───────────▼──────────────┐
         │   Vue3 Frontend (Nginx)  │
         └───────────┬──────────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
    ▼                ▼                ▼
┌────────┐    ┌──────────┐    ┌──────────┐
│Backend │    │  Flask   │    │ XXL-Job  │
│:8081   │    │Crawler   │    │Admin     │
│        │    │:5000     │    │:8080     │
└───┬────┘    └────┬─────┘    └────┬─────┘
    │              │               │
    └──────────────┴───────────────┘
                   │
            ┌──────▼──────┐
            │   MySQL     │
            │   :3306     │
            └─────────────┘
```

## 🚀 快速开始

### 前置要求

- Docker 20.10+
- Docker Compose 1.29+
- 至少 4GB 可用内存
- 至少 10GB 可用磁盘空间

### 1. 克隆项目（如已完成可跳过）

```bash
cd /root/VulSystem
```

### 2. 检查项目结构

```bash
tree -L 1
# 应该看到以下目录结构：
# ├── backend/              # SpringBoot 后端
# ├── flask-crawler/        # Flask 爬虫服务
# ├── frontend/             # Vue3 前端
# ├── docker-compose.yml    # Docker 编排文件
# ├── .env                  # 环境变量配置
# ├── xxl-job-init.sql      # XXL-Job 数据库初始化
# └── test_data_corrected.sql # VulSystem 数据库初始化
```

### 3. 配置环境变量

环境变量已经在 `.env` 文件中配置好了。**重要：在生产环境中请修改数据库密码！**

```bash
# 查看当前配置
cat .env

# 如需修改，编辑 .env 文件
vi .env
```

### 4. 启动所有服务

```bash
# 构建并启动所有服务（首次运行需要 10-15 分钟）
docker-compose up -d --build

# 查看启动日志
docker-compose logs -f

# 或者查看特定服务的日志
docker-compose logs -f backend
docker-compose logs -f flask-crawler
docker-compose logs -f frontend
```

### 5. 验证部署

等待约 2-3 分钟后，访问以下地址验证：

- **前端界面**: http://120.26.147.209 或 http://localhost
- **后端 API**: http://120.26.147.209:8081
- **Flask 爬虫**: http://120.26.147.209:5000
- **XXL-Job 管理**: http://120.26.147.209:8080/xxl-job-admin
  - 默认账号：admin
  - 默认密码：123456

### 6. 检查服务状态

```bash
# 查看所有容器状态
docker-compose ps

# 应该看到 5 个服务都在运行：
# - vulsystem-mysql
# - vulsystem-xxl-job
# - vulsystem-backend
# - vulsystem-flask-crawler
# - vulsystem-frontend
```

## 🔧 常用命令

### 服务管理

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务（保留数据）
docker-compose down

# 停止并删除所有数据（谨慎使用！）
docker-compose down -v

# 重启所有服务
docker-compose restart

# 重启单个服务
docker-compose restart backend
docker-compose restart flask-crawler
docker-compose restart frontend
```

### 日志查看

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f mysql

# 查看最近 100 行日志
docker-compose logs --tail=100 backend
```

### 重新构建

```bash
# 代码更新后重新构建
docker-compose build

# 强制重新构建（不使用缓存）
docker-compose build --no-cache

# 重新构建并启动
docker-compose up -d --build
```

## 📊 服务说明

### MySQL (3306)
- 数据库名称：kulin (VulSystem) 和 xxl_job (XXL-Job)
- 默认用户：root
- 数据持久化：vulsystem_mysql_data

### XXL-Job Admin (8080)
- 访问路径：/xxl-job-admin
- 默认账号：admin / 123456
- 执行器名称：vulsystem-executor

### SpringBoot Backend (8081)
- 健康检查：/actuator/health
- API 文档：查看项目中的 接口文档.md
- 日志位置：./logs/backend/

### Flask Crawler (5000)
- 漏洞爬取服务
- 支持 GitHub、NVD、AVD 数据源
- 日志位置：./logs/flask/

### Vue3 Frontend (80)
- 前端界面
- Nginx 反向代理
- 自动路由到后端服务

## 🔒 安全建议

### 生产环境配置

1. **修改数据库密码**
```bash
# 编辑 .env 文件
DB_PASSWORD=your_very_strong_password_here
```

2. **修改 XXL-Job 管理员密码**
   - 登录 XXL-Job: http://your-ip:8080/xxl-job-admin
   - 进入"用户管理"修改 admin 密码

3. **限制数据库外部访问**
```yaml
# 在 docker-compose.yml 中注释掉 MySQL 的 ports 部分
# ports:
#   - "3306:3306"
```

4. **配置防火墙**
```bash
# 只开放必要的端口
firewall-cmd --permanent --add-port=80/tcp
firewall-cmd --permanent --add-port=8080/tcp
firewall-cmd --reload
```

## 🐛 故障排查

### 问题 1: 容器无法启动

```bash
# 查看容器状态
docker-compose ps

# 查看详细日志
docker-compose logs <service-name>

# 检查端口占用
netstat -tulpn | grep -E '80|3306|5000|8080|8081'
```

### 问题 2: 数据库连接失败

```bash
# 检查 MySQL 健康状态
docker-compose exec mysql mysqladmin ping -uroot -p

# 进入 MySQL 容器
docker-compose exec mysql bash

# 连接数据库
mysql -uroot -p
```

### 问题 3: 前端无法访问后端

```bash
# 检查网络连通性
docker-compose exec frontend ping backend
docker-compose exec frontend ping flask-crawler

# 检查 Nginx 配置
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf
```

### 问题 4: 构建失败

```bash
# 清理 Docker 缓存
docker system prune -a

# 重新构建
docker-compose build --no-cache
```

## 📦 数据备份

### 备份数据库

```bash
# 备份 VulSystem 数据库
docker-compose exec -T mysql mysqldump -uroot -p$DB_PASSWORD kulin > backup_vulsystem_$(date +%Y%m%d).sql

# 备份 XXL-Job 数据库
docker-compose exec -T mysql mysqldump -uroot -p$DB_PASSWORD xxl_job > backup_xxljob_$(date +%Y%m%d).sql
```

### 恢复数据库

```bash
# 恢复 VulSystem 数据库
docker-compose exec -T mysql mysql -uroot -p$DB_PASSWORD kulin < backup_vulsystem.sql

# 恢复 XXL-Job 数据库
docker-compose exec -T mysql mysql -uroot -p$DB_PASSWORD xxl_job < backup_xxljob.sql
```

## 🔄 更新部署

```bash
# 1. 备份数据
./backup.sh

# 2. 拉取最新代码
git pull

# 3. 重新构建并启动
docker-compose up -d --build

# 4. 查看日志确认
docker-compose logs -f
```

## 📝 端口映射总结

| 服务 | 容器端口 | 主机端口 | 说明 |
|------|---------|---------|------|
| Frontend | 80 | 80 | Vue3 前端界面 |
| Backend | 8081 | 8081 | SpringBoot API |
| Flask Crawler | 5000 | 5000 | 爬虫服务 API |
| XXL-Job Admin | 8080 | 8080 | 任务调度管理 |
| MySQL | 3306 | 3306 | 数据库（可关闭外部访问） |

## 🌐 公网访问配置

当前配置支持通过公网 IP 访问：
- 前端：http://120.26.147.209
- 确保云服务器安全组/防火墙开放了 80、8080、8081、5000 端口

如需配置域名和 HTTPS，请参考后续的 HTTPS 配置指南。

## 💡 提示

1. 首次启动需要构建镜像，耗时较长（10-15分钟）
2. 后端服务依赖数据库，会等待数据库健康检查通过
3. 日志文件会保存在 `./logs/` 目录下
4. 数据持久化在 Docker volumes 中，删除容器不会丢失数据
5. 使用 `docker-compose down -v` 会删除所有数据，请谨慎操作

## 📞 技术支持

如遇到问题：
1. 查看日志：`docker-compose logs -f`
2. 检查容器状态：`docker-compose ps`
3. 查看网络：`docker network ls`
4. 提交 Issue 到 GitHub

---

**部署时间**: 2025-10-10
**维护者**: VulSystem Team
**服务器 IP**: 120.26.147.209
