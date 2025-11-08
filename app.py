"""
Flask Web 服务器 - 颜色校正系统后端
提供 RESTful API 接口用于前端调用
"""

import os
import json
import base64
import numpy as np
import cv2
from io import BytesIO
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from PIL import Image
import traceback

from src.pipeline import ColorCorrectionPipeline
from src.color_checker_detector import ColorCheckerDetector
from src.color_space import ColorSpace

# 初始化 Flask 应用
app = Flask(__name__)
CORS(app)

# 配置
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp', 'tiff'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# 创建上传文件夹
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 全局变量存储当前会话的数据
session_data = {
    'calibration_image': None,
    'target_image': None,
    'pipeline': None,
    'correction_method': 'polynomial'
}


def allowed_file(filename):
    """检查文件是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def image_to_base64(image_array):
    """将 numpy 数组转换为 base64 字符串"""
    if image_array is None:
        return None
    
    # 确保是 uint8 类型
    if image_array.dtype != np.uint8:
        image_array = (image_array * 255).astype(np.uint8)
    
    # 转换为 BGR（OpenCV 格式）
    if len(image_array.shape) == 3 and image_array.shape[2] == 3:
        image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
    else:
        image_bgr = image_array
    
    # 编码为 JPEG
    _, buffer = cv2.imencode('.jpg', image_bgr)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{img_base64}"


@app.route('/', methods=['GET'])
def index():
    """返回主页面"""
    return send_file('test.html', mimetype='text/html')


@app.route('/api/upload', methods=['POST'])
def upload_image():
    """上传图像接口"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '没有文件被上传'}), 400
        
        file = request.files['file']
        image_type = request.form.get('type', 'target')  # 'calibration' 或 'target'
        
        if file.filename == '':
            return jsonify({'success': False, 'error': '文件名为空'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': '不支持的文件格式'}), 400
        
        # 读取图像
        img_data = file.read()
        if len(img_data) > MAX_FILE_SIZE:
            return jsonify({'success': False, 'error': '文件过大'}), 400
        
        # 使用 OpenCV 读取
        nparr = np.frombuffer(img_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({'success': False, 'error': '无法读取图像文件'}), 400
        
        # 转换为 RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 存储到会话
        if image_type == 'calibration':
            session_data['calibration_image'] = image_rgb
        else:
            session_data['target_image'] = image_rgb
        
        # 返回图像预览
        preview = image_to_base64(image_rgb)
        
        return jsonify({
            'success': True,
            'message': f'{image_type} 图像上传成功',
            'preview': preview,
            'size': image_rgb.shape
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/detect-colorchecker', methods=['POST'])
def detect_colorchecker():
    """检测色卡接口"""
    try:
        if session_data['calibration_image'] is None:
            return jsonify({'success': False, 'error': '请先上传校准图像'}), 400

        detector = ColorCheckerDetector()
        result = detector.detect(session_data['calibration_image'])

        if not result['detected']:
            return jsonify({
                'success': False,
                'error': '未检测到色卡，请确保色卡清晰可见',
                'confidence': 0
            }), 400

        # 返回检测结果
        return jsonify({
            'success': True,
            'detected': True,
            'confidence': float(result['confidence']),
            'message': f'色卡检测成功，置信度: {result["confidence"]:.2%}'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/correct', methods=['POST'])
def correct_image():
    """颜色校正接口"""
    try:
        if session_data['calibration_image'] is None:
            return jsonify({'success': False, 'error': '请先上传校准图像'}), 400
        
        if session_data['target_image'] is None:
            return jsonify({'success': False, 'error': '请先上传目标图像'}), 400
        
        # 获取校正方法
        method = request.json.get('method', 'polynomial')
        session_data['correction_method'] = method
        
        # 创建处理管道
        pipeline = ColorCorrectionPipeline(correction_method=method)
        
        # 执行处理
        corrected, info = pipeline.process(
            session_data['calibration_image'],
            session_data['target_image']
        )
        
        # 存储结果
        session_data['pipeline'] = pipeline
        session_data['corrected_image'] = corrected
        session_data['correction_info'] = info
        
        # 返回结果
        target_preview = image_to_base64(session_data['target_image'])
        corrected_preview = image_to_base64(corrected)

        return jsonify({
            'success': True,
            'message': '颜色校正完成',
            'target_image': target_preview,
            'corrected_image': corrected_preview,
            'metrics': {
                'mean_delta_e': float(info.get('mean_delta_e', 0)),
                'max_delta_e': float(info.get('max_delta_e', 0)),
                'min_delta_e': float(info.get('min_delta_e', 0)),
                'method': method
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/compare', methods=['POST'])
def compare_images():
    """生成对比图像接口"""
    try:
        if session_data['target_image'] is None or session_data.get('corrected_image') is None:
            return jsonify({'success': False, 'error': '请先执行颜色校正'}), 400
        
        pipeline = session_data['pipeline']
        
        # 生成对比图像
        comparison = pipeline.create_comparison_image(
            session_data['target_image'],
            session_data['corrected_image']
        )
        
        comparison_preview = image_to_base64(comparison)

        return jsonify({
            'success': True,
            'comparison_image': comparison_preview
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/download', methods=['GET'])
def download_image():
    """下载校正后的图像"""
    try:
        if session_data.get('corrected_image') is None:
            return jsonify({'success': False, 'error': '没有可下载的图像'}), 400
        
        # 转换为 BGR
        corrected_bgr = cv2.cvtColor(session_data['corrected_image'], cv2.COLOR_RGB2BGR)
        
        # 编码为 JPEG
        _, buffer = cv2.imencode('.jpg', corrected_bgr)
        
        # 返回文件
        return send_file(
            BytesIO(buffer),
            mimetype='image/jpeg',
            as_attachment=True,
            download_name='corrected_image.jpg'
        )
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/reset', methods=['POST'])
def reset_session():
    """重置会话"""
    try:
        session_data['calibration_image'] = None
        session_data['target_image'] = None
        session_data['pipeline'] = None
        session_data['corrected_image'] = None
        session_data['correction_info'] = None
        
        return jsonify({'success': True, 'message': '会话已重置'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/status', methods=['GET'])
def get_status():
    """获取当前状态"""
    try:
        return jsonify({
            'success': True,
            'has_calibration': session_data['calibration_image'] is not None,
            'has_target': session_data['target_image'] is not None,
            'has_result': session_data.get('corrected_image') is not None,
            'method': session_data['correction_method']
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """404 错误处理"""
    return jsonify({'success': False, 'error': '页面未找到'}), 404


@app.errorhandler(500)
def internal_error(error):
    """500 错误处理"""
    return jsonify({'success': False, 'error': '服务器内部错误'}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("颜色校正系统 Web 服务器")
    print("=" * 60)
    print("访问地址: http://localhost:8000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=8000)

