# VulSystem 数据库配置总结

## 📊 数据库连接配置

### 当前状态：✅ 已正确配置为使用Docker内部MySQL服务

---

## 1️⃣ MySQL服务配置

**容器名称**: `vulsystem-mysql`
**内部主机名**: `mysql` (Docker网络内)
**外部访问端口**: `3306`
**数据库**:
- `kulin` - VulSystem主数据库
- `xxl_job` - XXL-Job任务调度数据库

**认证信息**:
- 用户名: `root`
- 密码: `VulSystem2025!Secure` (来自.env文件的DB_PASSWORD)

---

## 2️⃣ XXL-Job配置

**配置文件**: `docker-compose.yml` (第60行)

**数据库连接URL**:
```
jdbc:mysql://mysql:3306/xxl_job?useUnicode=true&characterEncoding=UTF-8&autoReconnect=true&serverTimezone=Asia/Shanghai
```

**环境变量**:
- `spring.datasource.url`: `jdbc:mysql://mysql:3306/xxl_job`
- `spring.datasource.username`: `${DB_USERNAME:-root}` → `root`
- `spring.datasource.password`: `${DB_PASSWORD:-changeme}` → `VulSystem2025!Secure`

**状态**: ✅ 已正确配置，使用Docker内部网络名称 `mysql`

---

## 3️⃣ Backend (Spring Boot) 配置

**配置文件**: `backend/src/main/resources/application.properties`

### 修改内容：

**修改前**:
```properties
spring.datasource.password=${DB_PASSWORD:15256785749rly}  # ❌ 错误的硬编码密码
spring.datasource.url=jdbc:mysql://${DB_HOST:localhost}:... # ❌ 默认localhost
```

**修改后**:
```properties
spring.datasource.password=${DB_PASSWORD:changeme}          # ✅ 使用环境变量
spring.datasource.url=jdbc:mysql://${DB_HOST:mysql}:...     # ✅ 默认Docker主机名
```

**环境变量映射** (通过docker-compose.yml传递):
- `DB_HOST`: `mysql` (Docker内部主机名)
- `DB_PORT`: `3306`
- `DB_NAME`: `kulin`
- `DB_USERNAME`: `root`
- `DB_PASSWORD`: `VulSystem2025!Secure`

**完整连接URL**:
```
jdbc:mysql://mysql:3306/kulin?serverTimezone=Asia/Shanghai&useUnicode=true&characterEncoding=utf-8&useSSL=false&allowPublicKeyRetrieval=true
```

**状态**: ✅ 已修复，现在正确使用Docker服务名

---

## 4️⃣ 数据库访问方式

### 从宿主机访问（外部）:
```bash
mysql -h 120.26.147.209 -P 3306 -uroot -p'VulSystem2025!Secure'
```

### 从Docker容器内访问:
```bash
# 使用便捷脚本
./mysql-query.sh kulin "SHOW TABLES;"

# 或直接使用docker exec
docker exec vulsystem-mysql bash -c 'mysql -uroot -p${MYSQL_ROOT_PASSWORD} kulin'
```

### 从其他容器访问:
```properties
jdbc:mysql://mysql:3306/kulin  # 使用服务名 'mysql'
```

---

## 5️⃣ 网络架构

```
┌─────────────────────────────────────────────┐
│         vulsystem-network (Docker Bridge)   │
│                                             │
│  ┌─────────┐      ┌──────────┐            │
│  │ backend │─────>│  mysql   │            │
│  │  :8081  │      │  :3306   │            │
│  └─────────┘      └──────────┘            │
│       │                 ▲                  │
│       │                 │                  │
│  ┌─────────┐           │                  │
│  │xxl-job  │───────────┘                  │
│  │  :8080  │                              │
│  └─────────┘                              │
│                                             │
└─────────────────────────────────────────────┘
         │
         │ Port Mapping
         ▼
    外部访问 :3306
```

---

## 6️⃣ 环境变量 (.env文件)

```bash
# 数据库配置
DB_NAME=kulin
DB_USERNAME=root
DB_PASSWORD=VulSystem2025!Secure
DB_PORT_EXTERNAL=3306

# XXL-Job配置
XXL_JOB_PORT=8080
```

---

## ✅ 配置验证清单

- [x] MySQL容器正常运行
- [x] xxl_job数据库已初始化
- [x] XXL-Job使用正确的数据库连接URL (`mysql:3306`)
- [x] Backend配置使用环境变量
- [x] Backend默认主机名改为 `mysql`
- [x] 所有服务在同一Docker网络内
- [x] 密码统一使用环境变量管理

---

## 🔧 下次启动服务

由于配置已修改，需要重新构建backend服务：

```bash
cd /root/VulSystem

# 重新构建backend
docker compose build backend

# 启动所有服务
docker compose up -d

# 查看服务状态
docker compose ps

# 查看backend日志
docker compose logs backend -f
```

---

## 📝 注意事项

1. **密码安全**: 当前密码在.env文件中，建议生产环境使用更安全的密钥管理方案
2. **数据持久化**: MySQL数据存储在Docker volume `vulsystem_mysql_data` 中
3. **首次启动**: Backend启动时会自动创建kulin数据库的表结构
4. **连接测试**: 可使用 `./mysql-query.sh` 脚本快速查询数据库

---

生成时间: 2025-10-10 19:19
修改者: Claude Code Assistant
