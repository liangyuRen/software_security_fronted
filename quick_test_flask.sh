#!/bin/bash

# Flask服务快速测试脚本
# 用于验证Flask服务和AutoDL集成是否正常工作

set -e

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

BASE_URL="http://localhost:5000"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Flask服务快速测试${NC}"
echo -e "${BLUE}========================================${NC}\n"

# 测试函数
test_endpoint() {
    local name="$1"
    local url="$2"
    local timeout="${3:-10}"

    echo -e "${YELLOW}测试: $name${NC}"

    if timeout $timeout curl -sf "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 通过${NC}\n"
        return 0
    else
        echo -e "${RED}✗ 失败${NC}\n"
        return 1
    fi
}

# 计数器
PASS=0
FAIL=0

# 1. 健康检查
echo -e "${BLUE}1. 基础服务测试${NC}\n"
if test_endpoint "健康检查" "$BASE_URL/vulnerabilities/test" 5; then
    ((PASS++))
else
    ((FAIL++))
fi

# 2. LLM服务测试
echo -e "${BLUE}2. LLM服务测试 (AutoDL集成)${NC}\n"

echo -e "${YELLOW}测试: Qwen模型${NC}"
if timeout 15 curl -sf "$BASE_URL/llm/query?query=你好&model=qwen" | jq -e '.code == 200' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 通过${NC}"
    response=$(curl -s "$BASE_URL/llm/query?query=你好&model=qwen" | jq -r '.obj')
    echo -e "  响应: $response\n"
    ((PASS++))
else
    echo -e "${RED}✗ 失败${NC}\n"
    ((FAIL++))
fi

echo -e "${YELLOW}测试: DeepSeek模型${NC}"
if timeout 15 curl -sf "$BASE_URL/llm/query?query=hello&model=deepseek" | jq -e '.code == 200' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 通过${NC}"
    response=$(curl -s "$BASE_URL/llm/query?query=hello&model=deepseek" | jq -r '.obj' | head -c 100)
    echo -e "  响应: ${response}...\n"
    ((PASS++))
else
    echo -e "${RED}✗ 失败${NC}\n"
    ((FAIL++))
fi

# 3. 爬虫服务测试
echo -e "${BLUE}3. 漏洞爬虫测试${NC}\n"

if test_endpoint "GitHub爬虫" "$BASE_URL/vulnerabilities/github" 15; then
    count=$(curl -s "$BASE_URL/vulnerabilities/github" | jq 'length')
    echo -e "  获取到 $count 条漏洞数据\n"
    ((PASS++))
else
    ((FAIL++))
fi

if test_endpoint "AVD爬虫" "$BASE_URL/vulnerabilities/avd" 15; then
    count=$(curl -s "$BASE_URL/vulnerabilities/avd" | jq 'length')
    echo -e "  获取到 $count 条漏洞数据\n"
    ((PASS++))
else
    ((FAIL++))
fi

if test_endpoint "NVD爬虫" "$BASE_URL/vulnerabilities/nvd" 15; then
    count=$(curl -s "$BASE_URL/vulnerabilities/nvd" | jq 'length')
    echo -e "  获取到 $count 条漏洞数据\n"
    ((PASS++))
else
    ((FAIL++))
fi

# 4. 修复建议测试
echo -e "${BLUE}4. 修复建议生成测试${NC}\n"

echo -e "${YELLOW}测试: SQL注入修复建议${NC}"
if timeout 20 curl -sf -X POST "$BASE_URL/llm/repair/suggestion" \
    -d "vulnerability_name=SQL注入" \
    -d "vulnerability_desc=用户输入未过滤" \
    -d "related_code=SELECT * FROM users" \
    -d "model=qwen" | jq -e '.code == 200' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 通过${NC}"
    advice_length=$(curl -s -X POST "$BASE_URL/llm/repair/suggestion" \
        -d "vulnerability_name=SQL注入" \
        -d "vulnerability_desc=用户输入未过滤" \
        -d "related_code=SELECT * FROM users" \
        -d "model=qwen" | jq -r '.obj.fix_advise' | wc -c)
    echo -e "  建议长度: ${advice_length} 字符\n"
    ((PASS++))
else
    echo -e "${RED}✗ 失败${NC}\n"
    ((FAIL++))
fi

# 5. 容器状态
echo -e "${BLUE}5. 容器状态${NC}\n"
echo -e "${YELLOW}Flask容器状态:${NC}"
docker ps --filter "name=flask-crawler" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

# 总结
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}测试总结${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "总计测试: $((PASS + FAIL))"
echo -e "${GREEN}通过: $PASS${NC}"
echo -e "${RED}失败: $FAIL${NC}"

TOTAL=$((PASS + FAIL))
if [ $TOTAL -gt 0 ]; then
    PERCENTAGE=$((PASS * 100 / TOTAL))
    echo -e "通过率: ${PERCENTAGE}%"
fi

# 关键服务状态
echo -e "\n${BLUE}关键服务状态:${NC}"
if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✓ 所有服务运行正常${NC}"
    echo -e "${GREEN}✓ AutoDL LLM服务连接正常${NC}"
    echo -e "${GREEN}✓ 漏洞爬虫服务正常${NC}"
    exit 0
else
    echo -e "${RED}✗ 有 $FAIL 个测试失败${NC}"
    echo -e "${YELLOW}请检查服务日志: docker logs vulsystem-flask-crawler${NC}"
    exit 1
fi
