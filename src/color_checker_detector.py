"""
色卡检测模块
自动检测图片中的 ColorChecker 或其他参考色卡
"""

import cv2
import numpy as np
from typing import Tuple, List, Optional


class ColorCheckerDetector:
    """色卡检测器"""
    
    # 标准 ColorChecker 24 色的参考值 (sRGB)
    STANDARD_COLORS = np.array([
        [115, 82, 68],      # 深棕色
        [194, 150, 130],    # 浅棕色
        [98, 122, 157],     # 蓝色
        [87, 108, 67],      # 绿色
        [133, 128, 177],    # 紫色
        [103, 188, 167],    # 青色
        [214, 126, 44],     # 橙色
        [80, 91, 166],      # 深蓝
        [193, 90, 99],      # 红色
        [94, 60, 108],      # 深紫
        [157, 188, 64],     # 黄绿
        [224, 163, 46],     # 黄色
        [56, 61, 150],      # 深蓝2
        [70, 148, 73],      # 绿色2
        [175, 54, 60],      # 红色2
        [231, 199, 31],     # 黄色2
        [187, 86, 149],     # 洋红
        [8, 133, 161],      # 青色2
        [243, 243, 242],    # 白色
        [200, 200, 200],    # 浅灰
        [160, 160, 160],    # 中灰
        [122, 122, 121],    # 深灰
        [85, 85, 85],       # 更深灰
        [52, 52, 52],       # 黑色
    ], dtype=np.uint8)
    
    def __init__(self, grid_size: Tuple[int, int] = (6, 4)):
        """
        初始化色卡检测器
        
        Args:
            grid_size: 色卡网格大小 (宽, 高)，默认 ColorChecker 是 6x4
        """
        self.grid_size = grid_size
        self.total_colors = grid_size[0] * grid_size[1]
    
    def detect(self, image: np.ndarray) -> Optional[dict]:
        """
        检测图片中的色卡
        
        Args:
            image: 输入图像 (H, W, 3) RGB 格式
            
        Returns:
            检测结果字典，包含：
            - 'detected': 是否检测到色卡
            - 'patches': 色卡块的位置和颜色
            - 'corners': 色卡的四个角点
            - 'confidence': 检测置信度
        """
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # 边缘检测
        edges = cv2.Canny(gray, 50, 150)
        
        # 查找轮廓
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return {'detected': False, 'confidence': 0}
        
        # 查找矩形轮廓
        rectangles = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 100:  # 过滤太小的轮廓
                continue
            
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            if len(approx) == 4:
                rectangles.append(approx)
        
        if not rectangles:
            return {'detected': False, 'confidence': 0}
        
        # 查找最大的矩形（假设色卡是最大的矩形）
        largest_rect = max(rectangles, key=lambda x: cv2.contourArea(x))
        
        # 获取四个角点
        corners = self._order_corners(largest_rect.reshape(4, 2))
        
        # 透视变换
        warped = self._perspective_transform(image, corners)
        
        # 提取色卡块
        patches = self._extract_patches(warped)
        
        # 计算置信度
        confidence = self._calculate_confidence(patches)
        
        return {
            'detected': True,
            'patches': patches,
            'corners': corners,
            'confidence': confidence,
            'warped': warped
        }
    
    def _order_corners(self, corners: np.ndarray) -> np.ndarray:
        """
        排序四个角点 (左上, 右上, 右下, 左下)
        """
        # 计算中心
        center = corners.mean(axis=0)
        
        # 按角度排序
        angles = np.arctan2(corners[:, 1] - center[1], corners[:, 0] - center[0])
        sorted_indices = np.argsort(angles)
        
        return corners[sorted_indices]
    
    def _perspective_transform(self, image: np.ndarray, corners: np.ndarray) -> np.ndarray:
        """
        透视变换，将色卡变为正方形
        """
        # 计算输出大小
        width = int(np.linalg.norm(corners[1] - corners[0]))
        height = int(np.linalg.norm(corners[2] - corners[1]))
        
        # 目标点
        dst_corners = np.array([
            [0, 0],
            [width, 0],
            [width, height],
            [0, height]
        ], dtype=np.float32)
        
        # 透视变换矩阵
        matrix = cv2.getPerspectiveTransform(
            corners.astype(np.float32),
            dst_corners
        )
        
        # 应用变换
        warped = cv2.warpPerspective(image, matrix, (width, height))
        
        return warped
    
    def _extract_patches(self, warped: np.ndarray) -> List[dict]:
        """
        从透视变换后的图像中提取色卡块
        """
        h, w = warped.shape[:2]
        patch_h = h // self.grid_size[1]
        patch_w = w // self.grid_size[0]
        
        patches = []
        for y in range(self.grid_size[1]):
            for x in range(self.grid_size[0]):
                y1 = y * patch_h
                y2 = (y + 1) * patch_h
                x1 = x * patch_w
                x2 = (x + 1) * patch_w
                
                patch = warped[y1:y2, x1:x2]
                
                # 计算平均颜色
                avg_color = patch.mean(axis=(0, 1)).astype(np.uint8)
                
                patches.append({
                    'position': (x, y),
                    'color': avg_color,
                    'patch': patch
                })
        
        return patches
    
    def _calculate_confidence(self, patches: List[dict]) -> float:
        """
        计算检测置信度
        基于检测到的色卡块数量和颜色均匀性
        """
        if not patches:
            return 0.0
        
        # 块数置信度
        block_confidence = len(patches) / self.total_colors
        
        # 颜色均匀性置信度
        uniformity_scores = []
        for patch_info in patches:
            patch = patch_info['patch']
            # 计算颜色标准差
            std = patch.std(axis=(0, 1)).mean()
            # 标准差越小，均匀性越好
            uniformity = 1.0 / (1.0 + std / 50.0)
            uniformity_scores.append(uniformity)
        
        uniformity_confidence = np.mean(uniformity_scores) if uniformity_scores else 0.0
        
        # 综合置信度
        confidence = 0.6 * block_confidence + 0.4 * uniformity_confidence
        
        return float(confidence)
    
    def get_reference_colors(self) -> np.ndarray:
        """获取标准参考颜色"""
        return self.STANDARD_COLORS.copy()

