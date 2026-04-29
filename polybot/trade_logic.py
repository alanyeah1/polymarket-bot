import os
import time
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()
TARGETS = [t.strip() for t in os.getenv("TARGET_WALLETS", "").split(',') if t.strip()]

# 備用節點清單
RPC_URLS = [
    'https://polygon-rpc.com',
    'https://1rpc.io/matic',
    'https://rpc.ankr.com/polygon',
    'https://polygon.llamarpc.com'
]

def get_connection():
    for url in RPC_URLS:
        try:
            w3 = Web3(Web3.HTTPProvider(url, request_kwargs={'timeout': 10}))
            if w3.is_connected():
                return w3, url
        except:
            continue
    return None, None

def run_bot():
    print("\n" + "="*40)
    print("探測網路中...")
    
    w3, active_url = get_connection()
    
    if not w3:
        print("❌ [錯誤] 嘗試了所有通道都無法連線！")
        print("💡 建議：請切換 WiFi/5G，或檢查是否開了 VPN 擋住連線。")
        return
        
    print(f"✅ [連線成功] 使用通道: {active_url}")
    print(f"📡 [監控中] 正在守候 {len(TARGETS)} 位高手...")
    print("="*40 + "\n")

    last_nonces = {}
    for addr in TARGETS:
        try:
            last_nonces[addr] = w3.eth.get_transaction_count(Web3.to_checksum_address(addr))
        except:
            last_nonces[addr] = 0

    while True:
        try:
            for addr in TARGETS:
                target = Web3.to_checksum_address(addr)
                current_nonce = w3.eth.get_transaction_count(target)
                if current_nonce > last_nonces[addr]:
                    print(f"\n🚨 【抓到了！】 高手有新動作！")
                    print(f"📍 地址: {addr}")
                    last_nonces[addr] = current_nonce
            time.sleep(10)
        except Exception as e:
            # 如果中途斷線，嘗試重新連線
            w3, _ = get_connection()
            time.sleep(5)

if __name__ == "__main__":
    run_bot()
