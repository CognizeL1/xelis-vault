# AI Knowledge Base — XELIS Vault

## Silex Language (xelis-vm)

### Compiler
- **Binary**: `/private/tmp/xelis-vm/target/release/silex-cli`
- **Compile**: `./silex-cli compile file.slx > output.hex`
- **Stdlib order matters**: `Random` must be listed BEFORE `Asset` in `cli/src/stdlib.rs` to avoid linking errors. Fixed version at `/private/tmp/xelis-vm/cli/src/stdlib.rs`.

### Syntax Gotchas (CRITICAL)
| Pattern | What to do |
|---|---|
| `let mut` | NOT ALLOWED — use `let x = ...` then `x = newval` on separate lines |
| Inline `if/else` in `let` | NOT ALLOWED — use explicit `if {} else {}` blocks instead |
| `null` in enum variant | NOT VALID — use placeholder struct variant instead |
| `burn` | RESERVED keyword — cannot use as fn/variable name |
| Forward references | Functions must be defined BEFORE they are called (no hoisting) |
| `entry` calling another `entry` | NOT ALLOWED — entries must call helper `fn` only |
| Comments | NEVER add — contract gas cost increases with bytecode size |

### Type System
- `u64` for amounts, `i64`, `bool`, `Address`, `Hash`, `Value`, `ValueCell`
- `Asset` struct with `asset_type`, `asset_uuid`
- Contract state: `store_map(key_type, value_type)` for persistent storage

### Patterns (From ForgeSwap Reference)
- **Constructor**: `hook constructor()` — runs once on deploy WITH `invoke` param in deploy TX. **This is the correct pattern** (used by all XELIS Forge contracts).
- **Init via entry**: `entry init()` — NOT auto-called. Must be invoked manually. Does NOT work with `hook constructor` invoke pattern.
- **Cross-contract call**: Contract::call(contract_hash, entry_index, params_vec, deposits_map)
- **Balances**: AssetBalances::get_balance_of(addr, asset_hash), .set_balance(), .transfer_balance()
- **Random**: Random::fill_bytes(buf) from stdlib (needs Random listed before Asset)
- **Deposits**: `get_deposits().len()` to check count, `get_deposit_for_asset(hash)` to read amount

### Hooks
```
hook constructor()  // runs on deploy WITH invoke param (VERIFIED)
hook init()         // runs at contract creation
hook stop()         // runs at contract deletion
hook execute(ctx)   // runs at every invocation
```

### Entries
```
entry some_fn(param: Type) -> ReturnType
```

---

## XELIS Blockchain — BlockDAG Architecture

### DAG Fundamentals
- **BlockDAG** allows multiple blocks at the same height (branches), unlike a linear chain
- Up to **3 previous blocks** can be referenced in a single block
- Max **9% difficulty difference** between tips selected in the same block
- **Topoheight** = unique topological position in DAG, assigned during ordering
- **Topoheight is dynamic** — can change during DAG reorg until block becomes stable
- **Stable height** = top_topoheight - 8 (STABLE_LIMIT). Blocks below this are immutable
- **Side blocks** receive only **30%** of block reward
- **Client Protocol**: same TX can appear in multiple blocks; executed only once based on topo order
- **Orphaned block**: previously ordered but deselected during DAG reorg; its TXs are reverted
- **Orphaned transaction**: TX from orphaned block that couldn't be re-added to mempool
- **Smart Contracts** enabled at V3 (Dec 2025). Block time reduced from 15s to 5s at V3.
- **V5 upgrade**: June 15, 2026 (~block 3,373,000) — TX base fee improvements

### Implications for Deployments
- A contract deploy TX needs **8+ confirmations** to be immutable
- Before stability, a DAG reorg can orphan the entire block containing the deploy
- **DAG reorgs are frequent on testnet** — blocks with `topo=None` are NOT ordered yet
- A TX can have `blocks=1` but `topo=None` (in a TIP block, not yet ordered)
- Only `topo != None` means the block is in the DAG order and less likely to be orphaned
- Contracts can be **evicted from the active registry** (100-contract default return cap). Count is 176+ on testnet.
- Old-batch contracts (`skip=100`) still exist and can be called, but wallet may not index them.
- Registry pagination: `get_contracts({})` = newest 100, `get_contracts({"skip": 100})` = remaining 76.

### Network Config
- **Testnet daemon**: `127.0.0.1:18081`
- **Testnet wallet**: `127.0.0.1:18082`
- **Auth**: `testnet_vault_2026:` (base64 = `dGVzdG5ldF92YXVsdF8yMDI2Og==`)
- **Miner**: `/Users/adrien/xelis/xelis_miner` (~380 H/s, difficulty=10000, ~26s/block)
- **Wallet address**: `xet:czr9q8k5xlzqdptq7n2vapyjfduldts6tw3e6apl99vknzvmu4zsq8z9j8v`
- **Testnet explorer**: testnet-explorer.xelis.io (may have cache lag vs local node)

### Wallet Nonce Workaround (CRITICAL)
The wallet (v1.22.0) systematically loses nonce tracking after 2-3 TXs:
1. `build_transaction` returns "Proof verification error" — nonce mismatch
2. `build_transaction` returns "Server returned error: [-32004] Invalid TX <hash>" — reusing old TX
3. Subsequent calls fail with same pattern

**Fix** (NOT rescan — causes infinite loop):
```bash
kill $(lsof -t -i :18082)
sleep 2
nohup /Users/adrien/xelis/xelis_wallet --network testnet --daemon-address http://127.0.0.1:18081 --rpc-bind-address 127.0.0.1:18082 --wallet-path /Users/adrien/xelis/data/testnet_vault_wallet.db --logs-path /private/tmp/xelis-wallet-logs/ --password testnet_vault_2026 --precomputed-tables-path /Users/adrien/xelis/ --precomputed-tables-l1 13 --force-stable-balance > /private/tmp/xelis-wallet-logs/stdout.log 2>&1 &
sleep 30  # Wait for sync
```

After restart, you get exactly **2-3 TXs** before nonce breaks again.

---

## XELIS RPC API — CORRECTED (v1.22.0)

### Daemon RPC Parameter Format
**NOT all daemon methods use `[]` params**. The format depends on the method:

| Method | Params Format | Example |
|---|---|---|
| `get_topoheight` | `[]` (array) | `get_topoheight([])` |
| `get_info` | `[]` (array) | `get_info([])` |
| `get_transaction` | `[hash]` (array) | `get_transaction([tx_hash])` |
| `get_height` | `[]` (array) | `get_height([])` |
| `get_balance` | `{"address":..., "asset":...}` (object) | `get_balance({...})` |
| `get_nonce` | `{"address":...}` (object) | `get_nonce({...})` |
| **`get_contracts`** | **`{}` (object)** | **`get_contracts({})`** |
| `get_contract_data` | `{"contract":..., "key":...}` (object) | `get_contract_data({...})` |
| `get_block_by_hash` | `{"hash":...}` (object) | `get_block_by_hash({...})` |
| `get_blocks_at_height` | `{"height":...}` (object) | `get_blocks_at_height({...})` |
| `count_contracts` | `[]` (array) | `count_contracts([])` |
| `get_tips` | `[]` (array) | `get_tips([])` |
| `get_mempool` | `[]` (array) | `get_mempool([])` |

**Rule of thumb**: Methods WITHOUT optional params use `[]`. Methods WITH optional params use `{}`.

### Wallet RPC — build_transaction API

#### Invoke Contract
```python
call = {
    "contract": contract_hash,
    "entry_id": <int>,          # 0-based for invoke_contract (see Entry Indexing section)
    "parameters": [...],         # NOT "params"
    "max_gas": 500000,
    "permission": "none",
    "deposits": {hash: {"amount": u64}},  # INSIDE invoke_contract
}
result = rpc("build_transaction", {"invoke_contract": call, "broadcast": True})
```

#### Deploy Contract
```python
# Without constructor hook:
result = rpc("build_transaction", {"deploy_contract": {"module": hex}, "broadcast": True})

# With constructor hook:
result = rpc("build_transaction", {
    "deploy_contract": {"module": hex, "invoke": {"max_gas": 500000}},
    "broadcast": True
})
```

#### ValueCell Types for Contract Parameters
```python
# u64 — value MUST be a string
{"type": "primitive", "value": {"type": "u64", "value": "50000000"}}

# Hash/Address — use STRING type (wallet rejects "hash" and "address" types)
{"type": "primitive", "value": {"type": "string", "value": "46c72cb5..."}}

# Read-only call (returns hex)
{"invoke_contract": {...call..., "hex_output": True}, "broadcast": False}# Or just omit broadcast:
{"invoke_contract": {...call..., "hex_output": True}}

# ❌ DO NOT use "hash" or "address" types — wallet rejects them
```

---

## Contract Address = Deploy TX Hash
- `tx_hash` = result of `build_transaction` → `result.hash`
- Contract address in `get_contracts` = deploy TX hash

---

## Entry Indexing — CRITICAL CORRECTION (May 27, 2026)

### invoke_contract RPC vs Contract::call() — DIFFERENT INDEXING

**For `invoke_contract` (RPC)**: ALWAYS 0-based chunk index. This applies to ALL contracts regardless of internal functions. Entry 0 = first chunk (init).

**For `Contract::call()` (cross-contract calls in Silex)**: The index depends on whether the target contract has internal `fn` functions. Internal fns reserve chunk positions, shifting entry indices.

### ALL key contracts have `fn only_admin()` internal function
This means ALL of them use 0-based chunk indexing with an internal fn shifting the callable entries:

#### PriceOracle — Entry Map (for invoke_contract RPC)
| invoke_contract Entry | Contract::call Entry | Name | Signature |
|---|---|---|---|
| 0 | 1 | `init()` | Initialize admin |
| ❌ | ❌ | `fn only_admin()` | Internal (not callable) |
| 1 | 2 | `propose_price(u64)` | Propose new price |
| 2 | 3 | `execute_price()` | Execute pending price |
| 3 | 4 | `get_price(Hash)` | Get active price |
| 4 | 5 | `get_pending_price()` | Get pending price |
| 5 | 6 | `cancel_pending()` | Cancel pending price |
| 6 | 7 | `transfer_admin(Address)` | Transfer admin |

#### xUSD — Entry Map (for invoke_contract RPC)
| invoke_contract Entry | Contract::call Entry | Name | Signature |
|---|---|---|---|
| 0 | 1 | `init()` | Initialize admin |
| ❌ | ❌ | `fn only_admin()` | Internal (not callable) |
| 1 | 2 | `create_asset()` | Create XUSD asset |
| 2 | 3 | `mint_tokens(Address, u64)` | Mint tokens |
| 3 | 4 | `burn_tokens(u64)` | Burn tokens |
| 4 | 5 | `transfer_tokens(Address, u64)` | Transfer tokens |
| 5 | 6 | `get_asset_hash()` | Get XUSD asset hash |
| 6 | 7 | `get_asset_info()` | Get asset info |
| 7 | 8 | `transfer_admin(Address)` | Transfer admin |

#### VaultEngine — Entry Map (for invoke_contract RPC)
Same as chunk index. Entries 1-9 are internal functions.

| Entry | Name | Signature | Status |
|---|---|---|---|
| 0 | `init()` | Initialize | ✅ Verified |
| 1-9 | *(Internal functions)* | — | ❌ Cannot call |
| 10 | `deposit(Hash, u64)` | Deposit collateral | ✅ Works (vault created) |
| 11 | `borrow(u64, u64)` | Borrow xUSD | 🐛 Fixed: calls oracle entry 4, xUSD entry 3 |
| 12 | `repay(u64, u64)` | Repay xUSD loan | ❓ Untested |
| 13 | `withdraw(u64, u64)` | Withdraw collateral | ❓ Untested |
| 14 | `redeem(u64)` | Redeem xUSD | ❓ Untested |
| 15 | `liquidate(u64)` | Liquidate vault | ❓ Untested |
| 16 | `get_queue()` | Get liquidation queue | ❓ Untested |
| 17 | `set_oracle_contract(Hash)` | Set oracle | ✅ STORED |
| 18 | `set_xusd_contract(Hash)` | Set xUSD | ✅ STORED |
| 19 | `set_xusd_asset(Hash)` | Set xUSD asset | ✅ STORED |
| 20 | `set_treasury(Address)` | Set treasury | ✅ Compiled |
| 21 | `transfer_admin(Address)` | Transfer admin | ✅ Compiled |
| 22 | `get_vault(u64)` | Get vault data | ✅ Hex OK |
| 23 | `get_health(u64)` | Get vault health | ❓ Untested |
| 24 | `is_liquidatable(u64)` | Check liquidatable | ❓ Untested |

### Cross-Contract Call Bug Fix
VaultEngine source was fixed to correct two cross-contract `Contract::call()` indices (which use the "Internal function aware" indexing):

1. **`get_xel_price()`**: `Contract::call(oc, 2u16, ...)`→`4u16` (PriceOracle.get_price is at Contract::call index 4, invoke_contract entry 3)
2. **`borrow()`**: `xusd_contract.call(1u16, ...)`→`3u16` (xUSD.mint_tokens is at Contract::call index 3, invoke_contract entry 2)

VaultEngine v3 (995b4ddf...) contains these fixes.

---

## Current Deployment State (May 27, 2026 ~15:00)

### Active Contracts
| Contract | Address (first 20) | Status |
|---|---|---|
| VaultEngine v3 (fixed) | `995b4ddf20af077f0fb6` | ✅ Init, wired |
| PriceOracle (fresh) | `67377a2c7ed4b22d8c40` | ✅ Init, price proposed |
| xUSD (fresh) | `5aa940b7108a8e2fb83d` | ✅ Init, asset created |

### Fresh Addresses (re-deployed after DAG reorg)
| Name | Full Hash |
|---|---|
| PriceOracle | `67377a2c7ed4b22d8c40f6afb363e0011bb262359e52dd2c6ecc62cb846868e9` |
| xUSD contract | `5aa940b7108a8e2fb83d4ce0f406acf777a374bd22608d4b9a96f36adb58ef7f` |
| xUSD asset hash | `4db841615115ebe523ad7dfe8b35dd966854f631d0c3990bb939e6ef4dca96fd` |

### VaultEngine v3 (995b4ddf...) State
- `init`: 1 ✅, `a`: admin ✅, `n`: 1 ✅
- `oc`: `67377a2c...` (fresh PO) ✅
- `xc`: `5aa940b7...` (fresh xUSD) ✅
- `xa`: `4db84161...` (fresh xUSD asset) ✅
- Vault 0: 1 XEL collateral, 0 borrow ✅

### PriceOracle State
- `init`: 1 ✅, `a`: admin ✅
- `p` (active price): None ⏳
- `pp` (pending price): 50000000 ($0.50/XEL) ✅
- `pt` (pending topo): 20089 ✅
- execute_price available at topo: 20089 + 720 = 20809
- Current topo: ~20104 (need ~705 more blocks, ~59 minutes)

---

## Common Errors

### "Invalid invoke contract"
- **invoke_contract entry index is 0-based** — entry 0 = init, entry 1 = first fn after init (may be internal!)
- If a contract has `fn only_admin()` as its second declaration, entry 1 = that fn (not callable). The first callable entry after init is **entry 2** (e.g. propose_price, create_asset).
- **Solution**: Check contract source for `fn` declarations between `entry` declarations.

### "Server returned error: [-32004] Invalid TX <hash>"
- Wallet is trying to reuse a TX hash from cache
- **Fix**: Restart wallet process (not rescan)

### "Proof verification error"
- Wallet nonce desync after DAG reorg or failed TX
- **Fix**: Restart wallet process

### "Tx nonce already used"
- Wallet nonce tracking desync
- **Fix**: Restart wallet process

---

## Reference: ForgeSwap Pattern (from github.com/XELIS-Forge/smart-contracts)
- Uses `hook constructor()` for initialization
- Uses `get_deposits().len()` before `get_deposit_for_asset()` to check deposits
- `get_deposit_for_asset(Hash::zero())` works on real daemon VM for native XEL
- The CLI compiler stub returning `None` is ONLY for simulation — real daemon has working implementation
- Deploy with `invoke` param to trigger constructor

## Documentation Sources
- Wallet API: https://docs.xelis.io/developers-api/wallet
- Daemon API: https://docs.xelis.io/developers-api/daemon
- Full API reference (GitHub): https://raw.githubusercontent.com/xelis-project/xelis-blockchain/master/API.md
- Smart Contracts guide: https://docs.xelis.io/getting-started/guides/contracts/create-your-first-contract
- XELIS VM: https://github.com/xelis-project/xelis-vm
- Forge Swap src: https://github.com/XELIS-Forge/smart-contracts
