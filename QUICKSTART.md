# 快速开始指南

## 项目概述

这是一个基于参考色卡的图像颜色校正系统，用于解决手机拍照与实物色差问题。

### 核心功能
- ✅ 自动色卡检测
- ✅ 多种颜色校正算法
- ✅ 颜色空间转换（RGB, LAB, HSV, XYZ）
- ✅ 完整的处理管道
- ✅ 质量评估和对比

## 安装

### 1. 创建虚拟环境
```bash
cd /Users/shangwenxue/work/swx/color
python3 -m venv venv
source venv/bin/activate
```

### 2. 安装依赖
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 快速使用

### 方式 1: Python API

```python
from src.pipeline import ColorCorrectionPipeline
import cv2

# 加载图像
cal_img = cv2.imread('calibration.jpg')
cal_img = cv2.cvtColor(cal_img, cv2.COLOR_BGR2RGB)

target_img = cv2.imread('target.jpg')
target_img = cv2.cvtColor(target_img, cv2.COLOR_BGR2RGB)

# 创建处理管道
pipeline = ColorCorrectionPipeline(correction_method='polynomial')

# 执行处理
corrected, info = pipeline.process(cal_img, target_img)

# 保存结果
result = cv2.cvtColor(corrected, cv2.COLOR_RGB2BGR)
cv2.imwrite('result.jpg', result)
```

### 方式 2: 命令行工具

```bash
# 基础用法
python -m src.cli calibration.jpg target.jpg -o corrected.jpg

# 使用不同方法
python -m src.cli calibration.jpg target.jpg -m lut_3d -o corrected.jpg

# 生成对比图像
python -m src.cli calibration.jpg target.jpg -c
```

### 方式 3: 运行演示

```bash
# 基础演示
python examples/demo.py

# 高级演示
python examples/advanced_demo.py
```

## 项目结构

```
color/
├── src/                          # 核心源代码
│   ├── __init__.py              # 包初始化
│   ├── color_space.py           # 颜色空间转换
│   ├── color_checker_detector.py # 色卡检测
│   ├── color_corrector.py       # 颜色校正算法
│   ├── pipeline.py              # 处理管道
│   └── cli.py                   # 命令行工具
├── examples/                     # 演示脚本
│   ├── demo.py                  # 基础演示
│   └── advanced_demo.py          # 高级演示
├── tests/                        # 测试代码
│   └── test_color_space.py      # 颜色空间测试
├── requirements.txt              # 依赖列表
├── setup.py                      # 安装脚本
├── README.md                     # 详细文档
├── GUIDE.md                      # 实用指南
└── QUICKSTART.md                 # 本文件
```

## 核心模块说明

### 1. ColorSpace (颜色空间转换)
```python
from src.color_space import ColorSpace

# RGB 到 LAB
lab = ColorSpace.rgb_to_lab(rgb_image)

# LAB 到 RGB
rgb = ColorSpace.lab_to_rgb(lab_image)

# RGB 到 HSV
hsv = ColorSpace.rgb_to_hsv(rgb_image)
```

### 2. ColorCheckerDetector (色卡检测)
```python
from src.color_checker_detector import ColorCheckerDetector

detector = ColorCheckerDetector()
result = detector.detect(image)

if result['detected']:
    print(f"检测置信度: {result['confidence']:.2%}")
    patches = result['patches']
    for patch in patches:
        print(f"颜色: {patch['color']}")
```

### 3. ColorCorrector (颜色校正)
```python
from src.color_corrector import ColorCorrector

# 创建校正器
corrector = ColorCorrector(method='polynomial')

# 训练模型
corrector.train(reference_colors, captured_colors)

# 校正图像
corrected = corrector.correct(image)
```

### 4. ColorCorrectionPipeline (完整管道)
```python
from src.pipeline import ColorCorrectionPipeline

# 创建管道
pipeline = ColorCorrectionPipeline(correction_method='polynomial')

# 校准
pipeline.calibrate(calibration_image)

# 校正
corrected = pipeline.correct_image(target_image)

# 比较
stats = pipeline.compare_images(original, corrected)
print(f"平均 Delta E: {stats['mean_delta_e']:.2f}")
```

## 校正方法对比

| 方法 | 速度 | 精度 | 适用场景 |
|------|------|------|---------|
| polynomial | ⚡⚡⚡ | ⭐⭐ | 大多数场景 |
| lut_3d | ⚡⚡ | ⭐⭐⭐ | 需要高精度 |
| direct_mapping | ⚡ | ⭐⭐⭐⭐ | 色块数量多 |

## 常见问题

### Q: 如何处理不同光源？
A: 为每种光源创建单独的校准图像，选择最接近的结果。

### Q: 色卡检测失败？
A: 确保色卡清晰可见，光线条件良好，色卡占据图像 20-50%。

### Q: 校正效果不理想？
A: 尝试不同的校正方法，检查校准图像质量，确保光源条件相似。

## 性能指标

- **色卡检测**: ~100-200ms (1080p 图像)
- **颜色校正**: 
  - 多项式: ~50-100ms
  - 3D LUT: ~100-200ms
  - 直接映射: ~200-500ms
- **颜色精度**: 平均 Delta E < 5 (优秀)

## 下一步

1. 查看 `README.md` 了解详细技术原理
2. 查看 `GUIDE.md` 了解实际应用场景
3. 运行 `examples/demo.py` 查看演示
4. 根据需要调整参数和方法

## 技术栈

- **Python 3.8+**
- **OpenCV**: 图像处理
- **NumPy**: 数值计算
- **SciPy**: 科学计算
- **scikit-learn**: 机器学习
- **Pillow**: 图像 I/O

## 许可证

MIT License

## 支持

如有问题，请查看：
- README.md - 详细文档
- GUIDE.md - 实用指南
- examples/ - 演示代码
- tests/ - 测试代码

