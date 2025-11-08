#!/bin/bash

# 颜色校正系统 Web 服务器启动脚本

echo "=========================================="
echo "🎨 颜色校正系统 Web 服务器"
echo "=========================================="

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，正在创建..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "📦 激活虚拟环境..."
source venv/bin/activate

# 检查依赖
echo "📋 检查依赖..."
pip list | grep -q flask
if [ $? -ne 0 ]; then
    echo "📥 安装 Flask 和 CORS..."
    pip install flask flask-cors
fi

# 检查必要的 Python 包
echo "✓ 依赖检查完成"

# 启动服务器
echo ""
echo "=========================================="
echo "🚀 启动 Web 服务器..."
echo "=========================================="
echo ""
echo "📍 访问地址: http://localhost:5000"
echo "📍 API 文档: http://localhost:5000/api/status"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

python app.py

