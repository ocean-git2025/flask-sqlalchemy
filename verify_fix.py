#!/usr/bin/env python3
"""验证修复效果的脚本"""

import json
import sqlite3
import time
import os
import sys
from datetime import datetime

# 确保路径兼容 Windows/Mac
DB_PATH = 'app.db'
LOG_FILE = 'verify_log.txt'

# 测试结果记录
test_results = []

# 记录日志
def log_message(message, level='INFO'):
    """记录日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] [{level}] {message}"
    print(log_entry)
    
    # 写入日志文件
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')
    except Exception as e:
        print(f"写入日志失败: {e}")

# 模拟 curl 命令调用接口
def test_api_endpoint(url, expected_status=200, test_name=""):
    """测试 API 接口"""
    start_time = time.time()
    success = False
    response_data = None
    
    try:
        import requests
        response = requests.get(url, timeout=10)
        status_code = response.status_code
        
        log_message(f"测试接口: {url}", 'INFO')
        log_message(f"状态码: {status_code}", 'INFO')
        
        if status_code == expected_status:
            data = response.json()
            log_message(f"返回数据: {json.dumps(data, indent=2, ensure_ascii=False)}", 'INFO')
            success = True
            response_data = data
        else:
            log_message(f"错误信息: {response.text}", 'ERROR')
            success = False
            response_data = response.text
    except Exception as e:
        error_msg = f"测试失败: {e}"
        log_message(error_msg, 'ERROR')
        success = False
        response_data = error_msg
    
    # 记录测试结果
    test_results.append({
        'name': test_name or url,
        'url': url,
        'expected_status': expected_status,
        'success': success,
        'response': response_data,
        'time': time.time() - start_time
    })
    
    # 输出测试结果
    if success:
        print(f"✅ {test_name} 测试通过")
    else:
        print(f"❌ {test_name} 测试失败")
    
    return success, response_data

# 查看数据库数据
def check_database_data():
    """检查数据库数据"""
    try:
        log_message("开始检查数据库数据", 'INFO')
        
        # 确保数据库文件存在
        if not os.path.exists(DB_PATH):
            log_message(f"数据库文件不存在: {DB_PATH}", 'ERROR')
            return 0
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 查看用户表结构
        log_message("\n数据库表结构:", 'INFO')
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        for column in columns:
            log_message(str(column), 'INFO')
        
        # 查看用户数据数量
        cursor.execute("SELECT COUNT(*) FROM user")
        count = cursor.fetchone()[0]
        log_message(f"\n用户数据数量: {count}", 'INFO')
        
        # 查看前 5 条用户数据
        log_message("\n前 5 条用户数据:", 'INFO')
        cursor.execute("SELECT id, username, email, created_at FROM user LIMIT 5")
        users = cursor.fetchall()
        for user in users:
            log_message(str(user), 'INFO')
        
        # 检查索引
        log_message("\n数据库索引:", 'INFO')
        cursor.execute("PRAGMA index_list(user)")
        indexes = cursor.fetchall()
        for idx in indexes:
            log_message(str(idx), 'INFO')
        
        conn.close()
        return count
    except Exception as e:
        error_msg = f"数据库检查失败: {e}"
        log_message(error_msg, 'ERROR')
        return 0

# 运行所有测试
def run_all_tests():
    """运行所有测试"""
    log_message("===== 开始验证修复效果 =====", 'INFO')
    print("\n===== 开始验证修复效果 =====\n")
    
    # 清空测试结果
    test_results.clear()
    
    # 清空日志文件
    try:
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            f.write('')
    except Exception:
        pass
    
    # 测试场景 1: 正常分页请求
    print("=== 测试场景 1: 正常分页请求 ===")
    test_api_endpoint(
        "http://127.0.0.1:5000/api/users?page=1&size=10",
        200,
        "正常分页请求"
    )
    
    # 测试场景 2: 非法 page 参数（page=0）
    print("\n=== 测试场景 2: 非法 page 参数（page=0）===")
    test_api_endpoint(
        "http://127.0.0.1:5000/api/users?page=0&size=10",
        400,
        "非法 page 参数"
    )
    
    # 测试场景 3: 非法 size 参数（size=100）
    print("\n=== 测试场景 3: 非法 size 参数（size=100）===")
    test_api_endpoint(
        "http://127.0.0.1:5000/api/users?page=1&size=100",
        400,
        "非法 size 参数"
    )
    
    # 测试场景 4: 非整数参数
    print("\n=== 测试场景 4: 非整数参数 ===")
    test_api_endpoint(
        "http://127.0.0.1:5000/api/users?page=abc&size=10",
        400,
        "非整数参数"
    )
    
    # 测试场景 5: 大页码请求
    print("\n=== 测试场景 5: 大页码请求 ===")
    test_api_endpoint(
        "http://127.0.0.1:5000/api/users?page=10&size=10",
        200,
        "大页码请求"
    )
    
    # 测试场景 6: 未传参数
    print("\n=== 测试场景 6: 未传参数 ===")
    test_api_endpoint(
        "http://127.0.0.1:5000/api/users",
        200,
        "未传参数"
    )
    
    # 测试场景 7: page 超过 1000
    print("\n=== 测试场景 7: page 超过 1000 ===")
    test_api_endpoint(
        "http://127.0.0.1:5000/api/users?page=1001&size=10",
        400,
        "page 超过 1000"
    )
    
    # 测试场景 8: 全空格参数
    print("\n=== 测试场景 8: 全空格参数 ===")
    test_api_endpoint(
        "http://127.0.0.1:5000/api/users?page=   1   &size=   10   ",
        200,
        "全空格参数"
    )
    
    # 检查数据库数据
    print("\n=== 检查数据库数据 ===")
    user_count = check_database_data()
    
    # 验证数据一致性
    print("\n=== 验证数据一致性 ===")
    if user_count >= 100:
        log_message("✅ 数据库数据完整，包含至少 100 条测试数据", 'INFO')
        print("✅ 数据库数据完整，包含至少 100 条测试数据")
    else:
        log_message(f"❌ 数据库数据不完整，仅包含 {user_count} 条数据", 'ERROR')
        print(f"❌ 数据库数据不完整，仅包含 {user_count} 条数据")
    
    # 输出测试结果汇总
    print("\n===== 测试结果汇总 =====")
    log_message("===== 测试结果汇总 =====", 'INFO')
    
    passed = sum(1 for r in test_results if r['success'])
    total = len(test_results)
    
    log_message(f"总测试数: {total}", 'INFO')
    log_message(f"通过测试: {passed}", 'INFO')
    log_message(f"失败测试: {total - passed}", 'INFO')
    
    print(f"总测试数: {total}")
    print(f"通过测试: {passed}")
    print(f"失败测试: {total - passed}")
    
    # 输出失败的测试
    if total - passed > 0:
        print("\n失败的测试:")
        log_message("\n失败的测试:", 'ERROR')
        for result in test_results:
            if not result['success']:
                print(f"- {result['name']}")
                log_message(f"- {result['name']}", 'ERROR')
    
    # 输出测试结论
    if passed == total:
        print("\n🎉 所有测试通过！修复效果良好。")
        log_message("🎉 所有测试通过！修复效果良好。", 'INFO')
    else:
        print("\n⚠️  部分测试失败，需要进一步修复。")
        log_message("⚠️  部分测试失败，需要进一步修复。", 'WARNING')
    
    print("\n===== 验证完成 =====")
    log_message("===== 验证完成 =====", 'INFO')

# 主验证函数
def main():
    """主验证函数"""
    # 清空日志文件
    try:
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            f.write(f"验证开始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    except Exception as e:
        print(f"创建日志文件失败: {e}")
    
    # 运行所有测试
    run_all_tests()

if __name__ == "__main__":
    main()