from web3 import Web3
import os

# 生成全新錢包
w3 = Web3()
acct = w3.eth.account.create()

print("--- 機器人專用錢包生成成功 ---")
print(f"你的地址 (Address): {acct.address}")
print(f"你的私鑰 (Private Key): {acct.key.hex()}")
print("-------------------------------")
print("⚠️ 警告：請立即將私鑰抄在紙上，不要截圖！")
print("這串私鑰稍後會自動幫你寫入 .env 保險箱。")

# 自動寫入保險箱
with open(".env", "a") as f:
    f.write(f"\nWALLET_ADDRESS='{acct.address}'")
    f.write(f"\nPRIVATE_KEY='{acct.key.hex()}'")
