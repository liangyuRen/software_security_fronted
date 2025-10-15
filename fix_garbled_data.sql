-- 修复数据库中已存在的乱码数据
-- 这个脚本会将错误编码的数据转换回正确的UTF-8

USE kulin;

-- 首先备份数据(可选)
-- CREATE TABLE vulnerability_backup AS SELECT * FROM vulnerability;
-- CREATE TABLE vulnerability_report_backup AS SELECT * FROM vulnerability_report;

-- 修复vulnerability表中的乱码数据
-- 原理: 数据以UTF-8存储,但被当作Latin1读取,导致乱码
-- 我们需要先将其转换回原始字节,再正确解释为UTF-8

UPDATE vulnerability
SET description = CONVERT(CAST(CONVERT(description USING latin1) AS BINARY) USING utf8mb4)
WHERE description LIKE '%æ%' OR description LIKE '%å%' OR description LIKE '%è%';

UPDATE vulnerability
SET name = CONVERT(CAST(CONVERT(name USING latin1) AS BINARY) USING utf8mb4)
WHERE name LIKE '%æ%' OR name LIKE '%å%' OR name LIKE '%è%';

-- 修复vulnerability_report表中的乱码数据
UPDATE vulnerability_report
SET description = CONVERT(CAST(CONVERT(description USING latin1) AS BINARY) USING utf8mb4)
WHERE description LIKE '%æ%' OR description LIKE '%å%' OR description LIKE '%è%';

UPDATE vulnerability_report
SET vulnerability_name = CONVERT(CAST(CONVERT(vulnerability_name USING latin1) AS BINARY) USING utf8mb4)
WHERE vulnerability_name LIKE '%æ%' OR vulnerability_name LIKE '%å%' OR vulnerability_name LIKE '%è%';

-- 验证修复结果
SELECT 'Fixed vulnerability records:' as info;
SELECT id, name, SUBSTRING(description, 1, 100) as description
FROM vulnerability
WHERE name IN ('redis', 'spring-boot-starter-web', 'mysql-connector-java')
LIMIT 5;

SELECT 'Fixed vulnerability_report records:' as info;
SELECT id, cve_id, SUBSTRING(description, 1, 100) as description
FROM vulnerability_report
LIMIT 5;
