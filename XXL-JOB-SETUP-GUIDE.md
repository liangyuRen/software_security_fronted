# XXL-Job 定时任务配置指南

## 概述

VulSystem 使用 XXL-Job 来实现漏洞数据的自动爬取功能。系统已经定义了三个定时任务处理器(Job Handler),需要在 XXL-Job 管理界面中手动配置对应的定时任务。

## 定时任务说明

系统已实现以下三个定时任务:

### 1. **githubVulnerabilityFetchJob** - GitHub 漏洞爬取
- **功能**: 从 GitHub Advisory Database 爬取最新漏洞数据
- **Handler名称**: `githubVulnerabilityFetchJob`
- **推荐执行周期**: 每天执行一次
- **Cron表达式**: `0 0 2 * * ?` (每天凌晨2点执行)

### 2. **avdVulnerabilityFetchJob** - 阿里云漏洞库爬取
- **功能**: 从阿里云漏洞库(AVD)爬取漏洞数据
- **Handler名称**: `avdVulnerabilityFetchJob`
- **推荐执行周期**: 每天执行一次
- **Cron表达式**: `0 0 3 * * ?` (每天凌晨3点执行)

### 3. **nvdVulnerabilityFetchJob** - NVD 国家漏洞库爬取
- **功能**: 从 NVD (National Vulnerability Database) 爬取漏洞数据
- **Handler名称**: `nvdVulnerabilityFetchJob`
- **推荐执行周期**: 每天执行一次
- **Cron表达式**: `0 0 4 * * ?` (每天凌晨4点执行)

## 配置步骤

### 第一步: 访问 XXL-Job 管理界面

1. 打开浏览器访问: **http://120.26.147.209:8080/xxl-job-admin**
2. 使用默认账号登录:
   - 账号: `admin`
   - 密码: `123456`

### 第二步: 配置执行器

1. 点击左侧菜单 **"执行器管理"**
2. 检查是否已存在名为 `vulsystem-executor` 的执行器
3. 如果不存在,点击 **"新增执行器"** 按钮:
   - **AppName**: `vulsystem-executor`
   - **名称**: `VulSystem漏洞检测执行器`
   - **注册方式**: 自动注册
   - **机器地址**: (留空,自动注册)
   - **执行器描述**: `VulSystem后端服务的任务执行器`
   - 点击保存

### 第三步: 添加定时任务

#### 1. 添加 GitHub 漏洞爬取任务

点击 **"任务管理"** > **"新增"**,填写以下信息:

```
执行器: vulsystem-executor
任务描述: GitHub漏洞数据爬取任务
路由策略: 第一个
Cron: 0 0 2 * * ?
运行模式: BEAN
JobHandler: githubVulnerabilityFetchJob
阻塞处理策略: 单机串行
任务超时时间: 1800 (秒,30分钟)
失败重试次数: 2
负责人: admin
报警邮件: (可选)
子任务ID: (留空)
任务参数: (留空)
```

#### 2. 添加 AVD 漏洞爬取任务

同样点击 **"新增"**:

```
执行器: vulsystem-executor
任务描述: 阿里云漏洞库数据爬取任务
路由策略: 第一个
Cron: 0 0 3 * * ?
运行模式: BEAN
JobHandler: avdVulnerabilityFetchJob
阻塞处理策略: 单机串行
任务超时时间: 1800
失败重试次数: 2
负责人: admin
报警邮件: (可选)
子任务ID: (留空)
任务参数: (留空)
```

#### 3. 添加 NVD 漏洞爬取任务

继续点击 **"新增"**:

```
执行器: vulsystem-executor
任务描述: NVD国家漏洞库数据爬取任务
路由策略: 第一个
Cron: 0 0 4 * * ?
运行模式: BEAN
JobHandler: nvdVulnerabilityFetchJob
阻塞处理策略: 单机串行
任务超时时间: 1800
失败重试次数: 2
负责人: admin
报警邮件: (可选)
子任务ID: (留空)
任务参数: (留空)
```

### 第四步: 启动任务

1. 在任务管理列表中,找到刚才创建的三个任务
2. 点击每个任务右侧的 **"启动"** 按钮
3. 确认任务状态变为 **"运行中"**

### 第五步: 测试任务执行

建议先手动触发一次任务进行测试:

1. 点击任务右侧的 **"执行一次"** 按钮
2. 点击 **"日志"** 查看执行结果
3. 检查是否成功调用 Flask 爬虫服务
4. 检查数据库中是否有新的漏洞数据

## Cron 表达式说明

Cron 表达式格式: `秒 分 时 日 月 周`

常用示例:
- `0 0 2 * * ?` - 每天凌晨2点执行
- `0 */30 * * * ?` - 每30分钟执行一次
- `0 0 */6 * * ?` - 每6小时执行一次
- `0 0 2 * * MON` - 每周一凌晨2点执行

## 任务工作流程

```
┌─────────────┐
│  XXL-Job    │
│  定时触发    │
└──────┬──────┘
       │
       ├─ githubVulnerabilityFetchJob
       │  └─→ 调用 Flask: /vulnerabilities/github
       │      └─→ 解析数据 → 检测匹配 → 存入数据库
       │
       ├─ avdVulnerabilityFetchJob
       │  └─→ 调用 Flask: /vulnerabilities/avd
       │      └─→ 解析数据 → 检测匹配 → 存入数据库
       │
       └─ nvdVulnerabilityFetchJob
          └─→ 调用 Flask: /vulnerabilities/nvd
              └─→ 解析数据 → 检测匹配 → 存入数据库
```

## 监控和维护

### 查看任务执行日志

1. 进入 XXL-Job 管理界面
2. 点击任务右侧的 **"日志"** 按钮
3. 查看任务执行记录和详细日志

### 查看后端日志

```bash
# 查看后端容器日志
docker compose logs -f backend

# 查看 XXL-Job 执行日志
docker compose exec backend cat logs/xxl-job/jobhandler/*.log
```

### 查看 Flask 爬虫日志

```bash
# 查看 Flask 容器日志
docker compose logs -f flask-crawler

# 查看本地日志文件
cat logs/flask/app.log
```

### 常见问题

#### 1. 执行器未注册

**现象**: 任务管理界面显示执行器离线

**解决方法**:
```bash
# 检查 backend 容器是否正常运行
docker compose ps backend

# 查看 backend 日志,确认 XXL-Job 连接状态
docker compose logs backend | grep xxl
```

#### 2. 任务执行失败

**现象**: 任务日志显示失败或超时

**排查步骤**:
1. 检查 Flask 服务是否正常: `docker compose ps flask-crawler`
2. 检查网络连通性: `docker compose exec backend ping flask-crawler`
3. 手动测试 Flask API: `curl http://120.26.147.209:5000/vulnerabilities/test`

#### 3. 数据未同步

**现象**: 任务执行成功但数据库无数据

**排查步骤**:
1. 查看任务日志,确认是否有数据返回
2. 检查数据库表: `vulnerability_report`、`vulnerability`
3. 检查 Flask API 返回的数据格式是否正确

## 高级配置

### 调整任务执行频率

如果需要更频繁地爬取漏洞数据,可以修改 Cron 表达式:

- **每小时执行**: `0 0 * * * ?`
- **每4小时执行**: `0 0 */4 * * ?`
- **每天多次执行**: 创建多个任务,设置不同的时间点

### 配置报警通知

1. 在 XXL-Job 管理界面配置邮件服务器 (application.properties)
2. 在任务配置中填写报警邮件地址
3. 设置失败重试次数和报警阈值

### 性能优化

- 如果爬取数据量大,可以增加任务超时时间
- 可以根据实际情况调整失败重试次数
- 建议错开不同任务的执行时间,避免资源冲突

## 安全建议

1. **修改默认密码**: 登录后立即修改 admin 账户密码
2. **访问限制**: 配置防火墙,限制只有内网可以访问 8080 端口
3. **日志监控**: 定期检查任务执行日志,及时发现异常

## 相关文档

- XXL-Job 官方文档: https://www.xuxueli.com/xxl-job/
- VulSystem 部署指南: [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
- API 接口文档: [接口文档.md](./接口文档.md)

---

**配置时间**: 2025-10-10
**维护者**: VulSystem Team
