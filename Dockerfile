# 使用 Playwright 官方映像（已包含所有瀏覽器依賴）
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# 設定工作目錄
WORKDIR /app

# 複製 requirements.txt
COPY requirements.txt .

# 安裝 Python 套件
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式代碼
COPY api.py .

# 暴露端口
EXPOSE 8000

# 設定環境變數
ENV PYTHONUNBUFFERED=1

# 啟動命令
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]


