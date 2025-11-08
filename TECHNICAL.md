# 技术文档 - 颜色校正系统

## 问题分析

### 手机拍照色差的根本原因

1. **光源差异**
   - 不同光源的色温不同（日光 6500K, 白炽灯 2700K）
   - 光源的光谱分布不同

2. **相机特性**
   - 不同手机的传感器响应曲线不同
   - ISP (Image Signal Processor) 处理算法不同
   - 白平衡算法的差异

3. **镜头特性**
   - 镜头的色差（chromatic aberration）
   - 镜头的畸变

### 解决方案原理

通过在图片中放置**标准参考色卡**（如 ColorChecker），建立拍摄颜色到标准颜色的映射关系：

```
拍摄颜色 (Captured Color) → 映射函数 → 标准颜色 (Reference Color)
```

然后将这个映射应用到整个图像。

## 核心算法

### 1. 颜色空间转换

#### RGB 到 LAB 转换

LAB 颜色空间是感知均匀的，更适合颜色校正：

```
RGB (0-1) → 应用 Gamma 校正 → RGB Linear
RGB Linear → 转换矩阵 → XYZ
XYZ → 非线性变换 → LAB
```

**优点**:
- L 通道代表亮度（0-100）
- A 通道代表红-绿（-128 到 127）
- B 通道代表黄-蓝（-128 到 127）
- 颜色差异与人眼感知相关

#### 转换矩阵 (sRGB)

```
RGB → XYZ:
[X]   [0.4124564  0.3575761  0.1804375] [R]
[Y] = [0.2126729  0.7151522  0.0721750] [G]
[Z]   [0.0193339  0.1191920  0.9503041] [B]

XYZ → RGB:
[R]   [3.2404542  -1.5371385  -0.4985314] [X]
[G] = [-0.9692660  1.8760108   0.0415560] [Y]
[B]   [0.0556434  -0.2040259   1.0572252] [Z]
```

### 2. 色卡检测

#### 检测流程

```
输入图像
  ↓
灰度转换
  ↓
边缘检测 (Canny)
  ↓
轮廓查找
  ↓
矩形识别
  ↓
透视变换
  ↓
色块提取
  ↓
颜色平均
```

#### 关键步骤

1. **边缘检测**: 使用 Canny 算子检测色卡边界
2. **轮廓识别**: 查找 4 边形轮廓
3. **透视变换**: 将倾斜的色卡变为正方形
4. **色块提取**: 将色卡分成 6×4 的 24 个色块
5. **颜色计算**: 计算每个色块的平均颜色

#### 置信度计算

```
置信度 = 0.6 × 块数置信度 + 0.4 × 均匀性置信度

块数置信度 = 检测到的块数 / 期望块数
均匀性置信度 = 平均(1 / (1 + 标准差 / 50))
```

### 3. 颜色校正算法

#### 方法 1: 多项式映射 (Polynomial Mapping)

在 LAB 颜色空间中进行 2 阶多项式回归：

```
对于每个通道 (L, A, B):
  y = w0 + w1*x1 + w2*x2 + w3*x3 + w4*x1² + w5*x2² + w6*x3² + ...
  
其中:
  x = [L, A, B] (输入颜色)
  y = 校正后的颜色
  w = 回归系数
```

**优点**:
- 快速（线性回归）
- 平衡准确性和效率
- 适合大多数场景

**缺点**:
- 可能无法捕捉复杂的颜色映射

#### 方法 2: 3D LUT (Look-Up Table)

创建 16×16×16 的三维查找表：

```
LUT[r][g][b] = 校正后的颜色

对于任意输入颜色 (r, g, b):
  1. 归一化到 [0, 15]
  2. 获取 8 个相邻的 LUT 值
  3. 三线性插值
```

**三线性插值公式**:

```
c = c000(1-r)(1-g)(1-b) + c100*r(1-g)(1-b) + 
    c010(1-r)*g(1-b) + c110*r*g(1-b) +
    c001(1-r)(1-g)*b + c101*r(1-g)*b +
    c011(1-r)*g*b + c111*r*g*b
```

**优点**:
- 高精度
- 可以捕捉复杂的颜色映射

**缺点**:
- 计算量较大
- 需要更多的训练数据

#### 方法 3: 直接映射 (Direct Mapping)

基于最近邻搜索：

```
对于每个像素:
  1. 在训练颜色中查找最近的颜色
  2. 返回对应的参考颜色
```

**优点**:
- 最准确（基于实际训练数据）
- 无需参数调整

**缺点**:
- 最慢
- 需要足够的训练样本

### 4. 质量评估 - Delta E

Delta E (CIE76) 是衡量两个颜色差异的标准：

```
ΔE = √((ΔL)² + (ΔA)² + (ΔB)²)

其中:
  ΔL = L1 - L2
  ΔA = A1 - A2
  ΔB = B1 - B2
```

**评估标准**:
- ΔE < 1: 人眼无法察觉
- ΔE 1-3: 优秀
- ΔE 3-5: 很好
- ΔE 5-10: 良好
- ΔE > 10: 需要改进

## 实现细节

### 颜色空间转换的数值稳定性

1. **Gamma 校正**:
   ```
   if RGB > 0.04045:
       RGB_linear = ((RGB + 0.055) / 1.055)^2.4
   else:
       RGB_linear = RGB / 12.92
   ```

2. **LAB 转换中的非线性变换**:
   ```
   delta = 6/29
   if f > delta:
       f_inv = f^3
   else:
       f_inv = 3 * delta^2 * (f - 4/29)
   ```

### 多项式回归的正则化

为了避免过拟合，可以添加 L2 正则化：

```
Loss = MSE + λ * ||w||²
```

### 3D LUT 的内存优化

对于 16×16×16 的 LUT：
- 内存占用: 16 × 16 × 16 × 3 × 4 bytes = 48 KB
- 可以轻松存储在内存中

## 性能优化

### 1. 向量化计算

使用 NumPy 的向量化操作代替循环：

```python
# 慢
for i in range(h):
    for j in range(w):
        result[i, j] = func(image[i, j])

# 快
result = func(image)  # NumPy 广播
```

### 2. 缓存计算结果

```python
# 缓存转换矩阵
self.transform_matrix = precompute_matrix()

# 缓存多项式特征
self.poly_features = PolynomialFeatures(degree=2)
```

### 3. 并行处理

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process_image, images))
```

## 扩展方向

### 1. 深度学习方法

使用神经网络学习颜色映射：

```
输入: RGB 图像
↓
CNN 特征提取
↓
全连接层
↓
输出: 校正后的 RGB 图像
```

### 2. 自适应校正

根据图像内容自适应调整校正参数。

### 3. 实时处理

使用 GPU 加速进行实时视频处理。

### 4. 自定义色卡

支持用户定义的参考颜色。

## 参考资源

- **色彩科学**: 
  - CIE LAB 颜色空间: https://en.wikipedia.org/wiki/CIELAB_color_space
  - Delta E: https://en.wikipedia.org/wiki/Color_difference

- **图像处理**:
  - OpenCV 文档: https://docs.opencv.org/
  - NumPy 文档: https://numpy.org/doc/

- **机器学习**:
  - scikit-learn: https://scikit-learn.org/
  - 多项式回归: https://en.wikipedia.org/wiki/Polynomial_regression

- **色卡标准**:
  - ColorChecker: https://www.xrite.com/
  - Macbeth ColorChecker: https://en.wikipedia.org/wiki/ColorChecker

