-- 检查数据库和表的字符集
USE kulin;

-- 检查数据库字符集
SHOW CREATE DATABASE kulin;

-- 检查vulnerability表的字符集
SHOW CREATE TABLE vulnerability;

-- 检查vulnerability_report表的字符集
SHOW CREATE TABLE vulnerability_report;

-- 查看vulnerability表中一些数据示例(使用HEX查看原始字节)
SELECT id, name,
       HEX(SUBSTRING(description, 1, 10)) as description_hex,
       SUBSTRING(description, 1, 50) as description_text
FROM vulnerability
WHERE name = 'redis'
LIMIT 1;

-- 查看表字段的字符集
SELECT TABLE_NAME, COLUMN_NAME, CHARACTER_SET_NAME, COLLATION_NAME
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'kulin'
  AND TABLE_NAME IN ('vulnerability', 'vulnerability_report')
  AND DATA_TYPE IN ('varchar', 'text', 'char');
