"""
高级演示脚本
展示颜色校正系统的高级用法和场景
"""

import sys
import os
import cv2
import numpy as np
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.pipeline import ColorCorrectionPipeline
from src.color_checker_detector import ColorCheckerDetector
from src.color_space import ColorSpace


def create_realistic_calibration_image():
    """
    创建更逼真的校准图像
    模拟实际的 ColorChecker 拍摄
    """
    image = np.ones((600, 800, 3), dtype=np.uint8) * 180
    
    # 添加背景纹理
    for i in range(0, 600, 20):
        for j in range(0, 800, 20):
            if (i // 20 + j // 20) % 2 == 0:
                image[i:i+20, j:j+20] = np.clip(
                    image[i:i+20, j:j+20].astype(np.float32) * 0.95,
                    0, 255
                ).astype(np.uint8)
    
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
        
        # 转换 BGR 格式
        color_bgr = color[::-1]
        cv2.rectangle(image, (x1, y1), (x2, y2), tuple(color_bgr), -1)
        
        # 添加边框
        cv2.rectangle(image, (x1, y1), (x2, y2), (100, 100, 100), 2)
    
    # 添加高斯噪声模拟相机噪声
    noise = np.random.normal(0, 5, image.shape)
    image = np.clip(image.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    
    return image


def create_realistic_target_image():
    """
    创建更逼真的目标图像
    模拟手机拍照的色差
    """
    # 创建一个包含多种颜色的图像
    image = np.ones((400, 600, 3), dtype=np.uint8) * 200
    
    # 定义颜色块
    color_blocks = [
        ([255, 0, 0], "红色"),
        ([0, 255, 0], "绿色"),
        ([0, 0, 255], "蓝色"),
        ([255, 255, 0], "黄色"),
        ([255, 0, 255], "洋红"),
        ([0, 255, 255], "青色"),
    ]
    
    for idx, (color, name) in enumerate(color_blocks):
        x1 = (idx % 3) * 200
        y1 = (idx // 3) * 200
        x2 = x1 + 200
        y2 = y1 + 200
        
        color_bgr = color[::-1]
        cv2.rectangle(image, (x1, y1), (x2, y2), tuple(color_bgr), -1)
    
    # 模拟手机拍照的色差
    # 增加红色偏差，减少绿色，蓝色偏移
    image_float = image.astype(np.float32)
    image_float[:, :, 2] = np.clip(image_float[:, :, 2] * 1.25, 0, 255)  # 增加红色
    image_float[:, :, 1] = np.clip(image_float[:, :, 1] * 0.85, 0, 255)  # 减少绿色
    image_float[:, :, 0] = np.clip(image_float[:, :, 0] * 0.95, 0, 255)  # 减少蓝色
    
    # 添加高斯噪声
    noise = np.random.normal(0, 3, image_float.shape)
    image_float = np.clip(image_float + noise, 0, 255)
    
    return image_float.astype(np.uint8)


def demo_method_comparison():
    """比较不同的校正方法"""
    print("\n" + "="*60)
    print("演示: 不同校正方法的对比")
    print("="*60)
    
    # 创建图像
    calibration_image = create_realistic_calibration_image()
    target_image = create_realistic_target_image()
    
    methods = ['polynomial', 'lut_3d', 'direct_mapping']
    results = {}
    
    for method in methods:
        print(f"\n使用方法: {method}")
        
        pipeline = ColorCorrectionPipeline(correction_method=method)
        corrected, info = pipeline.process(calibration_image, target_image)
        
        if info['status'] == 'success':
            # 计算统计信息
            stats = pipeline.compare_images(target_image, corrected)
            results[method] = {
                'image': corrected,
                'stats': stats
            }
            
            print(f"  ✓ 校正成功")
            print(f"    平均 Delta E: {stats['mean_delta_e']:.2f}")
            print(f"    最大 Delta E: {stats['max_delta_e']:.2f}")
        else:
            print(f"  ✗ 校正失败")
    
    # 保存结果
    output_dir = Path(__file__).parent.parent / 'output'
    output_dir.mkdir(exist_ok=True)
    
    # 保存原始图像
    cv2.imwrite(
        str(output_dir / 'target_original.jpg'),
        cv2.cvtColor(target_image, cv2.COLOR_RGB2BGR)
    )
    
    # 保存每种方法的结果
    for method, result in results.items():
        cv2.imwrite(
            str(output_dir / f'corrected_{method}.jpg'),
            cv2.cvtColor(result['image'], cv2.COLOR_RGB2BGR)
        )
    
    # 打印对比总结
    print("\n" + "-"*60)
    print("方法对比总结:")
    print("-"*60)
    for method, result in results.items():
        stats = result['stats']
        print(f"\n{method}:")
        print(f"  平均 Delta E: {stats['mean_delta_e']:.2f}")
        print(f"  最大 Delta E: {stats['max_delta_e']:.2f}")
        print(f"  标准差: {stats['std_delta_e']:.2f}")


def demo_batch_processing():
    """批量处理演示"""
    print("\n" + "="*60)
    print("演示: 批量处理")
    print("="*60)
    
    # 创建校准图像
    calibration_image = create_realistic_calibration_image()
    
    # 创建处理管道
    pipeline = ColorCorrectionPipeline(correction_method='polynomial')
    
    # 校准
    if not pipeline.calibrate(calibration_image):
        print("✗ 校准失败")
        return
    
    print("✓ 校准成功")
    
    # 处理多个目标图像
    output_dir = Path(__file__).parent.parent / 'output'
    output_dir.mkdir(exist_ok=True)
    
    for i in range(3):
        print(f"\n处理图像 {i+1}/3...")
        
        # 创建目标图像
        target_image = create_realistic_target_image()
        
        # 校正
        corrected = pipeline.correct_image(target_image)
        
        # 保存结果
        output_path = output_dir / f'batch_corrected_{i+1}.jpg'
        cv2.imwrite(
            str(output_path),
            cv2.cvtColor(corrected, cv2.COLOR_RGB2BGR)
        )
        
        print(f"  ✓ 已保存: {output_path}")


def demo_color_analysis():
    """颜色分析演示"""
    print("\n" + "="*60)
    print("演示: 颜色分析")
    print("="*60)
    
    # 创建图像
    calibration_image = create_realistic_calibration_image()
    target_image = create_realistic_target_image()
    
    # 创建处理管道
    pipeline = ColorCorrectionPipeline(correction_method='polynomial')
    corrected, info = pipeline.process(calibration_image, target_image)
    
    if info['status'] == 'success':
        # 分析颜色分布
        print("\n原始图像颜色分析:")
        target_lab = ColorSpace.rgb_to_lab(target_image)
        print(f"  L 范围: [{target_lab[..., 0].min():.1f}, {target_lab[..., 0].max():.1f}]")
        print(f"  A 范围: [{target_lab[..., 1].min():.1f}, {target_lab[..., 1].max():.1f}]")
        print(f"  B 范围: [{target_lab[..., 2].min():.1f}, {target_lab[..., 2].max():.1f}]")
        
        print("\n校正后图像颜色分析:")
        corrected_lab = ColorSpace.rgb_to_lab(corrected)
        print(f"  L 范围: [{corrected_lab[..., 0].min():.1f}, {corrected_lab[..., 0].max():.1f}]")
        print(f"  A 范围: [{corrected_lab[..., 1].min():.1f}, {corrected_lab[..., 1].max():.1f}]")
        print(f"  B 范围: [{corrected_lab[..., 2].min():.1f}, {corrected_lab[..., 2].max():.1f}]")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("颜色校正系统 - 高级演示")
    print("="*60)
    
    try:
        demo_method_comparison()
        demo_batch_processing()
        demo_color_analysis()
        
        print("\n" + "="*60)
        print("所有演示完成！")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

