import time
import base64
import os
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from playwright.async_api import async_playwright
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
    user_id: str = Field(None, description="查詢的身分證字號")
    result_text: str = Field(None, description="罰單頁面文字內容")
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


async def query_penalty(user_id: str, birthday: str, headless: bool = True) -> dict:
    """查詢交通罰單"""
    
    # 檢查 API Key
    if not CAPTCHA_API_KEY or CAPTCHA_API_KEY == "YOUR_API_KEY":
        raise ValueError("未設定 2captcha API Key，請在 .env 檔案中設定 CAPTCHA_API_KEY")
    
    print("正在啟動 Playwright...")
    async with async_playwright() as p:
        print("正在啟動 Chromium 瀏覽器...")
        browser = await p.chromium.launch(
            headless=headless,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu'
            ]
        )
        print("✓ 瀏覽器已啟動")
        page = await browser.new_page()
        print("✓ 新分頁已建立")
        
        try:
            print(f"正在前往目標網頁: {TARGET_URL}")
            await page.goto(TARGET_URL, timeout=30000)
            
            print(f"正在填寫身分證字號: {user_id}")
            await page.locator("#id1").fill(user_id)
            
            print(f"正在填寫出生年月日: {birthday}")
            await page.locator("#birthday").fill(birthday)
            
            print("正在抓取驗證碼圖片...")
            
            # 直接從 img 元素抓取圖片並轉為 base64
            captcha_element = page.locator("#pickimg1")
            await captcha_element.wait_for(timeout=10000)
            
            # 截取驗證碼圖片
            captcha_screenshot = await captcha_element.screenshot()
            captcha_base64 = base64.b64encode(captcha_screenshot).decode('utf-8')
            
            print(f"✓ 驗證碼圖片已抓取 (大小: {len(captcha_screenshot)} bytes)")
            
            # 使用 2captcha API 識別驗證碼
            captcha_code = solve_captcha(captcha_base64, CAPTCHA_API_KEY)
            
            print(f"正在填寫驗證碼: {captcha_code}")
            # 使用更精確的選擇器定位第一個驗證碼輸入框（搜尋表單中的）
            await page.get_by_role("table", name="搜尋表單").locator("#validateStr").fill(captcha_code)
            print("驗證碼已填寫。")
            
            print("正在點擊查詢按鈕...")
            # 直接執行 onclick 事件中的 JavaScript 函數
            await page.evaluate("query(1)")
            
            # 等待頁面跳轉
            print("等待查詢結果...")
            await asyncio.sleep(3)
            
            # 獲取當前頁面 URL
            result_url = page.url
            print(f"當前頁面: {result_url}")
            
            # 第一步：抓取可線上繳納的罰單 (method=pagination)
            print("正在抓取可線上繳納的罰單內容...")
            pagination_text = ""
            
            try:
                # 等待 tab_frame 元素出現
                tab_frame = page.locator(".tab_frame")
                await tab_frame.wait_for(timeout=10000, state="visible")
                
                # 提取純文字內容
                pagination_text = await tab_frame.inner_text()
                print(f"✓ 已抓取可線上繳納罰單內容 (長度: {len(pagination_text)} 字元)")
                
            except Exception as e:
                print(f"⚠️ 抓取可線上繳納罰單時發生錯誤: {e}")
                pagination_text = "無法抓取可線上繳納罰單內容"
            
            # 第二步：導航到不可線上繳納的罰單頁面 (method=nopayPagination)
            print("正在前往不可線上繳納罰單頁面...")
            nopay_url = "https://www.mvdis.gov.tw/m3-emv-vil/vil/penaltyQueryPay?method=nopayPagination#gsc.tab=0"
            nopay_text = ""
            
            try:
                await page.goto(nopay_url, timeout=30000)
                print(f"✓ 已前往: {nopay_url}")
                
                # 等待頁面載入
                await asyncio.sleep(2)
                
                # 抓取 tab_frame 元素的文字內容
                tab_frame = page.locator(".tab_frame")
                await tab_frame.wait_for(timeout=10000, state="visible")
                
                # 提取純文字內容
                nopay_text = await tab_frame.inner_text()
                print(f"✓ 已抓取不可線上繳納罰單內容 (長度: {len(nopay_text)} 字元)")
                
            except Exception as e:
                print(f"⚠️ 抓取不可線上繳納罰單時發生錯誤: {e}")
                nopay_text = "無法抓取不可線上繳納罰單內容"
            
            # 合併兩個頁面的內容
            result_text = f"=== 可線上繳納的罰單 ===\n{pagination_text}\n\n=== 不可線上繳納的罰單 ===\n{nopay_text}"
            
            print("查詢完成！")
            
            return {
                "success": True,
                "message": "查詢成功",
                "user_id": user_id,
                "result_text": result_text
            }
            
        except Exception as e:
            print(f"發生錯誤: {e}")
            return {
                "success": False,
                "message": "查詢失敗",
                "error": str(e),
                "result_text": None
            }
        finally:
            await browser.close()


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
        
        # 直接調用 async 函數
        result = await query_penalty(
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
