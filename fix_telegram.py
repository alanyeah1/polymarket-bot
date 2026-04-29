import asyncio
import os
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))

async def send_test_message():
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="🧪 測試訊息 - 如果你睇到呢個，Telegram 就 Work 咗！")
        print("✅ 測試成功！")
    except TelegramError as e:
        print(f"❌ Telegram Error: {e}")
    except Exception as e:
        print(f"❌ 其他錯誤: {e}")

asyncio.run(send_test_message())
