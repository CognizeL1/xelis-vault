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
| Compilation & static analysis (18+ syntax bugs fixed) | ✅ |
| Comprehensive bug audit (24 bugs: 7 critical, 8 elevated, 6 medium, 3 minor) | ✅ Complete |

All contracts compile cleanly. All 24 bugs identified and catalogued for fix sprint.

---

## Phase 0.5: Bug Fix Sprint 🔧

| Task | Status |
|------|--------|
| Fix 7 critical bugs (PriceOracle zero-store, VaultEngine missing mint/burn/transfer, GovernanceVault asset hash) | 🔧 In progress |
| Fix 8 elevated bugs (transfer to caller, flash loan finality, auction reveal timing, Insurance drain) | 📅 Sprint 2 |
| Fix 6 medium + 3 minor bugs | 📅 Sprint 3 |
| Re-test all contracts after fixes | 📅 Sprint 3 |

---

## Phase 1: VM & Deployment 🔧

### Current Status: Syscall ID Mismatch Fixed

The silex-cli stdlib (`cli/src/stdlib.rs`) has been **fully rewritten** to match the daemon's `build_environment()` registration order exactly. The main registration sequence in `cli/src/main.rs` was also fixed to remove `iterator::register` for V0 compatibility.

### Root Cause (Resolved)

All native functions in XELIS VM share a single flat `Vec<NativeFunction>`. The syscall ID is simply the index in this vector. When the compiler and daemon register functions in different orders — or register different sets of functions — the resulting bytecode has wrong syscall IDs. Specific issues found and fixed:

1. **Iterator position**: `xstd::register` in silex-cli always included `iterator::register`, but the daemon only registers iterator for V1+ contracts. Now omitted for V0.
2. **Ciphertext static method name**: Daemon registers `generate` (not `new`) — now uses `generate`.
3. **Extra compiler stubs**: Functions like `Contract::get_storage`, `get_metadata`, `set_metadata`, `schedule_execution` were removed.
4. **ScheduledExecution mismatch**: Now matches daemon function set exactly.
5. **Method registration order**: Proof methods now registered before contract/scheduled-execution methods, matching daemon.

**Fix applied**: silex-cli environment is byte-for-byte identical to daemon's `build_environment()` for V0.

| Task | Status |
|------|--------|
| Identify root cause (function registration order mismatch) | ✅ |
| Fix xstd registration order (remove iterator for V0) | ✅ |
| Rewrite stdlib.rs to match daemon's `build_environment()` exactly | ✅ |
| Deploy and test `Storage::store` / `Storage::load` on testnet | 🔧 In progress |
| Deploy PriceOracle → xUSD → VaultEngine on testnet | 📅 |
| Full vault lifecycle test (deposit → borrow → repay → withdraw) | 📅 |
| Liquidation path test | 📅 |

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

## Phase 7: XelisVault Messenger 1.0 📅

| Task | Timeline |
|------|----------|
| 1-to-1 encrypted messaging contract | Q4 2026 |
| Payment+message bundling | Q4 2026 |
| Proof-of-delivery | Q4 2026 |
| XELIS public key crypto integration | Q4 2026 |

---

## Phase 8: XelisVault Messenger 2.0 📅

| Task | Timeline |
|------|----------|
| Group messaging (50 members) | Q1 2027 |
| Role-based access (admin, mod, member) | Q1 2027 |
| Thread support | Q1 2027 |
| Self-destructing messages | Q1 2027 |

---

## Phase 9: XelisVault Messenger 3.0 📅

| Task | Timeline |
|------|----------|
| DAO governance channels | Q2 2027 |
| Proposal-linked messaging | Q2 2027 |
| VLT-gated access | Q2 2027 |
| Vote-signaling | Q2 2027 |

---

## Phase 10: XelisVault Messenger 4.0 📅

| Task | Timeline |
|------|----------|
| File attachments (IPFS/Arweave) | Q2 2027 |
| Reactions and typing indicators | Q2 2027 |
| Mobile SDK | Q3 2027 |

---

## Current Sprint (May 26)

### Active
- **[Adrien]** Deploying TestStorage.slx to testnet to verify storage persistence
- **[Adrien]** Fixing 7 critical bugs identified in comprehensive audit
- **[Adrien]** Applying contract logic fixes (PriceOracle, VaultEngine, GovernanceVault)

### This Week
- [ ] Verify `storage_store` debug file is created on contract invocation
- [ ] Fix critical bugs: PriceOracle zero-store, VaultEngine mint/burn/transfer, GovernanceVault asset hash
- [ ] Fix elevated bugs: xUSD/VLT transfer-to-caller, auction reveal timing, PrivateInsurance drain
- [ ] Recompile all contracts with corrected silex-cli

### Next Week
- [ ] Deploy first core contracts (PriceOracle, xUSD, VaultEngine) to testnet
- [ ] Run full deposit → borrow → repay → withdraw lifecycle on testnet
- [ ] Deploy all 19 contracts to testnet
- [ ] SDK integration tests

### Coming Up
- [ ] Dashboard MVP
- [ ] Public testnet announcement
- [ ] XelisVault Messenger design phase

---

[⬅ Back to README](../README.md)
