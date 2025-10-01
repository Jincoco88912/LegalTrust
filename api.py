import time
import base64
import os
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from playwright.sync_api import sync_playwright
from twocaptcha import TwoCaptcha
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()

# FastAPI 應用實例
app = FastAPI(
    title="交通罰單查詢 API",
    description="使用 Playwright + 2captcha 自動查詢台灣交通違規罰單",
    version="1.0.0"
)

# 從環境變數讀取 API Key
CAPTCHA_API_KEY = os.getenv("CAPTCHA_API_KEY", "")
TARGET_URL = os.getenv("TARGET_URL", "https://www.mvdis.gov.tw/m3-emv-vil/vil/penaltyQueryPay")

# 請求模型
class PenaltyQueryRequest(BaseModel):
    user_id: str = Field(..., description="身分證字號", example="A123456789")
    birthday: str = Field(..., description="出生年月日（民國年 YYYMMDD）", example="0780702")
    headless: bool = Field(True, description="是否使用無頭模式（不顯示瀏覽器）", example=True)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "A123456789",
                "birthday": "0780702",
                "headless": True
            }
        }

# 回應模型
class PenaltyQueryResponse(BaseModel):
    success: bool = Field(..., description="查詢是否成功")
    message: str = Field(..., description="訊息")
    captcha_code: str = Field(None, description="識別的驗證碼")
    user_id: str = Field(None, description="查詢的身分證字號")
    result_url: str = Field(None, description="結果頁面 URL")
    error: str = Field(None, description="錯誤訊息")


def solve_captcha(image_base64: str, api_key: str) -> str:
    """使用 2captcha API 解驗證碼"""
    try:
        print("正在呼叫 2captcha API 識別驗證碼...")
        solver = TwoCaptcha(api_key)
        
        # 使用 ImageToTextTask
        result = solver.normal(image_base64, 
                              case=True,      # 區分大小寫
                              numeric=4,      # 必須包含數字和字母
                              minLength=4,    # 最小長度
                              maxLength=4)    # 最大長度
        
        print(f"✓ 驗證碼識別成功: {result['code']}")
        return result['code']
    
    except Exception as e:
        print(f"✗ 驗證碼識別失敗: {e}")
        raise


def query_penalty(user_id: str, birthday: str, headless: bool = True) -> dict:
    """查詢交通罰單"""
    
    # 檢查 API Key
    if not CAPTCHA_API_KEY or CAPTCHA_API_KEY == "YOUR_API_KEY":
        raise ValueError("未設定 2captcha API Key，請在 .env 檔案中設定 CAPTCHA_API_KEY")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        
        try:
            print(f"正在前往目標網頁: {TARGET_URL}")
            page.goto(TARGET_URL, timeout=30000)
            
            print(f"正在填寫身分證字號: {user_id}")
            page.locator("#id1").fill(user_id)
            
            print(f"正在填寫出生年月日: {birthday}")
            page.locator("#birthday").fill(birthday)
            
            print("正在抓取驗證碼圖片...")
            
            # 直接從 img 元素抓取圖片並轉為 base64
            captcha_element = page.locator("#pickimg1")
            captcha_element.wait_for(timeout=10000)
            
            # 截取驗證碼圖片
            captcha_screenshot = captcha_element.screenshot()
            captcha_base64 = base64.b64encode(captcha_screenshot).decode('utf-8')
            
            print(f"✓ 驗證碼圖片已抓取 (大小: {len(captcha_screenshot)} bytes)")
            
            # 使用 2captcha API 識別驗證碼
            captcha_code = solve_captcha(captcha_base64, CAPTCHA_API_KEY)
            
            print(f"正在填寫驗證碼: {captcha_code}")
            # 使用更精確的選擇器定位第一個驗證碼輸入框（搜尋表單中的）
            page.get_by_role("table", name="搜尋表單").locator("#validateStr").fill(captcha_code)
            print("驗證碼已填寫。")
            
            print("正在點擊查詢按鈕...")
            # 直接執行 onclick 事件中的 JavaScript 函數
            page.evaluate("query(1)")
            
            # 等待結果載入
            print("等待查詢結果...")
            time.sleep(3)
            
            # 獲取當前頁面 URL
            result_url = page.url
            
            print("查詢完成！")
            
            return {
                "success": True,
                "message": "查詢成功",
                "captcha_code": captcha_code,
                "user_id": user_id,
                "result_url": result_url
            }
            
        except Exception as e:
            print(f"發生錯誤: {e}")
            return {
                "success": False,
                "message": "查詢失敗",
                "error": str(e)
            }
        finally:
            browser.close()


@app.get("/")
async def root():
    """API 根目錄"""
    return {
        "message": "交通罰單查詢 API",
        "version": "1.0.0",
        "endpoints": {
            "POST /query": "查詢交通罰單",
            "GET /health": "健康檢查"
        }
    }


@app.get("/health")
async def health_check():
    """健康檢查"""
    api_key_configured = bool(CAPTCHA_API_KEY and CAPTCHA_API_KEY != "YOUR_API_KEY")
    
    return {
        "status": "healthy",
        "api_key_configured": api_key_configured,
        "target_url": TARGET_URL
    }


@app.post("/query", response_model=PenaltyQueryResponse)
async def query_penalty_endpoint(request: PenaltyQueryRequest):
    """
    查詢交通罰單
    
    - **user_id**: 身分證字號（例如：A123456789）
    - **birthday**: 出生年月日，民國年格式 YYYMMDD（例如：0780702 代表民國78年7月2日）
    - **headless**: 是否使用無頭模式（True=不顯示瀏覽器，False=顯示瀏覽器）
    """
    try:
        print(f"\n{'='*50}")
        print(f"收到查詢請求：身分證字號={request.user_id}, 生日={request.birthday}")
        print(f"{'='*50}\n")
        
        # 使用 asyncio.to_thread 在線程中執行同步的 Playwright 代碼
        result = await asyncio.to_thread(
            query_penalty,
            request.user_id,
            request.birthday,
            request.headless
        )
        
        return PenaltyQueryResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"伺服器錯誤: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
