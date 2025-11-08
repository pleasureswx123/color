"""
颜色校正系统演示脚本
展示如何使用颜色校正系统进行图像处理
"""

import sys
import os
import cv2
import numpy as np
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.pipeline import ColorCorrectionPipeline
from src.color_checker_detector import ColorCheckerDetector
from src.color_space import ColorSpace


def create_synthetic_calibration_image():
    """
    创建合成的校准图像（包含色卡）
    用于演示目的
    """
    # 创建 800x600 的图像
    image = np.ones((600, 800, 3), dtype=np.uint8) * 200
    
    # 获取标准色卡颜色
    detector = ColorCheckerDetector()
    colors = detector.get_reference_colors()
    
    # 绘制 6x4 的色卡
    patch_size = 80
    start_x, start_y = 100, 100
    
    for idx, color in enumerate(colors):
        row = idx // 6
        col = idx % 6
        
        x1 = start_x + col * patch_size
        y1 = start_y + row * patch_size
        x2 = x1 + patch_size
        y2 = y1 + patch_size
        
        # 转换 BGR 格式用于 OpenCV
        color_bgr = color[::-1]
        cv2.rectangle(image, (x1, y1), (x2, y2), tuple(color_bgr), -1)
    
    return image


def create_synthetic_target_image():
    """
    创建合成的目标图像
    模拟手机拍照的色差
    """
    # 创建一个彩色图像
    image = np.ones((400, 600, 3), dtype=np.uint8)
    
    # 添加不同的颜色块
    colors = [
        [255, 0, 0],      # 红
        [0, 255, 0],      # 绿
        [0, 0, 255],      # 蓝
        [255, 255, 0],    # 黄
        [255, 0, 255],    # 洋红
        [0, 255, 255],    # 青
    ]
    
    for idx, color in enumerate(colors):
        x1 = (idx % 3) * 200
        y1 = (idx // 3) * 200
        x2 = x1 + 200
        y2 = y1 + 200
        
        color_bgr = color[::-1]
        cv2.rectangle(image, (x1, y1), (x2, y2), tuple(color_bgr), -1)
    
    # 模拟手机拍照的色差（增加红色偏差）
    image_float = image.astype(np.float32)
    image_float[:, :, 2] = np.clip(image_float[:, :, 2] * 1.3, 0, 255)  # 增加红色
    image_float[:, :, 1] = np.clip(image_float[:, :, 1] * 0.9, 0, 255)  # 减少绿色
    
    return image_float.astype(np.uint8)


def demo_basic_correction():
    """基础颜色校正演示"""
    print("\n" + "="*60)
    print("演示 1: 基础颜色校正")
    print("="*60)
    
    # 创建合成图像
    calibration_image = create_synthetic_calibration_image()
    target_image = create_synthetic_target_image()
    
    # 创建处理管道
    pipeline = ColorCorrectionPipeline(correction_method='polynomial')
    
    # 执行完整处理流程
    corrected, info = pipeline.process(calibration_image, target_image)
    
    if info['status'] == 'success':
        print(f"✓ 校正成功")
        print(f"  校正方法: {info['correction_method']}")
        
        # 比较图像
        comparison = pipeline.compare_images(target_image, corrected)
        print(f"\n颜色差异统计:")
        print(f"  平均 Delta E: {comparison['mean_delta_e']:.2f}")
        print(f"  最大 Delta E: {comparison['max_delta_e']:.2f}")
        print(f"  最小 Delta E: {comparison['min_delta_e']:.2f}")
        print(f"  标准差: {comparison['std_delta_e']:.2f}")
        
        # 保存结果
        output_dir = Path(__file__).parent.parent / 'output'
        output_dir.mkdir(exist_ok=True)
        
        # 转换为 BGR 用于 OpenCV
        cv2.imwrite(
            str(output_dir / 'original.jpg'),
            cv2.cvtColor(target_image, cv2.COLOR_RGB2BGR)
        )
        cv2.imwrite(
            str(output_dir / 'corrected.jpg'),
            cv2.cvtColor(corrected, cv2.COLOR_RGB2BGR)
        )
        
        # 创建对比图像
        comparison_img = pipeline.create_comparison_image(target_image, corrected)
        cv2.imwrite(
            str(output_dir / 'comparison.jpg'),
            cv2.cvtColor(comparison_img, cv2.COLOR_RGB2BGR)
        )
        
        print(f"\n✓ 结果已保存到 {output_dir}")
    else:
        print(f"✗ 校正失败: {info['status']}")


def demo_color_space_conversion():
    """颜色空间转换演示"""
    print("\n" + "="*60)
    print("演示 2: 颜色空间转换")
    print("="*60)
    
    # 创建测试颜色
    test_colors = np.array([
        [[255, 0, 0]],      # 红
        [[0, 255, 0]],      # 绿
        [[0, 0, 255]],      # 蓝
        [[255, 255, 255]],  # 白
        [[0, 0, 0]],        # 黑
    ], dtype=np.uint8)
    
    print("\nRGB -> LAB 转换:")
    for i, color in enumerate(test_colors):
        lab = ColorSpace.rgb_to_lab(color)
        print(f"  RGB{tuple(color[0])}: LAB({lab[0, 0, 0]:.1f}, {lab[0, 0, 1]:.1f}, {lab[0, 0, 2]:.1f})")
    
    print("\nRGB -> HSV 转换:")
    for i, color in enumerate(test_colors):
        hsv = ColorSpace.rgb_to_hsv(color)
        print(f"  RGB{tuple(color[0])}: HSV({hsv[0, 0, 0]}, {hsv[0, 0, 1]}, {hsv[0, 0, 2]})")


def demo_color_checker_detection():
    """色卡检测演示"""
    print("\n" + "="*60)
    print("演示 3: 色卡检测")
    print("="*60)
    
    # 创建合成校准图像
    calibration_image = create_synthetic_calibration_image()
    
    # 检测色卡
    detector = ColorCheckerDetector()
    result = detector.detect(calibration_image)
    
    if result['detected']:
        print(f"✓ 检测到色卡")
        print(f"  检测置信度: {result['confidence']:.2%}")
        print(f"  检测到的色块数: {len(result['patches'])}")
        
        # 显示前 6 个色块的颜色
        print(f"\n前 6 个色块的颜色 (RGB):")
        for i, patch in enumerate(result['patches'][:6]):
            color = patch['color']
            print(f"  块 {i+1}: RGB({color[0]}, {color[1]}, {color[2]})")
    else:
        print(f"✗ 未检测到色卡")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("颜色校正系统演示")
    print("="*60)
    
    try:
        # 运行演示
        demo_color_space_conversion()
        demo_color_checker_detection()
        demo_basic_correction()
        
        print("\n" + "="*60)
        print("所有演示完成！")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

