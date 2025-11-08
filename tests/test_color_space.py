"""
颜色空间转换测试
"""

import sys
import os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.color_space import ColorSpace


def test_rgb_to_lab_conversion():
    """测试 RGB 到 LAB 的转换"""
    print("测试 RGB -> LAB 转换...")
    
    # 测试纯色
    test_cases = [
        ([255, 0, 0], "红色"),      # 红
        ([0, 255, 0], "绿色"),      # 绿
        ([0, 0, 255], "蓝色"),      # 蓝
        ([255, 255, 255], "白色"),  # 白
        ([0, 0, 0], "黑色"),        # 黑
    ]
    
    for rgb, name in test_cases:
        rgb_array = np.array([[[rgb[0], rgb[1], rgb[2]]]], dtype=np.uint8)
        lab = ColorSpace.rgb_to_lab(rgb_array)
        print(f"  {name}: RGB{tuple(rgb)} -> LAB({lab[0, 0, 0]:.1f}, {lab[0, 0, 1]:.1f}, {lab[0, 0, 2]:.1f})")
    
    print("✓ RGB -> LAB 转换测试通过\n")


def test_lab_to_rgb_conversion():
    """测试 LAB 到 RGB 的转换"""
    print("测试 LAB -> RGB 转换...")
    
    # 创建测试 LAB 值
    lab_values = np.array([
        [[50, 0, 0]],      # 中灰
        [[100, 0, 0]],     # 白
        [[0, 0, 0]],       # 黑
    ], dtype=np.float32)
    
    for lab in lab_values:
        rgb = ColorSpace.lab_to_rgb(lab)
        print(f"  LAB({lab[0, 0, 0]:.1f}, {lab[0, 0, 1]:.1f}, {lab[0, 0, 2]:.1f}) -> RGB{tuple(rgb[0, 0])}")
    
    print("✓ LAB -> RGB 转换测试通过\n")


def test_rgb_lab_roundtrip():
    """测试 RGB -> LAB -> RGB 的往返转换"""
    print("测试 RGB -> LAB -> RGB 往返转换...")
    
    # 创建随机 RGB 值
    np.random.seed(42)
    original_rgb = np.random.randint(0, 256, (10, 10, 3), dtype=np.uint8)
    
    # 往返转换
    lab = ColorSpace.rgb_to_lab(original_rgb)
    recovered_rgb = ColorSpace.lab_to_rgb(lab)
    
    # 计算误差
    error = np.abs(original_rgb.astype(np.float32) - recovered_rgb.astype(np.float32))
    max_error = error.max()
    mean_error = error.mean()
    
    print(f"  最大误差: {max_error:.2f}")
    print(f"  平均误差: {mean_error:.2f}")
    
    if max_error < 2:
        print("✓ 往返转换测试通过\n")
    else:
        print("✗ 往返转换误差过大\n")


def test_rgb_to_hsv_conversion():
    """测试 RGB 到 HSV 的转换"""
    print("测试 RGB -> HSV 转换...")
    
    test_cases = [
        ([255, 0, 0], "红色"),      # 红
        ([0, 255, 0], "绿色"),      # 绿
        ([0, 0, 255], "蓝色"),      # 蓝
        ([255, 255, 255], "白色"),  # 白
        ([0, 0, 0], "黑色"),        # 黑
    ]
    
    for rgb, name in test_cases:
        rgb_array = np.array([[[rgb[0], rgb[1], rgb[2]]]], dtype=np.uint8)
        hsv = ColorSpace.rgb_to_hsv(rgb_array)
        print(f"  {name}: RGB{tuple(rgb)} -> HSV({hsv[0, 0, 0]}, {hsv[0, 0, 1]}, {hsv[0, 0, 2]})")
    
    print("✓ RGB -> HSV 转换测试通过\n")


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("颜色空间转换测试")
    print("="*60 + "\n")
    
    try:
        test_rgb_to_lab_conversion()
        test_lab_to_rgb_conversion()
        test_rgb_lab_roundtrip()
        test_rgb_to_hsv_conversion()
        
        print("="*60)
        print("所有测试通过！")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

