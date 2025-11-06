# 📊 VulSystem 数据库内容概览

## 数据库基本信息

| 项目 | 值 |
|------|-----|
| **数据库名** | kulin |
| **总表数** | 8 |
| **总数据行数** | 30,064 |
| **总大小** | 7.7 MB |
| **运行状态** | ✅ 正常 |

---

## 数据库架构

```
kulin (VulSystem 主数据库)
├── 用户管理
│   └── user (8条记录)
├── 项目管理
│   ├── project (24条记录)
│   ├── project_vulnerability (15条关系)
│   └── white_list (15条记录)
├── 漏洞数据
│   ├── vulnerability (15条记录)
│   ├── vulnerability_report (29,954条记录) ⭐ 主要数据
│   └── vulnerability_report_vulnerability (15条关系)
└── 公司管理
    └── company (0条记录)

xxl_job (任务调度数据库)
├── 任务配置
├── 任务执行日志
└── 用户管理
```

---

## 📋 表详细信息

### 1. **user** 表 (8条记录)

**用途:** 系统用户管理

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| user_name | varchar(255) | 用户名 |
| email | varchar(255) | 邮箱 |
| company_name | varchar(255) | 公司名称 |
| role | varchar(255) | 角色 (admin/user/manager) |
| isvip | tinyint | VIP标志 |
| isvalid | tinyint | 是否有效 |
| password | varchar(255) | 密码 |
| phone | varchar(255) | 电话 |
| team | varchar(255) | 团队 |
| confirm_code | varchar(255) | 确认码 |
| activation_time | datetime | 激活时间 |

**用户列表:**

| ID | 用户名 | 邮箱 | 公司 | 角色 | VIP | 有效 |
|----|--------|------|------|------|-----|------|
| 9 | 管理员 | admin@example.com | 默认公司 | admin | ✅ | ✅ |
| 10 | 张三 | user1@example.com | 默认公司 | user | ❌ | ✅ |
| 11 | 李四 | user2@example.com | 默认公司 | user | ❌ | ✅ |
| 12 | 王经理 | manager@example.com | 默认公司 | manager | ✅ | ✅ |
| 13 | rly | 211850116@smail.nju.edu.cn | company | user | ❌ | ❌ |
| 14 | sy | 1394281238@qq.com | company | user | ❌ | ❌ |
| 15 | admin | admin@admin.com | company | user | ❌ | ❌ |
| 16 | test | test@test.com | company | user | ❌ | ❌ |

---

### 2. **company** 表 (0条记录)

**用途:** 公司信息管理

**当前状态:** 空表 (无数据)

---

### 3. **project** 表 (24条记录)

**用途:** 漏洞分析项目管理

**表结构:**
- id: 主键
- name: 项目名称
- language: 编程语言
- description: 项目描述
- create_time: 创建时间
- component_count: 组件数量
- vulnerability_count: 漏洞数量
- risk_level: 风险等级
- analysis_status: 分析状态
- risk_threshold: 风险阈值
- file: 上传文件路径
- roadmap_file: 路线图文件
- last_analysis_time: 最后分析时间

**项目列表 (部分):**

| ID | 项目名称 | 语言 | 组件数 | 漏洞数 | 状态 |
|----|---------|------|--------|--------|------|
| 1 | 电商平台后端系统 | Java | 0 | 0 | ⏳ Pending |
| 2 | 企业日志分析系统 | Java | 0 | 0 | ⏳ Pending |
| 3 | 社交媒体API服务 | Java | 0 | 0 | ⏳ Pending |
| 4 | 网络代理服务 | C | 0 | 0 | ⏳ Pending |
| 5 | 分布式缓存系统 | Java | 0 | 0 | ⏳ Pending |
| 6 | 高性能Web服务器 | C | 0 | 0 | ⏳ Pending |
| 7 | AI智能推荐引擎 | Java | 0 | 0 | ⏳ Pending |
| 8 | 计算机视觉处理库 | C | 0 | 0 | ⏳ Pending |
| 9-24 | ... (其他项目) | Java | 0 | 0 | ⏳ Pending |

**⚠️ 注意:** 所有项目的组件数和漏洞数都是0，说明还未进行实际的依赖扫描分析。

---

### 4. **vulnerability** 表 (15条记录)

**用途:** 漏洞库 - 存储已识别的漏洞组件

**表结构:**
- id: 主键
- name: 组件名称
- language: 编程语言
- riskLevel: 风险等级 (CRITICAL/HIGH/MEDIUM/LOW)
- description: 描述
- time: 发现时间
- isaccept: 是否接受
- isdelete: 是否删除

**已知漏洞组件:**

| ID | 组件名称 | 语言 | 风险等级 | 接受 |
|----|---------|------|--------|------|
| 1 | spring-boot-starter-web | Java | HIGH | ❌ |
| 2 | mysql-connector-java | Java | MEDIUM | ❌ |
| 3 | fastjson | Java | CRITICAL | ❌ |
| 4 | log4j-core | Java | HIGH | ❌ |
| 5 | jackson-databind | Java | HIGH | ❌ |
| 6 | org.springframework | Java | HIGH | ❌ |
| 7 | com.alibaba.fastjson | Java | CRITICAL | ❌ |
| 8 | openssl | C | MEDIUM | ❌ |
| 9 | curl | C | LOW | ❌ |
| 10 | redis | Java | HIGH | ❌ |
| 11 | apache-commons | Java | HIGH | ❌ |
| 12 | nginx | C | MEDIUM | ❌ |
| 13 | tensorflow | Java | MEDIUM | ❌ |
| 14 | pytorch | Java | LOW | ❌ |
| 15 | opencv | C | HIGH | ❌ |

---

### 5. **white_list** 表 (15条记录)

**用途:** 组件白名单 - 扫描到的依赖组件存储

**表结构:**
- id: 主键
- project_id: 所属项目ID
- name: 组件名称
- version: 版本号
- language: 编程语言
- package_manager: 包管理器 (npm/pip/maven等)
- file_path: 文件路径
- description: 组件描述
- source_url: 来源URL
- created_time: 创建时间
- isdelete: 是否删除

**白名单组件示例:**

| ID | 组件名 | 版本 | 语言 | 包管理器 | 文件路径 |
|----|--------|------|------|---------|---------|
| 1 | spring-boot-starter-web | NULL | Java | NULL | /libs/spring-boot-starter-web-2.6.0.jar |
| 2 | mysql-connector-java | NULL | Java | NULL | /libs/mysql-connector-java-8.0.28.jar |
| 3 | fastjson | NULL | Java | NULL | /libs/fastjson-1.2.76.jar |
| 4 | log4j-core | NULL | Java | NULL | /libs/log4j-core-2.14.1.jar |
| 5 | jackson-databind | NULL | Java | NULL | /libs/jackson-databind-2.12.3.jar |
| ... | ... | ... | ... | ... | ... |

**⚠️ 观察:**
- 所有版本字段都是NULL (未记录版本)
- 包管理器字段都是NULL
- 这与之前分析中"版本约束丢失"的问题一致 ❌

---

### 6. **vulnerability_report** 表 (29,954条记录) ⭐

**用途:** 漏洞报告库 - 爬取的最新漏洞数据

**表结构:**
- id: 主键
- cve_id: CVE编号
- vulnerability_name: 漏洞名称
- description: 漏洞描述
- riskLevel: 风险等级
- disclosure_time: 披露时间
- referenceLink: 参考链接
- affects_whitelist: 是否影响白名单中的组件
- isdelete: 是否删除

**数据统计:**

| CVE编号 | 漏洞名 | 风险等级 | 影响白名单 |
|---------|--------|--------|----------|
| CVE-2024-1001 | spring-boot-starter-web;org.springframework | HIGH | ✅ |
| CVE-2024-1002 | mysql-connector-java | MEDIUM | ✅ |
| CVE-2024-1003 | fastjson;com.alibaba.fastjson | CRITICAL | ✅ |
| CVE-2024-1004 | log4j-core | HIGH | ✅ |
| CVE-2024-1005 | jackson-databind | HIGH | ✅ |
| ... (29,954条) | ... | ... | ... |

**数据观察:**
- 29,954条CVE记录（大部分来自XXL-Job定时爬取）
- 所有记录都标记为"影响白名单" (affects_whitelist = 1)
- 这说明漏洞库非常庞大，但与白名单的匹配可能存在问题

---

### 7. **project_vulnerability** 表 (15条关系)

**用途:** 项目与漏洞的关联表

**关联数据:**

| 项目名 | 漏洞组件 | 风险等级 |
|--------|---------|--------|
| 电商平台后端系统 | spring-boot-starter-web | HIGH |
| 电商平台后端系统 | mysql-connector-java | MEDIUM |
| 电商平台后端系统 | fastjson | CRITICAL |
| 企业日志分析系统 | log4j-core | HIGH |
| 企业日志分析系统 | jackson-databind | HIGH |
| 社交媒体API服务 | org.springframework | HIGH |
| 社交媒体API服务 | com.alibaba.fastjson | CRITICAL |
| 网络代理服务 | openssl | MEDIUM |
| 网络代理服务 | curl | LOW |
| 分布式缓存系统 | redis | HIGH |
| 分布式缓存系统 | apache-commons | HIGH |
| 高性能Web服务器 | nginx | MEDIUM |
| AI智能推荐引擎 | tensorflow | MEDIUM |
| AI智能推荐引擎 | pytorch | LOW |
| 计算机视觉处理库 | opencv | HIGH |

---

### 8. **vulnerability_report_vulnerability** 表 (15条关系)

**用途:** 漏洞报告与漏洞的关联表

**当前状态:** 与project_vulnerability结构相同，存储15条关系。

---

## 📈 数据统计概览

### 按语言分布

| 语言 | 项目数 | 漏洞组件数 | 占比 |
|------|--------|---------|------|
| Java | 20 | 11 | 73% |
| C | 3 | 4 | 27% |
| Odoo | 1 | - | - |
| **总计** | **24** | **15** | **100%** |

### 按风险等级分布

| 风险等级 | 数量 | 占比 |
|---------|------|------|
| CRITICAL | 2 | 13% |
| HIGH | 9 | 60% |
| MEDIUM | 3 | 20% |
| LOW | 1 | 7% |

### 漏洞报告统计

| 项目 | 数量 |
|------|------|
| 总CVE记录 | 29,954 |
| 风险等级分布 | 未统计 |
| 影响白名单 | 100% (29,954条) |

---

## 🔴 数据质量问题

### 1. **版本信息缺失**
```
white_list 表中所有组件的版本都是 NULL
影响: 无法进行版本级别的漏洞匹配
```

### 2. **包管理器未记录**
```
white_list 表中所有组件的 package_manager 都是 NULL
影响: 无法追踪依赖来源
```

### 3. **项目分析状态未更新**
```
所有 project 的 analysis_status 都是 'pending'
component_count 和 vulnerability_count 都是 0
影响: 项目分析流程可能未启动或有问题
```

### 4. **company 表为空**
```
company 表没有数据
影响: 公司管理功能可能无法使用
```

### 5. **许多用户未激活**
```
8个用户中，只有4个 isvalid = 1
影响: 部分用户无法使用系统
```

---

## 🎯 建议改进

### 立即改进（第一阶段）

1. **补充版本信息** 📌
   ```sql
   UPDATE white_list
   SET version = 'version_from_path'
   WHERE version IS NULL;
   ```

2. **更新包管理器信息** 📌
   ```sql
   UPDATE white_list
   SET package_manager = CASE
       WHEN language = 'Java' THEN 'maven'
       WHEN language = 'C' THEN 'system'
       ELSE 'unknown'
   END;
   ```

3. **检查项目分析流程**
   - 验证项目上传功能是否正常
   - 检查依赖扫描服务是否运行
   - 查看日志了解分析失败原因

4. **创建公司数据**
   ```sql
   INSERT INTO company (name, description)
   VALUES ('默认公司', '系统默认公司');
   ```

### 后续改进（第二、三阶段）

1. **实施漏洞与项目的关联分析**
   - 当前 project_vulnerability 只有15条关系（对应示例数据）
   - 应该与 vulnerability_report 进行自动匹配

2. **优化漏洞匹配算法**
   - 当前所有CVE都标记为影响白名单
   - 需要基于版本和包名的精确匹配

3. **实现项目的动态分析**
   - 重新上传项目文件
   - 触发依赖扫描
   - 自动匹配漏洞

---

## 💾 数据库备份

**备份位置:**
```
Docker Volume: vulsystem_mysql_data
```

**备份命令:**
```bash
docker exec vulsystem-mysql mysqldump -u root -p123456 kulin > kulin_backup.sql
```

**恢复命令:**
```bash
docker exec -i vulsystem-mysql mysql -u root -p123456 kulin < kulin_backup.sql
```

---

## 🔍 进一步查询

### 查询高风险漏洞
```sql
SELECT * FROM vulnerability
WHERE riskLevel IN ('CRITICAL', 'HIGH')
ORDER BY riskLevel DESC;
```

### 查询受影响的项目
```sql
SELECT
    p.name as project,
    COUNT(pv.id) as vulnerability_count,
    GROUP_CONCAT(v.riskLevel) as risk_levels
FROM project p
LEFT JOIN project_vulnerability pv ON p.id = pv.project_id
LEFT JOIN vulnerability v ON pv.vulnerability_id = v.id
GROUP BY p.id;
```

### 查询未被任何项目使用的漏洞组件
```sql
SELECT v.* FROM vulnerability v
LEFT JOIN project_vulnerability pv ON v.id = pv.vulnerability_id
WHERE pv.id IS NULL;
```

---

## 📊 总结

**数据现状:**
- ✅ 用户系统完整（8个用户）
- ✅ 项目管理框架完整（24个项目）
- ⚠️ 漏洞库庞大（29,954条CVE）
- ❌ 版本信息缺失
- ❌ 依赖扫描未执行
- ❌ 漏洞匹配不精确

**下一步行动:**
1. 修复数据质量问题（版本、包管理器）
2. 重新运行项目依赖扫描
3. 实施改进的漏洞匹配算法

