#!/usr/bin/env python3
"""
Flask服务部署测试脚本
测试所有端点,包括与AutoDL服务的集成
"""

import requests
import json
from typing import Dict, Any
import time

# 配置
BASE_URL = "http://localhost:5000"
COLORS = {
    'GREEN': '\033[92m',
    'RED': '\033[91m',
    'YELLOW': '\033[93m',
    'BLUE': '\033[94m',
    'END': '\033[0m'
}

def print_section(title: str):
    """打印分节标题"""
    print(f"\n{COLORS['BLUE']}{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}{COLORS['END']}\n")

def print_result(test_name: str, success: bool, details: str = ""):
    """打印测试结果"""
    status = f"{COLORS['GREEN']}✓ PASS" if success else f"{COLORS['RED']}✗ FAIL"
    print(f"{status}{COLORS['END']} | {test_name}")
    if details:
        print(f"       {COLORS['YELLOW']}详情: {details}{COLORS['END']}")

def test_endpoint(name: str, method: str, url: str, **kwargs) -> Dict[str, Any]:
    """通用端点测试函数"""
    try:
        print(f"\n{COLORS['YELLOW']}测试: {name}{COLORS['END']}")
        print(f"URL: {url}")

        start_time = time.time()
        if method.upper() == 'GET':
            response = requests.get(url, timeout=30, **kwargs)
        elif method.upper() == 'POST':
            response = requests.post(url, timeout=30, **kwargs)
        else:
            raise ValueError(f"不支持的方法: {method}")

        elapsed_time = time.time() - start_time

        print(f"状态码: {response.status_code}")
        print(f"响应时间: {elapsed_time:.2f}秒")

        try:
            data = response.json()
            print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}")
        except:
            print(f"响应内容: {response.text[:500]}")
            data = {"raw": response.text}

        return {
            'success': response.status_code == 200,
            'status_code': response.status_code,
            'data': data,
            'elapsed_time': elapsed_time
        }
    except Exception as e:
        print(f"{COLORS['RED']}错误: {str(e)}{COLORS['END']}")
        return {
            'success': False,
            'error': str(e)
        }

def main():
    print_section("Flask服务部署测试")

    results = {}

    # 1. 基础健康检查
    print_section("1. 基础健康检查")
    result = test_endpoint(
        "健康检查",
        "GET",
        f"{BASE_URL}/vulnerabilities/test"
    )
    results['health_check'] = result
    print_result("健康检查", result['success'])

    # 2. 测试漏洞爬虫端点
    print_section("2. 漏洞数据爬虫测试")

    # GitHub漏洞
    result = test_endpoint(
        "GitHub漏洞爬虫",
        "GET",
        f"{BASE_URL}/vulnerabilities/github"
    )
    results['github_crawler'] = result
    print_result("GitHub漏洞爬虫", result['success'],
                 f"获取到 {len(result.get('data', [])) if isinstance(result.get('data'), list) else 0} 条数据")

    # AVD漏洞
    result = test_endpoint(
        "AVD漏洞爬虫",
        "GET",
        f"{BASE_URL}/vulnerabilities/avd"
    )
    results['avd_crawler'] = result
    print_result("AVD漏洞爬虫", result['success'],
                 f"获取到 {len(result.get('data', [])) if isinstance(result.get('data'), list) else 0} 条数据")

    # NVD漏洞
    result = test_endpoint(
        "NVD漏洞爬虫",
        "GET",
        f"{BASE_URL}/vulnerabilities/nvd"
    )
    results['nvd_crawler'] = result
    print_result("NVD漏洞爬虫", result['success'],
                 f"获取到 {len(result.get('data', [])) if isinstance(result.get('data'), list) else 0} 条数据")

    # 3. 测试LLM服务(与AutoDL集成)
    print_section("3. LLM服务测试 (AutoDL集成)")

    # Qwen模型
    result = test_endpoint(
        "Qwen模型查询",
        "GET",
        f"{BASE_URL}/llm/query",
        params={'query': '你好,请简单介绍一下自己', 'model': 'qwen'}
    )
    results['llm_qwen'] = result
    print_result("Qwen模型", result['success'] and result.get('data', {}).get('code') == 200,
                 f"响应: {result.get('data', {}).get('obj', '')[:100]}...")

    # DeepSeek模型
    result = test_endpoint(
        "DeepSeek模型查询",
        "GET",
        f"{BASE_URL}/llm/query",
        params={'query': '什么是SQL注入漏洞?', 'model': 'deepseek'}
    )
    results['llm_deepseek'] = result
    print_result("DeepSeek模型", result['success'] and result.get('data', {}).get('code') == 200,
                 f"响应: {result.get('data', {}).get('obj', '')[:100]}...")

    # 4. 测试修复建议生成(POST请求)
    print_section("4. 漏洞修复建议生成测试")

    repair_data = {
        'vulnerability_name': 'SQL注入',
        'vulnerability_desc': '用户输入未经过滤直接拼接到SQL语句中',
        'related_code': 'String sql = "SELECT * FROM users WHERE id=" + userId;',
        'model': 'qwen'
    }

    result = test_endpoint(
        "修复建议生成",
        "POST",
        f"{BASE_URL}/llm/repair/suggestion",
        data=repair_data
    )
    results['repair_suggestion'] = result
    print_result("修复建议生成", result['success'] and result.get('data', {}).get('code') == 200,
                 f"建议长度: {len(str(result.get('data', {}).get('obj', {}).get('fix_advise', '')))} 字符")

    # 5. 测试漏洞检测端点
    print_section("5. 漏洞检测测试")

    detect_data = {
        'language': 'java',
        'detect_strategy': 'TinyModel',
        'cve_id': 'CVE-2024-TEST',
        'desc': '这是一个测试漏洞描述,包含Jackson数据绑定漏洞的相关信息',
        'company': 'test',
        'similarityThreshold': 0.45,
        'white_list': []
    }

    result = test_endpoint(
        "漏洞检测 (TinyModel策略)",
        "POST",
        f"{BASE_URL}/vulnerabilities/detect",
        json=detect_data,
        headers={'Content-Type': 'application/json'}
    )
    results['detect_tinymodel'] = result
    print_result("漏洞检测 (TinyModel)", result['success'],
                 f"检测结果: {str(result.get('data', ''))[:100]}...")

    # 6. 测试解析端点
    print_section("6. 依赖解析测试")

    # 注意: 这些测试需要实际的项目文件夹路径,这里只测试端点可用性
    result = test_endpoint(
        "POM解析端点可用性",
        "GET",
        f"{BASE_URL}/parse/pom_parse",
        params={'project_folder': '/nonexistent'}
    )
    results['pom_parse'] = result
    print_result("POM解析端点", result.get('status_code') in [200, 400, 500],
                 "端点可访问(期望失败因为路径不存在)")

    result = test_endpoint(
        "C依赖解析端点可用性",
        "GET",
        f"{BASE_URL}/parse/c_parse",
        params={'project_folder': '/nonexistent'}
    )
    results['c_parse'] = result
    print_result("C依赖解析端点", result.get('status_code') in [200, 400, 500],
                 "端点可访问(期望失败因为路径不存在)")

    # 7. 总结报告
    print_section("测试总结报告")

    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r.get('success', False))

    print(f"总测试数: {total_tests}")
    print(f"{COLORS['GREEN']}通过: {passed_tests}{COLORS['END']}")
    print(f"{COLORS['RED']}失败: {total_tests - passed_tests}{COLORS['END']}")
    print(f"通过率: {(passed_tests/total_tests*100):.1f}%")

    # 关键服务状态
    print(f"\n{COLORS['BLUE']}关键服务状态:{COLORS['END']}")

    # Flask服务
    flask_healthy = results.get('health_check', {}).get('success', False)
    print(f"{'✓' if flask_healthy else '✗'} Flask服务: {'运行正常' if flask_healthy else '异常'}")

    # LLM服务 (AutoDL集成)
    llm_healthy = any([
        results.get('llm_qwen', {}).get('success', False),
        results.get('llm_deepseek', {}).get('success', False)
    ])
    print(f"{'✓' if llm_healthy else '✗'} LLM服务 (AutoDL): {'连接正常' if llm_healthy else '连接失败'}")

    # 爬虫服务
    crawler_healthy = any([
        results.get('github_crawler', {}).get('success', False),
        results.get('avd_crawler', {}).get('success', False),
        results.get('nvd_crawler', {}).get('success', False)
    ])
    print(f"{'✓' if crawler_healthy else '✗'} 爬虫服务: {'运行正常' if crawler_healthy else '异常'}")

    # 检测服务
    detect_healthy = results.get('detect_tinymodel', {}).get('success', False)
    print(f"{'✓' if detect_healthy else '✗'} 漏洞检测服务: {'运行正常' if detect_healthy else '异常'}")

    # 保存详细结果到文件
    with open('/root/VulSystem/test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n详细测试结果已保存到: /root/VulSystem/test_results.json")

    # 返回状态码
    return 0 if passed_tests == total_tests else 1

if __name__ == "__main__":
    exit(main())
