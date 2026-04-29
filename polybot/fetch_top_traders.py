"""
🔍 Polymarket 聰明錢追蹤器 v2.0
功能：
  1. 抓日/週/月/總四個排行榜
  2. 交叉比對，找出「多榜都上」的真·聰明錢
  3. 產出跟單候選名單
"""
import requests
import json
import os
from datetime import datetime
from collections import defaultdict

PROFIT_URL = "https://lb-api.polymarket.com/profit"
WINDOWS = {"1d": "日榜", "7d": "週榜", "30d": "月榜", "all": "總榜"}

def fetch(window, limit=50):
    try:
        r = requests.get(PROFIT_URL, params={"window": window, "limit": limit}, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"❌ {window} 失敗：{e}")
        return []

def display(traders, label, window):
    if not traders:
        return
    print(f"\n{'='*70}")
    print(f"🏆 {label} ({window}) Top {len(traders)}")
    print(f"{'='*70}")
    for i, t in enumerate(traders[:20], 1):
        addr = t.get("proxyWallet", "?")
        short = f"{addr[:6]}...{addr[-6:]}"
        profit = t.get("amount", 0)
        name = t.get("name", "")[:15]
        flag = "🔥" if profit > 10000 else "✨" if profit > 1000 else "  "
        print(f"{i:>3} {short:<22} {profit:>12.2f}  {name} {flag}")

def save(traders, window):
    os.makedirs("data", exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    fn = f"data/traders_{window}_{ts}.json"
    with open(fn, "w") as f:
        json.dump(traders, f, indent=2)
    # 也存個「最新」版方便讀取
    with open(f"data/latest_{window}.json", "w") as f:
        json.dump(traders, f, indent=2)
    print(f"💾 {fn}")

def cross_analysis(all_data):
    """
    交叉比對：找出在多個榜都上的錢包
    """
    print(f"\n{'='*70}")
    print("🔬 交叉比對分析：尋找真·聰明錢")
    print(f"{'='*70}")
    
    # 統計每個錢包在幾個榜出現
    wallet_appearance = defaultdict(lambda: {
        "count": 0,
        "windows": [],
        "profits": {},
        "name": "",
        "address": ""
    })
    
    for window, traders in all_data.items():
        for t in traders:
            addr = t.get("proxyWallet", "?")
            if addr == "?":
                continue
            wallet_appearance[addr]["count"] += 1
            wallet_appearance[addr]["windows"].append(window)
            wallet_appearance[addr]["profits"][window] = t.get("amount", 0)
            wallet_appearance[addr]["name"] = t.get("name", "")
            wallet_appearance[addr]["address"] = addr
    
    # 排序：先按出現次數，再按總獲利
    ranked = sorted(
        wallet_appearance.values(),
        key=lambda x: (x["count"], sum(x["profits"].values())),
        reverse=True
    )
    
    # 分類
    god_tier = [w for w in ranked if w["count"] >= 4]   # 四榜全上 👑
    elite = [w for w in ranked if w["count"] == 3]       # 三榜 ⭐⭐⭐
    stable = [w for w in ranked if w["count"] == 2]      # 兩榜 ⭐⭐
    
    print(f"\n👑 神級（四榜全上）：{len(god_tier)} 個")
    for w in god_tier[:10]:
        addr_short = f"{w['address'][:6]}...{w['address'][-6:]}"
        profits_str = " | ".join([f"{k}:{v:.0f}" for k, v in w["profits"].items()])
        print(f"   {addr_short}  {w['name'][:15]:<15}  {profits_str}")
    
    print(f"\n⭐⭐⭐ 頂級（三榜上）：{len(elite)} 個")
    for w in elite[:10]:
        addr_short = f"{w['address'][:6]}...{w['address'][-6:]}"
        profits_str = " | ".join([f"{k}:{v:.0f}" for k, v in w["profits"].items()])
        print(f"   {addr_short}  {w['name'][:15]:<15}  {profits_str}")
    
    print(f"\n⭐⭐ 穩定（兩榜上）：{len(stable)} 個")
    for w in stable[:10]:
        addr_short = f"{w['address'][:6]}...{w['address'][-6:]}"
        profits_str = " | ".join([f"{k}:{v:.0f}" for k, v in w["profits"].items()])
        print(f"   {addr_short}  {w['name'][:15]:<15}  {profits_str}")
    
    # 儲存跟單候選名單
    candidates = {
        "analyzed_at": datetime.now().isoformat(),
        "god_tier": god_tier,
        "elite": elite,
        "stable": stable,
    }
    with open("data/smart_money_candidates.json", "w") as f:
        json.dump(candidates, f, indent=2)
    print(f"\n💾 已存跟單候選名單：data/smart_money_candidates.json")
    
    return candidates

def main():
    print("=" * 70)
    print("🎯 Polymarket 聰明錢追蹤 v2.0")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)
    
    all_data = {}
    for window, label in WINDOWS.items():
        print(f"\n📊 抓取 {label} ({window})...")
        traders = fetch(window, limit=50)
        if traders:
            all_data[window] = traders
            display(traders, label, window)
            save(traders, window)
    
    if len(all_data) >= 2:
        cross_analysis(all_data)
    
    print("\n" + "=" * 70)
    print("✅ 完成！檢視跟單候選：cat data/smart_money_candidates.json")
    print("=" * 70)

if __name__ == "__main__":
    main()
