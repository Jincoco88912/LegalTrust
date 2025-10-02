#!/bin/bash

echo "🚀 啟動交通罰單查詢 API (Playwright 官方映像)..."
echo ""

# 檢查 .env 檔案
if [ ! -f .env ]; then
    echo "❌ 錯誤：找不到 .env 檔案"
    echo "請建立 .env 檔案並設定 CAPTCHA_API_KEY"
    exit 1
fi

# 檢查 Docker 是否運行
if ! docker info > /dev/null 2>&1; then
    echo "❌ 錯誤：Docker 未運行"
    echo "請先啟動 Docker Desktop"
    exit 1
fi

# 停止舊的容器
echo "🛑 停止舊的容器..."
docker compose down

# 建構並啟動
echo "🔨 建構映像並啟動服務..."
docker compose up -d --build

# 等待服務啟動
echo ""
echo "⏳ 等待服務啟動..."
sleep 5

# 檢查健康狀態
echo ""
echo "🔍 檢查服務狀態..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ 服務啟動成功！"
    echo ""
    echo "📊 服務資訊："
    echo "   - API 端點: http://localhost:8000"
    echo "   - API 文檔: http://localhost:8000/docs"
    echo "   - 健康檢查: http://localhost:8000/health"
    echo ""
    echo "📋 查看日誌："
    echo "   docker compose logs -f"
else
    echo "⚠️  服務可能還在啟動中..."
    echo "請執行以下命令查看日誌："
    echo "   docker compose logs -f"
fi

echo ""
echo "✨ 完成！"
