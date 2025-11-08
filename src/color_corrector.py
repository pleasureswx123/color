"""
颜色校正模块
实现多种颜色校正算法
"""

import numpy as np
from scipy.interpolate import griddata
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from typing import Tuple, Optional
from .color_space import ColorSpace


class ColorCorrector:
    """颜色校正器"""
    
    def __init__(self, method: str = 'polynomial'):
        """
        初始化颜色校正器
        
        Args:
            method: 校正方法 ('polynomial', 'lut_3d', 'direct_mapping')
        """
        self.method = method
        self.correction_model = None
        self.reference_colors = None
        self.captured_colors = None
    
    def train(self, reference_colors: np.ndarray, captured_colors: np.ndarray):
        """
        训练校正模型
        
        Args:
            reference_colors: 标准参考颜色 (N, 3) RGB
            captured_colors: 拍摄的颜色 (N, 3) RGB
        """
        self.reference_colors = reference_colors.astype(np.float32)
        self.captured_colors = captured_colors.astype(np.float32)
        
        if self.method == 'polynomial':
            self._train_polynomial()
        elif self.method == 'lut_3d':
            self._train_lut_3d()
        elif self.method == 'direct_mapping':
            self._train_direct_mapping()
    
    def _train_polynomial(self):
        """训练多项式映射模型"""
        # 使用 LAB 颜色空间进行校正
        ref_lab = ColorSpace.rgb_to_lab(
            self.reference_colors.reshape(1, -1, 3)
        ).reshape(-1, 3)
        
        cap_lab = ColorSpace.rgb_to_lab(
            self.captured_colors.reshape(1, -1, 3)
        ).reshape(-1, 3)
        
        # 为每个通道训练多项式回归
        self.correction_model = {}
        
        for channel in range(3):
            # 生成多项式特征 (2 阶)
            poly = PolynomialFeatures(degree=2, include_bias=True)
            X_poly = poly.fit_transform(cap_lab)
            
            # 训练线性回归
            model = LinearRegression()
            model.fit(X_poly, ref_lab[:, channel])
            
            self.correction_model[channel] = {
                'poly': poly,
                'model': model
            }
    
    def _train_lut_3d(self):
        """训练 3D LUT 模型"""
        # 创建 3D 查找表
        lut_size = 16
        lut = np.zeros((lut_size, lut_size, lut_size, 3), dtype=np.float32)
        
        # 为每个 LUT 点计算校正值
        for i in range(lut_size):
            for j in range(lut_size):
                for k in range(lut_size):
                    # 归一化坐标
                    r = i / (lut_size - 1)
                    g = j / (lut_size - 1)
                    b = k / (lut_size - 1)
                    
                    # 查找最近的训练点
                    query_color = np.array([r, g, b]) * 255
                    distances = np.linalg.norm(
                        self.captured_colors - query_color,
                        axis=1
                    )
                    
                    # 使用最近的 4 个点进行插值
                    nearest_indices = np.argsort(distances)[:4]
                    nearest_distances = distances[nearest_indices]
                    
                    # 反距离加权
                    weights = 1.0 / (nearest_distances + 1e-6)
                    weights /= weights.sum()
                    
                    corrected = np.average(
                        self.reference_colors[nearest_indices],
                        axis=0,
                        weights=weights
                    )
                    
                    lut[i, j, k] = corrected
        
        self.correction_model = lut
    
    def _train_direct_mapping(self):
        """训练直接映射模型"""
        # 存储映射关系
        self.correction_model = {
            'reference': self.reference_colors,
            'captured': self.captured_colors
        }
    
    def correct(self, image: np.ndarray) -> np.ndarray:
        """
        对图像进行颜色校正
        
        Args:
            image: 输入图像 (H, W, 3) RGB
            
        Returns:
            校正后的图像 (H, W, 3) RGB
        """
        if self.correction_model is None:
            raise ValueError("模型未训练，请先调用 train() 方法")
        
        if self.method == 'polynomial':
            return self._correct_polynomial(image)
        elif self.method == 'lut_3d':
            return self._correct_lut_3d(image)
        elif self.method == 'direct_mapping':
            return self._correct_direct_mapping(image)
    
    def _correct_polynomial(self, image: np.ndarray) -> np.ndarray:
        """使用多项式映射进行校正"""
        # 转换到 LAB 颜色空间
        lab = ColorSpace.rgb_to_lab(image)
        
        h, w = image.shape[:2]
        lab_reshaped = lab.reshape(-1, 3)
        
        # 应用多项式校正
        corrected_lab = np.zeros_like(lab_reshaped)
        
        for channel in range(3):
            poly = self.correction_model[channel]['poly']
            model = self.correction_model[channel]['model']
            
            X_poly = poly.transform(lab_reshaped)
            corrected_lab[:, channel] = model.predict(X_poly)
        
        corrected_lab = corrected_lab.reshape(h, w, 3)
        
        # 转换回 RGB
        corrected_rgb = ColorSpace.lab_to_rgb(corrected_lab)
        
        return corrected_rgb
    
    def _correct_lut_3d(self, image: np.ndarray) -> np.ndarray:
        """使用 3D LUT 进行校正"""
        lut = self.correction_model
        lut_size = lut.shape[0]
        
        # 归一化图像到 [0, lut_size-1]
        image_normalized = image.astype(np.float32) / 255.0 * (lut_size - 1)
        
        h, w = image.shape[:2]
        corrected = np.zeros_like(image, dtype=np.float32)
        
        # 三线性插值
        for y in range(h):
            for x in range(w):
                r, g, b = image_normalized[y, x]
                
                # 获取整数和小数部分
                r_int, r_frac = int(r), r - int(r)
                g_int, g_frac = int(g), g - int(g)
                b_int, b_frac = int(b), b - int(b)
                
                # 确保索引在范围内
                r_int = min(r_int, lut_size - 2)
                g_int = min(g_int, lut_size - 2)
                b_int = min(b_int, lut_size - 2)
                
                # 三线性插值
                c000 = lut[r_int, g_int, b_int]
                c001 = lut[r_int, g_int, b_int + 1]
                c010 = lut[r_int, g_int + 1, b_int]
                c011 = lut[r_int, g_int + 1, b_int + 1]
                c100 = lut[r_int + 1, g_int, b_int]
                c101 = lut[r_int + 1, g_int, b_int + 1]
                c110 = lut[r_int + 1, g_int + 1, b_int]
                c111 = lut[r_int + 1, g_int + 1, b_int + 1]
                
                c00 = c000 * (1 - r_frac) + c100 * r_frac
                c01 = c001 * (1 - r_frac) + c101 * r_frac
                c10 = c010 * (1 - r_frac) + c110 * r_frac
                c11 = c011 * (1 - r_frac) + c111 * r_frac
                
                c0 = c00 * (1 - g_frac) + c10 * g_frac
                c1 = c01 * (1 - g_frac) + c11 * g_frac
                
                corrected[y, x] = c0 * (1 - b_frac) + c1 * b_frac
        
        return np.clip(corrected, 0, 255).astype(np.uint8)
    
    def _correct_direct_mapping(self, image: np.ndarray) -> np.ndarray:
        """使用直接映射进行校正"""
        reference = self.correction_model['reference']
        captured = self.correction_model['captured']
        
        h, w = image.shape[:2]
        image_reshaped = image.reshape(-1, 3).astype(np.float32)
        
        corrected = np.zeros_like(image_reshaped)
        
        # 对每个像素查找最近的训练颜色
        for i, pixel in enumerate(image_reshaped):
            distances = np.linalg.norm(captured - pixel, axis=1)
            nearest_idx = np.argmin(distances)
            corrected[i] = reference[nearest_idx]
        
        return corrected.reshape(h, w, 3).astype(np.uint8)

