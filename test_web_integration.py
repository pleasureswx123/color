"""
Web 服务集成测试脚本
测试前后端通信和颜色校正功能
"""

import os
import sys
import requests
import json
import cv2
import numpy as np
from io import BytesIO
from PIL import Image

# 测试配置
API_BASE = 'http://localhost:5000'
TIMEOUT = 30

def create_test_image(width=800, height=600, color_type='calibration'):
    """创建测试图像"""
    if color_type == 'calibration':
        # 创建包含色块的校准图像
        image = np.ones((height, width, 3), dtype=np.uint8) * 200
        
        # 添加 ColorChecker 模拟色块
        colors = [
            (255, 0, 0),      # 红
            (0, 255, 0),      # 绿
            (0, 0, 255),      # 蓝
            (255, 255, 0),    # 黄
            (255, 0, 255),    # 洋红
            (0, 255, 255),    # 青
        ]
        
        block_size = 100
        for i, color in enumerate(colors):
            x = (i % 3) * block_size + 50
            y = (i // 3) * block_size + 50
            image[y:y+block_size, x:x+block_size] = color
    else:
        # 创建目标图像（模拟色差）
        image = np.ones((height, width, 3), dtype=np.uint8) * 180
        
        # 添加色差的色块
        colors = [
            (255, 100, 100),  # 红（偏绿）
            (100, 255, 100),  # 绿（偏红）
            (100, 100, 255),  # 蓝（正常）
            (255, 255, 100),  # 黄（偏蓝）
            (255, 100, 255),  # 洋红（偏绿）
            (100, 255, 255),  # 青（偏红）
        ]
        
        block_size = 100
        for i, color in enumerate(colors):
            x = (i % 3) * block_size + 50
            y = (i // 3) * block_size + 50
            image[y:y+block_size, x:x+block_size] = color
    
    return image

def image_to_bytes(image):
    """将 numpy 数组转换为字节"""
    _, buffer = cv2.imencode('.jpg', image)
    return BytesIO(buffer.tobytes())

def test_api_status():
    """测试 API 状态"""
    print("\n" + "="*60)
    print("测试 1: 检查 API 状态")
    print("="*60)
    
    try:
        response = requests.get(f'{API_BASE}/api/status', timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print("✓ API 状态检查成功")
            print(f"  - 有校准图像: {data['has_calibration']}")
            print(f"  - 有目标图像: {data['has_target']}")
            print(f"  - 有结果: {data['has_result']}")
            return True
        else:
            print(f"✗ API 状态检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        return False

def test_upload_calibration():
    """测试上传校准图像"""
    print("\n" + "="*60)
    print("测试 2: 上传校准图像")
    print("="*60)
    
    try:
        # 创建测试图像
        image = create_test_image(color_type='calibration')
        
        # 上传
        files = {'file': ('calibration.jpg', image_to_bytes(image), 'image/jpeg')}
        data = {'type': 'calibration'}
        
        response = requests.post(
            f'{API_BASE}/api/upload',
            files=files,
            data=data,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✓ 校准图像上传成功")
                print(f"  - 消息: {result['message']}")
                print(f"  - 图像大小: {result['size']}")
                return True
            else:
                print(f"✗ 上传失败: {result['error']}")
                return False
        else:
            print(f"✗ 上传失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 上传异常: {e}")
        return False

def test_upload_target():
    """测试上传目标图像"""
    print("\n" + "="*60)
    print("测试 3: 上传目标图像")
    print("="*60)
    
    try:
        # 创建测试图像
        image = create_test_image(color_type='target')
        
        # 上传
        files = {'file': ('target.jpg', image_to_bytes(image), 'image/jpeg')}
        data = {'type': 'target'}
        
        response = requests.post(
            f'{API_BASE}/api/upload',
            files=files,
            data=data,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✓ 目标图像上传成功")
                print(f"  - 消息: {result['message']}")
                print(f"  - 图像大小: {result['size']}")
                return True
            else:
                print(f"✗ 上传失败: {result['error']}")
                return False
        else:
            print(f"✗ 上传失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 上传异常: {e}")
        return False

def test_detect_colorchecks():
    """测试色卡检测"""
    print("\n" + "="*60)
    print("测试 4: 检测色卡")
    print("="*60)
    
    try:
        response = requests.post(
            f'{API_BASE}/api/detect-colorchecks',
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✓ 色卡检测成功")
                print(f"  - 消息: {result['message']}")
                print(f"  - 置信度: {result['confidence']:.2%}")
                return True
            else:
                print(f"⚠ 色卡检测失败: {result['error']}")
                print(f"  - 置信度: {result.get('confidence', 0):.2%}")
                return False
        else:
            print(f"✗ 检测失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 检测异常: {e}")
        return False

def test_correct_image(method='polynomial'):
    """测试颜色校正"""
    print("\n" + "="*60)
    print(f"测试 5: 颜色校正 ({method})")
    print("="*60)
    
    try:
        payload = {'method': method}
        response = requests.post(
            f'{API_BASE}/api/correct',
            json=payload,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✓ 颜色校正成功")
                print(f"  - 消息: {result['message']}")
                print(f"  - 平均 Delta E: {result['stats']['mean_delta_e']:.2f}")
                print(f"  - 最大 Delta E: {result['stats']['max_delta_e']:.2f}")
                print(f"  - 最小 Delta E: {result['stats']['min_delta_e']:.2f}")
                print(f"  - 使用方法: {result['stats']['method']}")
                return True
            else:
                print(f"✗ 校正失败: {result['error']}")
                return False
        else:
            print(f"✗ 校正失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 校正异常: {e}")
        return False

def test_compare_images():
    """测试生成对比图像"""
    print("\n" + "="*60)
    print("测试 6: 生成对比图像")
    print("="*60)
    
    try:
        response = requests.post(
            f'{API_BASE}/api/compare',
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✓ 对比图像生成成功")
                return True
            else:
                print(f"✗ 生成失败: {result['error']}")
                return False
        else:
            print(f"✗ 生成失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 生成异常: {e}")
        return False

def test_download_image():
    """测试下载图像"""
    print("\n" + "="*60)
    print("测试 7: 下载校正后的图像")
    print("="*60)
    
    try:
        response = requests.get(
            f'{API_BASE}/api/download',
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            print("✓ 图像下载成功")
            print(f"  - 文件大小: {len(response.content)} 字节")
            return True
        else:
            print(f"✗ 下载失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 下载异常: {e}")
        return False

def test_reset_session():
    """测试重置会话"""
    print("\n" + "="*60)
    print("测试 8: 重置会话")
    print("="*60)
    
    try:
        response = requests.post(
            f'{API_BASE}/api/reset',
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✓ 会话重置成功")
                return True
            else:
                print(f"✗ 重置失败: {result['error']}")
                return False
        else:
            print(f"✗ 重置失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 重置异常: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🧪 Web 服务集成测试")
    print("="*60)
    print(f"API 地址: {API_BASE}")
    
    results = []
    
    # 运行测试
    results.append(("API 状态检查", test_api_status()))
    results.append(("上传校准图像", test_upload_calibration()))
    results.append(("上传目标图像", test_upload_target()))
    results.append(("检测色卡", test_detect_colorchecks()))
    results.append(("颜色校正", test_correct_image('polynomial')))
    results.append(("生成对比图像", test_compare_images()))
    results.append(("下载图像", test_download_image()))
    results.append(("重置会话", test_reset_session()))
    
    # 打印总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status}: {name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！Web 服务运行正常。")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败。")

if __name__ == '__main__':
    print("\n💡 提示: 请确保 Flask 服务器正在运行 (python app.py)")
    print("等待 3 秒后开始测试...\n")
    
    import time
    time.sleep(3)
    
    run_all_tests()

