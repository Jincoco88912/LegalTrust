# 使用官方 Python 3.11 slim 映像作為基礎
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 安裝系統依賴（Playwright 需要）
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements.txt
COPY requirements.txt .

# 安裝 Python 套件
RUN pip install --no-cache-dir -r requirements.txt

# 安裝 Playwright 瀏覽器（僅安裝 Chromium）
RUN playwright install chromium
RUN playwright install-deps chromium

# 複製應用程式代碼
COPY api.py .

# 暴露端口
EXPOSE 8000

# 設定環境變數
ENV PYTHONUNBUFFERED=1

# 啟動命令
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
