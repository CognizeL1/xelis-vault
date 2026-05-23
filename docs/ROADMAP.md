# XELIS Vault — Roadmap

> *Last updated: May 2026*

---

## Phase 0: Foundation ✅

| Task | Status |
|------|--------|
| Whitepaper v2 | ✅ |
| Architecture docs | ✅ |
| All 19 smart contracts written | ✅ |
| Compilation & static analysis fixes | ✅ |

## Phase 1: Core Lending ✅

| Task | Status |
|------|--------|
| VaultEngine — deposit / borrow / repay / withdraw / liquidate / redeem | ✅ Compiled (380 LOC) |
| xUSD Confidential Asset — mint / burn / transfer | ✅ Compiled |
| InterestRateModel — kinked rates | ✅ Compiled |
| PriceOracle — XEL price feed via contract call | ✅ Compiled |
| InsurancePool — stake / claim / member tracking | ✅ Compiled |
| FlashLoan — reentrancy-safe uncollateralized flash loans | ✅ Compiled |
| TypeScript SDK | ✅ Built |
| Liquidation Bot | ✅ Built |
| Dashboard (React) | 🚧 In progress |
| Devnet deploy | 🚧 In progress |

> **Milestone achieved** — All 19 contracts compile, 18 bugs fixed (7 static analysis + 11 compilation)

## Phase 2: Peg, Governance & Markets ✅

| Task | Status |
|------|--------|
| **Redemption Mechanism** — fair-queue redeem with fee & burn | ✅ Compiled |
| **VLT Governance Token** — create / mint / burn_vlt / transfer | ✅ Compiled |
| **GovernanceVault** — stake VLT with absolute locktopo, voting power | ✅ Compiled |
| **Timelock** — 48h delay, reentrancy-safe execution | ✅ Compiled |
| **Private Lending Marketplace** — borrow positions, repay-to-unlock | ✅ Compiled |
| **Peer-to-Peer Lending** — bilateral confidential loans | ✅ Compiled |
| **Sealed-Bid Auctions** — bid / reveal / settle with reveal window | ✅ Compiled |

> **Milestone** — All Phase 2 contracts compiled and bug-fixed

## Phase 3: Institutional ✅

| Task | Status |
|------|--------|
| **Compliance Module** — KYC/AML with address-indexed dedup | ✅ Compiled |
| **Syndicated Loans** — multi-lender credit pools | ✅ Compiled |
| **Treasury Vault** — confidential multi-sig for DAOs/institutions | ✅ Compiled |
| **RWA Tokenization Standard** — AssetVault with revaluation | ✅ Compiled |
| **Private Revenue Sharing** — holder-tracked revenue distribution | ✅ Compiled |
| **Private Payroll** — time-based accrual payroll | ✅ Compiled |

> **Milestone** — All Phase 3 contracts compiled and bug-fixed

## Phase 4: Complete ✅

| Task | Status |
|------|--------|
| **Private Insurance** — P2P risk markets with join dedup | ✅ Compiled |
| **Multi-Collateral Support** — borrow against any asset (by pool) | ✅ Compiled |
| **All 19 contracts** — compiled, analyzed, fixed | ✅ Complete |

> **Milestone** — Full contract suite ready for deployment

## Phase 5: Deployment 🚧

| Task | Timeline |
|------|----------|
| **Fix silex-cli hex format** — output binary-format hex instead of JSON | Current |
| **Deploy core contracts** — PriceOracle → xUSD → VaultEngine | Next |
| **Test full lifecycle on devnet** — vault creation, liquidation, redeem | Week 1 |
| **Security Audit** — professional smart contract audit | Q3 2026 |
| **Bug Bounties** — community security rewards | Q3 2026 |
| **Testnet Launch** | Q3 2026 |
| **Mainnet Launch** | Q3 2026 |

---

## Current Sprint

### Blocker: Wallet hex format
The `build_transaction` RPC expects the module as hex-encoded **binary** (custom `Serializer` format), but `silex-cli` outputs hex-encoded **JSON**. Fixing silex-cli to output binary hex is the critical path to deployment.

### In Progress
- [ ] Fix silex-cli to output binary-format hex (custom `Module::write` format)
- [ ] Dashboard React (UI components)
- [ ] SDK expansion
- [ ] Deployment scripts

### Post-Deployment
- [ ] Deploy PriceOracle → set price
- [ ] Deploy xUSD → create asset
- [ ] Deploy VaultEngine → set addresses
- [ ] Test vault lifecycle: deposit → borrow → repay → withdraw
- [ ] Test liquidation path
- [ ] Deploy VLT + GovernanceVault + Timelock
- [ ] Deploy remaining 14 contracts

---

## Legend

- ✅ **Done** — Deployed and verified
- 🚧 **In progress** — Currently being worked on
- 🔲 **Pending** — Not yet started
- 📅 **Planned** — Scheduled for future

---

[⬅ Back to README](../README.md)
