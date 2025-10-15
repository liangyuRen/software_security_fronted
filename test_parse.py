#!/usr/bin/env python3
import json
import requests
from datetime import datetime

# 测试 Flask API 返回的数据格式
print("Testing Flask crawler API data format...")
print("=" * 60)

# 测试 NVD API
print("\n1. Testing NVD API:")
try:
    response = requests.get("http://localhost:5000/vulnerabilities/nvd", timeout=30)
    nvd_data = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   Count: {len(nvd_data)} records")

    if nvd_data:
        sample = nvd_data[0]
        print(f"\n   Sample record:")
        print(f"   - cveId: {sample.get('cveId')}")
        print(f"   - vulnerabilityName: {sample.get('vulnerabilityName')[:50]}...")
        print(f"   - disclosureTime: {sample.get('disclosureTime')} (type: {type(sample.get('disclosureTime')).__name__})")
        print(f"   - riskLevel: {sample.get('riskLevel')}")
        print(f"   - affectsWhitelist: {sample.get('affectsWhitelist')}")
        print(f"   - isDelete: {sample.get('isDelete')}")

        # 验证日期格式
        date_str = sample.get('disclosureTime')
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            print(f"   ✅ Date format is valid (yyyy-MM-dd)")
        except:
            print(f"   ❌ Date format is INVALID")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 测试 AVD API
print("\n2. Testing AVD API:")
try:
    response = requests.get("http://localhost:5000/vulnerabilities/avd", timeout=30)
    avd_data = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   Count: {len(avd_data)} records")

    if avd_data:
        sample = avd_data[0]
        print(f"\n   Sample record:")
        print(f"   - cveId: {sample.get('cveId')}")
        print(f"   - vulnerabilityName: {sample.get('vulnerabilityName')[:50]}...")
        print(f"   - disclosureTime: {sample.get('disclosureTime')}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 测试 GitHub API
print("\n3. Testing GitHub API:")
try:
    response = requests.get("http://localhost:5000/vulnerabilities/github", timeout=30)
    github_data = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   Count: {len(github_data)} records")

    if github_data:
        sample = github_data[0]
        print(f"\n   Sample record:")
        print(f"   - cveId: {sample.get('cveId')}")
        print(f"   - vulnerabilityName: {sample.get('vulnerabilityName')[:50]}...")
        print(f"   - disclosureTime: {sample.get('disclosureTime')}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("Test completed!")
