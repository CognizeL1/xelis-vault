#!/usr/bin/env python3
import json, os, time, base64, urllib.request, hashlib

DAEMON = "http://127.0.0.1:18081/json_rpc"
WALLET = "http://127.0.0.1:18082/json_rpc"
AUTH = base64.b64encode(b":testnet_vault_2026").decode()
BUILD = "/Users/adrien/opencode/xelis-vault/build"
SILEX = "/private/tmp/xelis-vm/target/release/silex-cli"

def dw(method, params, timeout=120):
    p = json.dumps({"jsonrpc":"2.0","id":"1","method":method,"params":params}).encode()
    r = urllib.request.Request(WALLET, data=p, headers={"Content-Type":"application/json"})
    r.add_header("Authorization", f"Basic {AUTH}")
    return json.loads(urllib.request.urlopen(r, timeout=timeout).read())

def dd(method, params, timeout=30):
    p = json.dumps({"jsonrpc":"2.0","id":"1","method":method,"params":params}).encode()
    r = urllib.request.Request(DAEMON, data=p, headers={"Content-Type":"application/json"})
    return json.loads(urllib.request.urlopen(r, timeout=timeout).read())

def wait_wallet(max_wait=300):
    for i in range(max_wait):
        try:
            r = dw("get_nonce", [], timeout=5)
            if "result" in r:
                return r["result"]
        except:
            pass
        if i % 10 == 0:
            print(f"  waiting for wallet... ({i}s)")
        time.sleep(1)
    return None

def deploy(name, has_ctor=True):
    hx = open(os.path.join(BUILD, f"{name}.hex")).read().strip()
    h = hashlib.blake2b(bytes.fromhex(hx), digest_size=32).hexdigest()
    
    for attempt in range(5):
        nonce = wait_wallet()
        if nonce is None:
            print(f"  SKIP {name}: wallet unreachable")
            return None
        
        params = {"module": hx}
        if has_ctor:
            params["invoke"] = {"max_gas": 1000000}
        
        try:
            r = dw("build_transaction", {"deploy_contract": params, "broadcast": True}, timeout=300)
            if "result" in r:
                tx = r["result"]
                print(f"  {name}: hash={tx['hash'][:16]}... nonce={tx['nonce']}")
                return tx["hash"]
            err = r.get("error", {}).get("message", str(r))
            if "proof verification" in err.lower():
                print(f"  {name}: proof error (attempt {attempt+1}), waiting 30s...")
                time.sleep(30)
                continue
            print(f"  {name}: FAIL {err}")
            return None
        except Exception as e:
            print(f"  {name}: EXCEPTION {e} (attempt {attempt+1})")
            time.sleep(30)
    print(f"  {name}: FAILED after 5 attempts")
    return None

def invoke(contract_hash, entry_id, parameters, permission="none"):
    for attempt in range(3):
        nonce = wait_wallet()
        if nonce is None:
            return None
        try:
            r = dw("build_transaction", {
                "invoke_contract": {
                    "contract": contract_hash,
                    "entry_id": entry_id,
                    "parameters": parameters,
                    "max_gas": 500000,
                    "permission": permission
                },
                "broadcast": True
            }, timeout=300)
            if "result" in r:
                tx = r["result"]
                print(f"  invoke({contract_hash[:16]}.., entry={entry_id}): hash={tx['hash'][:16]}... nonce={tx['nonce']}")
                return tx["hash"]
            err = r.get("error", {}).get("message", str(r))
            print(f"  invoke FAIL: {err}")
            return None
        except Exception as e:
            print(f"  invoke EXCEPTION: {e}")
            time.sleep(20)
    return None

# ─── MAIN ───
registry = {}

# Phase 1: Deploy all contracts
print("\n=== PHASE 1: DEPLOY ALL CONTRACTS ===")

# No constructor
h = deploy("InterestRateModel", False)
if h: registry["InterestRateModel"] = h

# Entry init (no constructor hook)
for name in ["PriceOracle", "xUSD"]:
    h = deploy(name, False)
    if h: registry[name] = h

# Hook constructor
for name in ["VLT", "ComplianceModule", "Timelock", "TreasuryVault",
             "RevenueShare", "InsurancePool", "FlashLoan", "PeerLoan",
             "SyndicatePool", "SealedBidAuction", "Payroll", "PrivateInsurance",
             "AssetVault", "GovernanceVault", "LendingMarket"]:
    h = deploy(name, True)
    if h: registry[name] = h

# VaultEngine — entry init
h = deploy("VaultEngine", False)
if h: registry["VaultEngine"] = h

# Phase 2: Call init() on entry-init contracts
print("\n=== PHASE 2: CALL init() ===")
for name in ["PriceOracle", "xUSD", "VaultEngine"]:
    c = registry.get(name)
    if c:
        print(f"  Calling {name}.init()...")
        invoke(c, 0, [])

# Phase 3: Save registry
print("\n=== REGISTRY ===")
reg_path = os.path.join(BUILD, "registry_core.json")
with open(reg_path, "w") as f:
    json.dump(registry, f, indent=2)
for n, c in registry.items():
    print(f"  {n}: {c}")
print(f"  Saved to {reg_path}")
