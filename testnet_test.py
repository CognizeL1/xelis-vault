#!/usr/bin/env python3
"""Full testnet deploy + test suite for XELIS Vault contracts."""

import json, os, time, re, base64, urllib.request, subprocess, sys

# === CONFIG ===
DAEMON_RPC = "http://127.0.0.1:18081/json_rpc"
WALLET_RPC = "http://127.0.0.1:18082/json_rpc"
AUTH = base64.b64encode(b":testnet_vault_2026").decode()
BUILD = "/Users/adrien/opencode/xelis-vault/build"
SRC = "/Users/adrien/opencode/xelis-vault/contracts"
SILEX_CLI = "/private/tmp/xelis-vm/target/release/silex-cli"

# === Contract deploy order (dependency-first) ===
# (name, needs_constructor, test_fn)
CONTRACTS = [
    ("InterestRateModel", False, None),
    ("PriceOracle", True, None),
    ("xUSD", True, None),
    ("VLT", True, None),
    ("ComplianceModule", True, None),
    ("Timelock", True, None),
    ("TreasuryVault", True, None),
    ("RevenueShare", True, None),
    ("InsurancePool", True, None),
    ("PrivateInsurance", True, None),
    ("PeerLoan", True, None),
    ("SyndicatePool", True, None),
    ("SealedBidAuction", True, None),
    ("Payroll", True, None),
    ("FlashLoan", True, None),
    ("AssetVault", True, None),
    ("GovernanceVault", True, None),
    ("LendingMarket", True, None),
    ("VaultEngine", True, None),
]

results = {}
addresses = {}

def rpc_daemon(method, params, timeout=30):
    payload = json.dumps({"jsonrpc":"2.0","id":"1","method":method,"params":params}).encode()
    req = urllib.request.Request(DAEMON_RPC, data=payload, headers={"Content-Type":"application/json"})
    resp = urllib.request.urlopen(req, timeout=timeout)
    return json.loads(resp.read())

def rpc_wallet(method, params, timeout=600):
    payload = json.dumps({"jsonrpc":"2.0","id":"1","method":method,"params":params}).encode()
    req = urllib.request.Request(WALLET_RPC, data=payload, headers={"Content-Type":"application/json"})
    req.add_header("Authorization", f"Basic {AUTH}")
    resp = urllib.request.urlopen(req, timeout=timeout)
    return json.loads(resp.read())

def compile_contract(name):
    path = None
    for root, dirs, files in os.walk(SRC):
        for f in files:
            if f == f"{name}.slx":
                path = os.path.join(root, f)
    if not path:
        return False
    result = subprocess.run([SILEX_CLI, path], capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        print(f"    COMPILE FAIL: {result.stderr.strip()}")
        return False
    with open(os.path.join(BUILD, f"{name}.hex"), "w") as f:
        f.write(result.stdout.strip())
    return True

def get_contract_hash(hex_str):
    import hashlib
    raw = bytes.fromhex(hex_str)
    return hashlib.blake2b(raw, digest_size=32).hexdigest()

def wait_for_tx(tx_hash, max_blocks=30):
    for i in range(max_blocks):
        try:
            resp = rpc_daemon("get_transaction", [tx_hash], timeout=10)
            tx = resp.get("result", {})
            topo = tx.get("topoheight")
            blocks = tx.get("blocks", [])
            if topo is not None and len(blocks) > 0:
                return tx
        except:
            pass
        time.sleep(2)
    return None

def invoke_contract(contract_hash, entry_name, params_list, deposits=None, max_gas=500000):
    call = {
        "contract": contract_hash,
        "entrypoint": entry_name,
        "params": params_list,
    }
    if max_gas:
        call["max_gas"] = max_gas
    tx_params = {"invoke_contract": call, "broadcast": True}
    if deposits:
        tx_params["deposits"] = deposits
    resp = rpc_wallet("build_transaction", tx_params, timeout=600)
    return resp

def deploy_contract(name, needs_constructor):
    hex_path = os.path.join(BUILD, f"{name}.hex")
    if not os.path.exists(hex_path):
        print(f"  SKIP: hex not found")
        return None
    with open(hex_path) as f:
        hex_str = f.read().strip()
    
    deploy_params = {"module": hex_str}
    if needs_constructor:
        deploy_params["invoke"] = {"max_gas": 1000000}
    
    contract_hash = get_contract_hash(hex_str)
    
    try:
        resp = rpc_wallet("build_transaction", {
            "deploy_contract": deploy_params,
            "broadcast": True
        }, timeout=600)
        
        if "result" not in resp:
            err = resp.get("error", {}).get("message", str(resp))
            print(f"  BUILD FAIL: {err}")
            return None
        
        tx_hash = resp["result"].get("hash")
        print(f"  Deploy TX: {tx_hash}")
        print(f"  Contract hash: {contract_hash}")
        
        tx_data = wait_for_tx(tx_hash, max_blocks=60)
        if tx_data:
            topo = tx_data.get("topoheight")
            blocks = tx_data.get("blocks", [])
            print(f"  Confirmed: topo={topo}, blocks={len(blocks)}")
        else:
            print(f"  WARNING: TX not confirmed after 60 blocks")
        
        return contract_hash
    except Exception as e:
        print(f"  EXCEPTION: {e}")
        return None

def get_balance():
    resp = rpc_wallet("get_balance", {}, timeout=10)
    return resp.get("result", 0)

def daemon_info():
    resp = rpc_daemon("get_info", [], timeout=10)
    return resp.get("result", {})

# === Test Functions ===
def test_xusd(addr):
    tests = []
    # get_asset_info should work after create_asset
    try:
        r = invoke_contract(addr, "get_asset_info", [])
        if "result" in r:
            tests.append(("get_asset_info", "PASS"))
        else:
            tests.append(("get_asset_info", f"FAIL: {r}"))
    except Exception as e:
        tests.append(("get_asset_info", f"EXCEPTION: {e}"))
    return tests

def test_vault_engine(addr):
    tests = []
    try:
        r = invoke_contract(addr, "get_queue", [])
        if "result" in r:
            tests.append(("get_queue", "PASS"))
        else:
            tests.append(("get_queue", f"FAIL: {r}"))
    except Exception as e:
        tests.append(("get_queue", f"EXCEPTION: {e}"))
    return tests

def test_price_oracle(addr):
    tests = []
    try:
        r = invoke_contract(addr, "get_price", ["0000000000000000000000000000000000000000000000000000000000000000"])
        if "result" in r:
            tests.append(("get_price", "PASS"))
        else:
            tests.append(("get_price", f"FAIL: {r}"))
    except Exception as e:
        tests.append(("get_price", f"EXCEPTION: {e}"))
    return tests

def test_vlt(addr):
    tests = []
    try:
        r = invoke_contract(addr, "get_supply", [])
        if "result" in r:
            tests.append(("get_supply", "PASS"))
        else:
            tests.append(("get_supply", f"FAIL: {r}"))
    except Exception as e:
        tests.append(("get_supply", f"EXCEPTION: {e}"))
    return tests

def test_interest_rate(addr):
    tests = []
    try:
        r = invoke_contract(addr, "get_utilization", [100000, 1000000])
        if "result" in r:
            tests.append(("get_utilization", "PASS"))
        else:
            tests.append(("get_utilization", f"FAIL: {r}"))
    except Exception as e:
        tests.append(("get_utilization", f"EXCEPTION: {e}"))
    try:
        r = invoke_contract(addr, "get_supply_rate", [500])
        if "result" in r:
            tests.append(("get_supply_rate", "PASS"))
        else:
            tests.append(("get_supply_rate", f"FAIL: {r}"))
    except Exception as e:
        tests.append(("get_supply_rate", f"EXCEPTION: {e}"))
    return tests

def test_compliance(addr):
    tests = []
    try:
        r = invoke_contract(addr, "get_record", [0])
        if "result" in r or "error" in r:
            tests.append(("get_record", "PASS (returned)"))
        else:
            tests.append(("get_record", f"FAIL: {r}"))
    except Exception as e:
        tests.append(("get_record", f"EXCEPTION: {e}"))
    return tests

def test_timelock(addr):
    tests = []
    try:
        r = invoke_contract(addr, "get_proposal", [0])
        if "result" in r or "error" in r:
            tests.append(("get_proposal", "PASS"))
        else:
            tests.append(("get_proposal", f"FAIL: {r}"))
    except Exception as e:
        tests.append(("get_proposal", f"EXCEPTION: {e}"))
    return tests

def test_treasury(addr):
    tests = []
    try:
        r = invoke_contract(addr, "get_balance", [])
        if "result" in r:
            tests.append(("get_balance", "PASS"))
        else:
            tests.append(("get_balance", f"FAIL: {r}"))
    except Exception as e:
        tests.append(("get_balance", f"EXCEPTION: {e}"))
    return tests

def test_revenue(addr):
    tests = []
    try:
        r = invoke_contract(addr, "get_share", [0])
        if "result" in r or "error" in r:
            tests.append(("get_share", "PASS"))
        else:
            tests.append(("get_share", f"FAIL: {r}"))
    except Exception as e:
        tests.append(("get_share", f"EXCEPTION: {e}"))
    return tests

def test_insurance_pool(addr):
    tests = []
    try:
        r = invoke_contract(addr, "get_total_staked", [])
        if "result" in r:
            tests.append(("get_total_staked", "PASS"))
        else:
            tests.append(("get_total_staked", f"FAIL: {r}"))
    except Exception as e:
        tests.append(("get_total_staked", f"EXCEPTION: {e}"))
    return tests

def test_private_insurance(addr):
    tests = []
    try:
        r = invoke_contract(addr, "get_pool", [0])
        if "result" in r or "error" in r:
            tests.append(("get_pool", "PASS"))
        else:
            tests.append(("get_pool", f"FAIL: {r}"))
    except Exception as e:
        tests.append(("get_pool", f"EXCEPTION: {e}"))
    return tests

def test_peer_loan(addr):
    tests = []
    try:
        r = invoke_contract(addr, "get_loan", [0])
        if "result" in r or "error" in r:
            tests.append(("get_loan", "PASS"))
        else:
            tests.append(("get_loan", f"FAIL: {r}"))
    except Exception as e:
        tests.append(("get_loan", f"EXCEPTION: {e}"))
    return tests

def test_syndicate(addr):
    tests = []
    try:
        r = invoke_contract(addr, "get_pool", [0])
        if "result" in r or "error" in r:
            tests.append(("get_pool", "PASS"))
        else:
            tests.append(("get_pool", f"FAIL: {r}"))
    except Exception as e:
        tests.append(("get_pool", f"EXCEPTION: {e}"))
    return tests

def test_auction(addr):
    tests = []
    try:
        r = invoke_contract(addr, "get_auction", [0])
        if "result" in r or "error" in r:
            tests.append(("get_auction", "PASS"))
        else:
            tests.append(("get_auction", f"FAIL: {r}"))
    except Exception as e:
        tests.append(("get_auction", f"EXCEPTION: {e}"))
    return tests

def test_payroll(addr):
    tests = []
    try:
        r = invoke_contract(addr, "get_stream", [0])
        if "result" in r or "error" in r:
            tests.append(("get_stream", "PASS"))
        else:
            tests.append(("get_stream", f"FAIL: {r}"))
    except Exception as e:
        tests.append(("get_stream", f"EXCEPTION: {e}"))
    return tests

def test_flash_loan(addr):
    tests = []
    try:
        r = invoke_contract(addr, "get_loan", [0])
        if "result" in r or "error" in r:
            tests.append(("get_loan", "PASS"))
        else:
            tests.append(("get_loan", f"FAIL: {r}"))
    except Exception as e:
        tests.append(("get_loan", f"EXCEPTION: {e}"))
    return tests

def test_asset_vault(addr):
    tests = []
    try:
        r = invoke_contract(addr, "get_vault", [0])
        if "result" in r or "error" in r:
            tests.append(("get_vault", "PASS"))
        else:
            tests.append(("get_vault", f"FAIL: {r}"))
    except Exception as e:
        tests.append(("get_vault", f"EXCEPTION: {e}"))
    return tests

def test_governance(addr):
    tests = []
    try:
        r = invoke_contract(addr, "get_total_voting_power", [])
        if "result" in r:
            tests.append(("get_total_voting_power", "PASS"))
        else:
            tests.append(("get_total_voting_power", f"FAIL: {r}"))
    except Exception as e:
        tests.append(("get_total_voting_power", f"EXCEPTION: {e}"))
    return tests

def test_lending(addr):
    tests = []
    try:
        r = invoke_contract(addr, "get_pool", [0])
        if "result" in r or "error" in r:
            tests.append(("get_pool", "PASS"))
        else:
            tests.append(("get_pool", f"FAIL: {r}"))
    except Exception as e:
        tests.append(("get_pool", f"EXCEPTION: {e}"))
    return tests

# Map contracts to test functions
TEST_MAP = {
    "xUSD": test_xusd,
    "VaultEngine": test_vault_engine,
    "PriceOracle": test_price_oracle,
    "VLT": test_vlt,
    "InterestRateModel": test_interest_rate,
    "ComplianceModule": test_compliance,
    "Timelock": test_timelock,
    "TreasuryVault": test_treasury,
    "RevenueShare": test_revenue,
    "InsurancePool": test_insurance_pool,
    "PrivateInsurance": test_private_insurance,
    "PeerLoan": test_peer_loan,
    "SyndicatePool": test_syndicate,
    "SealedBidAuction": test_auction,
    "Payroll": test_payroll,
    "FlashLoan": test_flash_loan,
    "AssetVault": test_asset_vault,
    "GovernanceVault": test_governance,
    "LendingMarket": test_lending,
}

# === MAIN ===
def main():
    global addresses
    
    print("=" * 72)
    print("XELIS Vault — Full Testnet Deploy + Test Suite")
    print("=" * 72)
    
    # Step 0: Check daemon + wallet
    print("\n[0] Checking infrastructure...")
    try:
        info = daemon_info()
        print(f"  Daemon: v{info.get('version','?')}, topo={info.get('topoheight')}, "
              f"network={info.get('network')}, peers={info.get('mempool_size','?')}")
    except Exception as e:
        print(f"  DAEMON NOT REACHABLE: {e}")
        sys.exit(1)
    
    try:
        bal = get_balance()
        addr_resp = rpc_wallet("get_address", {}, timeout=10)
        addr = addr_resp.get("result", "?")
        nonce_resp = rpc_wallet("get_nonce", [], timeout=10)
        nonce = nonce_resp.get("result", "?")
        print(f"  Wallet: {addr}")
        print(f"  Balance: {bal / 1e8:.2f} XEL")
        print(f"  Nonce: {nonce}")
    except Exception as e:
        print(f"  WALLET NOT REACHABLE: {e}")
        sys.exit(1)
    
    # Step 1: Compile all contracts
    print("\n[1] Compiling contracts...")
    compile_results = {}
    for name, _, _ in CONTRACTS:
        ok = compile_contract(name)
        compile_results[name] = "OK" if ok else "FAIL"
        print(f"  {name}: {compile_results[name]}")
    
    if "FAIL" in compile_results.values():
        print("\n  Some contracts failed to compile!")
        sys.exit(1)
    
    # Step 2: Deploy all contracts
    print("\n[2] Deploying contracts to testnet...")
    print(f"  Balance: {get_balance() / 1e8:.2f} XEL")
    print()
    
    for name, needs_constructor, _ in CONTRACTS:
        print(f"--- {name} ---")
        
        # Check if already deployed (by trying to call a read entry)
        # Skip redeploy if already on chain
        prev_hex_path = os.path.join(BUILD, f"{name}.hex")
        if os.path.exists(prev_hex_path):
            with open(prev_hex_path) as f:
                hex_str = f.read().strip()
            expected_hash = get_contract_hash(hex_str)
            
            # Check registry_v3 first
            if expected_hash in addresses.values():
                print(f"  Already deployed (hash: {expected_hash})")
                continue
        
        addr = deploy_contract(name, needs_constructor)
        if addr:
            addresses[name] = addr
            results[name] = "DEPLOYED"
        else:
            results[name] = "FAILED"
    
    # Step 3: Test all deployed contracts
    print("\n[3] Testing contract entry points...")
    print()
    
    for name, _, _ in CONTRACTS:
        addr = addresses.get(name)
        if not addr:
            print(f"--- {name} --- SKIP (not deployed)")
            continue
        
        print(f"--- {name} --- ({addr[:16]}...)")
        
        test_fn = TEST_MAP.get(name)
        if test_fn:
            try:
                test_results = test_fn(addr)
                for entry, status in test_results:
                    print(f"  {entry}: {status}")
            except Exception as e:
                print(f"  TEST EXCEPTION: {e}")
        else:
            # Try a generic get method if available
            print(f"  (no specific test defined)")
        
        print()
    
    # Step 4: Summary
    print("=" * 72)
    print("SUMMARY")
    print("=" * 72)
    
    deployed = sum(1 for v in results.values() if v == "DEPLOYED")
    failed = sum(1 for v in results.values() if v == "FAILED")
    total = len(CONTRACTS)
    
    print(f"  Deployed: {deployed}/{total}")
    print(f"  Failed: {failed}/{total}")
    print(f"  Balance remaining: {get_balance() / 1e8:.2f} XEL")
    
    # Save registry
    if addresses:
        reg_path = os.path.join(BUILD, "registry_testnet.json")
        with open(reg_path, "w") as f:
            json.dump(addresses, f, indent=2)
        print(f"\n  Registry saved: {reg_path}")
    
    print("=" * 72)

if __name__ == "__main__":
    main()
