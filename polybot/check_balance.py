import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()
address = os.getenv("WALLET_ADDRESS")

# 使用最穩定的公共節點
nodes = [
    'https://polygon-rpc.com',
    'https://rpc-mainnet.maticvigil.com',
    'https://1rpc.io/matic'
]

def get_balances():
    w3 = None
    for url in nodes:
        _w3 = Web3(Web3.HTTPProvider(url))
        if _w3.is_connected():
            w3 = _w3
            break
            
    if not w3:
        print("❌ 錯誤：所有連線節點都失敗，請檢查手機網路是否開啟。")
        return

    try:
        addr = Web3.to_checksum_address(address)
        matic = w3.from_wei(w3.eth.get_balance(addr), 'ether')
        
        # USDC 查詢
        USDC_ADDRESS = "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"
        USDC_ABI = '[{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"}]'
        usdc_contract = w3.eth.contract(address=Web3.to_checksum_address(USDC_ADDRESS), abi=USDC_ABI)
        usdc = usdc_contract.functions.balanceOf(addr).call() / 10**6
        
        print("-" * 35)
        print(f"💰 帳戶報表 (連線成功)")
        print(f"⛽ MATIC: {matic:.4f}")
        print(f"💵 USDC: {usdc:.2f}")
        print("-" * 35)
    except Exception as e:
        print(f"❌ 執行錯誤: {e}")

if __name__ == "__main__":
    get_balances()
