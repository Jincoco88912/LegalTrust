#!/bin/bash

echo "🛑 停止交通罰單查詢 API..."
echo ""

# 停止並移除容器
docker compose down

echo ""
echo "✨ 服務已停止！"
