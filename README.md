# 交通罰單查詢 API

基於 FastAPI + Playwright + 2captcha 的自動化交通罰單查詢服務。

## 🚀 快速部署（Docker）

### 前置需求

1. 確保 Docker Desktop 已啟動
2. 確保有 `.env` 檔案並設定好 API Key

### 1. 設定環境變數

編輯 `.env` 檔案並填入您的 2captcha API Key：

```bash
CAPTCHA_API_KEY=your_2captcha_api_key_here
TARGET_URL=https://www.mvdis.gov.tw/m3-emv-vil/vil/penaltyQueryPay
```

### 2. 啟動服務

```bash
# 使用啟動腳本（推薦）
./start.sh

# 或直接使用 docker compose
docker compose up -d --build
```

> 💡 本專案使用 Playwright 官方 Docker 映像，已包含所有必要的瀏覽器依賴，穩定可靠。

### 3. 測試服務

```bash
# 健康檢查
curl http://localhost:8000/health

# API 文檔
# 瀏覽器訪問 http://localhost:8000/docs
```

### 4. 停止服務

```bash
# 使用停止腳本
./stop.sh

# 或直接使用 docker compose
docker compose down
```

## 📝 API 使用

### 查詢罰單

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "A123456789",
    "birthday": "0780702",
    "headless": true
  }'
```

### 參數說明

- `user_id`: 身分證字號
- `birthday`: 出生年月日（民國年 YYYMMDD）
- `headless`: 是否使用無頭模式（預設：true）

## 🔧 常用指令

```bash
# 查看日誌
docker compose logs -f

# 重啟服務
docker compose restart

# 重新建構映像
docker compose up -d --build

# 查看容器狀態
docker compose ps
```

## 📊 服務資訊

- **API 端點**: http://localhost:8000
- **API 文檔**: http://localhost:8000/docs
- **健康檢查**: http://localhost:8000/health

## ⚠️ 注意事項

1. 請確保已安裝 Docker 和 Docker Compose
2. 請勿將 `.env` 檔案上傳至版本控制
3. 2captcha API Key 需要到 https://2captcha.com/ 註冊取得
4. 本專案僅供學習和測試使用

## 📞 支援

如有問題，請查看日誌：
```bash
docker compose logs -f
```

## 🐛 常見問題

**Q: 為什麼在 Docker 中無法查詢，API 會卡住？**

A: 本專案已使用 Playwright 官方 Docker 映像並配置了 async API，完全解決了這個問題。關鍵配置：
- 使用 Playwright 官方映像（包含所有瀏覽器依賴）
- 配置 `shm_size: '2gb'`（Chromium 需要共享內存）
- 使用 async Playwright API（避免非同步環境中的死鎖）

**Q: 如何確認服務是否正常運作？**

A: 執行健康檢查：
```bash
curl http://localhost:8000/health
```

