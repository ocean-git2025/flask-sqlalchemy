#!/usr/bin/env python3
"""
验证脚本 - 用于验证 Flask-SQLAlchemy 项目的修复效果
支持 Windows 和 Mac 平台
"""

import os
import sys
import json
import time
import logging
import subprocess
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('verify.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 测试配置
TEST_SERVER_PORT = 5000
TEST_SERVER_URL = f"http://127.0.0.1:{TEST_SERVER_PORT}"

class VerifyFix:
    def __init__(self):
        self.server_process = None
        self.test_results = []
    
    def run_command(self, cmd, cwd=None):
        """运行命令并返回结果"""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or PROJECT_ROOT,
                capture_output=True,
                text=True,
                shell=True
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            logger.error(f"运行命令失败: {cmd}, 错误: {e}")
            return 1, "", str(e)
    
    def start_server(self):
        """启动测试服务器"""
        logger.info("启动测试服务器...")
        try:
            # 在后台启动服务器
            if sys.platform == 'win32':
                # Windows 平台
                self.server_process = subprocess.Popen(
                    [sys.executable, "run.py"],
                    cwd=PROJECT_ROOT,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            else:
                # Mac/Linux 平台
                self.server_process = subprocess.Popen(
                    [sys.executable, "run.py"],
                    cwd=PROJECT_ROOT,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            
            # 等待服务器启动
            time.sleep(3)
            
            # 检查服务器是否启动成功
            if self.server_process.poll() is not None:
                stderr = self.server_process.stderr.read()
                logger.error(f"服务器启动失败: {stderr}")
                return False
            
            logger.info("服务器启动成功")
            return True
        except Exception as e:
            logger.error(f"启动服务器失败: {e}")
            return False
    
    def stop_server(self):
        """停止测试服务器"""
        if self.server_process:
            logger.info("停止测试服务器...")
            try:
                if sys.platform == 'win32':
                    # Windows 平台
                    subprocess.run(["taskkill", "/F", "/PID", str(self.server_process.pid)], capture_output=True)
                else:
                    # Mac/Linux 平台
                    self.server_process.terminate()
                    self.server_process.wait(timeout=5)
                logger.info("服务器停止成功")
            except Exception as e:
                logger.error(f"停止服务器失败: {e}")
            finally:
                self.server_process = None
    
    def test_api(self, endpoint, expected_status=200, description=""):
        """测试 API 接口"""
        logger.info(f"测试接口: {description} - {endpoint}")
        
        try:
            if sys.platform == 'win32':
                # Windows 平台使用 PowerShell
                cmd = f"Invoke-WebRequest -Uri '{TEST_SERVER_URL}{endpoint}' -Method GET -ErrorAction SilentlyContinue"
                code, stdout, stderr = self.run_command(f"powershell -Command \"{cmd}\"")
                
                # 解析结果
                if "200 OK" in stdout:
                    status_code = 200
                    response_json = stdout.split('\n')[-1]
                elif "400 Bad Request" in stdout:
                    status_code = 400
                    response_json = stdout.split('\n')[-1]
                else:
                    status_code = 500
                    response_json = stderr
            else:
                # Mac/Linux 平台使用 curl
                cmd = f"curl -s -w '\n%{{http_code}}' '{TEST_SERVER_URL}{endpoint}'"
                code, stdout, stderr = self.run_command(cmd)
                
                # 解析结果
                parts = stdout.split('\n')
                if len(parts) >= 2:
                    status_code = int(parts[-1])
                    response_json = '\n'.join(parts[:-1])
                else:
                    status_code = 500
                    response_json = stderr
            
            # 验证结果
            success = status_code == expected_status
            self.test_results.append({
                "description": description,
                "endpoint": endpoint,
                "expected_status": expected_status,
                "actual_status": status_code,
                "success": success,
                "response": response_json[:500]  # 只记录前 500 字符
            })
            
            if success:
                logger.info(f"✓ 测试通过: {description}")
            else:
                logger.error(f"✗ 测试失败: {description}, 期望状态码: {expected_status}, 实际状态码: {status_code}")
            
            return success
        except Exception as e:
            logger.error(f"测试接口失败: {description}, 错误: {e}")
            self.test_results.append({
                "description": description,
                "endpoint": endpoint,
                "expected_status": expected_status,
                "actual_status": 500,
                "success": False,
                "response": str(e)
            })
            return False
    
    def test_database(self):
        """测试数据库数据一致性"""
        logger.info("测试数据库数据一致性...")
        
        # 检查数据库文件是否存在
        db_file = os.path.join(PROJECT_ROOT, "users.db")
        if not os.path.exists(db_file):
            logger.error("数据库文件不存在")
            self.test_results.append({
                "description": "数据库文件存在性",
                "success": False,
                "message": "数据库文件不存在"
            })
            return False
        
        # 检查数据库文件大小
        db_size = os.path.getsize(db_file)
        if db_size < 1024:  # 小于 1KB 可能是空数据库
            logger.error(f"数据库文件太小: {db_size} 字节")
            self.test_results.append({
                "description": "数据库文件大小",
                "success": False,
                "message": f"数据库文件太小: {db_size} 字节"
            })
            return False
        
        logger.info(f"✓ 数据库文件存在，大小: {db_size} 字节")
        self.test_results.append({
            "description": "数据库文件存在性",
            "success": True,
            "message": f"数据库文件存在，大小: {db_size} 字节"
        })
        
        return True
    
    def run_all_tests(self):
        """运行所有测试"""
        logger.info("开始验证修复效果...")
        
        try:
            # 1. 初始化数据库
            logger.info("初始化数据库...")
            code, stdout, stderr = self.run_command([sys.executable, "init_db.py"])
            if code != 0:
                logger.error(f"初始化数据库失败: {stderr}")
                return False
            logger.info("数据库初始化成功")
            
            # 2. 启动服务器
            if not self.start_server():
                return False
            
            # 3. 运行 API 测试
            logger.info("运行 API 测试...")
            
            # 正常场景测试
            self.test_api("/api/users?page=1&size=10", 200, "正常分页查询")
            self.test_api("/api/users", 200, "默认参数查询")
            
            # 异常场景测试
            self.test_api("/api/users?page=0&size=10", 400, "page=0 参数错误")
            self.test_api("/api/users?page=1&size=100", 400, "size=100 参数错误")
            self.test_api("/api/users?page=1001&size=10", 400, "page=1001 参数错误")
            self.test_api("/api/users?page=abc&size=10", 400, "非整数 page 参数")
            self.test_api("/api/users?page=1&size=abc", 400, "非整数 size 参数")
            
            # 边缘场景测试
            self.test_api("/api/users?page=1&size=1", 200, "size=1 边界测试")
            self.test_api("/api/users?page=1&size=50", 200, "size=50 边界测试")
            self.test_api("/api/users?page=1000&size=10", 200, "page=1000 边界测试")
            
            # 4. 测试数据库一致性
            self.test_database()
            
            return True
        finally:
            # 5. 停止服务器
            self.stop_server()
    
    def generate_report(self):
        """生成验证报告"""
        logger.info("\n" + "="*80)
        logger.info("验证修复效果报告")
        logger.info("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.get("success", False))
        failed_tests = total_tests - passed_tests
        
        logger.info(f"总测试数: {total_tests}")
        logger.info(f"通过测试: {passed_tests}")
        logger.info(f"失败测试: {failed_tests}")
        logger.info("")
        
        if failed_tests > 0:
            logger.info("失败测试详情:")
            logger.info("-"*80)
            for result in self.test_results:
                if not result.get("success", False):
                    logger.info(f"测试: {result.get('description', '未知')}")
                    logger.info(f"接口: {result.get('endpoint', 'N/A')}")
                    logger.info(f"期望状态: {result.get('expected_status', 'N/A')}")
                    logger.info(f"实际状态: {result.get('actual_status', 'N/A')}")
                    logger.info(f"响应: {result.get('response', 'N/A')}")
                    logger.info("-"*80)
        
        logger.info("")
        if failed_tests == 0:
            logger.info("所有测试通过！修复效果验证成功。")
        else:
            logger.warning("部分测试失败，需要进一步修复。")
        
        logger.info("="*80)

if __name__ == "__main__":
    verify = VerifyFix()
    try:
        verify.run_all_tests()
    finally:
        verify.stop_server()
        verify.generate_report()
