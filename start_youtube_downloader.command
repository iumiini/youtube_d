#!/bin/bash

# YouTube下載器啟動腳本
# 雙擊此文件即可啟動應用

# 設定顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}  YouTube 下載器啟動中...${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# 進入腳本所在目錄
cd "$(dirname "$0")"

# 檢查Python是否安裝
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 錯誤：找不到 Python 3${NC}"
    echo "請先安裝 Python 3"
    read -p "按任意鍵退出..."
    exit 1
fi

# 檢查FFmpeg是否安裝
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${YELLOW}⚠️  警告：找不到 FFmpeg${NC}"
    echo "下載MP3需要FFmpeg，請執行: brew install ffmpeg"
    echo ""
fi

# 檢查虛擬環境是否存在
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  正在建立虛擬環境...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ 建立虛擬環境失敗${NC}"
        read -p "按Enter鍵退出..."
        exit 1
    fi
fi

# 啟動虛擬環境並檢查依賴
echo -e "${YELLOW}📦 檢查依賴套件...${NC}"
source venv/bin/activate

# 檢查依賴是否安裝
if ! python -c "import flask" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  正在安裝依賴...${NC}"
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ 安裝依賴失敗${NC}"
        read -p "按Enter鍵退出..."
        exit 1
    fi
fi

echo -e "${GREEN}✅ 啟動 Flask 服務器...${NC}"
echo -e "${GREEN}🌐 應用將在 http://localhost:8080 啟動${NC}"
echo ""

# 等待3秒後自動打開瀏覽器
(sleep 3 && open http://localhost:8080) &

# 啟動Flask應用（使用虛擬環境的Python）
python -m flask run --host=0.0.0.0 --port=8080

# 如果程序退出
echo ""
echo -e "${YELLOW}應用已停止${NC}"
read -p "按Enter鍵關閉此窗口..."
