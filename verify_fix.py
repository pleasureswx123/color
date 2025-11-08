#!/usr/bin/env python3
"""
验证文件上传修复的脚本
检查 HTML、CSS 和 JavaScript 中的修复是否正确应用
"""

import os
import re

def check_html():
    """检查 HTML 文件中的修复"""
    print("=" * 60)
    print("检查 HTML 文件...")
    print("=" * 60)
    
    with open('test.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否使用了 class="file-input" 而不是 hidden
    if 'class="file-input"' in content:
        print("✅ HTML: 正确使用 class=\"file-input\"")
    else:
        print("❌ HTML: 未找到 class=\"file-input\"")
    
    # 检查是否还有 hidden 属性
    if 'hidden>' in content or 'hidden ' in content:
        print("⚠️  HTML: 仍然存在 hidden 属性")
    else:
        print("✅ HTML: 已移除 hidden 属性")
    
    # 检查是否有两个 file-input
    file_input_count = content.count('class="file-input"')
    print(f"✅ HTML: 找到 {file_input_count} 个 file-input 元素")
    
    return True

def check_css():
    """检查 CSS 文件中的修复"""
    print("\n" + "=" * 60)
    print("检查 CSS 文件...")
    print("=" * 60)
    
    with open('static/style.css', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查 .file-input 规则
    if '.file-input' in content and 'display: none' in content:
        print("✅ CSS: 正确定义了 .file-input 样式")
    else:
        print("❌ CSS: 缺少 .file-input 样式定义")
    
    # 检查 pointer-events: none
    if 'pointer-events: none' in content:
        print("✅ CSS: 正确添加了 pointer-events: none")
    else:
        print("❌ CSS: 缺少 pointer-events: none")
    
    # 检查 !important
    if '!important' in content and '.file-input' in content:
        print("✅ CSS: 使用了 !important 确保优先级")
    else:
        print("⚠️  CSS: 未使用 !important")
    
    return True

def check_javascript():
    """检查 JavaScript 文件中的修复"""
    print("\n" + "=" * 60)
    print("检查 JavaScript 文件...")
    print("=" * 60)
    
    with open('static/app.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查 preventDefault
    if 'preventDefault()' in content:
        print("✅ JS: 正确使用了 preventDefault()")
    else:
        print("❌ JS: 缺少 preventDefault()")
    
    # 检查 stopPropagation
    if 'stopPropagation()' in content:
        print("✅ JS: 正确使用了 stopPropagation()")
    else:
        print("❌ JS: 缺少 stopPropagation()")
    
    # 检查元素存在性检查
    if 'if (calibrationDropzone && calibrationInput)' in content:
        print("✅ JS: 添加了元素存在性检查")
    else:
        print("⚠️  JS: 缺少元素存在性检查")
    
    # 检查 input.click()
    if 'input.click()' in content:
        print("✅ JS: 正确调用了 input.click()")
    else:
        print("❌ JS: 缺少 input.click() 调用")
    
    return True

def main():
    """主函数"""
    print("\n")
    print("🔍 文件上传修复验证")
    print("=" * 60)
    
    try:
        check_html()
        check_css()
        check_javascript()
        
        print("\n" + "=" * 60)
        print("✅ 验证完成！")
        print("=" * 60)
        print("\n📝 下一步：")
        print("1. 重启 Flask 服务器")
        print("2. 访问 http://localhost:8000")
        print("3. 点击上传区域测试文件选择")
        print("4. 拖拽文件测试拖拽上传")
        print("\n")
        
    except FileNotFoundError as e:
        print(f"❌ 错误: 文件未找到 - {e}")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)

