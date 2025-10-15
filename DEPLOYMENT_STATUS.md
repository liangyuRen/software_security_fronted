# VulSystem 部署状态报告

## 部署时间
- **开始时间**: 2025-10-10 16:37
- **当前状态**: 部署进行中

## 已完成的配置修复

### 1. XXL-Job 配置优化
已将硬编码的 `localhost` 地址修改为支持 Docker 环境的配置:

**修改文件**:
- `backend/src/main/java/com/nju/backend/config/XxlJobConfig.java`
- `backend/src/main/resources/application.properties`
- `backend/src/main/java/com/nju/backend/service/vulnerabilityReport/util/VulnerabilityJobHandler.java`

**修改内容**:
- XXL-Job Admin 地址: `http://xxl-job-admin:8080/xxl-job-admin`
- Flask 爬虫服务地址: `http://flask-crawler:5000`
- 使用环境变量进行配置,支持灵活部署

### 2. Docker Compose 脚本更新
将 `docker-compose` 命令更新为 `docker compose` (V2版本)

**修改文件**:
- `start.sh`

## 服务架构

```
┌─────────────────────────────────────────────────┐
│           Nginx (Frontend) :80                  │
│         Vue3 前端应用                            │
└────────────┬────────────────────────────────────┘
             │
      ┌──────┴──────┬──────────┬─────────────┐
      │             │          │             │
┌─────▼─────┐ ┌────▼────┐ ┌───▼──────┐ ┌───▼────────┐
│ Backend   │ │ Flask   │ │ XXL-Job  │ │   MySQL    │
│ :8081     │ │Crawler  │ │Admin     │ │   :3306    │
│           │ │:5000    │ │:8080     │ │            │
│ Spring    │ │         │ │          │ │ kulin      │
│ Boot      │ │ Python  │ │定时调度  │ │ xxl_job    │
└───────────┘ └─────────┘ └──────────┘ └────────────┘
```

## 定时任务配置

系统包含以下三个自动爬取任务:

1. **githubVulnerabilityFetchJob**
   - 功能: 从 GitHub Advisory Database 爬取漏洞
   - 推荐 Cron: `0 0 2 * * ?` (每天2点)

2. **avdVulnerabilityFetchJob**
   - 功能: 从阿里云漏洞库爬取漏洞
   - 推荐 Cron: `0 0 3 * * ?` (每天3点)

3. **nvdVulnerabilityFetchJob**
   - 功能: 从 NVD 爬取漏洞
   - 推荐 Cron: `0 0 4 * * ?` (每天4点)

## 部署后需要执行的步骤

### 1. 等待所有容器启动完成 (约10-15分钟)

检查容器状态:
```bash
docker compose ps
```

应该看到 5 个容器都处于 `running` 状态:
- vulsystem-mysql
- vulsystem-xxl-job
- vulsystem-backend
- vulsystem-flask-crawler
- vulsystem-frontend

### 2. 验证服务可访问性

- 前端: http://120.26.147.209
- 后端: http://120.26.147.209:8081
- Flask: http://120.26.147.209:5000
- XXL-Job: http://120.26.147.209:8080/xxl-job-admin

### 3. 配置 XXL-Job 定时任务

**重要**: 请按照 `XXL-JOB-SETUP-GUIDE.md` 文档配置定时任务:

1. 访问 XXL-Job 管理界面
2. 登录 (admin / 123456)
3. 添加执行器 `vulsystem-executor`
4. 创建三个定时任务
5. 启动任务

详细步骤请参考: [XXL-JOB-SETUP-GUIDE.md](./XXL-JOB-SETUP-GUIDE.md)

### 4. 测试任务执行

登录 XXL-Job 后:
1. 手动执行一次任务
2. 查看执行日志
3. 检查数据库是否有数据更新

## 日志查看

### 查看所有服务日志
```bash
docker compose logs -f
```

### 查看特定服务日志
```bash
docker compose logs -f backend
docker compose logs -f flask-crawler
docker compose logs -f mysql
docker compose logs -f xxl-job-admin
docker compose logs -f frontend
```

### 查看本地日志文件
```bash
# 后端日志
tail -f logs/backend/*.log

# Flask 日志
tail -f logs/flask/*.log
```

## 常用管理命令

### 重启服务
```bash
# 重启所有服务
docker compose restart

# 重启单个服务
docker compose restart backend
docker compose restart flask-crawler
```

### 停止服务
```bash
# 停止所有服务(保留数据)
docker compose down

# 停止并删除数据(谨慎!)
docker compose down -v
```

### 更新代码后重新部署
```bash
# 重新构建并启动
docker compose up -d --build

# 只重新构建 backend
docker compose up -d --build backend
```

## 数据持久化

以下数据会持久化保存:

1. **MySQL 数据**: volume `vulsystem_mysql_data`
2. **上传文件**: volume `vulsystem_uploads`
3. **日志文件**: 本地 `./logs/` 目录

即使容器删除,数据也不会丢失。

## 端口映射

| 服务 | 容器端口 | 主机端口 | 用途 |
|-----|---------|---------|-----|
| Frontend | 80 | 80 | Web 界面 |
| Backend | 8081 | 8081 | REST API |
| Flask | 5000 | 5000 | 爬虫 API |
| XXL-Job | 8080 | 8080 | 任务管理 |
| MySQL | 3306 | 3306 | 数据库 |

## 安全建议

1. **修改默认密码**
   - MySQL root 密码 (已在 .env 中配置)
   - XXL-Job admin 密码 (登录后修改)

2. **限制端口访问**
   - 建议关闭 MySQL 3306 端口的外部访问
   - 配置防火墙规则

3. **配置 HTTPS**
   - 生产环境建议配置 SSL 证书
   - 使用 Nginx 反向代理

## 下一步操作

1. ✅ 等待 Docker 镜像构建完成
2. ✅ 验证所有容器正常运行
3. ⏳ 配置 XXL-Job 定时任务
4. ⏳ 测试漏洞爬取功能
5. ⏳ 配置生产环境安全策略

## 相关文档

- [部署指南](./DEPLOYMENT_GUIDE.md) - 完整部署文档
- [XXL-Job 配置指南](./XXL-JOB-SETUP-GUIDE.md) - 定时任务配置
- [接口文档](./接口文档.md) - API 接口说明
- [Docker 部署说明](./DOCKER_DEPLOYMENT.md) - Docker 相关说明

## 故障排查

如遇问题,请检查:

1. Docker 服务是否正常运行
2. 容器日志中是否有错误信息
3. 网络连通性是否正常
4. 端口是否被占用

---

**部署状态**: 进行中
**最后更新**: 2025-10-10 16:50
