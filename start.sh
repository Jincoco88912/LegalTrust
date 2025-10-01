#!/bin/bash

# 交通罰單查詢 API - 一鍵啟動腳本

echo "======================================"
echo "交通罰單查詢 API - Docker 部署"
echo "======================================"
echo ""

# 檢查 .env 檔案
if [ ! -f .env ]; then
    echo "❌ 錯誤：找不到 .env 檔案"
    echo "請先複製 .env.example 為 .env 並填入您的 API Key"
    echo ""
    echo "執行以下命令："
    echo "  cp .env.example .env"
    echo "  nano .env"
    exit 1
fi

# 檢查 CAPTCHA_API_KEY
if ! grep -q "CAPTCHA_API_KEY=." .env; then
    echo "⚠️  警告：.env 中未設定 CAPTCHA_API_KEY"
    echo "請編輯 .env 檔案並設定您的 2captcha API Key"
    exit 1
fi

echo "✓ .env 檔案檢查通過"
echo ""

# 停止舊容器（如果存在）
echo "🔄 停止舊容器..."
docker-compose down 2>/dev/null

echo ""
echo "🏗️  建立 Docker 映像..."
docker-compose build

if [ $? -ne 0 ]; then
    echo "❌ Docker 映像建立失敗"
    exit 1
fi

echo ""
echo "🚀 啟動服務..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo "❌ 服務啟動失敗"
    exit 1
fi

echo ""
echo "⏳ 等待服務啟動..."
sleep 5

echo ""
echo "🔍 檢查服務狀態..."
docker-compose ps

echo ""
echo "======================================"
echo "✅ 部署完成！"
echo "======================================"
echo ""
echo "📊 服務資訊："
echo "  • API 端點: http://localhost:8000"
echo "  • API 文檔: http://localhost:8000/docs"
echo "  • 健康檢查: http://localhost:8000/health"
echo ""
echo "📝 常用指令："
echo "  • 查看日誌: docker-compose logs -f"
echo "  • 停止服務: docker-compose down"
echo "  • 重啟服務: docker-compose restart"
echo ""
echo "🧪 測試 API："
echo '  curl http://localhost:8000/health'
echo ""
