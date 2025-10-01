# 🐳 Docker 部署指南

本文檔說明如何使用 Docker 一鍵部署交通罰單查詢 API 服務。

## 📋 前置需求

- Docker (>= 20.10)
- Docker Compose (>= 1.29)
- 已設定好的 `.env` 檔案

## 🚀 快速開始

### 方法一：使用 Docker Compose（推薦）

#### 1. 確認 .env 檔案已設定

```bash
# 檢查 .env 檔案是否存在
cat .env

# 應該包含：
# CAPTCHA_API_KEY=your_api_key_here
# TARGET_URL=https://www.mvdis.gov.tw/m3-emv-vil/vil/penaltyQueryPay
```

#### 2. 一鍵啟動服務

```bash
docker compose up -d
```

就這麼簡單！🎉

#### 3. 查看服務狀態

```bash
# 查看運行狀態
docker compose ps

# 查看日誌
docker compose logs -f

# 查看最近 100 行日誌
docker compose logs --tail=100
```

#### 4. 測試 API

```bash
# 健康檢查
curl http://localhost:8000/health

# 查詢罰單
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "A123456789",
    "birthday": "0780702"
  }'
```

#### 5. 停止服務

```bash
# 停止但保留容器
docker compose stop

# 停止並刪除容器
docker compose down

# 停止並刪除容器及映像
docker compose down --rmi all
```

---

### 方法二：使用 Docker 指令

#### 1. 建立 Docker 映像

```bash
docker build -t penalty-query-api .
```

#### 2. 執行容器

```bash
docker run -d \
  --name penalty-query-api \
  -p 8000:8000 \
  --env-file .env \
  penalty-query-api
```

#### 3. 查看日誌

```bash
docker logs -f penalty-query-api
```

#### 4. 停止容器

```bash
docker stop penalty-query-api
docker rm penalty-query-api
```

---

## 📊 Docker Compose 指令速查表

| 指令 | 說明 |
|------|------|
| `docker compose up -d` | 啟動服務（背景執行） |
| `docker compose up --build` | 重新建立映像並啟動 |
| `docker compose down` | 停止並移除容器 |
| `docker compose ps` | 查看服務狀態 |
| `docker compose logs -f` | 即時查看日誌 |
| `docker compose restart` | 重啟服務 |
| `docker compose exec penalty-query-api bash` | 進入容器 shell |

---

## 🔧 進階配置

### 修改端口映射

編輯 `docker compose.yml`：

```yaml
ports:
  - "8080:8000"  # 將本機 8080 映射到容器 8000
```

### 設定資源限制

已在 `docker compose.yml` 中預設配置：

```yaml
deploy:
  resources:
    limits:
      cpus: '2'      # 最多使用 2 個 CPU
      memory: 2G     # 最多使用 2GB 記憶體
```

### 查看資源使用情況

```bash
docker stats penalty-query-api
```

---

## 🏗️ 多容器部署（擴展）

如果需要多個實例處理高併發：

```bash
# 啟動 3 個實例
docker compose up -d --scale penalty-query-api=3
```

注意：需要配置 Nginx 或其他負載均衡器。

---

## 🔍 健康檢查

Docker Compose 已配置自動健康檢查：

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s      # 每 30 秒檢查一次
  timeout: 10s       # 超時時間 10 秒
  retries: 3         # 重試 3 次
  start_period: 40s  # 啟動後 40 秒才開始檢查
```

查看健康狀態：

```bash
docker inspect --format='{{.State.Health.Status}}' penalty-query-api
```

---

## 📝 環境變數說明

在 `.env` 檔案中設定：

| 變數 | 必填 | 說明 | 範例 |
|------|------|------|------|
| `CAPTCHA_API_KEY` | ✅ | 2captcha API Key | `93e6cae8fe54f02d...` |
| `TARGET_URL` | ❌ | 目標網址 | `https://www.mvdis.gov.tw/...` |
| `USER_ID` | ❌ | 預設身分證字號 | `A123456789` |
| `BIRTHDAY` | ❌ | 預設生日 | `0780702` |

---

## 🐛 故障排除

### 問題 1：容器無法啟動

```bash
# 查看詳細日誌
docker compose logs

# 檢查容器狀態
docker compose ps
```

### 問題 2：找不到 .env 檔案

```bash
# 複製範例檔案
cp .env.example .env

# 編輯並填入您的 API Key
nano .env
```

### 問題 3：端口已被占用

```bash
# 查看哪個程式占用 8000 端口
lsof -i :8000

# 修改 docker compose.yml 中的端口映射
ports:
  - "8001:8000"
```

### 問題 4：映像建立失敗

```bash
# 清理並重新建立
docker compose down
docker compose build --no-cache
docker compose up -d
```

### 問題 5：Playwright 瀏覽器錯誤

```bash
# 重新建立映像（確保安裝了瀏覽器驅動）
docker compose build --no-cache
```

---

## 🔄 更新部署

當程式碼更新後：

```bash
# 1. 停止現有容器
docker compose down

# 2. 重新建立映像
docker compose build

# 3. 啟動新容器
docker compose up -d
```

或一行搞定：

```bash
docker compose up -d --build
```

---

## 📦 映像管理

### 查看映像

```bash
docker images | grep penalty-query-api
```

### 清理未使用的映像

```bash
docker image prune -a
```

### 匯出映像（用於離線部署）

```bash
# 匯出
docker save -o penalty-query-api.tar penalty-query-api:latest

# 匯入（在另一台機器）
docker load -i penalty-query-api.tar
```

---

## 🌐 生產環境部署建議

### 1. 使用 HTTPS

配合 Nginx + Let's Encrypt：

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. 設定開機自動啟動

```bash
# 設定 restart policy
docker compose up -d --restart=always
```

### 3. 監控和日誌

```bash
# 使用 Docker 日誌驅動
docker compose logs --since 1h > app.log

# 或整合 ELK Stack / Prometheus
```

### 4. 備份配置

```bash
# 定期備份 .env 和 docker compose.yml
tar -czf backup-$(date +%Y%m%d).tar.gz .env docker compose.yml
```

---

## 📊 效能優化

### 1. 使用映像快取

```bash
# 建立時使用 BuildKit
DOCKER_BUILDKIT=1 docker compose build
```

### 2. 多階段建構（進階）

可以進一步優化 Dockerfile 減少映像大小。

### 3. 限制併發請求

在應用層面設定 worker 數量：

```yaml
command: uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 🎯 完整部署流程範例

```bash
# 1. 克隆專案
git clone <repository-url>
cd LegalTrust

# 2. 設定環境變數
cp .env.example .env
nano .env  # 填入 API Key

# 3. 啟動服務
docker compose up -d

# 4. 查看狀態
docker compose ps
docker compose logs -f

# 5. 測試 API
curl http://localhost:8000/health

# 6. 訪問文檔
# 瀏覽器開啟 http://localhost:8000/docs
```

---

## ✅ 驗證清單

部署前檢查：

- [ ] `.env` 檔案已正確設定
- [ ] Docker 和 Docker Compose 已安裝
- [ ] 8000 端口未被占用
- [ ] 有足夠的磁碟空間（至少 2GB）
- [ ] 網路連線正常

部署後檢查：

- [ ] 容器正在運行 (`docker compose ps`)
- [ ] 健康檢查通過 (`curl http://localhost:8000/health`)
- [ ] API 文檔可訪問 (`http://localhost:8000/docs`)
- [ ] 查詢功能正常

---

## 📞 支援

如有問題，請：
1. 查看日誌：`docker compose logs -f`
2. 檢查健康狀態：`docker inspect penalty-query-api`
3. 提交 Issue 或聯繫維護者

---

## 📄 授權

本專案僅供學習和測試使用。
