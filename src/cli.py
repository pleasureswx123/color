"""
命令行工具
用于快速进行颜色校正
"""

import argparse
import cv2
import sys
from pathlib import Path
from .pipeline import ColorCorrectionPipeline


def load_image(image_path: str):
    """加载图像"""
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"无法加载图像: {image_path}")
    
    # 转换 BGR 到 RGB
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def save_image(image, output_path: str):
    """保存图像"""
    # 转换 RGB 到 BGR
    image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    cv2.imwrite(output_path, image_bgr)
    print(f"✓ 图像已保存: {output_path}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='颜色校正工具 - 使用参考色卡进行图像颜色校正'
    )
    
    parser.add_argument(
        'calibration_image',
        help='包含参考色卡的校准图像路径'
    )
    
    parser.add_argument(
        'target_image',
        help='需要校正的目标图像路径'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='corrected.jpg',
        help='输出图像路径 (默认: corrected.jpg)'
    )
    
    parser.add_argument(
        '-m', '--method',
        choices=['polynomial', 'lut_3d', 'direct_mapping'],
        default='polynomial',
        help='校正方法 (默认: polynomial)'
    )
    
    parser.add_argument(
        '-c', '--comparison',
        action='store_true',
        help='生成对比图像'
    )
    
    args = parser.parse_args()
    
    try:
        print("\n" + "="*60)
        print("颜色校正工具")
        print("="*60)
        
        # 加载图像
        print(f"\n加载校准图像: {args.calibration_image}")
        calibration_image = load_image(args.calibration_image)
        
        print(f"加载目标图像: {args.target_image}")
        target_image = load_image(args.target_image)
        
        # 创建处理管道
        print(f"\n使用方法: {args.method}")
        pipeline = ColorCorrectionPipeline(correction_method=args.method)
        
        # 执行处理
        print("\n处理中...")
        corrected, info = pipeline.process(calibration_image, target_image)
        
        if info['status'] == 'success':
            print("✓ 校正成功")
            
            # 保存结果
            save_image(corrected, args.output)
            
            # 生成对比图像
            if args.comparison:
                comparison_path = Path(args.output).stem + '_comparison.jpg'
                comparison_img = pipeline.create_comparison_image(target_image, corrected)
                save_image(comparison_img, comparison_path)
            
            # 显示统计信息
            comparison_stats = pipeline.compare_images(target_image, corrected)
            print(f"\n颜色差异统计:")
            print(f"  平均 Delta E: {comparison_stats['mean_delta_e']:.2f}")
            print(f"  最大 Delta E: {comparison_stats['max_delta_e']:.2f}")
            print(f"  最小 Delta E: {comparison_stats['min_delta_e']:.2f}")
            
        else:
            print(f"✗ 校正失败: {info['status']}")
            sys.exit(1)
        
        print("\n" + "="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

