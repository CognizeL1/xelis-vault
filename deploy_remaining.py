#!/usr/bin/env python3
import json, os, time, base64, urllib.request, hashlib

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

def deploy(name, has_ctor=True):
    hx = open(os.path.join(BUILD, f"{name}.hex")).read().strip()
    h = hashlib.blake2b(bytes.fromhex(hx), digest_size=32).hexdigest()
    
    for attempt in range(5):
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
                for w in range(12):
                    time.sleep(5)
                    dr = dd("get_transaction", [tx_hash], timeout=10)
                    dt = dr.get("result", {})
                    blk = dt.get("blocks")
                    if blk is not None and (isinstance(blk, list) and len(blk) > 0 or isinstance(blk, str)):
                        print(f"  [{name}] confirmed in block")
                        return tx_hash
                print(f"  [{name}] broadcast (awaiting block)")
                return tx_hash
            err = r.get("error", {}).get("message", str(r))
            if "proof verification" in err.lower():
                print(f"  [{name}] proof error (attempt {attempt+1}), retry 30s...")
                time.sleep(30)
                continue
            print(f"  [{name}] FAIL: {err[:200]}")
            return None
        except Exception as e:
            print(f"  [{name}] EXCEPTION: {e} (attempt {attempt+1})")
            time.sleep(10)
    return None

def invoke_hash(contract_hash, entry_id, parameters, label=""):
    for attempt in range(3):
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
                print(f"  [{label}] invoke(entry={entry_id}) TX={tx['hash'][:20]}... nonce={tx['nonce']}")
                return tx["hash"]
            err = r.get("error", {}).get("message", str(r))
            print(f"  [{label}] FAIL: {err[:200]}")
            return None
        except Exception as e:
            print(f"  [{label}] EXCEPTION: {e}")
            time.sleep(10)
    return None

# Load existing registry
reg_path = os.path.join(BUILD, "registry_core.json")
registry = json.load(open(reg_path))

print(f"Current registry: {len(registry)} contracts")

# Deploy PeerLoan (has ctor)
print(f"\n{'='*60}")
print("Deploy PeerLoan")
h = deploy("PeerLoan", True)
if h:
    registry["PeerLoan"] = {"tx_hash": h, "contract_hash": h, "nonce": None}

# Deploy SyndicatePool (has ctor)
print(f"\n{'='*60}")
print("Deploy SyndicatePool")
h = deploy("SyndicatePool", True)
if h:
    registry["SyndicatePool"] = {"tx_hash": h, "contract_hash": h, "nonce": None}

# Deploy SealedBidAuction (has ctor)
print(f"\n{'='*60}")
print("Deploy SealedBidAuction")
h = deploy("SealedBidAuction", True)
if h:
    registry["SealedBidAuction"] = {"tx_hash": h, "contract_hash": h, "nonce": None}

# Deploy VaultEngine (no ctor, entry init)
print(f"\n{'='*60}")
print("Deploy VaultEngine + init()")
h = deploy("VaultEngine", False)
if h:
    registry["VaultEngine"] = {"tx_hash": h, "contract_hash": h, "nonce": None}
    print("  Calling VaultEngine.init()...")
    invoke_hash(h, 0, [], "VaultEngine.init")

# Save updated registry
with open(reg_path, "w") as f:
    json.dump(registry, f, indent=2)

print(f"\n{'='*60}")
print(f"Registry updated: {len(registry)} contracts")
for name, info in registry.items():
    print(f"  {name}: {info['tx_hash'][:20]}...")
