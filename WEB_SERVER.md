# Web 服务器运行指南

## 📋 概述

这是一个完整的 Web 应用，包含：
- **后端**: Flask Web 服务器 (`app.py`)
- **前端**: 单页面应用 (`test.html`)
- **静态资源**: CSS 和 JavaScript (`static/` 目录)

## 🚀 快速开始

### 1. 安装依赖

首先确保已安装所有必要的 Python 包：

```bash
cd /Users/shangwenxue/work/swx/color

# 激活虚拟环境
source venv/bin/activate

# 安装 Flask 和 CORS 支持
pip install flask flask-cors
```

### 2. 启动 Web 服务器

```bash
# 方式 1: 直接运行
python app.py

# 方式 2: 使用 Flask 命令
export FLASK_APP=app.py
flask run

# 方式 3: 指定端口
python app.py --port 8000
```

### 3. 访问应用

打开浏览器访问：
```
http://localhost:5000
```

## 📁 文件结构

```
color/
├── app.py                    # Flask 后端服务器
├── test.html                 # 前端主页面
├── static/
│   ├── style.css            # 样式表
│   └── app.js               # 前端逻辑
├── src/                      # 颜色校正核心模块
│   ├── color_space.py
│   ├── color_checker_detector.py
│   ├── color_corrector.py
│   ├── pipeline.py
│   └── cli.py
└── uploads/                  # 上传文件临时存储
```

## 🔌 API 接口文档

### 1. 上传图像

**端点**: `POST /api/upload`

**参数**:
- `file`: 图像文件 (multipart/form-data)
- `type`: 图像类型 ('calibration' 或 'target')

**响应**:
```json
{
  "success": true,
  "message": "校准图像上传成功",
  "preview": "data:image/jpeg;base64,...",
  "size": [1080, 1920, 3]
}
```

### 2. 检测色卡

**端点**: `POST /api/detect-colorchecks`

**响应**:
```json
{
  "success": true,
  "detected": true,
  "confidence": 0.95,
  "message": "色卡检测成功，置信度: 95%"
}
```

### 3. 执行颜色校正

**端点**: `POST /api/correct`

**请求体**:
```json
{
  "method": "polynomial"
}
```

**响应**:
```json
{
  "success": true,
  "message": "颜色校正完成",
  "corrected": "data:image/jpeg;base64,...",
  "stats": {
    "mean_delta_e": 3.45,
    "max_delta_e": 8.92,
    "min_delta_e": 0.12,
    "method": "polynomial"
  }
}
```

### 4. 生成对比图像

**端点**: `POST /api/compare`

**响应**:
```json
{
  "success": true,
  "comparison": "data:image/jpeg;base64,..."
}
```

### 5. 下载校正后的图像

**端点**: `GET /api/download`

**响应**: 返回 JPEG 图像文件

### 6. 重置会话

**端点**: `POST /api/reset`

**响应**:
```json
{
  "success": true,
  "message": "会话已重置"
}
```

### 7. 获取状态

**端点**: `GET /api/status`

**响应**:
```json
{
  "success": true,
  "has_calibration": true,
  "has_target": true,
  "has_result": false,
  "method": "polynomial"
}
```

## 🎨 前端功能

### 上传功能
- ✅ 支持拖拽上传
- ✅ 支持点击选择文件
- ✅ 实时预览
- ✅ 文件验证

### 参数选择
- ✅ 三种校正方法选择
- ✅ 方法说明和对比
- ✅ 实时状态更新

### 结果展示
- ✅ 原图和校正图并排显示
- ✅ 质量指标展示（Delta E）
- ✅ 对比图像生成
- ✅ 结果下载

### 用户交互
- ✅ 进度显示
- ✅ 错误提示
- ✅ 成功反馈
- ✅ 响应式设计

## 🔧 配置选项

### Flask 配置

在 `app.py` 中修改：

```python
# 上传文件夹
UPLOAD_FOLDER = 'uploads'

# 允许的文件格式
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp', 'tiff'}

# 最大文件大小 (50MB)
MAX_FILE_SIZE = 50 * 1024 * 1024

# 服务器配置
app.run(debug=True, host='0.0.0.0', port=5000)
```

### 前端配置

在 `static/app.js` 中修改：

```javascript
// API 基础 URL
const API_BASE = 'http://localhost:5000'

// 超时时间
const TIMEOUT = 30000
```

## 🐛 故障排除

### 问题 1: 端口已被占用

```bash
# 查看占用端口的进程
lsof -i :5000

# 使用不同的端口
python app.py --port 8000
```

### 问题 2: 模块导入错误

```bash
# 确保在项目目录中
cd /Users/shangwenxue/work/swx/color

# 确保虚拟环境已激活
source venv/bin/activate

# 重新安装依赖
pip install -r requirements.txt
pip install flask flask-cors
```

### 问题 3: 上传文件失败

- 检查 `uploads/` 目录是否存在
- 检查文件大小是否超过 50MB
- 检查文件格式是否支持

### 问题 4: 色卡检测失败

- 确保色卡清晰可见
- 确保光线条件良好
- 确保色卡占据图像 20-50%
- 尝试调整图像角度

### 问题 5: 校正结果不理想

- 尝试不同的校正方法
- 检查校准图像质量
- 确保光源条件相似
- 查看 Delta E 值评估质量

## 📊 性能优化

### 1. 图像压缩

在上传前压缩图像以加快处理：

```javascript
// 在 app.js 中添加
function compressImage(file, quality = 0.8) {
    // 实现图像压缩逻辑
}
```

### 2. 缓存

使用浏览器缓存减少网络请求：

```python
# 在 app.py 中添加
@app.after_request
def add_cache_headers(response):
    response.cache_control.max_age = 3600
    return response
```

### 3. 异步处理

对于大文件，使用异步处理：

```python
from celery import Celery

celery = Celery(app.name)
celery.conf.update(app.config)

@celery.task
def correct_image_async(calibration_id, target_id):
    # 异步处理逻辑
    pass
```

## 🔒 安全性

### 1. 文件验证

```python
# 验证文件类型
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

# 验证文件大小
MAX_FILE_SIZE = 50 * 1024 * 1024
```

### 2. CORS 配置

```python
from flask_cors import CORS

# 允许特定域名
CORS(app, resources={
    r"/api/*": {"origins": ["http://localhost:3000"]}
})
```

### 3. 输入验证

```python
# 验证请求参数
if method not in ['polynomial', 'lut_3d', 'direct_mapping']:
    return jsonify({'error': '无效的方法'}), 400
```

## 📈 监控和日志

### 启用日志

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/api/correct', methods=['POST'])
def correct_image():
    logger.info('开始颜色校正')
    # ...
    logger.info('颜色校正完成')
```

### 性能监控

```python
import time

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    elapsed = time.time() - request.start_time
    logger.info(f'请求耗时: {elapsed:.2f}s')
    return response
```

## 🚀 部署

### 使用 Gunicorn

```bash
# 安装 Gunicorn
pip install gunicorn

# 运行
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 使用 Docker

```dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "app.py"]
```

### 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📝 常见问题

### Q: 如何处理大文件上传？
A: 使用分块上传或压缩图像。

### Q: 如何提高处理速度？
A: 使用多项式方法，或使用 GPU 加速。

### Q: 如何保存用户会话？
A: 使用数据库或 Redis 存储会话数据。

### Q: 如何支持多用户并发？
A: 使用任务队列（Celery）或多进程。

## 📞 支持

- 查看 README.md 了解项目信息
- 查看 TECHNICAL.md 了解技术细节
- 查看 INTEGRATION.md 了解集成方法

---

**准备好了吗？** 👉 运行 `python app.py` 开始使用！

