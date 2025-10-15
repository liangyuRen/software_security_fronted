-- 修复数据库编码问题
-- 将所有表和列转换为utf8mb4编码

USE kulin;

-- 修改数据库默认编码
ALTER DATABASE kulin CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- 修改所有表的编码
ALTER TABLE company CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE component CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE dependency CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE project CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE report CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE user CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE vul CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 如果存在其他表,也需要转换
-- 可以使用以下查询生成所有表的转换语句:
-- SELECT CONCAT('ALTER TABLE ', table_name, ' CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;')
-- FROM information_schema.tables
-- WHERE table_schema = 'kulin';

-- 查看结果
SHOW VARIABLES LIKE 'character%';
SHOW VARIABLES LIKE 'collation%';
SELECT SCHEMA_NAME, DEFAULT_CHARACTER_SET_NAME, DEFAULT_COLLATION_NAME
FROM information_schema.SCHEMATA
WHERE SCHEMA_NAME='kulin';
