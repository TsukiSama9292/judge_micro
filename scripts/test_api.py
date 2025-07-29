#!/usr/bin/env python3
"""
Judge Microservice API 快速測試腳本

這個腳本會啟動 API 服務器並執行基本測試來驗證功能是否正常。
"""

import subprocess
import time
import requests
import json
import sys
import os
from pathlib import Path

# 設定項目根目錄
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

def start_api_server():
    """啟動 API 服務器"""
    print("🚀 啟動 Judge Microservice API 服務器...")
    
    # 改變到項目根目錄
    os.chdir(PROJECT_ROOT)
    
    # 啟動 uvicorn 服務器
    cmd = [
        "uvicorn",
        "judge_micro.api.main:get_app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--factory",
        "--reload"
    ]
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待服務器啟動
        print("⏳ 等待服務器啟動...")
        time.sleep(5)
        
        # 檢查服務器是否啟動成功
        try:
            response = requests.get("http://localhost:8000/", timeout=10)
            if response.status_code == 200:
                print("✅ API 服務器啟動成功！")
                return process
            else:
                print(f"❌ 服務器啟動失敗，狀態碼: {response.status_code}")
                return None
        except requests.RequestException as e:
            print(f"❌ 無法連接到服務器: {e}")
            return None
            
    except FileNotFoundError:
        print("❌ 找不到 uvicorn，請先安裝：pip install uvicorn")
        return None
    except Exception as e:
        print(f"❌ 啟動服務器時發生錯誤: {e}")
        return None

def test_basic_api():
    """測試基本 API 功能"""
    print("\n📋 開始 API 基本功能測試...")
    
    base_url = "http://localhost:8000"
    
    # 測試 1: 健康檢查
    print("1️⃣ 測試健康檢查端點...")
    try:
        response = requests.get(f"{base_url}/")
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "running"
        print("   ✅ 健康檢查通過")
    except Exception as e:
        print(f"   ❌ 健康檢查失敗: {e}")
        return False
    
    # 測試 2: 獲取服務狀態
    print("2️⃣ 測試服務狀態端點...")
    try:
        response = requests.get(f"{base_url}/judge/status")
        assert response.status_code == 200
        result = response.json()
        print(f"   ✅ 服務狀態: {result.get('status', 'unknown')}")
    except Exception as e:
        print(f"   ❌ 服務狀態檢查失敗: {e}")
        return False
    
    # 測試 3: 獲取支援語言
    print("3️⃣ 測試支援語言端點...")
    try:
        response = requests.get(f"{base_url}/judge/languages")
        assert response.status_code == 200
        result = response.json()
        languages = [lang["language"] for lang in result["supported_languages"]]
        assert "c" in languages
        assert "cpp" in languages
        print(f"   ✅ 支援語言: {', '.join(languages)}")
    except Exception as e:
        print(f"   ❌ 支援語言檢查失敗: {e}")
        return False
    
    return True

def test_c_language():
    """測試 C 語言評測"""
    print("\n🔧 開始 C 語言評測測試...")
    
    request_data = {
        "language": "c",
        "user_code": '''#include <stdio.h>

int solve(int *a, int *b) {
    *a = *a * 2;      // 3 * 2 = 6
    *b = *b * 2 + 1;  // 4 * 2 + 1 = 9
    printf("Hello from C!\\n");
    return 0;
}''',
        "solve_params": [
            {"name": "a", "type": "int", "input_value": 3},
            {"name": "b", "type": "int", "input_value": 4}
        ],
        "expected": {"a": 6, "b": 9},
        "function_type": "int"
    }
    
    try:
        print("   📤 提交 C 語言代碼...")
        response = requests.post(
            "http://localhost:8000/judge/submit", 
            json=request_data,
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"   ❌ HTTP 錯誤: {response.status_code}")
            print(f"   回應內容: {response.text}")
            return False
        
        result = response.json()
        print(f"   📋 評測狀態: {result['status']}")
        
        if result['status'] == 'SUCCESS':
            print(f"   ✅ 結果匹配: {result['match']}")
            print(f"   📊 執行時間: {result.get('metrics', {}).get('total_execution_time', 'N/A')}s")
            return True
        else:
            print(f"   ❌ 評測失敗: {result.get('message', 'Unknown error')}")
            if 'compile_output' in result:
                print(f"   編譯錯誤: {result['compile_output']}")
            return False
            
    except requests.RequestException as e:
        print(f"   ❌ 請求失敗: {e}")
        return False
    except Exception as e:
        print(f"   ❌ 測試失敗: {e}")
        return False

def test_cpp_language():
    """測試 C++ 語言評測"""
    print("\n⚡ 開始 C++ 語言評測測試...")
    
    request_data = {
        "language": "cpp",
        "user_code": '''#include <iostream>

int solve(int &a, int &b) {
    a = a * 2;      // 3 * 2 = 6
    b = b * 2 + 1;  // 4 * 2 + 1 = 9
    std::cout << "Hello from C++!" << std::endl;
    return 0;
}''',
        "solve_params": [
            {"name": "a", "type": "int", "input_value": 3},
            {"name": "b", "type": "int", "input_value": 4}
        ],
        "expected": {"a": 6, "b": 9},
        "function_type": "int",
        "compiler_settings": {
            "standard": "cpp17",
            "flags": "-Wall -Wextra -O2 -std=c++17"
        }
    }
    
    try:
        print("   📤 提交 C++ 語言代碼...")
        response = requests.post(
            "http://localhost:8000/judge/submit", 
            json=request_data,
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"   ❌ HTTP 錯誤: {response.status_code}")
            print(f"   回應內容: {response.text}")
            return False
        
        result = response.json()
        print(f"   📋 評測狀態: {result['status']}")
        
        if result['status'] == 'SUCCESS':
            print(f"   ✅ 結果匹配: {result['match']}")
            print(f"   📊 執行時間: {result.get('metrics', {}).get('total_execution_time', 'N/A')}s")
            return True
        else:
            print(f"   ❌ 評測失敗: {result.get('message', 'Unknown error')}")
            return False
            
    except requests.RequestException as e:
        print(f"   ❌ 請求失敗: {e}")
        return False
    except Exception as e:
        print(f"   ❌ 測試失敗: {e}")
        return False

def test_error_handling():
    """測試錯誤處理"""
    print("\n🚨 開始錯誤處理測試...")
    
    # 測試編譯錯誤
    print("   測試編譯錯誤...")
    error_code = {
        "language": "c",
        "user_code": '''#include <stdio.h>
int solve(int *a) {
    *a = 42  // 故意缺少分號
    return 0;
}''',
        "solve_params": [{"name": "a", "type": "int", "input_value": 1}],
        "expected": {"a": 42},
        "function_type": "int"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/judge/submit", 
            json=error_code,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['status'] == 'COMPILE_ERROR':
                print("   ✅ 編譯錯誤正確檢測")
                return True
            else:
                print(f"   ❌ 預期編譯錯誤，但得到: {result['status']}")
                return False
        else:
            print(f"   ❌ HTTP 錯誤: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ 錯誤處理測試失敗: {e}")
        return False

def test_batch_submit():
    """測試批量提交"""
    print("\n📦 開始批量提交測試...")
    
    batch_data = {
        "tests": [
            {
                "language": "c",
                "user_code": "int solve(int *a) { *a = 10; return 0; }",
                "solve_params": [{"name": "a", "type": "int", "input_value": 1}],
                "expected": {"a": 10},
                "function_type": "int"
            },
            {
                "language": "cpp",
                "user_code": "int solve(int &a) { a = 20; return 0; }",
                "solve_params": [{"name": "a", "type": "int", "input_value": 1}],
                "expected": {"a": 20},
                "function_type": "int"
            }
        ],
        "show_progress": False
    }
    
    try:
        print("   📤 提交批量測試...")
        response = requests.post(
            "http://localhost:8000/judge/batch", 
            json=batch_data,
            timeout=120
        )
        
        if response.status_code != 200:
            print(f"   ❌ HTTP 錯誤: {response.status_code}")
            return False
        
        result = response.json()
        summary = result['summary']
        
        print(f"   📊 總測試數: {summary['total_tests']}")
        print(f"   ✅ 成功數: {summary['success_count']}")
        print(f"   ❌ 失敗數: {summary['error_count']}")
        print(f"   📈 成功率: {summary['success_rate']:.2%}")
        
        return summary['success_count'] == summary['total_tests']
        
    except Exception as e:
        print(f"   ❌ 批量提交測試失敗: {e}")
        return False

def run_all_tests():
    """執行所有測試"""
    print("🧪 Judge Microservice API 功能測試")
    print("=" * 50)
    
    # 啟動 API 服務器
    server_process = start_api_server()
    if not server_process:
        print("❌ 無法啟動 API 服務器，測試終止")
        return False
    
    try:
        # 執行測試
        tests = [
            ("基本 API 功能", test_basic_api),
            ("C 語言評測", test_c_language),
            ("C++ 語言評測", test_cpp_language),
            ("錯誤處理", test_error_handling),
            ("批量提交", test_batch_submit)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🧪 執行測試: {test_name}")
            if test_func():
                passed += 1
                print(f"✅ {test_name} 通過")
            else:
                print(f"❌ {test_name} 失敗")
        
        # 測試結果總結
        print("\n" + "=" * 50)
        print(f"🏁 測試完成！通過 {passed}/{total} 個測試")
        
        if passed == total:
            print("🎉 所有測試都通過了！API 正常工作")
            return True
        else:
            print("⚠️ 有部分測試失敗，請檢查問題")
            return False
            
    finally:
        # 停止服務器
        if server_process:
            print("\n🛑 停止 API 服務器...")
            server_process.terminate()
            server_process.wait()

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
