"""
🔬 錢包深度分析器 v1.0
功能：輸入錢包地址，抓取完整交易歷史並分析
"""
import requests
import json
import sys
from datetime import datetime
from collections import Counter

# Polymarket Data API
DATA_API = "https://data-api.polymarket.com"

def fetch_positions(wallet):
    """抓當前持倉"""
    try:
        r = requests.get(f"{DATA_API}/positions", params={"user": wallet}, timeout=15)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"❌ positions 失敗：{e}")
    return []

def fetch_trades(wallet, limit=500):
    """抓交易紀錄"""
    try:
        r = requests.get(
            f"{DATA_API}/trades",
            params={"user": wallet, "limit": limit},
            timeout=20
        )
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"❌ trades 失敗：{e}")
    return []

def fetch_activity(wallet, limit=200):
    """抓活動紀錄"""
    try:
        r = requests.get(
            f"{DATA_API}/activity",
            params={"user": wallet, "limit": limit},
            timeout=20
        )
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"❌ activity 失敗：{e}")
    return []

def analyze(wallet, name=""):
    print(f"\n{'='*70}")
    print(f"🔬 分析錢包：{name or wallet[:10]+'...'}")
    print(f"📍 地址：{wallet}")
    print(f"{'='*70}")
    
    # 1. 當前持倉
    positions = fetch_positions(wallet)
    print(f"\n💼 當前持倉：{len(positions)} 個")
    total_value = 0
    if positions:
        for i, p in enumerate(positions[:10], 1):
            title = p.get("title", "?")[:40]
            size = p.get("size", 0)
            cur_val = p.get("currentValue", 0)
            pnl = p.get("cashPnl", 0)
            pct = p.get("percentPnl", 0)
            total_value += cur_val
            emoji = "📈" if pnl > 0 else "📉"
            print(f"  {i}. {emoji} {title}")
            print(f"     大小:{size:.0f} | 現值:{cur_val:.2f} | 盈虧:{pnl:+.2f} ({pct:+.1f}%)")
        print(f"\n  💰 總持倉價值：{total_value:.2f} USDC")
    
    # 2. 交易紀錄
    trades = fetch_trades(wallet, limit=100)
    print(f"\n📊 最近交易：{len(trades)} 筆")
    if trades:
        # 統計
        buy_count = sum(1 for t in trades if t.get("side") == "BUY")
        sell_count = sum(1 for t in trades if t.get("side") == "SELL")
        total_volume = sum(float(t.get("size", 0)) * float(t.get("price", 0)) for t in trades)
        avg_size = total_volume / len(trades) if trades else 0
        
        print(f"  買單：{buy_count} | 賣單：{sell_count}")
        print(f"  總交易量：{total_volume:.2f} USDC")
        print(f"  平均單筆：{avg_size:.2f} USDC")
        
        # 最近 5 筆
        print(f"\n  🕐 最近 5 筆交易：")
        for t in trades[:5]:
            side = t.get("side", "?")
            title = t.get("title", "?")[:35]
            price = float(t.get("price", 0))
            size = float(t.get("size", 0))
            ts = t.get("timestamp", 0)
            dt = datetime.fromtimestamp(ts).strftime("%m-%d %H:%M") if ts else "?"
            emoji = "🟢" if side == "BUY" else "🔴"
            print(f"    {emoji} {dt} {side} @ {price:.3f} size:{size:.0f}  {title}")
        
        # 最常玩的市場類型
        titles = [t.get("title", "") for t in trades]
        keywords = []
        for title in titles:
            for kw in ["Trump", "Biden", "Bitcoin", "ETH", "Election", "NBA", "NFL", 
                       "Super Bowl", "Fed", "Oscar", "Ukraine", "China"]:
                if kw.lower() in title.lower():
                    keywords.append(kw)
        if keywords:
            top_topics = Counter(keywords).most_common(5)
            print(f"\n  🎯 常玩主題：{', '.join([f'{k}({v})' for k, v in top_topics])}")
    
    # 儲存
    import os
    os.makedirs("data/wallets", exist_ok=True)
    with open(f"data/wallets/{wallet}.json", "w") as f:
        json.dump({
            "wallet": wallet,
            "name": name,
            "positions": positions,
            "trades": trades,
            "analyzed_at": datetime.now().isoformat()
        }, f, indent=2)
    print(f"\n  💾 已存：data/wallets/{wallet}.json")

def main():
    # 從候選名單讀神級
    try:
        with open("data/smart_money_candidates.json") as f:
            candidates = json.load(f)
    except FileNotFoundError:
        print("❌ 找不到候選名單，請先跑 fetch_top_traders.py")
        return
    
    print("🎯 準備分析神級錢包...")
    god_tier = candidates.get("god_tier", [])
    elite = candidates.get("elite", [])
    
    # 分析神級
    for w in god_tier:
        analyze(w["address"], w["name"])
    
    # 分析頂級前 3 名
    print(f"\n\n{'#'*70}")
    print("# 繼續分析頂級（三榜上）前 3 名")
    print(f"{'#'*70}")
    for w in elite[:3]:
        analyze(w["address"], w["name"])
    
    print("\n" + "=" * 70)
    print("✅ 分析完成！")
    print("=" * 70)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 指定錢包
        analyze(sys.argv[1])
    else:
        main()
