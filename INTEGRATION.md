# 集成指南 - 如何在项目中使用颜色校正系统

## 集成方式

### 方式 1: 作为 Python 包导入

```python
from src.pipeline import ColorCorrectionPipeline
from src.color_checker_detector import ColorCheckerDetector
from src.color_space import ColorSpace
import cv2

# 创建处理管道
pipeline = ColorCorrectionPipeline(correction_method='polynomial')

# 加载图像
calibration_image = cv2.imread('calibration.jpg')
calibration_image = cv2.cvtColor(calibration_image, cv2.COLOR_BGR2RGB)

target_image = cv2.imread('target.jpg')
target_image = cv2.cvtColor(target_image, cv2.COLOR_BGR2RGB)

# 执行处理
corrected, info = pipeline.process(calibration_image, target_image)

# 保存结果
result = cv2.cvtColor(corrected, cv2.COLOR_RGB2BGR)
cv2.imwrite('corrected.jpg', result)
```

### 方式 2: 作为命令行工具

```bash
# 基础用法
python -m src.cli calibration.jpg target.jpg -o corrected.jpg

# 使用不同方法
python -m src.cli calibration.jpg target.jpg -m lut_3d -o corrected.jpg

# 生成对比图像
python -m src.cli calibration.jpg target.jpg -c
```

### 方式 3: 作为 Web 服务

```python
from flask import Flask, request, send_file
from src.pipeline import ColorCorrectionPipeline
import cv2
import io

app = Flask(__name__)
pipeline = ColorCorrectionPipeline()

@app.route('/calibrate', methods=['POST'])
def calibrate():
    file = request.files['image']
    image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    success = pipeline.calibrate(image)
    return {'success': success}

@app.route('/correct', methods=['POST'])
def correct():
    file = request.files['image']
    image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    corrected = pipeline.correct_image(image)
    corrected_bgr = cv2.cvtColor(corrected, cv2.COLOR_RGB2BGR)
    
    _, buffer = cv2.imencode('.jpg', corrected_bgr)
    return send_file(io.BytesIO(buffer), mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(debug=True)
```

## 实际应用示例

### 示例 1: 电商产品拍照系统

```python
import os
from pathlib import Path
from src.pipeline import ColorCorrectionPipeline
import cv2

class ProductPhotoProcessor:
    def __init__(self, calibration_image_path):
        self.pipeline = ColorCorrectionPipeline(correction_method='polynomial')
        
        # 一次校准
        cal_image = cv2.imread(calibration_image_path)
        cal_image = cv2.cvtColor(cal_image, cv2.COLOR_BGR2RGB)
        self.pipeline.calibrate(cal_image)
    
    def process_product_photos(self, input_dir, output_dir):
        """批量处理产品照片"""
        Path(output_dir).mkdir(exist_ok=True)
        
        for filename in os.listdir(input_dir):
            if filename.lower().endswith(('.jpg', '.png')):
                input_path = os.path.join(input_dir, filename)
                output_path = os.path.join(output_dir, filename)
                
                # 加载图像
                image = cv2.imread(input_path)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                
                # 校正
                corrected = self.pipeline.correct_image(image)
                
                # 保存
                corrected_bgr = cv2.cvtColor(corrected, cv2.COLOR_RGB2BGR)
                cv2.imwrite(output_path, corrected_bgr)
                
                print(f"✓ 已处理: {filename}")

# 使用
processor = ProductPhotoProcessor('calibration.jpg')
processor.process_product_photos('input_photos', 'output_photos')
```

### 示例 2: 实时视频处理

```python
import cv2
from src.pipeline import ColorCorrectionPipeline

def process_video(input_video, output_video, calibration_image_path):
    """实时处理视频"""
    pipeline = ColorCorrectionPipeline()
    
    # 校准
    cal_image = cv2.imread(calibration_image_path)
    cal_image = cv2.cvtColor(cal_image, cv2.COLOR_BGR2RGB)
    pipeline.calibrate(cal_image)
    
    # 打开视频
    cap = cv2.VideoCapture(input_video)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # 创建视频写入器
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
    
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 转换为 RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 校正
        corrected = pipeline.correct_image(frame_rgb)
        
        # 转换回 BGR
        corrected_bgr = cv2.cvtColor(corrected, cv2.COLOR_RGB2BGR)
        
        # 写入
        out.write(corrected_bgr)
        
        frame_count += 1
        if frame_count % 30 == 0:
            print(f"已处理 {frame_count} 帧")
    
    cap.release()
    out.release()
    print(f"✓ 视频处理完成: {output_video}")

# 使用
process_video('input.mp4', 'output.mp4', 'calibration.jpg')
```

### 示例 3: 医学影像处理

```python
from src.pipeline import ColorCorrectionPipeline
from src.color_space import ColorSpace
import cv2
import numpy as np

class MedicalImageProcessor:
    def __init__(self, reference_image_path):
        self.pipeline = ColorCorrectionPipeline(correction_method='lut_3d')
        
        # 使用高精度的 3D LUT 方法
        ref_image = cv2.imread(reference_image_path)
        ref_image = cv2.cvtColor(ref_image, cv2.COLOR_BGR2RGB)
        self.pipeline.calibrate(ref_image)
    
    def process_and_analyze(self, image_path):
        """处理并分析医学图像"""
        # 加载图像
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 校正
        corrected = self.pipeline.correct_image(image)
        
        # 分析颜色分布
        original_lab = ColorSpace.rgb_to_lab(image)
        corrected_lab = ColorSpace.rgb_to_lab(corrected)
        
        # 计算统计信息
        stats = {
            'original_l_mean': original_lab[..., 0].mean(),
            'corrected_l_mean': corrected_lab[..., 0].mean(),
            'original_a_std': original_lab[..., 1].std(),
            'corrected_a_std': corrected_lab[..., 1].std(),
            'original_b_std': original_lab[..., 2].std(),
            'corrected_b_std': corrected_lab[..., 2].std(),
        }
        
        return corrected, stats

# 使用
processor = MedicalImageProcessor('reference.jpg')
corrected, stats = processor.process_and_analyze('medical_image.jpg')
print(f"原始 L 均值: {stats['original_l_mean']:.2f}")
print(f"校正后 L 均值: {stats['corrected_l_mean']:.2f}")
```

### 示例 4: 自定义色卡

```python
from src.color_corrector import ColorCorrector
from src.color_space import ColorSpace
import numpy as np
import cv2

# 定义自定义参考颜色
custom_reference_colors = np.array([
    [255, 0, 0],      # 红
    [0, 255, 0],      # 绿
    [0, 0, 255],      # 蓝
    [255, 255, 0],    # 黄
    [255, 0, 255],    # 洋红
    [0, 255, 255],    # 青
    [255, 255, 255],  # 白
    [0, 0, 0],        # 黑
], dtype=np.uint8)

# 定义拍摄的颜色（模拟色差）
captured_colors = np.array([
    [255, 50, 50],    # 红（偏绿）
    [50, 255, 50],    # 绿（偏红）
    [50, 50, 255],    # 蓝（正常）
    [255, 255, 50],   # 黄（偏蓝）
    [255, 50, 255],   # 洋红（偏绿）
    [50, 255, 255],   # 青（偏红）
    [255, 255, 255],  # 白（正常）
    [0, 0, 0],        # 黑（正常）
], dtype=np.uint8)

# 创建校正器
corrector = ColorCorrector(method='polynomial')
corrector.train(custom_reference_colors, captured_colors)

# 校正图像
image = cv2.imread('image.jpg')
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
corrected = corrector.correct(image)

# 保存
corrected_bgr = cv2.cvtColor(corrected, cv2.COLOR_RGB2BGR)
cv2.imwrite('corrected.jpg', corrected_bgr)
```

## 性能优化建议

### 1. 缓存校正模型

```python
import pickle

# 保存模型
with open('correction_model.pkl', 'wb') as f:
    pickle.dump(pipeline.corrector, f)

# 加载模型
with open('correction_model.pkl', 'rb') as f:
    pipeline.corrector = pickle.load(f)
```

### 2. 并行处理

```python
from concurrent.futures import ThreadPoolExecutor
import os

def process_image(image_path):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return pipeline.correct_image(image)

# 并行处理多个图像
image_paths = [os.path.join('input', f) for f in os.listdir('input')]
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process_image, image_paths))
```

### 3. 图像预处理

```python
# 降低分辨率以加快处理
def process_with_resize(image, scale=0.5):
    h, w = image.shape[:2]
    small_image = cv2.resize(image, (int(w*scale), int(h*scale)))
    corrected_small = pipeline.correct_image(small_image)
    corrected = cv2.resize(corrected_small, (w, h))
    return corrected
```

## 故障排除

### 问题 1: 导入错误

```python
# 确保 src 目录在 Python 路径中
import sys
sys.path.insert(0, '/path/to/color')
from src.pipeline import ColorCorrectionPipeline
```

### 问题 2: 内存不足

```python
# 使用更小的 LUT 大小或多项式方法
pipeline = ColorCorrectionPipeline(correction_method='polynomial')
```

### 问题 3: 处理速度慢

```python
# 使用多项式方法而不是 3D LUT
# 或者降低图像分辨率
# 或者使用多线程处理
```

## 总结

颜色校正系统可以轻松集成到各种应用中：
- 电商平台
- 医学影像系统
- 视频处理软件
- 摄影应用
- 质量检测系统

选择合适的集成方式和参数，可以获得最佳的性能和精度。

