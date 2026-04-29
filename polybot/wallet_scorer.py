"""
🎯 錢包可跟單性評分器 v1.0
篩選條件：
  ✅ 最近 30 天有活動
  ✅ 有買有賣（不是單向鯨魚）
  ✅ 單筆金額 < 500 USDC（跟得起）
  ✅ 當前持倉有正收益（還在賺）
  ✅ 交易次數適中（不是機器人）
"""
import requests
import json
import os
from datetime import datetime, timedelta
from collections import Counter

DATA_API = "https://data-api.polymarket.com"

# 你的本金和風險承受
YOUR_CAPITAL = 256  # USDC
MAX_COPY_SIZE = 25  # 你願意單筆跟 25 USDC 以內

def fetch_positions(wallet):
    try:
        r = requests.get(f"{DATA_API}/positions", params={"user": wallet}, timeout=15)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []

def fetch_trades(wallet, limit=200):
    try:
        r = requests.get(f"{DATA_API}/trades", 
                        params={"user": wallet, "limit": limit}, timeout=20)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []

def score_wallet(wallet, name=""):
    """給錢包打分（0-100）"""
    positions = fetch_positions(wallet)
    trades = fetch_trades(wallet)
    
    score = 0
    reasons = []
    red_flags = []
    
    # 1. 有持倉嗎？（+10）
    if positions:
        score += 10
        reasons.append(f"✅ 有 {len(positions)} 個持倉")
    else:
        red_flags.append("❌ 沒持倉（可能不活躍）")
    
    # 2. 當前持倉有賺嗎？（+20）
    if positions:
        total_pnl = sum(p.get("cashPnl", 0) for p in positions)
        total_value = sum(p.get("currentValue", 0) for p in positions)
        if total_value > 0:
            positive_count = sum(1 for p in positions if p.get("cashPnl", 0) > 0)
            win_rate = positive_count / len(positions) * 100
            if win_rate > 60:
                score += 20
                reasons.append(f"✅ 持倉勝率 {win_rate:.0f}%")
            elif win_rate > 40:
                score += 10
                reasons.append(f"⚠️ 持倉勝率 {win_rate:.0f}%")
            else:
                red_flags.append(f"❌ 持倉勝率只有 {win_rate:.0f}%")
        else:
            red_flags.append("❌ 持倉價值為 0（可能全虧）")
    
    # 3. 有交易嗎？（+10）
    if trades:
        score += 10
        reasons.append(f"✅ 有 {len(trades)} 筆交易紀錄")
    
    # 4. 最近活躍嗎？（+15）
    if trades:
        latest_ts = max(int(t.get("timestamp", 0)) for t in trades)
        days_ago = (datetime.now().timestamp() - latest_ts) / 86400
        if days_ago < 7:
            score += 15
            reasons.append(f"✅ {days_ago:.1f} 天前還在交易")
        elif days_ago < 30:
            score += 8
            reasons.append(f"⚠️ {days_ago:.1f} 天前才交易")
        else:
            red_flags.append(f"❌ 已經 {days_ago:.0f} 天沒交易了")
    
    # 5. 有買有賣嗎？（+15）
    if trades:
        buys = sum(1 for t in trades if t.get("side") == "BUY")
        sells = sum(1 for t in trades if t.get("side") == "SELL")
        if sells > 0:
            ratio = sells / max(buys, 1)
            if 0.3 < ratio < 3:
                score += 15
                reasons.append(f"✅ 買賣均衡 B:{buys} S:{sells}")
            else:
                score += 5
                red_flags.append(f"⚠️ 買賣失衡 B:{buys} S:{sells}")
        else:
            red_flags.append(f"❌ 只買不賣（可能是機器人）B:{buys} S:{sells}")
    
    # 6. 單筆金額你跟得起嗎？（+20）
    if trades:
        sizes = []
        for t in trades:
            size_usdc = float(t.get("size", 0)) * float(t.get("price", 0))
            sizes.append(size_usdc)
        avg_size = sum(sizes) / len(sizes) if sizes else 0
        
        if avg_size < 100:
            score += 20
            reasons.append(f"✅ 平均單筆 {avg_size:.0f} USDC（你能跟）")
        elif avg_size < 500:
            score += 15
            reasons.append(f"✅ 平均單筆 {avg_size:.0f} USDC（按比例跟）")
        elif avg_size < 2000:
            score += 10
            reasons.append(f"⚠️ 平均單筆 {avg_size:.0f} USDC（要縮小比例）")
        else:
            red_flags.append(f"❌ 平均單筆 {avg_size:.0f} USDC（太大，跟不起）")
    
    # 7. 市場多樣性（+10）
    if trades:
        markets = set(t.get("conditionId", "") for t in trades)
        if len(markets) > 10:
            score += 10
            reasons.append(f"✅ 玩 {len(markets)} 個不同市場（分散）")
        elif len(markets) > 3:
            score += 5
            reasons.append(f"⚠️ 只玩 {len(markets)} 個市場（集中）")
        else:
            red_flags.append(f"❌ 只玩 {len(markets)} 個市場（高集中，可能是套利 bot）")
    
    return {
        "wallet": wallet,
        "name": name,
        "score": score,
        "reasons": reasons,
        "red_flags": red_flags,
        "trade_count": len(trades),
        "position_count": len(positions),
    }

def main():
    try:
        with open("data/smart_money_candidates.json") as f:
            candidates = json.load(f)
    except FileNotFoundError:
        print("❌ 請先跑 fetch_top_traders.py")
        return
    
    all_wallets = (candidates.get("god_tier", []) + 
                   candidates.get("elite", []) + 
                   candidates.get("stable", [])[:10])  # 只看前 10 個穩定
    
    print("=" * 70)
    print(f"🎯 評分 {len(all_wallets)} 個候選錢包")
    print(f"💰 你的本金：{YOUR_CAPITAL} USDC")
    print(f"📏 願意單筆跟：{MAX_COPY_SIZE} USDC")
    print("=" * 70)
    
    results = []
    for i, w in enumerate(all_wallets, 1):
        print(f"\n[{i}/{len(all_wallets)}] 分析 {w.get('name','?')[:15]} ...", end=" ")
        result = score_wallet(w["address"], w.get("name", ""))
        results.append(result)
        print(f"分數：{result['score']}/100")
    
    # 排序
    results.sort(key=lambda x: x["score"], reverse=True)
    
    print(f"\n{'='*70}")
    print("🏆 跟單評分排行榜")
    print(f"{'='*70}")
    
    for i, r in enumerate(results, 1):
        addr = r["wallet"]
        short = f"{addr[:6]}...{addr[-6:]}"
        name = r["name"][:15]
        score = r["score"]
        
        # 評級
        if score >= 80:
            grade = "🥇 A+ 強烈推薦跟單"
        elif score >= 60:
            grade = "🥈 B  可以考慮"
        elif score >= 40:
            grade = "🥉 C  觀察中"
        else:
            grade = "❌ D  不建議"
        
        print(f"\n{i}. {short}  {name:<15}  {score}/100  {grade}")
        for reason in r["reasons"][:3]:
            print(f"   {reason}")
        for flag in r["red_flags"][:2]:
            print(f"   {flag}")
    
    # 儲存
    with open("data/wallet_scores.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # 最終推薦
    top = [r for r in results if r["score"] >= 60]
    print(f"\n{'='*70}")
    print(f"✨ 最終跟單名單：{len(top)} 個錢包（60 分以上）")
    print(f"{'='*70}")
    for r in top:
        print(f"   ✅ {r['wallet']}  {r['name']}  ({r['score']}/100)")

if __name__ == "__main__":
    main()
