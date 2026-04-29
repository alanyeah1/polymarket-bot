"""
🔬 Polymarket API 參數探測器
測試所有可能的時間窗格式
"""
import requests

URL = "https://lb-api.polymarket.com/profit"

# 各種可能的參數
candidates = [
    "1d", "1w", "1m", "all",
    "7d", "30d", "24h", "168h",
    "day", "week", "month",
    "daily", "weekly", "monthly",
    "DAY", "WEEK", "MONTH",
]

print("🔬 探測 Polymarket API window 參數\n")
print(f"{'參數':<12}{'狀態':<10}{'結果'}")
print("-" * 50)

valid = []
for c in candidates:
    try:
        r = requests.get(URL, params={"window": c, "limit": 3}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            print(f"{c:<12}{'✅ OK':<10}{len(data)} 筆")
            valid.append(c)
        else:
            print(f"{c:<12}{'❌ '+str(r.status_code):<10}")
    except Exception as e:
        print(f"{c:<12}{'❌ ERR':<10}{str(e)[:30]}")

print(f"\n✅ 可用參數：{valid}")
