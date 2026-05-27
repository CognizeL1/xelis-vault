#!/usr/bin/env python3
import json, os, time, base64, urllib.request, hashlib

DAEMON = "http://127.0.0.1:18081/json_rpc"
WALLET = "http://127.0.0.1:18082/json_rpc"
AUTH = base64.b64encode(b":testnet_vault_2026").decode()
BUILD = "/Users/adrien/opencode/xelis-vault/build"
NONCE_RESERVE = 20

def dw(method, params, timeout=120):
    p = json.dumps({"jsonrpc":"2.0","id":"1","method":method,"params":params}).encode()
    r = urllib.request.Request(WALLET, data=p, headers={"Content-Type":"application/json"})
    r.add_header("Authorization", f"Basic {AUTH}")
    return json.loads(urllib.request.urlopen(r, timeout=timeout).read())

def dd(method, params, timeout=30):
    p = json.dumps({"jsonrpc":"2.0","id":"1","method":method,"params":params}).encode()
    r = urllib.request.Request(DAEMON, data=p, headers={"Content-Type":"application/json"})
    return json.loads(urllib.request.urlopen(r, timeout=timeout).read())

def get_nonce():
    try:
        r = dw("get_nonce", [], timeout=5)
        return r.get("result")
    except:
        return None

def deploy(name, has_ctor=True):
    hx = open(os.path.join(BUILD, f"{name}.hex")).read().strip()
    h = hashlib.blake2b(bytes.fromhex(hx), digest_size=32).hexdigest()
    
    for attempt in range(10):
        nonce = get_nonce()
        if nonce is None:
            print(f"  [{name}] wallet unreachable, retry in 10s...")
            time.sleep(10)
            continue
        
        params = {"module": hx}
        if has_ctor:
            params["invoke"] = {"max_gas": 1000000}
        
        try:
            r = dw("build_transaction", {"deploy_contract": params, "broadcast": True}, timeout=300)
            if "result" in r:
                tx = r["result"]
                tx_hash = tx["hash"]
                tx_nonce = tx["nonce"]
                print(f"  [{name}] TX={tx_hash[:20]}... nonce={tx_nonce} contract={h[:20]}...")
                
                # Wait for confirmation (check every 5s up to 60s)
                for w in range(12):
                    time.sleep(5)
                    dr = dd("get_transaction", [tx_hash], timeout=10)
                    dt = dr.get("result", {})
                    blk = dt.get("blocks")
                    topo = dt.get("topoheight")
                    in_block = blk is not None and (isinstance(blk, list) and len(blk) > 0 or isinstance(blk, str))
                    if in_block:
                        print(f"  [{name}] confirmed in block, topo={topo}")
                        return tx_hash
                
                print(f"  [{name}] broadcast but not yet confirmed (will continue)")
                return tx_hash
            
            err = r.get("error", {}).get("message", str(r))
            if "proof verification" in err.lower():
                print(f"  [{name}] proof error (attempt {attempt+1}), waiting 30s...")
                time.sleep(30)
                continue
            if "nonce" in err.lower() and "expected" in err.lower():
                print(f"  [{name}] nonce mismatch: {err}")
                print(f"  [{name}] triggering rescan + waiting 30s...")
                dw("rescan", {}, timeout=300)
                time.sleep(30)
                continue
            print(f"  [{name}] FAIL: {err[:200]}")
            return None
        except Exception as e:
            print(f"  [{name}] EXCEPTION: {e} (attempt {attempt+1})")
            time.sleep(10)
    
    print(f"  [{name}] FAILED after 10 attempts")
    return None

def invoke(contract_hash, entry_id, parameters, entry_name=""):
    for attempt in range(3):
        nonce = get_nonce()
        if nonce is None:
            time.sleep(10)
            continue
        try:
            r = dw("build_transaction", {
                "invoke_contract": {
                    "contract": contract_hash,
                    "entry_id": entry_id,
                    "parameters": parameters,
                    "max_gas": 500000,
                    "permission": "none"
                },
                "broadcast": True
            }, timeout=300)
            if "result" in r:
                tx = r["result"]
                print(f"  [{entry_name}].init() TX={tx['hash'][:20]}... nonce={tx['nonce']}")
                
                for w in range(12):
                    time.sleep(5)
                    dr = dd("get_transaction", [tx["hash"]], timeout=10)
                    dt = dr.get("result", {})
                    blk = dt.get("blocks")
                    if blk is not None and (isinstance(blk, list) and len(blk) > 0 or isinstance(blk, str)):
                        print(f"  [{entry_name}].init() confirmed")
                        return tx["hash"]
                return tx["hash"]
            
            err = r.get("error", {}).get("message", str(r))
            print(f"  [{entry_name}].init() FAIL: {err[:200]}")
            return None
        except Exception as e:
            print(f"  [{entry_name}].init() EXCEPTION: {e}")
            time.sleep(10)
    return None

def wait_for_mining(seconds=30):
    print(f"\n  Waiting {seconds}s for mining...")
    for i in range(seconds // 5):
        time.sleep(5)
        print(f"  ...{i*5+5}s", end="", flush=True)
    print()

registry = {}

# Step 0: InterestRateModel already deployed at nonce 186
IR_TX = "e65ab0c29b157654eca0d0c5713eaab7a5f793ae641f02ab5e9dfa5aab69dbcd"
IR_HX = open(os.path.join(BUILD, "InterestRateModel.hex")).read().strip()
IR_HASH = hashlib.blake2b(bytes.fromhex(IR_HX), digest_size=32).hexdigest()
registry["InterestRateModel"] = {
    "tx_hash": IR_TX,
    "contract_hash": IR_HASH,
    "nonce": 186
}
print(f"\n{'='*60}")
print(f"PRE-DEPLOYED: InterestRateModel TX={IR_TX[:20]}... contract={IR_HASH[:20]}... nonce=186")

# Step 1: PriceOracle (no ctor, entry init)
print(f"\n{'='*60}")
print("PHASE 1: Deploy PriceOracle + init()")
h = deploy("PriceOracle", False)
if h:
    registry["PriceOracle"] = {"tx_hash": h, "contract_hash": h, "nonce": None}
    wait_for_mining(15)
    print("  Calling PriceOracle.init()...")
    invoke(h, 0, [], "PriceOracle")

# Step 2: xUSD (no ctor, entry init)
print(f"\n{'='*60}")
print("PHASE 2: Deploy xUSD + init()")
h = deploy("xUSD", False)
if h:
    registry["xUSD"] = {"tx_hash": h, "contract_hash": h, "nonce": None}
    wait_for_mining(15)
    print("  Calling xUSD.init()...")
    invoke(h, 0, [], "xUSD")

# Step 3: 15 contracts with constructor hooks
print(f"\n{'='*60}")
print("PHASE 3: Deploy 15 constructor-hook contracts")
for name in ["VLT", "ComplianceModule", "Timelock", "TreasuryVault",
             "RevenueShare", "InsurancePool", "FlashLoan", "PeerLoan",
             "SyndicatePool", "SealedBidAuction", "Payroll", "PrivateInsurance",
             "AssetVault", "GovernanceVault", "LendingMarket"]:
    h = deploy(name, True)
    if h:
        registry[name] = {"tx_hash": h, "contract_hash": h, "nonce": None}

# Step 4: VaultEngine (no ctor, entry init)
print(f"\n{'='*60}")
print("PHASE 4: Deploy VaultEngine + init()")
h = deploy("VaultEngine", False)
if h:
    registry["VaultEngine"] = {"tx_hash": h, "contract_hash": h, "nonce": None}
    wait_for_mining(15)
    print("  Calling VaultEngine.init()...")
    invoke(h, 0, [], "VaultEngine")

# Save registry
reg_path = os.path.join(BUILD, "registry_core.json")
with open(reg_path, "w") as f:
    json.dump(registry, f, indent=2)

print(f"\n{'='*60}")
print("DEPLOYMENT SUMMARY")
print(f"{'='*60}")
total = len(registry)
ok = sum(1 for v in registry.values() if v["tx_hash"] is not None)
print(f"  Deployed: {ok}/{total}")
print(f"  Registry: {reg_path}")
for name, info in registry.items():
    print(f"  {name}: {info['tx_hash'][:20]}... (nonce {info['nonce']})")
