# 交通罰單查詢 FastAPI 服務

這是一個基於 FastAPI 的 RESTful API 服務，可以透過 HTTP 請求自動查詢台灣交通違規罰單。

## 🚀 快速開始

### 1. 安裝相依套件

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. 設定環境變數

確保 `.env` 檔案中已設定 2captcha API Key：

```bash
CAPTCHA_API_KEY=your_2captcha_api_key_here
TARGET_URL=https://www.mvdis.gov.tw/m3-emv-vil/vil/penaltyQueryPay
```

### 3. 啟動 API 服務

```bash
python api.py
```

或使用 uvicorn（推薦用於生產環境）：

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

服務將在 `http://localhost:8000` 啟動。

## 📚 API 文檔

啟動服務後，可以訪問以下網址查看自動生成的 API 文檔：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 API 端點

### 1. 根目錄

```http
GET /
```

**回應範例：**
```json
{
  "message": "交通罰單查詢 API",
  "version": "1.0.0",
  "endpoints": {
    "POST /query": "查詢交通罰單",
    "GET /health": "健康檢查"
  }
}
```

### 2. 健康檢查

```http
GET /health
```

**回應範例：**
```json
{
  "status": "healthy",
  "api_key_configured": true,
  "target_url": "https://www.mvdis.gov.tw/m3-emv-vil/vil/penaltyQueryPay"
}
```

### 3. 查詢罰單 ⭐ 主要功能

```http
POST /query
Content-Type: application/json
```

**請求參數：**

| 參數 | 類型 | 必填 | 說明 | 範例 |
|------|------|------|------|------|
| user_id | string | ✅ | 身分證字號 | "A123456789" |
| birthday | string | ✅ | 出生年月日（民國年 YYYMMDD） | "0780702" |
| headless | boolean | ❌ | 是否使用無頭模式（預設：true） | true |

**請求範例：**
```json
{
  "user_id": "A123456789",
  "birthday": "0780702",
  "headless": true
}
```

**成功回應範例：**
```json
{
  "success": true,
  "message": "查詢成功",
  "captcha_code": "K3V9",
  "user_id": "A123456789",
  "result_url": "https://www.mvdis.gov.tw/m3-emv-vil/vil/penaltyQueryPay",
  "error": null
}
```

**失敗回應範例：**
```json
{
  "success": false,
  "message": "查詢失敗",
  "captcha_code": null,
  "user_id": null,
  "result_url": null,
  "error": "Timeout 30000ms exceeded"
}
```

## 💻 使用範例

### 使用 Python requests

```python
import requests

url = "http://localhost:8000/query"
payload = {
    "user_id": "A123456789",
    "birthday": "0780702",
    "headless": True
}

response = requests.post(url, json=payload)
result = response.json()

if result["success"]:
    print(f"查詢成功！驗證碼: {result['captcha_code']}")
else:
    print(f"查詢失敗：{result['error']}")
```

### 使用 curl

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "A123456789",
    "birthday": "0780702",
    "headless": true
  }'
```

### 使用 JavaScript (fetch)

```javascript
fetch('http://localhost:8000/query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    user_id: 'A123456789',
    birthday: '0780702',
    headless: true
  })
})
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      console.log('查詢成功！驗證碼:', data.captcha_code);
    } else {
      console.log('查詢失敗:', data.error);
    }
  });
```

## 🧪 測試 API

使用提供的測試腳本：

```bash
# 確保 API 服務正在運行
python test_api.py
```

## 📋 參數說明

### user_id（身分證字號）
- 格式：1 個英文字母 + 9 個數字
- 範例：`A123456789`

### birthday（出生年月日）
- 格式：民國年 YYYMMDD（7 位數字）
- 範例：`0780702` 代表民國 78 年 7 月 2 日
- 注意：民國年需補零，如民國 8 年寫成 `0080101`

### headless（無頭模式）
- `true`：不顯示瀏覽器視窗（適合生產環境）
- `false`：顯示瀏覽器視窗（適合除錯）

## ⚙️ 進階設定

### 修改監聽位址和埠號

```bash
uvicorn api:app --host 0.0.0.0 --port 8080
```

### 啟用自動重載（開發模式）

```bash
uvicorn api:app --reload
```

### 使用多個 worker（生產環境）

```bash
uvicorn api:app --workers 4
```

## 🔒 安全建議

1. ⚠️ **不要將 API Key 暴露在公開的地方**
2. ⚠️ **建議在生產環境使用 HTTPS**
3. ⚠️ **考慮加入 API 認證機制（如 JWT）**
4. ⚠️ **設定請求頻率限制（Rate Limiting）**
5. ⚠️ **不要將 `.env` 檔案上傳至 Git**

## 🐛 錯誤處理

### 常見錯誤碼

| 狀態碼 | 說明 |
|--------|------|
| 200 | 請求成功 |
| 400 | 請求參數錯誤（如未設定 API Key） |
| 500 | 伺服器內部錯誤 |

### 常見錯誤訊息

- `未設定 2captcha API Key`：請在 `.env` 中設定 `CAPTCHA_API_KEY`
- `Timeout exceeded`：網頁載入超時，請檢查網路連線
- `驗證碼識別失敗`：2captcha API 無法識別驗證碼，會自動重試

## 📊 效能說明

- 單次查詢平均耗時：**15-25 秒**
  - 網頁載入：3-5 秒
  - 驗證碼識別：10-15 秒
  - 表單提交：2-3 秒
- 建議併發請求數：**2-5 個**（避免過度消耗資源）

## 💰 成本估算

- 每次查詢消耗：約 **$0.001 USD**（2captcha 費用）
- 1000 次查詢：約 **$1 USD**

## 📝 待辦事項

- [ ] 加入 API 認證機制
- [ ] 實作請求頻率限制
- [ ] 加入查詢結果快取
- [ ] 支援批次查詢
- [ ] 加入 Webhook 通知
- [ ] Docker 容器化部署

## 🤝 貢獻

歡迎提交 Issue 或 Pull Request！

## ⚖️ 授權

本專案僅供學習和測試使用，請遵守相關法律規定。
