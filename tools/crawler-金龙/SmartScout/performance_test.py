#!/usr/bin/env python3
"""
SmartScout 性能测试脚本
测量API响应时间，验证性能指标
"""

import time
import requests
import statistics
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
TEST_ITERATIONS = 5  # 每次测试的迭代次数

def measure_response_time(endpoint: str, method: str = "GET", payload: dict = None):
    """测量单个端点的响应时间"""
    times = []

    for i in range(TEST_ITERATIONS):
        start_time = time.time()
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=30)
            elif method == "POST":
                response = requests.post(f"{BASE_URL}{endpoint}", json=payload, timeout=30)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")

            response.raise_for_status()
            elapsed = (time.time() - start_time) * 1000  # 转换为毫秒
            times.append(elapsed)

        except Exception as e:
            print(f"  ✗ 请求失败: {e}")
            times.append(float('inf'))  # 用无穷大表示失败

    if all(t == float('inf') for t in times):
        return None

    # 过滤掉失败（无穷大）的测量
    valid_times = [t for t in times if t != float('inf')]
    if not valid_times:
        return None

    return {
        "avg": statistics.mean(valid_times),
        "min": min(valid_times),
        "max": max(valid_times),
        "std": statistics.stdev(valid_times) if len(valid_times) > 1 else 0,
        "success_rate": len(valid_times) / TEST_ITERATIONS * 100
    }

def print_result(endpoint_name: str, result: dict, threshold: float = 500):
    """打印性能测试结果"""
    if result is None:
        print(f"  ✗ {endpoint_name}: 测试失败")
        return False

    avg_time = result['avg']
    status = "✓" if avg_time <= threshold else "⚠"
    color_code = "\033[32m" if avg_time <= threshold else "\033[33m" if avg_time <= threshold * 2 else "\033[31m"
    reset_code = "\033[0m"

    print(f"  {status} {endpoint_name}:")
    print(f"    平均响应时间: {color_code}{avg_time:.2f}ms{reset_code} (阈值: {threshold}ms)")
    print(f"    最短/最长: {result['min']:.2f}ms / {result['max']:.2f}ms")
    print(f"    标准差: {result['std']:.2f}ms")
    print(f"    成功率: {result['success_rate']:.0f}%")

    return avg_time <= threshold

def main():
    """主性能测试函数"""
    print("="*70)
    print("SmartScout 性能测试")
    print("="*70)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试服务器: {BASE_URL}")
    print(f"每次测试迭代次数: {TEST_ITERATIONS}")
    print()

    # 检查服务器连接
    print("1. 检查服务器连接...")
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            print("  ✓ 服务器连接正常")
        else:
            print(f"  ✗ 服务器返回异常状态: {health_response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("  ✗ 无法连接到服务器")
        return False

    # 测试端点列表
    tests = [
        {
            "name": "健康检查",
            "endpoint": "/health",
            "method": "GET",
            "payload": None,
            "threshold": 100
        },
        {
            "name": "规则确诊",
            "endpoint": "/api/rule-diagnosis",
            "method": "POST",
            "payload": {
                "urls": ["https://www.ccgp.gov.cn"],
                "initial_blacklist": [],
                "initial_whitelist": []
            },
            "threshold": 2000  # 规则确诊可能需要更长时间
        },
        {
            "name": "保存规则",
            "endpoint": "/api/rules/test_project",
            "method": "POST",
            "payload": {
                "blacklist": ["测试"],
                "whitelist": ["消防"],
                "human_confirmed": True
            },
            "threshold": 300
        },
        {
            "name": "启动生产",
            "endpoint": "/api/production/test_project/start",
            "method": "POST",
            "payload": {
                "target_count": 10,
                "concurrency": 2,
                "max_pages": 5
            },
            "threshold": 200
        },
        {
            "name": "获取结果",
            "endpoint": "/api/results/test_project",
            "method": "GET",
            "payload": None,
            "threshold": 300
        },
        {
            "name": "任务状态",
            "endpoint": "/api/tasks/test_task",
            "method": "GET",
            "payload": None,
            "threshold": 200
        }
    ]

    print("\n2. 开始性能测试...")
    results = []
    all_passed = True

    for test in tests:
        print(f"\n测试: {test['name']}")
        print(f"  端点: {test['method']} {test['endpoint']}")

        result = measure_response_time(test['endpoint'], test['method'], test['payload'])
        passed = print_result(test['name'], result, test['threshold'])

        if result:
            results.append({
                "test": test['name'],
                "endpoint": test['endpoint'],
                "passed": passed,
                **result
            })

        if not passed:
            all_passed = False

    # 汇总结果
    print("\n" + "="*70)
    print("性能测试汇总")
    print("="*70)

    if not results:
        print("无有效测试结果")
        return False

    # 计算总体统计
    avg_times = [r['avg'] for r in results if 'avg' in r]
    success_rates = [r['success_rate'] for r in results if 'success_rate' in r]

    print(f"测试端点总数: {len(results)}")
    print(f"通过测试数: {sum(1 for r in results if r['passed'])}")
    print(f"总体平均响应时间: {statistics.mean(avg_times):.2f}ms")
    print(f"总体最短响应时间: {min(avg_times):.2f}ms")
    print(f"总体最长响应时间: {max(avg_times):.2f}ms")
    print(f"总体平均成功率: {statistics.mean(success_rates):.1f}%")

    # 性能建议
    print("\n性能建议:")
    slow_endpoints = [r for r in results if r['avg'] > 500]
    if slow_endpoints:
        print("  ⚠ 以下端点响应时间超过500ms:")
        for r in slow_endpoints:
            print(f"    • {r['test']}: {r['avg']:.2f}ms")
    else:
        print("  ✓ 所有端点响应时间均在500ms以内")

    # 检查成功率
    low_success = [r for r in results if r['success_rate'] < 80]
    if low_success:
        print("  ⚠ 以下端点成功率较低:")
        for r in low_success:
            print(f"    • {r['test']}: {r['success_rate']:.0f}%")
    else:
        print("  ✓ 所有端点成功率均超过80%")

    # 保存结果到文件
    result_file = "logs/performance_test.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "base_url": BASE_URL,
            "iterations": TEST_ITERATIONS,
            "results": results,
            "summary": {
                "total_tests": len(results),
                "passed_tests": sum(1 for r in results if r['passed']),
                "avg_response_time": statistics.mean(avg_times),
                "avg_success_rate": statistics.mean(success_rates)
            }
        }, f, indent=2, ensure_ascii=False)

    print(f"\n详细结果已保存到: {result_file}")

    return all_passed

if __name__ == "__main__":
    try:
        success = main()
        exit_code = 0 if success else 1
        print(f"\n性能测试{'通过' if success else '失败'}")
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        exit(1)
    except Exception as e:
        print(f"\n测试发生异常: {e}")
        exit(1)