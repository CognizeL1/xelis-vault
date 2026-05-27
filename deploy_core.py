#!/usr/bin/env python3
import json, os, time, base64, urllib.request, subprocess, hashlib

DAEMON = "http://127.0.0.1:18081/json_rpc"
WALLET = "http://127.0.0.1:18082/json_rpc"
AUTH = base64.b64encode(b":testnet_vault_2026").decode()
BUILD = "/Users/adrien/opencode/xelis-vault/build"
SRC = "/Users/adrien/opencode/xelis-vault/contracts"
SILEX = "/private/tmp/xelis-vm/target/release/silex-cli"

def dw(method, params, timeout=60):
    p = json.dumps({"jsonrpc":"2.0","id":"1","method":method,"params":params}).encode()
    r = urllib.request.Request(WALLET, data=p, headers={"Content-Type":"application/json"})
    r.add_header("Authorization", f"Basic {AUTH}")
    return json.loads(urllib.request.urlopen(r, timeout=timeout).read())

def dd(method, params, timeout=30):
    p = json.dumps({"jsonrpc":"2.0","id":"1","method":method,"params":params}).encode()
    r = urllib.request.Request(DAEMON, data=p, headers={"Content-Type":"application/json"})
    return json.loads(urllib.request.urlopen(r, timeout=timeout).read())

def deploy(name, has_ctor, ctor_gas=1000000):
    print(f"\n{'='*60}")
    print(f"DEPLOY: {name}")
    hx = open(os.path.join(BUILD, f"{name}.hex")).read().strip()
    h = hashlib.blake2b(bytes.fromhex(hx), digest_size=32).hexdigest()
    print(f"  hash: {h[:16]}...")
    params = {"module": hx}
    if has_ctor:
        params["invoke"] = {"max_gas": ctor_gas}
    try:
        r = dw("build_transaction", {"deploy_contract": params, "broadcast": True}, timeout=600)
        if "result" not in r:
            print(f"  FAIL: {r.get('error',{}).get('message',r)}")
            return None
        tx = r["result"]
        tx_hash = tx.get("hash")
        nonce = tx.get("nonce")
        print(f"  TX: {tx_hash} (nonce {nonce})")
        return tx_hash
    except Exception as e:
        print(f"  EXCEPTION: {e}")
        return None

def invoke(contract_hash, entry, params_list, max_gas=500000, deposits=None):
    call = {"contract": contract_hash, "entrypoint": entry, "params": params_list, "max_gas": max_gas}
    txp = {"invoke_contract": call, "broadcast": True}
    if deposits:
        txp["deposits"] = deposits
    try:
        r = dw("build_transaction", txp, timeout=300)
        if "result" in r:
            return r["result"].get("hash")
        else:
            print(f"  INVOKE FAIL: {r.get('error',{}).get('message',r)}")
            return None
    except Exception as e:
        print(f"  INVOKE EXCEPTION: {e}")
        return None

def wait_tx(tx_hash, max_wait=120):
    for i in range(max_wait):
        try:
            r = dd("get_transaction", [tx_hash], timeout=10)
            tx = r.get("result", {})
            topo = tx.get("topoheight")
            blk = len(tx.get("blocks", []))
            if blk > 0:
                print(f"  confirm: topo={topo} blocks={blk} (wait={i}s)")
                if topo is not None:
                    return True
            else:
                if i % 10 == 0:
                    print(f"  waiting... (topo={topo} blocks={blk} {i}s)")
        except:
            if i % 10 == 0:
                print(f"  retrying... ({i}s)")
        time.sleep(1)
    return False

def verify(name, tx_hash):
    r = dd("get_transaction", [tx_hash], timeout=10)
    t = r.get("result", {})
    topo = t.get("topoheight")
    blk = len(t.get("blocks", []))
    print(f"  {name}: tx={tx_hash[:16]}... topo={topo} blocks={blk}")
    return t

# ─── ORDER: deploy each, connect to InterestRateModel (first deployed) ───

registry = {}

# 0. InterestRateModel
h = deploy("InterestRateModel", False)
if h: registry["InterestRateModel"] = h

# 1. PriceOracle — entry init (no constructor hook)
h = deploy("PriceOracle", False)
if h:
    registry["PriceOracle"] = h
    # call init()
    print("  Calling PriceOracle.init()...")
    txh = invoke(h, "init", [])
    if txh: print(f"  init TX: {txh}")

# 2. xUSD — entry init (no constructor hook)
h = deploy("xUSD", False)
if h:
    registry["xUSD"] = h
    print("  Calling xUSD.init()...")
    txh = invoke(h, "init", [])
    if txh: print(f"  init TX: {txh}")

# 3-19. hook constructor contracts
for name in ["VLT", "ComplianceModule", "Timelock", "TreasuryVault",
             "RevenueShare", "InsurancePool", "FlashLoan", "PeerLoan",
             "SyndicatePool", "SealedBidAuction", "Payroll", "PrivateInsurance",
             "AssetVault", "GovernanceVault", "LendingMarket"]:
    h = deploy(name, True)
    if h:
        registry[name] = h

# 19. VaultEngine — entry init (no constructor hook)
h = deploy("VaultEngine", False)
if h:
    registry["VaultEngine"] = h
    print("  Calling VaultEngine.init()...")
    txh = invoke(h, "init", [])
    if txh: print(f"  init TX: {txh}")

# summary
print(f"\n{'='*60}")
print(f"DEPLOYMENT SUMMARY")
print(f"{'='*60}")
reg_path = os.path.join(BUILD, "registry_core.json")
with open(reg_path, "w") as f:
    json.dump(registry, f, indent=2)
print(f"  Registry: {reg_path}")
for name, txh in registry.items():
    print(f"  {name}: {txh}")
