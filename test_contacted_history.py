"""
测试已联络历史功能
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_contacted_history_features():
    print("=" * 60)
    print("测试已联络历史功能")
    print("=" * 60)

    # 1. 测试获取当前配置（应该包含 contacted_history_count）
    print("\n1. 获取过滤配置...")
    response = requests.get(f"{BASE_URL}/api/filter-config")
    if response.status_code == 200:
        config = response.json()
        print(f"✓ 配置加载成功")
        print(f"  - 已联络历史记录数: {config.get('contacted_history_count', 0)}")
    else:
        print(f"✗ 获取配置失败: {response.status_code}")
        return

    # 2. 测试获取联络历史记录列表
    print("\n2. 获取已联络历史记录列表...")
    response = requests.get(f"{BASE_URL}/api/contacted-history")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ 获取成功")
        print(f"  - 记录总数: {data['total']}")
        print(f"  - 前3条记录:")
        for record in data['records'][:3]:
            print(f"    · {record['频道名']} / {record['邮箱']} / {record['联络日期']}")
    else:
        print(f"✗ 获取失败: {response.status_code}")

    # 3. 测试添加单条记录
    print("\n3. 添加测试记录...")
    test_record = {
        "频道名": "测试频道",
        "email": "test@example.com",
        "联络日期": "2026-08-01",
        "备注": "自动化测试添加"
    }
    response = requests.post(
        f"{BASE_URL}/api/contacted-history",
        json=test_record
    )
    if response.status_code == 200:
        result = response.json()
        print(f"✓ 添加成功: {result['message']}")
    else:
        print(f"✗ 添加失败: {response.status_code} - {response.text}")

    # 4. 测试获取联络历史阈值
    print("\n4. 获取联络历史阈值...")
    response = requests.get(f"{BASE_URL}/api/filter-config/contact-threshold")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ 当前阈值: {data['threshold_days']} 天")
    else:
        print(f"✗ 获取阈值失败: {response.status_code}")

    # 5. 测试更新联络历史阈值
    print("\n5. 更新联络历史阈值...")
    response = requests.put(
        f"{BASE_URL}/api/filter-config/contact-threshold",
        json={"threshold_days": 60}
    )
    if response.status_code == 200:
        result = response.json()
        print(f"✓ {result['message']}")
    else:
        print(f"✗ 更新失败: {response.status_code}")

    # 6. 验证阈值是否更新成功
    print("\n6. 验证阈值更新...")
    response = requests.get(f"{BASE_URL}/api/filter-config/contact-threshold")
    if response.status_code == 200:
        data = response.json()
        if data['threshold_days'] == 60:
            print(f"✓ 阈值已更新为: {data['threshold_days']} 天")
        else:
            print(f"✗ 阈值未正确更新，当前为: {data['threshold_days']} 天")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_contacted_history_features()
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到API服务器，请确保后端正在运行")
    except Exception as e:
        print(f"✗ 测试失败: {e}")
