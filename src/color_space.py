"""
颜色空间转换模块
支持 RGB, LAB, HSV, XYZ 等颜色空间的转换
"""

import numpy as np
from scipy.ndimage import map_coordinates


class ColorSpace:
    """颜色空间转换工具类"""
    
    @staticmethod
    def rgb_to_lab(rgb):
        """
        RGB 转 LAB 颜色空间
        输入: RGB 图像 (H, W, 3), 值范围 [0, 255]
        输出: LAB 图像 (H, W, 3), L: [0, 100], A: [-128, 127], B: [-128, 127]
        """
        # 归一化到 [0, 1]
        rgb_normalized = rgb.astype(np.float32) / 255.0
        
        # RGB 到 XYZ
        xyz = ColorSpace._rgb_to_xyz(rgb_normalized)
        
        # XYZ 到 LAB
        lab = ColorSpace._xyz_to_lab(xyz)
        
        return lab
    
    @staticmethod
    def lab_to_rgb(lab):
        """
        LAB 转 RGB 颜色空间
        输入: LAB 图像 (H, W, 3)
        输出: RGB 图像 (H, W, 3), 值范围 [0, 255]
        """
        # LAB 到 XYZ
        xyz = ColorSpace._lab_to_xyz(lab)
        
        # XYZ 到 RGB
        rgb_normalized = ColorSpace._xyz_to_rgb(xyz)
        
        # 转换到 [0, 255] 并裁剪
        rgb = np.clip(rgb_normalized * 255.0, 0, 255).astype(np.uint8)
        
        return rgb
    
    @staticmethod
    def _rgb_to_xyz(rgb):
        """RGB (0-1) 到 XYZ"""
        # 应用 gamma 校正
        mask = rgb > 0.04045
        rgb_linear = np.where(
            mask,
            np.power((rgb + 0.055) / 1.055, 2.4),
            rgb / 12.92
        )
        
        # RGB 到 XYZ 的转换矩阵 (sRGB)
        transform = np.array([
            [0.4124564, 0.3575761, 0.1804375],
            [0.2126729, 0.7151522, 0.0721750],
            [0.0193339, 0.1191920, 0.9503041]
        ])
        
        # 应用转换
        shape = rgb_linear.shape
        rgb_reshaped = rgb_linear.reshape(-1, 3)
        xyz_reshaped = rgb_reshaped @ transform.T
        xyz = xyz_reshaped.reshape(shape)
        
        return xyz
    
    @staticmethod
    def _xyz_to_rgb(xyz):
        """XYZ 到 RGB (0-1)"""
        # XYZ 到 RGB 的转换矩阵 (sRGB)
        transform = np.array([
            [3.2404542, -1.5371385, -0.4985314],
            [-0.9692660, 1.8760108, 0.0415560],
            [0.0556434, -0.2040259, 1.0572252]
        ])
        
        # 应用转换
        shape = xyz.shape
        xyz_reshaped = xyz.reshape(-1, 3)
        rgb_reshaped = xyz_reshaped @ transform.T
        rgb_linear = rgb_reshaped.reshape(shape)
        
        # 反向 gamma 校正
        mask = rgb_linear > 0.0031308
        rgb = np.where(
            mask,
            1.055 * np.power(rgb_linear, 1/2.4) - 0.055,
            12.92 * rgb_linear
        )
        
        return np.clip(rgb, 0, 1)
    
    @staticmethod
    def _xyz_to_lab(xyz):
        """XYZ 到 LAB"""
        # D65 标准光源
        ref_white = np.array([0.95047, 1.00000, 1.08883])
        
        # 归一化
        xyz_normalized = xyz / ref_white
        
        # 应用非线性变换
        delta = 6/29
        mask = xyz_normalized > delta**3
        f = np.where(
            mask,
            np.power(xyz_normalized, 1/3),
            xyz_normalized / (3 * delta**2) + 4/29
        )
        
        # 计算 LAB
        L = 116 * f[..., 1] - 16
        A = 500 * (f[..., 0] - f[..., 1])
        B = 200 * (f[..., 1] - f[..., 2])
        
        lab = np.stack([L, A, B], axis=-1)
        return lab
    
    @staticmethod
    def _lab_to_xyz(lab):
        """LAB 到 XYZ"""
        L = lab[..., 0]
        A = lab[..., 1]
        B = lab[..., 2]
        
        # 反向计算
        fy = (L + 16) / 116
        fx = A / 500 + fy
        fz = fy - B / 200
        
        # 反向非线性变换
        delta = 6/29
        
        def f_inv(f):
            mask = f > delta
            return np.where(
                mask,
                np.power(f, 3),
                3 * delta**2 * (f - 4/29)
            )
        
        # D65 标准光源
        ref_white = np.array([0.95047, 1.00000, 1.08883])
        
        xyz = np.stack([
            f_inv(fx) * ref_white[0],
            f_inv(fy) * ref_white[1],
            f_inv(fz) * ref_white[2]
        ], axis=-1)
        
        return xyz
    
    @staticmethod
    def rgb_to_hsv(rgb):
        """RGB 到 HSV"""
        rgb_normalized = rgb.astype(np.float32) / 255.0
        
        r, g, b = rgb_normalized[..., 0], rgb_normalized[..., 1], rgb_normalized[..., 2]
        
        max_val = np.maximum(np.maximum(r, g), b)
        min_val = np.minimum(np.minimum(r, g), b)
        delta = max_val - min_val
        
        # 计算 H
        h = np.zeros_like(r)
        mask_r = max_val == r
        mask_g = max_val == g
        mask_b = max_val == b
        
        h[mask_r] = 60 * (((g[mask_r] - b[mask_r]) / delta[mask_r]) % 6)
        h[mask_g] = 60 * (((b[mask_g] - r[mask_g]) / delta[mask_g]) + 2)
        h[mask_b] = 60 * (((r[mask_b] - g[mask_b]) / delta[mask_b]) + 4)
        
        # 计算 S
        s = np.where(max_val != 0, delta / max_val, 0)
        
        # 计算 V
        v = max_val
        
        hsv = np.stack([h, s * 255, v * 255], axis=-1).astype(np.uint8)
        return hsv

