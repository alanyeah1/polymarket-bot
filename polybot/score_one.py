"""
🎯 單錢包即時評分
用法：python score_one.py <錢包地址>
"""
import sys
import requests
from datetime import datetime

DATA_API = "https://data-api.polymarket.com"

def analyze(wallet):
    print(f"\n{'='*65}")
    print(f"🔬 深度分析：{wallet}")
    print(f"{'='*65}")
    
    # 抓持倉
    try:
        r = requests.get(f"{DATA_API}/positions", params={"user": wallet}, timeout=15)
        positions = r.json() if r.status_code == 200 else []
    except:
        positions = []
    
    # 抓交易
    try:
        r = requests.get(f"{DATA_API}/trades", 
                        params={"user": wallet, "limit": 200}, timeout=20)
        trades = r.json() if r.status_code == 200 else []
    except:
        trades = []
    
    score = 0
    print(f"\n📋 基本資訊")
    print(f"   持倉數：{len(positions)}")
    print(f"   交易數：{len(trades)}")
    
    # ========== 評分 ==========
    
    # 1. 持倉勝率
    if positions:
        score += 10
        total_value = sum(p.get("currentValue", 0) for p in positions)
        total_pnl = sum(p.get("cashPnl", 0) for p in positions)
        positive = sum(1 for p in positions if p.get("cashPnl", 0) > 0)
        win_rate = positive / len(positions) * 100
        
        print(f"\n💼 持倉狀況")
        print(f"   總持倉價值：{total_value:.2f} USDC")
        print(f"   總未實現盈虧：{total_pnl:+.2f} USDC")
        print(f"   持倉勝率：{win_rate:.0f}% ({positive}/{len(positions)})")
        
        if total_value > 100:
            score += 10
            print(f"   ✅ 持倉價值 > 100（還在玩）")
        else:
            print(f"   ⚠️ 持倉價值太低")
        
        if win_rate >= 60:
            score += 20
            print(f"   ✅ 持倉勝率高")
        elif win_rate >= 40:
            score += 10
            print(f"   ⚠️ 持倉勝率中等")
        else:
            print(f"   ❌ 持倉勝率低")
    else:
        print(f"\n❌ 沒有持倉")
    
    # 2. 最近活躍度
    if trades:
        latest = max(int(t.get("timestamp", 0)) for t in trades)
        days = (datetime.now().timestamp() - latest) / 86400
        print(f"\n⏰ 活躍度")
        print(f"   最近交易：{days:.1f} 天前")
        
        if days < 3:
            score += 20
            print(f"   ✅ 非常活躍")
        elif days < 7:
            score += 15
            print(f"   ✅ 活躍")
        elif days < 30:
            score += 5
            print(f"   ⚠️ 不太活躍")
        else:
            print(f"   ❌ 已沉寂")
    
    # 3. 買賣平衡
    if trades:
        buys = sum(1 for t in trades if t.get("side") == "BUY")
        sells = sum(1 for t in trades if t.get("side") == "SELL")
        print(f"\n📊 交易行為")
        print(f"   買單：{buys}，賣單：{sells}")
        
        if sells > 0 and 0.3 < sells/max(buys,1) < 3:
            score += 15
            print(f"   ✅ 有進有出")
        elif sells == 0:
            print(f"   ❌ 只買不賣（像機器人）")
        else:
            score += 5
            print(f"   ⚠️ 買賣不平衡")
    
    # 4. 單筆金額
    if trades:
        sizes = [float(t.get("size", 0)) * float(t.get("price", 0)) for t in trades]
        avg_size = sum(sizes) / len(sizes)
        max_size = max(sizes)
        median = sorted(sizes)[len(sizes)//2]
        
        print(f"\n💰 下注金額")
        print(f"   平均：{avg_size:.2f} USDC")
        print(f"   中位數：{median:.2f} USDC")
        print(f"   最大：{max_size:.2f} USDC")
        
        # 以 256 USDC 本金來評
        if avg_size < 50:
            score += 20
            print(f"   ✅ 你跟得起（比例 1:1）")
        elif avg_size < 200:
            score += 15
            print(f"   ✅ 按比例跟（1:4 或 1:8）")
        elif avg_size < 1000:
            score += 10
            print(f"   ⚠️ 只能小比例跟（1:20）")
        elif avg_size < 5000:
            score += 5
            print(f"   ⚠️ 跟起來很難")
        else:
            print(f"   ❌ 鯨魚，你跟不起")
    
    # 5. 市場多樣性
    if trades:
        markets = set(t.get("conditionId", "") for t in trades)
        print(f"\n🎯 市場分散度")
        print(f"   玩過 {len(markets)} 個不同市場")
        
        if len(markets) > 20:
            score += 10
            print(f"   ✅ 很分散（像投資組合）")
        elif len(markets) > 5:
            score += 5
            print(f"   ⚠️ 中等分散")
        else:
            print(f"   ❌ 太集中（可能是套利 bot）")
    
    # 最近 5 筆交易
    if trades:
        print(f"\n🕐 最近 5 筆交易")
        for t in trades[:5]:
            side = t.get("side", "?")
            title = t.get("title", "?")[:40]
            price = float(t.get("price", 0))
            size = float(t.get("size", 0))
            ts = int(t.get("timestamp", 0))
            dt = datetime.fromtimestamp(ts).strftime("%m-%d %H:%M") if ts else "?"
            emoji = "🟢" if side == "BUY" else "🔴"
            size_usdc = size * price
            print(f"   {emoji} {dt} {side} @ {price:.3f} ${size_usdc:.0f}")
            print(f"      {title}")
    
    # 當前持倉 Top 5
    if positions:
        print(f"\n💎 當前持倉 Top 5（按價值）")
        sorted_pos = sorted(positions, key=lambda x: x.get("currentValue", 0), reverse=True)
        for p in sorted_pos[:5]:
            title = p.get("title", "?")[:40]
            val = p.get("currentValue", 0)
            pnl = p.get("cashPnl", 0)
            pct = p.get("percentPnl", 0)
            emoji = "📈" if pnl > 0 else "📉"
            print(f"   {emoji} {title}")
            print(f"      現值:{val:.2f}  盈虧:{pnl:+.2f} ({pct:+.1f}%)")
    
    # ========== 最終評分 ==========
    print(f"\n{'='*65}")
    print(f"🏆 總分：{score}/100")
    
    if score >= 80:
        verdict = "🥇 A+ 強烈推薦！立即加入跟單名單"
    elif score >= 65:
        verdict = "🥈 A  非常值得跟單"
    elif score >= 50:
        verdict = "🥉 B  可以跟，但需觀察"
    elif score >= 35:
        verdict = "⚠️ C  風險較高，不建議新手"
    else:
        verdict = "❌ D  不要跟！"
    
    print(f"📝 結論：{verdict}")
    print(f"{'='*65}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python score_one.py <錢包地址1> [錢包地址2] ...")
        sys.exit(1)
    
    for wallet in sys.argv[1:]:
        analyze(wallet)
