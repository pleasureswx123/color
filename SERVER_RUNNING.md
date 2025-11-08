# 🚀 颜色校正系统 - Web 应用已启动

## ✅ 服务器状态

**后端服务器已成功启动！**

- 🌐 **访问地址**: http://localhost:8000
- 🔧 **服务器**: Flask (开发模式)
- 📍 **主机**: 0.0.0.0
- 🔌 **端口**: 8000
- 🐛 **调试器**: 已激活 (PIN: 457-380-309)

## 📖 如何使用

### 1. 打开浏览器
在你的浏览器中访问：
```
http://localhost:8000
```

### 2. 使用应用
应用界面包含以下功能：

#### 📤 上传图像
- **校准图像**: 上传包含 ColorChecker 24 色卡的照片
- **目标图像**: 上传需要校正的照片
- 支持拖拽上传或点击选择文件

#### ⚙️ 选择校正方法
- **Polynomial** (多项式): 快速、精度中等
- **LUT 3D** (3D查找表): 平衡速度和精度
- **Direct Mapping** (直接映射): 最精确但较慢

#### 🎨 执行校正
1. 点击 "检测色卡" 按钮检测校准图像中的 ColorChecker
2. 点击 "开始校正" 按钮执行颜色校正
3. 查看结果和 Delta E 指标

#### 📊 查看结果
- 原图和校正后的图像并排显示
- 显示 Delta E 颜色差异指标
- 支持生成对比图像

#### 💾 下载结果
- 点击 "下载校正图像" 按钮下载校正后的图像

## 🔌 API 端点

后端提供以下 RESTful API 端点：

| 方法 | 端点 | 功能 |
|------|------|------|
| GET | `/` | 获取前端页面 |
| POST | `/api/upload` | 上传图像 |
| POST | `/api/detect-colorchecker` | 检测色卡 |
| POST | `/api/correct` | 执行颜色校正 |
| POST | `/api/compare` | 生成对比图像 |
| GET | `/api/download` | 下载校正图像 |
| POST | `/api/reset` | 重置会话 |
| GET | `/api/status` | 获取当前状态 |

## 📁 项目结构

```
/Users/shangwenxue/work/swx/color/
├── app.py                    # Flask 后端服务器
├── test.html                 # 前端页面
├── static/
│   ├── app.js               # 前端 JavaScript 逻辑
│   └── style.css            # 前端样式
├── src/                      # 核心颜色校正模块
│   ├── color_space.py
│   ├── color_checker_detector.py
│   ├── color_corrector.py
│   └── pipeline.py
└── requirements.txt          # Python 依赖
```

## 🛑 停止服务器

在终端中按 `Ctrl+C` 停止服务器。

## 🔄 重启服务器

```bash
cd /Users/shangwenxue/work/swx/color
source venv/bin/activate
python app.py
```

## 📝 日志

服务器日志会在终端中实时显示，包括：
- 请求日志
- 错误信息
- 调试信息

## ⚠️ 注意事项

1. **色卡检测**: 确保上传的校准图像中清晰可见 ColorChecker 24 色卡
2. **图像格式**: 支持 JPG、PNG、BMP、TIFF 格式
3. **文件大小**: 单个文件不超过 50MB
4. **浏览器兼容性**: 支持现代浏览器（Chrome、Firefox、Safari、Edge）

## 🎯 快速开始示例

1. 准备两张图像：
   - `calibration.jpg` - 包含 ColorChecker 的照片
   - `target.jpg` - 需要校正的照片

2. 打开 http://localhost:8000

3. 上传两张图像

4. 选择校正方法（推荐 Polynomial）

5. 点击 "检测色卡" 和 "开始校正"

6. 查看结果并下载

## 💡 提示

- 使用高质量的校准图像以获得最佳结果
- 确保光线条件相似
- 如果色卡检测失败，尝试调整图像角度或光线
- 不同的校正方法适合不同的场景

---

**祝你使用愉快！** 🎉

