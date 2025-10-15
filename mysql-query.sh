#!/bin/bash
# VulSystem MySQL Query Helper Script
# Usage: ./mysql-query.sh [database] [query]
# Example: ./mysql-query.sh kulin "SHOW TABLES;"

DATABASE=${1:-kulin}
QUERY=${2:-"SHOW TABLES;"}

docker exec vulsystem-mysql bash -c "mysql -uroot -p\${MYSQL_ROOT_PASSWORD} ${DATABASE} -e \"${QUERY}\"" 2>&1 | grep -v "Warning"
