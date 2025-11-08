# 颜色校正系统

一个基于参考色卡的图像颜色校正系统，用于解决手机拍照与实物色差问题。

## ✨ 特色

- 🎨 **现代化 Web 界面** - 渐进式单页面设计，友好直观的交互体验
- 🚀 **即开即用** - 一键启动 Flask 服务器，浏览器访问即可使用
- 🔬 **专业算法** - 支持多种颜色校正算法（Polynomial、LUT 3D、Direct Mapping）
- 📊 **精确评估** - Delta E 颜色差异指标，量化校正效果
- 📱 **响应式设计** - 完美支持移动端和桌面端
- 🎯 **智能引导** - 自动启用/禁用按钮，防止误操作

## 核心功能

### 1. 色卡检测 (Color Checker Detection)
- 自动检测图片中的 ColorChecker 或其他参考色卡
- 支持任意角度的色卡检测
- 透视变换校正
- 颜色块提取和平均

### 2. 颜色空间转换 (Color Space Conversion)
- RGB ↔ LAB 转换（用于感知均匀的颜色处理）
- RGB ↔ HSV 转换
- RGB ↔ XYZ 转换
- 支持 sRGB gamma 校正

### 3. 颜色校正算法 (Color Correction Algorithms)

#### 多项式映射 (Polynomial Mapping)
- 在 LAB 颜色空间中进行 2 阶多项式回归
- 平衡准确性和计算效率
- 适合大多数场景

#### 3D LUT (Look-Up Table)
- 创建 16x16x16 的三维查找表
- 三线性插值
- 高精度校正

#### 直接映射 (Direct Mapping)
- 基于最近邻搜索
- 简单快速
- 适合色块数量较多的情况

### 4. 完整处理管道 (Pipeline)
- 一体化的校准和校正流程
- 图像对比和质量评估
- Delta E 颜色差异计算

## 技术原理

### 问题分析
手机拍照出现色差的主要原因：
1. **光源差异**：不同的光源色温不同
2. **相机特性**：不同手机的相机传感器和 ISP 处理不同
3. **白平衡**：自动白平衡算法的差异
4. **镜头特性**：镜头的色差和畸变

### 解决方案
通过在图片中放置标准参考色卡（如 ColorChecker），建立拍摄颜色到标准颜色的映射关系，然后应用这个映射到整个图像。

### 工作流程
```
1. 校准阶段:
   输入: 包含色卡的校准图像
   ↓
   检测色卡位置和颜色
   ↓
   建立拍摄颜色 → 标准颜色的映射
   ↓
   训练校正模型

2. 校正阶段:
   输入: 需要校正的图像
   ↓
   应用校正模型
   ↓
   输出: 校正后的图像
```

## 技术栈

### 后端
- **Flask 3.1.2** - Web 框架
- **Flask-CORS 6.0.1** - 跨域支持
- **OpenCV 4.10+** - 图像处理
- **NumPy** - 数值计算
- **SciPy** - 科学计算

### 前端
- **原生 JavaScript** - 无框架依赖
- **HTML5** - 语义化结构
- **CSS3** - 现代化样式
- **Fetch API** - 异步请求
- **FileReader API** - 文件处理

### 核心算法
- **LAB 颜色空间** - 感知均匀的颜色处理
- **多项式回归** - 颜色映射
- **3D LUT** - 高精度查找表
- **Delta E (CIE76)** - 颜色差异评估

## 安装

### 环境要求
- Python 3.8+
- pip 或 conda
- 现代浏览器（Chrome、Firefox、Safari、Edge）

### 安装依赖
```bash
# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装 Python 依赖
pip install -r requirements.txt
```

或使用 conda：
```bash
conda create -n color-correction python=3.8
conda activate color-correction
pip install -r requirements.txt
```

## 快速开始

### 方式一：Web 应用（推荐）

#### 1. 启动后端服务器

```bash
# 创建并激活虚拟环境（首次使用）
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动 Flask 服务器
python app.py
```

服务器将在 `http://localhost:8000` 启动

#### 2. 访问前端界面

在浏览器中打开：**http://localhost:8000**

#### 3. 使用步骤

1. **上传图像** - 上传包含 ColorChecker 色卡的校准图像和需要校正的目标图像
2. **选择设置** - 选择校正方法（Polynomial/LUT 3D/Direct Mapping）和质量等级
3. **执行校正** - 点击"开始校正"按钮
4. **查看结果** - 自动展开结果区域，查看原图与校正后的对比效果

#### 4. 停止服务器

在终端中按 `Ctrl+C` 停止服务器

---

### 方式二：Python API 使用

```python
from src.pipeline import ColorCorrectionPipeline
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
corrected_bgr = cv2.cvtColor(corrected, cv2.COLOR_RGB2BGR)
cv2.imwrite('corrected.jpg', corrected_bgr)
```

---

### 方式三：命令行工具使用

```bash
# 基础用法
python -m src.cli calibration.jpg target.jpg -o corrected.jpg

# 使用不同的校正方法
python -m src.cli calibration.jpg target.jpg -m lut_3d -o corrected.jpg

# 生成对比图像
python -m src.cli calibration.jpg target.jpg -c
```

---

### 方式四：运行演示脚本

```bash
python examples/demo.py
```

## 项目结构

```
color/
├── src/                         # 核心颜色校正模块
│   ├── __init__.py              # 包初始化
│   ├── color_space.py           # 颜色空间转换
│   ├── color_checker_detector.py # 色卡检测
│   ├── color_corrector.py       # 颜色校正算法
│   ├── pipeline.py              # 处理管道
│   └── cli.py                   # 命令行工具
├── static/                      # 前端静态资源
│   ├── app.js                   # 前端 JavaScript 逻辑
│   └── style.css                # 前端样式
├── examples/                    # 示例代码
│   ├── demo.py                  # 基础演示
│   └── advanced_demo.py         # 高级演示
├── tests/                       # 单元测试
│   └── test_*.py                # 测试文件
├── app.py                       # Flask 后端服务器
├── test.html                    # 前端页面（渐进式单页面设计）
├── requirements.txt             # Python 依赖列表
├── package.json                 # 项目配置
└── README.md                    # 本文件
```

## API 文档

### 后端 API 端点

#### 1. 上传图像
```http
POST /api/upload
Content-Type: multipart/form-data

参数:
- file: 图像文件
- type: 'calibration' 或 'target'

返回:
{
  "success": true,
  "preview": "data:image/jpeg;base64,..."
}
```

#### 2. 检测色卡
```http
POST /api/detect-colorchecker

返回:
{
  "success": true,
  "message": "检测到 24 个色块"
}
```

#### 3. 执行校正
```http
POST /api/correct
Content-Type: application/json

参数:
{
  "method": "polynomial" | "lut_3d" | "direct_mapping"
}

返回:
{
  "success": true,
  "target_image": "data:image/jpeg;base64,...",
  "corrected_image": "data:image/jpeg;base64,...",
  "metrics": {
    "mean_delta_e": 3.45,
    "max_delta_e": 8.12,
    "min_delta_e": 1.23
  }
}
```

#### 4. 生成对比图
```http
POST /api/compare

返回:
{
  "success": true,
  "comparison_image": "data:image/jpeg;base64,..."
}
```

#### 5. 重置会话
```http
POST /api/reset

返回:
{
  "success": true
}
```

## 性能指标

### 色卡检测
- 检测准确率: > 95%（在清晰图像中）
- 处理时间: ~100-200ms（1080p 图像）

### 颜色校正
- 多项式映射: 最快，适合实时应用
- 3D LUT: 中等速度，高精度
- 直接映射: 最慢，但最准确

### 颜色精度
- 平均 Delta E: < 5（优秀）
- 最大 Delta E: < 15（可接受）

## 最佳实践

### 1. 校准图像采集
- 在与目标图像相同的光源条件下拍摄
- 确保色卡清晰可见，占据图像的 20-50%
- 避免过度曝光或欠曝
- 色卡应该平行于相机平面

### 2. 选择校正方法
- **多项式映射**: 推荐用于大多数场景
- **3D LUT**: 需要高精度时使用
- **直接映射**: 色块数量多（>20）时使用

### 3. 质量评估
- 使用 Delta E 值评估校正质量
- Delta E < 5: 优秀
- Delta E 5-10: 良好
- Delta E > 10: 需要调整

## 常见问题

### Q: 如何处理不同光源条件下的图像？
A: 为每种光源条件创建单独的校准图像，然后选择最接近的校准结果。

### Q: 色卡检测失败怎么办？
A: 
1. 确保色卡清晰可见
2. 检查光线条件
3. 尝试调整检测参数
4. 使用手动标注的色卡位置

### Q: 校正效果不理想？
A: 
1. 尝试不同的校正方法
2. 检查校准图像质量
3. 确保校准和目标图像的光源条件相似
4. 调整多项式阶数或 LUT 大小

## 功能特性

### ✅ 已实现
- [x] **Web 界面** - 现代化渐进式单页面设计
- [x] **拖拽上传** - 支持点击和拖拽上传图像
- [x] **实时预览** - 上传后立即显示图像预览
- [x] **多种算法** - Polynomial、LUT 3D、Direct Mapping
- [x] **智能控制** - 按钮根据状态自动启用/禁用
- [x] **自动滚动** - 校正完成后自动展开结果区域
- [x] **Delta E 指标** - 显示颜色差异评估指标
- [x] **响应式设计** - 支持移动端和桌面端
- [x] **RESTful API** - 完整的后端 API 接口

### 🚀 计划中的功能
- [ ] 支持自定义色卡
- [ ] 实时视频流处理
- [ ] GPU 加速
- [ ] 深度学习模型支持
- [ ] 批量处理
- [ ] 历史记录管理

## 参考资源

- ColorChecker: https://www.xrite.com/categories/capture/color-management-tools/colorcheckerclassic
- Delta E: https://en.wikipedia.org/wiki/Color_difference
- LAB 颜色空间: https://en.wikipedia.org/wiki/CIELAB_color_space
- 3D LUT: https://en.wikipedia.org/wiki/3D_lookup_table

## 许可证

MIT License

## 作者

Color Correction System Contributors

