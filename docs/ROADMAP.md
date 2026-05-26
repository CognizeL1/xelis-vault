# XELIS Vault — Roadmap

> *Last updated: May 26, 2026*

---

## Legend

- ✅ **Done** — Deployed and/or verified
- 🔧 **In progress** — Currently being actively worked on
- 📅 **Planned** — Scheduled for future iteration

---

## Phase 0: Contracts & Compilation ✅

| Task | Status |
|------|--------|
| Whitepaper v2 | ✅ |
| Architecture docs | ✅ |
| All 19 smart contracts (core, markets, treasury, compliance, governance) | ✅ Written |
| Compilation & static analysis (18+ bugs fixed) | ✅ |

All contracts compile cleanly. No syntax errors, no undefined references.

---

## Phase 1: VM & Deployment 🔧

### Current Blocker: Storage Persistence

The VM executes but `storage_store` / `storage_load` are never reached. We traced this to a **syscall ID mismatch** between the silex-compiler and the daemon runtime.

| Task | Status |
|------|--------|
| Identify root cause (function registration order mismatch) | ✅ |
| Fix xstd registration order (remove iterator for V0) | ✅ Done |
| Rewrite stdlib.rs to match daemon's `build_environment()` exactly | 🔧 In progress |
| Fix module binary serialization format | 🚧 Next |
| Deploy and test `Storage::store` / `Storage::load` on testnet | 🚧 |
| Deploy PriceOracle → xUSD → VaultEngine on testnet | 📅 |
| Full vault lifecycle test (deposit → borrow → repay → withdraw) | 📅 |
| Liquidation path test | 📅 |

### Root Cause Detail

All native functions in XELIS VM share a single flat `Vec<NativeFunction>`. The syscall ID is simply the index in this vector. When the compiler and daemon register functions in different orders — or register different sets of functions — the resulting bytecode has wrong syscall IDs. Specific issues found:

1. **Iterator position**: `xstd::register` in silex-cli always includes `iterator::register`, but the daemon only registers iterator for V1+ contracts. This shifts all subsequent IDs for V0 contracts.

2. **Ciphertext static method name**: Daemon registers `generate` (not `new`) for creating ciphertexts from address + amount.

3. **Extra compiler stubs**: Several functions registered by the silex stdlib don't exist in the daemon (e.g., `Contract::get_storage`, `Contract::get_metadata`, `Contract::set_metadata`, `Contract::schedule_execution`).

4. **ScheduledExecution mismatch**: Different function sets and names between compiler and daemon.

5. **Method registration order**: Proof methods are registered before contract/scheduled-execution methods in the daemon, but after them in the compiler.

**Fix**: Rewrite the silex-cli environment to exactly mirror the daemon's `build_environment()` registration order, function by function.

---

## Phase 2: Core Lending on Testnet 📅

| Task | Timeline |
|------|----------|
| Deploy PriceOracle (set initial XEL price) | Week 1 post-fix |
| Deploy xUSD (create confidential asset) | Week 1 |
| Deploy InterestRateModel | Week 1 |
| Deploy VaultEngine (set oracle, xUSD, interest model addresses) | Week 2 |
| Test deposit → borrow → repay → withdraw lifecycle | Week 2 |
| Test redemption path | Week 2 |
| Test liquidation path | Week 2 |
| Deploy InsurancePool + FlashLoan | Week 2 |

---

## Phase 3: Peg, Governance & Markets 📅

| Task | Timeline |
|------|----------|
| XELIS Forge xUSD/XEL pool | Week 3 |
| VLT token deployment (10M confidential asset) | Week 3 |
| GovernanceVault + Timelock | Week 3 |
| Private Lending Marketplace | Week 4 |
| Peer-to-Peer Lending | Week 4 |
| Sealed-Bid Auctions | Week 5 |

---

## Phase 4: Institutional 📅

| Task | Timeline |
|------|----------|
| Compliance Module (ZK KYC/AML) | Week 6 |
| Syndicated Loans | Week 6 |
| Treasury Vault (multi-sig) | Week 7 |
| RWA Tokenization Standard (AssetVault) | Week 7 |

---

## Phase 5: Expansion 📅

| Task | Timeline |
|------|----------|
| Revenue Sharing | Week 8 |
| Private Payroll | Week 8 |
| Private Insurance | Week 9 |
| Multi-Collateral Support | Week 9 |

---

## Phase 6: Production 📅

| Task | Timeline |
|------|----------|
| Professional Security Audit | Q3 2026 |
| Bug Bounty Program | Q3 2026 |
| Public Testnet Launch | Q3 2026 |
| Mainnet Launch | Q3 2026 |
| Cross-chain xUSD (Trocador) | Q3 2026 |
| Position NFTs (tradeable debt) | Q3 2026 |
| Credit scores (under-collateralized loans) | Q3 2026 |
| Full DAO governance | Q3 2026 |
| Institutional API | Q4 2026 |

---

## Current Sprint (May 26)

### Active
- **[Adrien]** Rewriting silex-cli stdlib to match daemon environment exactly
- **[Adrien]** Deploying TestStorage.slx to testnet to verify storage persistence
- **[Adrien]** Testing module binary serialization format

### This Week
- [ ] Fix registration order completely
- [ ] Verify `storage_store` debug file is created on contract invocation
- [ ] Deploy first core contracts (PriceOracle, xUSD, VaultEngine)
- [ ] Run full deposit → borrow → repay → withdraw lifecycle on testnet

### Next Week
- [ ] Deploy all 19 contracts to testnet
- [ ] SDK integration tests
- [ ] Dashboard MVP
- [ ] Public testnet announcement

---

[⬅ Back to README](../README.md)
