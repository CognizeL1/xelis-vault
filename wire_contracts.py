#!/usr/bin/env python3
import json, os, time, base64, urllib.request

DAEMON = "http://127.0.0.1:18081/json_rpc"
WALLET = "http://127.0.0.1:18082/json_rpc"
AUTH = base64.b64encode(b":testnet_vault_2026").decode()
BUILD = "/Users/adrien/opencode/xelis-vault/build"

def dw(method, params, timeout=120):
    p = json.dumps({"jsonrpc":"2.0","id":"1","method":method,"params":params}).encode()
    r = urllib.request.Request(WALLET, data=p, headers={"Content-Type":"application/json"})
    r.add_header("Authorization", f"Basic {AUTH}")
    return json.loads(urllib.request.urlopen(r, timeout=timeout).read())

def dd(method, params, timeout=30):
    p = json.dumps({"jsonrpc":"2.0","id":"1","method":method,"params":params}).encode()
    r = urllib.request.Request(DAEMON, data=p, headers={"Content-Type":"application/json"})
    return json.loads(urllib.request.urlopen(r, timeout=timeout).read())

def vc_u64(v):
    return {"type":"primitive","value":{"type":"u64","value":str(v)}}

def vc_opaque(v):
    return {"type":"primitive","value":{"type":"opaque","value":v}}

def invoke_id(contract_hash, entry_id, params_vc, deposits=None, label=""):
    call = {
        "contract": contract_hash,
        "entry_id": entry_id,
        "parameters": params_vc,
        "max_gas": 500000,
        "permission": "none"
    }
    tx_params = {"invoke_contract": call, "broadcast": True}
    if deposits:
        tx_params["deposits"] = deposits
    try:
        r = dw("build_transaction", tx_params, timeout=300)
        if "result" in r:
            tx = r["result"]
            print(f"  [{label}] TX={tx['hash'][:20]}... nonce={tx['nonce']}")
            for w in range(6):
                time.sleep(5)
                dr = dd("get_transaction", [tx["hash"]], timeout=10)
                dt = dr.get("result", {})
                blk = dt.get("blocks")
                if blk is not None and (isinstance(blk, list) and len(blk) > 0):
                    print(f"  [{label}] confirmed")
                    return tx["hash"]
            return tx["hash"]
        err = r.get("error", {}).get("message", str(r))
        print(f"  [{label}] FAIL: {err[:300]}")
        return None
    except Exception as e:
        print(f"  [{label}] EXCEPTION: {e}")
        return None

reg = json.load(open(os.path.join(BUILD, "registry_core.json")))

PO = reg["PriceOracle"]["tx_hash"]
XUSD = reg["xUSD"]["tx_hash"]
IRM = reg["InterestRateModel"]["tx_hash"]
VE = reg["VaultEngine"]["tx_hash"]

print(f"PriceOracle:       {PO[:20]}...")
print(f"xUSD:              {XUSD[:20]}...")
print(f"InterestRateModel: {IRM[:20]}...")
print(f"VaultEngine:       {VE[:20]}...")

# Entry indices:
# xUSD: init=0, create_asset=1, mint_tokens=2, burn_tokens=3, transfer_tokens=4, get_asset_hash=5, get_asset_info=6, transfer_admin=7
# PriceOracle: init=0, propose_price=1, execute_price=2, get_price=3, get_pending_price=4, cancel_pending=5, transfer_admin=6
# VaultEngine: init=0, deposit=1, borrow=2, repay=3, withdraw=4, redeem=5, liquidate=6, get_queue=7,
#              set_oracle_contract=8, set_xusd_contract=9, set_xusd_asset=10, set_treasury=11, transfer_admin=12,
#              get_vault=13, get_health=14, is_liquidatable=15

# Step 1: xUSD.create_asset() with 1 XEL deposit
print(f"\n{'='*60}")
print("Step 1: xUSD.create_asset()")
# Try without deposit first to see error
invoke_id(XUSD, 1, [], label="xUSD.create_asset")

# Step 2: xUSD.get_asset_hash()
print(f"\n{'='*60}")
print("Step 2: xUSD.get_asset_hash()")
invoke_id(XUSD, 5, [], label="xUSD.get_asset_hash")

# Step 3: PriceOracle.propose_price($0.50 = 50000000)
print(f"\n{'='*60}")
print("Step 3: PriceOracle.propose_price(50000000)")
invoke_id(PO, 1, [vc_u64(50000000)], label="Oracle.propose_price")

# Step 4: VaultEngine.set_oracle_contract()
print(f"\n{'='*60}")
print("Step 4: VaultEngine.set_oracle_contract()")
invoke_id(VE, 8, [vc_opaque(PO)], label="VE.set_oracle_contract")

# Step 5: VaultEngine.set_xusd_contract()
print(f"\n{'='*60}")
print("Step 5: VaultEngine.set_xusd_contract()")
invoke_id(VE, 9, [vc_opaque(XUSD)], label="VE.set_xusd_contract")

print(f"\n{'='*60}")
print("Wiring complete!")
print("Remaining:")
print("  - Maybe xUSD.create_asset with proper deposit format")
print("  - Get xUSD asset hash (blake3(hash ++ be64(1)))")
print("  - VaultEngine.set_xusd_asset(asset_hash)")
print("  - Wait 720 blocks, then PriceOracle.execute_price()")
