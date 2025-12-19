# 📹 YouTube 下載器 (youtube_d)

一個簡單易用的YouTube影片和音樂下載器，支援MP3和MP4格式下載。

## ✨ 功能特點

- 🎵 下載YouTube影片為MP3音頻格式
- 🎬 下載YouTube影片為MP4視頻格式
- 📱 響應式網頁界面，支援手機和電腦
- 📂 自動管理下載的文件
- ⚡ 快速且易於使用

## 🚀 安裝與使用

### 環境要求

- Python 3.7+
- FFmpeg（用於音頻轉換）

### 安裝步驟

1. **克隆或下載本專案**

```bash
git clone <repository-url>
cd youtube_d
```

2. **安裝FFmpeg**

macOS:
```bash
brew install ffmpeg
```

Ubuntu/Debian:
```bash
sudo apt update
sudo apt install ffmpeg
```

Windows:
- 從 [FFmpeg官網](https://ffmpeg.org/download.html) 下載並安裝
- 將FFmpeg添加到系統PATH環境變數

3. **安裝Python依賴**

```bash
pip install -r requirements.txt
```

### 運行應用

```bash
python app.py
```

應用將在 `http://localhost:5000` 啟動。

在瀏覽器中打開此網址即可使用。

## 📖 使用說明

1. 在輸入框中貼上YouTube影片網址
2. 選擇下載格式：
   - 點擊 "🎵 下載 MP3" 下載音頻
   - 點擊 "🎬 下載 MP4" 下載影片
3. 等待下載完成
4. 下載的文件會保存在 `downloads` 資料夾中
5. 可以在頁面底部查看所有已下載的文件

## 📁 專案結構

```
youtube_d/
├── app.py                  # Flask應用主程式
├── requirements.txt        # Python依賴列表
├── templates/
│   └── index.html         # 前端HTML界面
├── static/
│   └── style.css          # CSS樣式文件
└── downloads/             # 下載文件存放目錄
```

## 🛠️ 技術棧

- **後端**: Flask (Python)
- **下載引擎**: yt-dlp
- **前端**: HTML + CSS + JavaScript
- **音視頻處理**: FFmpeg

## ⚠️ 注意事項

1. 請確保您有權下載相關內容
2. 下載速度取決於您的網路連接和YouTube伺服器
3. 某些受版權保護的內容可能無法下載
4. 下載的文件會佔用磁碟空間，請定期清理

## 📝 授權

本專案僅供學習和個人使用。

## 🤝 貢獻

歡迎提交問題和改進建議！