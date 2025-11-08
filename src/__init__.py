"""
颜色校正系统
用于手机拍照的颜色校正和色差补偿
"""

from .color_space import ColorSpace
from .color_checker_detector import ColorCheckerDetector
from .color_corrector import ColorCorrector
from .pipeline import ColorCorrectionPipeline

__all__ = [
    'ColorSpace',
    'ColorCheckerDetector',
    'ColorCorrector',
    'ColorCorrectionPipeline'
]

__version__ = '1.0.0'

