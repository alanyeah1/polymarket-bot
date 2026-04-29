import os
from dotenv import load_dotenv

load_dotenv()
TP = float(os.getenv("TAKE_PROFIT"))
SL = float(os.getenv("STOP_LOSS"))

def decide_trade(entry_price, current_price):
    # 計算漲跌幅
    change = (current_price - entry_price) / entry_price
    
    print(f"入場價: {entry_price} | 當前價: {current_price} | 盈虧: {change:.2%}")
    
    if change >= TP:
        return "🔥 觸發止盈！立即以 20% 漲幅賣出獲利。"
    elif change <= -SL:
        return "❄️ 觸發止損！為保護資金，立即賣出止蝕。"
    else:
        return "⏳ 繼續持倉中..."

# 模擬情境測試
print("--- 模擬：價格上漲到 25% ---")
print(decide_trade(0.50, 0.63))

print("\n--- 模擬：價格下跌到 20% ---")
print(decide_trade(0.50, 0.40))
