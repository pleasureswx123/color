"""
颜色校正处理管道
整合检测、校正、输出的完整流程
"""

import cv2
import numpy as np
from typing import Optional, Tuple
from .color_checker_detector import ColorCheckerDetector
from .color_corrector import ColorCorrector
from .color_space import ColorSpace


class ColorCorrectionPipeline:
    """颜色校正处理管道"""
    
    def __init__(self, correction_method: str = 'polynomial'):
        """
        初始化处理管道
        
        Args:
            correction_method: 校正方法 ('polynomial', 'lut_3d', 'direct_mapping')
        """
        self.detector = ColorCheckerDetector()
        self.corrector = ColorCorrector(method=correction_method)
        self.is_trained = False
    
    def calibrate(self, calibration_image: np.ndarray) -> bool:
        """
        使用包含色卡的校准图像进行校准
        
        Args:
            calibration_image: 包含色卡的图像 (H, W, 3) RGB
            
        Returns:
            是否校准成功
        """
        # 检测色卡
        detection_result = self.detector.detect(calibration_image)
        
        if not detection_result['detected']:
            print("未检测到色卡")
            return False
        
        print(f"色卡检测置信度: {detection_result['confidence']:.2%}")
        
        # 获取检测到的颜色
        patches = detection_result['patches']
        captured_colors = np.array([p['color'] for p in patches])
        
        # 获取标准参考颜色
        reference_colors = self.detector.get_reference_colors()
        
        # 确保颜色数量匹配
        if len(captured_colors) != len(reference_colors):
            print(f"颜色数量不匹配: 检测到 {len(captured_colors)}, 期望 {len(reference_colors)}")
            return False
        
        # 训练校正模型
        self.corrector.train(reference_colors, captured_colors)
        self.is_trained = True
        
        print(f"校准成功，检测到 {len(captured_colors)} 个色块")
        return True
    
    def correct_image(self, image: np.ndarray) -> np.ndarray:
        """
        对图像进行颜色校正
        
        Args:
            image: 输入图像 (H, W, 3) RGB
            
        Returns:
            校正后的图像 (H, W, 3) RGB
        """
        if not self.is_trained:
            raise ValueError("管道未校准，请先调用 calibrate() 方法")
        
        return self.corrector.correct(image)
    
    def process(self, calibration_image: np.ndarray, 
                target_image: np.ndarray) -> Tuple[np.ndarray, dict]:
        """
        完整处理流程：校准 + 校正
        
        Args:
            calibration_image: 包含色卡的校准图像
            target_image: 需要校正的目标图像
            
        Returns:
            (校正后的图像, 处理信息字典)
        """
        info = {}
        
        # 校准
        if not self.calibrate(calibration_image):
            info['status'] = 'calibration_failed'
            return None, info
        
        info['calibration_success'] = True
        
        # 校正
        corrected = self.correct_image(target_image)
        
        info['status'] = 'success'
        info['correction_method'] = self.corrector.method
        
        return corrected, info
    
    def compare_images(self, original: np.ndarray, 
                      corrected: np.ndarray) -> dict:
        """
        比较原始图像和校正后的图像
        
        Args:
            original: 原始图像
            corrected: 校正后的图像
            
        Returns:
            比较结果字典
        """
        # 转换到 LAB 颜色空间
        original_lab = ColorSpace.rgb_to_lab(original)
        corrected_lab = ColorSpace.rgb_to_lab(corrected)
        
        # 计算 Delta E (CIE76)
        delta_e = np.sqrt(np.sum((original_lab - corrected_lab) ** 2, axis=2))
        
        # 统计信息
        stats = {
            'mean_delta_e': float(delta_e.mean()),
            'max_delta_e': float(delta_e.max()),
            'min_delta_e': float(delta_e.min()),
            'std_delta_e': float(delta_e.std()),
            'pixels_improved': int((delta_e > 0).sum())
        }
        
        return stats
    
    def create_comparison_image(self, original: np.ndarray,
                               corrected: np.ndarray) -> np.ndarray:
        """
        创建对比图像 (左原始，右校正)
        
        Args:
            original: 原始图像
            corrected: 校正后的图像
            
        Returns:
            对比图像
        """
        # 确保尺寸相同
        h, w = original.shape[:2]
        
        # 创建对比图像
        comparison = np.hstack([original, corrected])
        
        return comparison

