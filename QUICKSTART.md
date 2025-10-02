# 🚀 快速開始指南

本指南說明如何快速部署交通罰單查詢 API。專案使用 Playwright 官方 Docker 映像，已解決所有瀏覽器依賴問題。

## 問題背景

原本在 Docker 中運行時，API 會卡住無法查詢，這是因為：
- Playwright 需要完整的瀏覽器運行環境（就像 Selenium）
- 標準 Python slim 映像缺少 Chromium 所需的系統庫
- 需要額外安裝數十個系統依賴才能正常運作

## 解決方案

使用 **Playwright 官方 Docker 映像**，已包含：
- ✅ Chromium 瀏覽器
- ✅ 所有必要的系統庫
- ✅ 字型檔案
- ✅ 其他運行時依賴

## 快速啟動（3 步驟）

### 1. 確保 Docker Desktop 正在運行

檢查 Docker 狀態：
```bash
docker info
```

如果出現錯誤，請先啟動 Docker Desktop。

### 2. 確認 .env 檔案已設定

確保 `.env` 檔案存在並包含：
```bash
CAPTCHA_API_KEY=your_2captcha_api_key_here
TARGET_URL=https://www.mvdis.gov.tw/m3-emv-vil/vil/penaltyQueryPay
```

### 3. 啟動服務

**方法 A：使用便捷腳本（推薦）**
```bash
./start.sh
```

**方法 B：手動啟動**
```bash
docker compose up -d --build
```

## 測試服務

### 健康檢查
```bash
curl http://localhost:8000/health
```

預期輸出：
```json
{
  "status": "healthy",
  "api_key_configured": true,
  "target_url": "https://www.mvdis.gov.tw/m3-emv-vil/vil/penaltyQueryPay"
}
```

### 查看 API 文檔
在瀏覽器中開啟：
```
http://localhost:8000/docs
```

### 測試查詢（使用範例資料）
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "A123456789",
    "birthday": "0780702",
    "headless": true
  }'
```

## 查看日誌

```bash
# 即時查看日誌
docker compose logs -f

# 查看最後 100 行
docker compose logs --tail=100
```

## 停止服務

**方法 A：使用便捷腳本**
```bash
./stop.sh
```

**方法 B：手動停止**
```bash
docker compose down
```

## 常見問題排查

### 1. Docker 連接錯誤
```
Cannot connect to the Docker daemon
```
**解決方法**：啟動 Docker Desktop

### 2. 服務啟動失敗
```bash
# 查看詳細錯誤訊息
docker compose logs

# 檢查容器狀態
docker compose ps
```

### 3. API Key 未設定
```json
{
  "detail": "未設定 2captcha API Key"
}
```
**解決方法**：檢查 `.env` 檔案中的 `CAPTCHA_API_KEY`

### 4. 查詢仍然卡住
```bash
# 重新建構映像（清除快取）
docker compose build --no-cache
docker compose up -d
```

## 技術細節

### 映像比較

| 項目 | 標準映像 | Playwright 官方映像 |
|-----|---------|------------------|
| 基礎 | python:3.11-slim | mcr.microsoft.com/playwright/python |
| 大小 | ~1.5GB | ~2.5GB |
| 穩定性 | 需手動配置依賴 | 官方維護，穩定可靠 |
| 啟動速度 | 快 | 中等 |
| 推薦用途 | 開發測試 | 生產環境 |

### 使用的檔案

- `Dockerfile` - 基於 Playwright 官方映像的 Dockerfile
- `docker-compose.yml` - Docker Compose 配置
- `start.sh` - 便捷啟動腳本
- `stop.sh` - 便捷停止腳本
- `api.py` - FastAPI 應用程式（使用 async Playwright）
- `requirements.txt` - Python 依賴套件

## 下一步

服務啟動後，您可以：

1. 📚 閱讀 API 文檔：http://localhost:8000/docs
2. 🧪 在 Swagger UI 中測試 API
3. 🔧 整合到您的應用程式中
4. 📊 監控服務日誌

如有任何問題，請查看完整的 [README.md](README.md)。


