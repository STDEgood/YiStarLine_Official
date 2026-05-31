#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YiStarLine 官网服务器
- 静态文件托管
- 下载计数 API
- 反馈留言 API
"""

import os
import json
from datetime import datetime
from flask import Flask, send_from_directory, request, jsonify, abort

app = Flask(__name__, static_folder='.', static_url_path='')

# 配置文件路径
DOWNLOAD_COUNTS_FILE = 'download_counts.json'
MESSAGES_FILE = 'messages.json'

# ---------- 辅助函数 ----------
def load_json(file_path, default=None):
    if default is None:
        default = {}
    if not os.path.exists(file_path):
        return default
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return default

def save_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ---------- 静态文件路由 ----------
# 让 Flask 直接托管当前目录下的所有文件，但我们需要优先处理 API
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    # 允许访问所有文件（包括 .html, .mp4, .css, .js 等）
    # 安全起见，防止目录遍历，但 send_from_directory 会自动处理
    return send_from_directory('.', filename)

# ---------- 下载计数 API ----------
@app.route('/api/download/<game_id>', methods=['POST'])
def record_download(game_id):
    """记录某个游戏的下载次数，game_id 例如 'YiS_Run', 'BackButNone', 'LAG', 'For_Microsoft'"""
    counts = load_json(DOWNLOAD_COUNTS_FILE)
    counts[game_id] = counts.get(game_id, 0) + 1
    save_json(DOWNLOAD_COUNTS_FILE, counts)
    return jsonify({'status': 'ok', 'game': game_id, 'total': counts[game_id]})

@app.route('/api/download_counts', methods=['GET'])
def get_download_counts():
    """获取所有游戏的下载次数"""
    counts = load_json(DOWNLOAD_COUNTS_FILE)
    return jsonify(counts)

# ---------- 反馈留言 API ----------
@app.route('/api/message', methods=['POST'])
def submit_message():
    data = request.get_json()
    if not data:
        return jsonify({'error': '需要 JSON 数据'}), 400
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    content = data.get('content', '').strip()
    if not name or not content:
        return jsonify({'error': '姓名和留言内容不能为空'}), 400
    messages = load_json(MESSAGES_FILE, default=[])
    messages.append({
        'id': len(messages) + 1,
        'name': name,
        'email': email,
        'content': content,
        'time': datetime.now().isoformat()
    })
    save_json(MESSAGES_FILE, messages)
    return jsonify({'status': 'ok', 'message': '留言已收到，谢谢！'})

@app.route('/api/messages', methods=['GET'])
def get_messages():
    """获取所有留言（仅用于管理，后续可加 token 鉴权）"""
    # 简单起见，先不做鉴权，如果你不想公开，可以注释掉这个路由
    messages = load_json(MESSAGES_FILE, default=[])
    # 返回最近50条
    return jsonify(messages[-50:])

# ---------- 启动服务器 ----------
if __name__ == '__main__':
    print("YiStarLine 官网服务器启动")
    print("访问 http://127.0.0.1:5000 查看首页")
    print("下载计数文件:", DOWNLOAD_COUNTS_FILE)
    print("留言文件:", MESSAGES_FILE)
    # 允许外部访问（把 host 设为 '0.0.0.0' 即可）
    app.run(host='0.0.0.0', port=5000, debug=True)