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

    # 定義多種下載策略，按順序嘗試
    strategies = [
        # 策略 1: iOS 客戶端（最穩定）
        {
            'name': 'iOS客戶端',
            'extractor_args': {
                'youtube': {
                    'player_client': ['ios'],
                }
            },
        },
        # 策略 2: Android 客戶端
        {
            'name': 'Android客戶端',
            'extractor_args': {
                'youtube': {
                    'player_client': ['android'],
                }
            },
        },
        # 策略 3: Web 客戶端（備用）
        {
            'name': 'Web客戶端',
            'extractor_args': {
                'youtube': {
                    'player_client': ['web'],
                }
            },
        },
        # 策略 4: 混合模式
        {
            'name': '混合模式',
            'extractor_args': {
                'youtube': {
                    'player_client': ['ios', 'android', 'web'],
                }
            },
        },
    ]

    last_error = None

    for strategy in strategies:
        try:
            print(f"嘗試使用 {strategy['name']} 下載...")

            # 基礎設定
            base_opts = {
                'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
                'quiet': False,
                'no_warnings': False,
                # 添加headers來避免403
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-us,en;q=0.5',
                    'Sec-Fetch-Mode': 'navigate',
                },
                # 使用當前策略的提取器選項
                'extractor_args': strategy['extractor_args'],
                # 添加更多選項來提高成功率
                'nocheckcertificate': True,
                'ignoreerrors': False,
                'no_color': True,
                'extract_flat': False,
                'age_limit': None,
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
                    # 最高畫質：優先選擇最高解析度
                    format_string = 'bestvideo+bestaudio/best'
                else:
                    # 指定畫質：嘗試多種格式組合以獲得最接近的畫質
                    format_string = (
                        f'bestvideo[height<={quality}]+bestaudio/'
                        f'bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/'
                        f'best[height<={quality}]/'
                        f'bestvideo+bestaudio/'
                        f'best'
                    )

                ydl_opts = {
                    **base_opts,
                    'format': format_string,
                    'merge_output_format': 'mp4',
                    # 確保合併視頻和音頻
                    'postprocessors': [{
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': 'mp4',
                    }] if format_type == 'mp4' else [],
                }

            # 執行下載
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'video')

                # 獲取實際下載的格式資訊
                actual_format = info.get('format', 'unknown')
                width = info.get('width', 0)
                height = info.get('height', 0)
                filesize = info.get('filesize', 0) or info.get('filesize_approx', 0)

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

                # 獲取實際文件大小
                actual_filesize = os.path.getsize(filepath) if os.path.exists(filepath) else 0
                filesize_mb = actual_filesize / (1024 * 1024)

                # 判斷實際畫質
                quality_label = 'unknown'
                if height >= 2160:
                    quality_label = '4K (2160p)'
                elif height >= 1440:
                    quality_label = '2K (1440p)'
                elif height >= 1080:
                    quality_label = 'Full HD (1080p)'
                elif height >= 720:
                    quality_label = 'HD (720p)'
                elif height >= 480:
                    quality_label = 'SD (480p)'
                elif height >= 360:
                    quality_label = '360p'
                elif height > 0:
                    quality_label = f'{height}p'

                print(f"✅ 使用 {strategy['name']} 下載成功！")
                return jsonify({
                    'success': True,
                    'message': f'下載完成！文件已保存到: {filepath}',
                    'filename': filename,
                    'filepath': filepath,
                    'resolution': f'{width}x{height}' if width and height else 'unknown',
                    'quality': quality_label,
                    'filesize_mb': round(filesize_mb, 2),
                    'strategy': strategy['name']
                })

        except yt_dlp.utils.DownloadError as e:
            last_error = e
            print(f"❌ {strategy['name']} 失敗: {str(e)}")
            continue  # 嘗試下一個策略

        except Exception as e:
            last_error = e
            print(f"❌ {strategy['name']} 發生錯誤: {str(e)}")
            continue  # 嘗試下一個策略

    # 如果所有策略都失敗了，返回錯誤
    if last_error:
        error_msg = str(last_error)

        # 針對常見錯誤提供更友善的訊息
        if isinstance(last_error, yt_dlp.utils.DownloadError):
            if '403' in error_msg or 'Forbidden' in error_msg:
                error_msg = '下載被YouTube拒絕（403錯誤）。所有下載策略都失敗了。\n這可能是因為：\n1. YouTube偵測到自動化下載\n2. 影片有地區限制\n3. 影片需要登入才能觀看\n4. 該影片暫時無法下載\n\n建議：請稍後再試，或嘗試其他影片'
            elif '404' in error_msg or 'not available' in error_msg.lower():
                error_msg = '找不到影片。可能原因：\n1. 影片已被刪除\n2. 影片設為私人\n3. 網址不正確'
            elif 'age' in error_msg.lower():
                error_msg = '此影片有年齡限制，無法下載'
            elif 'copyright' in error_msg.lower():
                error_msg = '此影片因版權問題無法下載'

        import traceback
        error_detail = traceback.format_exc()
        print(f"所有策略都失敗。最後錯誤: {error_detail}")

        return jsonify({
            'success': False,
            'error': f'下載失敗: {error_msg}',
            'detail': error_detail if app.debug else None
        }), 500

    # 理論上不應該到達這裡
    return jsonify({
        'success': False,
        'error': '未知錯誤：所有下載策略都未能完成'
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
