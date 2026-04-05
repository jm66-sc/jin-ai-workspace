#!/usr/bin/env python3
# test_network_direct.py - 直接网络测试

import os
import sys
import requests
import socket
import ssl

# 清除所有代理设置
for proxy_var in ['https_proxy', 'http_proxy', 'HTTPS_PROXY', 'HTTP_PROXY', 'all_proxy', 'ALL_PROXY']:
    os.environ.pop(proxy_var, None)

print("="*60)
print("🌐 直接网络连通性测试")
print("="*60)

target_url = "https://www.ccgp-sichuan.gov.cn"
print(f"目标URL: {target_url}")
print(f"Python: {sys.version.split()[0]}")

# 1. 测试DNS解析
print("\n1. DNS解析测试...")
try:
    import socket
    hostname = "www.ccgp-sichuan.gov.cn"
    ip_list = socket.gethostbyname_ex(hostname)[2]
    print(f"   ✅ 解析成功: {hostname} -> {ip_list}")
except Exception as e:
    print(f"   ❌ DNS解析失败: {e}")

# 2. 测试TCP连接
print("\n2. TCP连接测试...")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    sock.connect(("www.ccgp-sichuan.gov.cn", 443))
    print(f"   ✅ TCP连接成功: 443端口开放")
    sock.close()
except Exception as e:
    print(f"   ❌ TCP连接失败: {e}")

# 3. 测试SSL/TLS握手
print("\n3. SSL/TLS握手测试...")
try:
    ctx = ssl.create_default_context()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    sock.connect(("www.ccgp-sichuan.gov.cn", 443))
    ssl_sock = ctx.wrap_socket(sock, server_hostname="www.ccgp-sichuan.gov.cn")
    print(f"   ✅ SSL握手成功")
    print(f"   证书信息: {ssl_sock.getpeercert()['subject']}")
    ssl_sock.close()
except Exception as e:
    print(f"   ❌ SSL握手失败: {e}")

# 4. 使用requests直接访问（强制不使用代理）
print("\n4. HTTP请求测试...")
try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    # 强制不使用代理
    response = requests.get(
        target_url,
        headers=headers,
        timeout=15,
        proxies={},  # 明确指定空代理
        verify=True  # 验证SSL证书
    )

    print(f"   ✅ HTTP请求成功")
    print(f"   状态码: {response.status_code}")
    print(f"   内容长度: {len(response.text)} 字符")
    print(f"   服务器: {response.headers.get('Server', 'N/A')}")
    print(f"   内容类型: {response.headers.get('Content-Type', 'N/A')}")

    # 检查是否有内容
    if len(response.text) > 0:
        print(f"   页面标题: {response.text[:200]}")

except requests.exceptions.ProxyError as e:
    print(f"   ❌ 代理错误（可能系统有代理配置）: {e}")
except requests.exceptions.ConnectTimeout as e:
    print(f"   ❌ 连接超时: {e}")
except requests.exceptions.ConnectionError as e:
    print(f"   ❌ 连接错误: {e}")
except requests.exceptions.SSLError as e:
    print(f"   ❌ SSL错误: {e}")
except Exception as e:
    print(f"   ❌ 请求失败: {type(e).__name__}: {e}")

# 5. 检查系统代理设置
print("\n5. 系统代理检查...")
try:
    # Mac系统代理检查
    result = os.popen('networksetup -getwebproxy Wi-Fi 2>/dev/null || echo "无法获取代理设置"').read()
    if "Enabled: Yes" in result:
        print(f"   ⚠️  系统代理已启用")
        print(f"   代理设置: {result}")
    else:
        print(f"   ✅ 系统代理未启用")
except Exception as e:
    print(f"   代理检查失败: {e}")

print("\n" + "="*60)
print("📊 测试完成总结")
print("="*60)

# 总结建议
print("\n🎯 建议:")
print("1. 如果所有测试都失败 → 网站可能屏蔽了您的IP或网络")
print("2. 如果TCP/SSL成功但HTTP失败 → 可能是网站防火墙")
print("3. 如果代理错误 → 需要禁用系统级代理")
print("4. 尝试: 切换网络、使用VPN、联系网站管理员")