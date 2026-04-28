import asyncio
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

VIRTUAL_MODE = True

async def send_telegram_message(message):
    if VIRTUAL_MODE:
        print(f"[Telegram] {message}")

def check_polymarket_markets():
    try:
        url = "https://gamma-api.polymarket.com/markets?limit=5"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            markets = response.json()
            return f"✅ Polymarket在線: {len(markets)} 個市場"
        else:
            return f"⚠️ 失敗: {response.status_code}"
    except Exception as e:
        return f"❌ 錯誤: {e}"

async def main():
    print(f"🤖 Bot啟動 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    await send_telegram_message("🚀 Bot已啟動！")
    
    counter = 0
    while True:
        try:
            counter += 1
            if counter % 360 == 0:
                await send_telegram_message(f"🟢 心跳 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
            
            market_status = check_polymarket_markets()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {market_status}")
            
            await asyncio.sleep(60)
        except KeyboardInterrupt:
            print("\n⏹️ Bot停止")
            break
        except Exception as e:
            print(f"❌ 錯誤: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
