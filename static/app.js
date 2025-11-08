/**
 * 颜色校正系统 - 前端 JavaScript
 * 处理用户交互和 API 调用
 */

// 全局状态
const state = {
    hasCalibration: false,
    hasTarget: false,
    hasResult: false,
    method: 'polynomial'
};

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeUploadAreas();
    initializeButtons();
    updateUI();
});

/**
 * 初始化上传区域
 */
function initializeUploadAreas() {
    // 校准图像
    const calibrationDropzone = document.getElementById('calibration-dropzone');
    const calibrationInput = document.getElementById('calibration-input');

    if (calibrationDropzone && calibrationInput) {
        calibrationDropzone.addEventListener('click', (e) => {
            e.stopPropagation();
            calibrationInput.click();
        });
        calibrationDropzone.addEventListener('dragover', handleDragOver);
        calibrationDropzone.addEventListener('dragleave', handleDragLeave);
        calibrationDropzone.addEventListener('drop', (e) => handleDrop(e, 'calibration'));
        calibrationInput.addEventListener('change', (e) => handleFileSelect(e, 'calibration'));
    }

    // 目标图像
    const targetDropzone = document.getElementById('target-dropzone');
    const targetInput = document.getElementById('target-input');

    if (targetDropzone && targetInput) {
        targetDropzone.addEventListener('click', (e) => {
            e.stopPropagation();
            targetInput.click();
        });
        targetDropzone.addEventListener('dragover', handleDragOver);
        targetDropzone.addEventListener('dragleave', handleDragLeave);
        targetDropzone.addEventListener('drop', (e) => handleDrop(e, 'target'));
        targetInput.addEventListener('change', (e) => handleFileSelect(e, 'target'));
    }
}

/**
 * 处理拖拽进入
 */
function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.style.borderColor = '#6366f1';
    e.currentTarget.style.background = 'rgba(99, 102, 241, 0.05)';
}

/**
 * 处理拖拽离开
 */
function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.style.borderColor = '#e5e7eb';
    e.currentTarget.style.background = '#f9fafb';
}

/**
 * 处理拖拽放下
 */
function handleDrop(e, type) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.style.borderColor = '#e5e7eb';
    e.currentTarget.style.background = '#f9fafb';

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        uploadFile(files[0], type);
    }
}

/**
 * 处理文件选择
 */
function handleFileSelect(e, type) {
    const file = e.target.files[0];
    if (file) {
        uploadFile(file, type);
    }
}

/**
 * 上传文件
 */
async function uploadFile(file, type) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            if (type === 'calibration') {
                state.hasCalibration = true;
                displayPreview(data.preview, 'calibration');
            } else {
                state.hasTarget = true;
                displayPreview(data.preview, 'target');
            }
            updateUI();
            updateStatus(`✓ ${type === 'calibration' ? '校准' : '目标'}图像上传成功`);
        } else {
            alert('上传失败: ' + data.error);
        }
    } catch (error) {
        alert('上传错误: ' + error.message);
    }
}

/**
 * 显示预览
 */
function displayPreview(base64, type) {
    const container = document.getElementById(`${type}-preview`);
    container.innerHTML = `<img src="${base64}" alt="预览">`;
}

/**
 * 初始化按钮
 */
function initializeButtons() {
    document.getElementById('method-select').addEventListener('change', (e) => {
        state.method = e.target.value;
    });

    document.getElementById('detect-btn').addEventListener('click', detectColorChecker);
    document.getElementById('correct-btn').addEventListener('click', correctImage);
    document.getElementById('download-btn').addEventListener('click', downloadImage);
    document.getElementById('compare-btn').addEventListener('click', compareImages);
    document.getElementById('reset-btn').addEventListener('click', resetSession);
}

/**
 * 检测色卡
 */
async function detectColorChecker() {
    if (!state.hasCalibration) {
        alert('请先上传校准图像');
        return;
    }

    showProgress('检测色卡中...');

    try {
        const response = await fetch('/api/detect-colorchecker', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            updateStatus('✓ 色卡检测成功');
        } else {
            updateStatus('✗ 色卡检测失败: ' + data.error);
        }
    } catch (error) {
        updateStatus('✗ 检测错误: ' + error.message);
    } finally {
        hideProgress();
    }
}

/**
 * 执行颜色校正
 */
async function correctImage() {
    if (!state.hasCalibration || !state.hasTarget) {
        alert('请先上传校准图像和目标图像');
        return;
    }

    showProgress('校正中...');

    try {
        const response = await fetch('/api/correct', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({method: state.method})
        });

        const data = await response.json();

        if (data.success) {
            state.hasResult = true;
            displayResult(data);
            updateUI();
            updateStatus('✓ 校正完成');
        } else {
            updateStatus('✗ 校正失败: ' + data.error);
        }
    } catch (error) {
        updateStatus('✗ 校正错误: ' + error.message);
    } finally {
        hideProgress();
    }
}

/**
 * 显示结果
 */
function displayResult(data) {
    // 显示原图和校正图
    document.getElementById('original-img').src = data.target_image;
    document.getElementById('corrected-img').src = data.corrected_image;

    // 显示指标
    if (data.metrics) {
        document.getElementById('delta-e-avg').textContent = data.metrics.mean_delta_e.toFixed(2);
        document.getElementById('delta-e-max').textContent = data.metrics.max_delta_e.toFixed(2);
        document.getElementById('delta-e-min').textContent = data.metrics.min_delta_e.toFixed(2);
    }
}

/**
 * 下载图像
 */
async function downloadImage() {
    try {
        const response = await fetch('/api/download');
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'corrected_image.jpg';
        a.click();
    } catch (error) {
        alert('下载失败: ' + error.message);
    }
}

/**
 * 生成对比图像
 */
async function compareImages() {
    showProgress('生成对比图像中...');

    try {
        const response = await fetch('/api/compare', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            // 显示对比图像
            const container = document.createElement('div');
            container.style.marginTop = '20px';
            container.innerHTML = `<img src="${data.comparison_image}" style="width: 100%; border-radius: 6px;">`;
            document.querySelector('.results-section').appendChild(container);
            updateStatus('✓ 对比图像生成完成');
        }
    } catch (error) {
        updateStatus('✗ 生成失败: ' + error.message);
    } finally {
        hideProgress();
    }
}

/**
 * 重置会话
 */
async function resetSession() {
    if (!confirm('确定要重置所有数据吗？')) {
        return;
    }

    try {
        await fetch('/api/reset', {method: 'POST'});
        state.hasCalibration = false;
        state.hasTarget = false;
        state.hasResult = false;

        // 清空预览
        document.getElementById('calibration-preview').innerHTML = '';
        document.getElementById('target-preview').innerHTML = '';
        document.getElementById('original-img').src = '';
        document.getElementById('corrected-img').src = '';

        updateUI();
        updateStatus('✓ 已重置，可以重新开始');

        // 滚动到顶部
        window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (error) {
        alert('重置失败: ' + error.message);
    }
}

/**
 * 显示进度
 */
function showProgress(text) {
    const container = document.getElementById('progress-container');
    document.getElementById('progress-text').textContent = text;
    container.style.display = 'block';
}

/**
 * 隐藏进度
 */
function hideProgress() {
    document.getElementById('progress-container').style.display = 'none';
}

/**
 * 更新状态
 */
function updateStatus(message) {
    const statusInfo = document.getElementById('status-info');
    if (message) {
        statusInfo.textContent = message;
        statusInfo.style.display = 'block';
    } else {
        statusInfo.style.display = 'none';
    }
}

/**
 * 更新 UI 状态
 */
function updateUI() {
    // 更新按钮状态
    const detectBtn = document.getElementById('detect-btn');
    const correctBtn = document.getElementById('correct-btn');

    // 只有上传了校准图像才能检测色卡
    detectBtn.disabled = !state.hasCalibration;

    // 只有上传了两张图像才能开始校正
    correctBtn.disabled = !(state.hasCalibration && state.hasTarget);

    // 显示/隐藏结果卡片
    const resultsCard = document.getElementById('results-card');
    if (state.hasResult) {
        resultsCard.style.display = 'block';
        // 平滑滚动到结果区域
        setTimeout(() => {
            resultsCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 100);
    } else {
        resultsCard.style.display = 'none';
    }
}
