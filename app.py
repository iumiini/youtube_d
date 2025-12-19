from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os
from pathlib import Path
import re

app = Flask(__name__)

# 設定下載目錄
DOWNLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


def sanitize_filename(filename):
    """清理文件名，移除非法字符"""
    # 移除非法字符
    filename = re.sub(r'[\\/*?:"<>|]', "", filename)
    return filename


@app.route('/')
def index():
    """首頁"""
    return render_template('index.html')


@app.route('/download', methods=['POST'])
def download():
    """處理下載請求"""
    data = request.get_json()
    url = data.get('url')
    format_type = data.get('format')  # 'mp3' or 'mp4'
    quality = data.get('quality', 'best')  # 畫質選項

    if not url:
        return jsonify({'success': False, 'error': '請提供YouTube網址'}), 400

    try:
        # 基礎設定，添加更多選項來避免403錯誤
        base_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
            # 添加headers和cookies來避免403
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            },
            # 使用更兼容的提取器選項
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                    'player_skip': ['webpage', 'configs'],
                }
            },
        }

        if format_type == 'mp3':
            # 下載MP3
            ydl_opts = {
                **base_opts,
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
        else:  # mp4
            # 下載MP4 - 根據用戶選擇的畫質
            if quality == 'best':
                format_string = 'best[ext=mp4]/best'
            else:
                # 選擇指定畫質或更低畫質的最佳選項
                format_string = f'bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/best[height<={quality}][ext=mp4]/best[ext=mp4]/best'

            ydl_opts = {
                **base_opts,
                'format': format_string,
                'merge_output_format': 'mp4',
            }

        # 執行下載
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'video')

            # 找到下載的文件
            if format_type == 'mp3':
                filename = f"{sanitize_filename(title)}.mp3"
            else:
                filename = f"{sanitize_filename(title)}.mp4"

            filepath = os.path.join(DOWNLOAD_FOLDER, filename)

            # 檢查文件是否存在
            if not os.path.exists(filepath):
                # 嘗試查找文件（有時候文件名會略有不同）
                for file in os.listdir(DOWNLOAD_FOLDER):
                    if title in file and (file.endswith('.mp3') if format_type == 'mp3' else file.endswith('.mp4')):
                        filepath = os.path.join(DOWNLOAD_FOLDER, file)
                        filename = file
                        break

            return jsonify({
                'success': True,
                'message': f'下載完成！文件已保存到: {filepath}',
                'filename': filename,
                'filepath': filepath
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'下載失敗: {str(e)}'
        }), 500


@app.route('/downloads')
def list_downloads():
    """列出所有已下載的文件"""
    files = []
    for filename in os.listdir(DOWNLOAD_FOLDER):
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)
        if os.path.isfile(filepath):
            files.append({
                'name': filename,
                'size': os.path.getsize(filepath),
                'path': filepath
            })
    return jsonify({'files': files})


if __name__ == '__main__':
    print(f"下載目錄: {DOWNLOAD_FOLDER}")
    app.run(debug=True, host='0.0.0.0', port=5000)
