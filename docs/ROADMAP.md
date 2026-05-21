# XELIS Vault — Roadmap

> *Last updated: May 2026*

---

## Phase 0: Foundation ✅

| Task | Status |
|------|--------|
| Whitepaper v2 | ✅ |
| Architecture docs | ✅ |
| Core smart contracts | ✅ |
| Devnet environment | ✅ |

## Phase 1: Core Lending 🚧

| Task | Status |
|------|--------|
| VaultEngine — deposit / borrow / repay / withdraw | ✅ Live on devnet |
| xUSD Confidential Asset — mint & burn | ✅ Live on devnet |
| InterestRateModel — kinked rates | ✅ Live on devnet |
| PriceOracle — XEL price feed | ✅ Live on devnet |
| InsurancePool — stake & claim | ✅ Compiled |
| FlashLoan — uncollateralized flash loans | ✅ Compiled |
| TypeScript SDK | ✅ Built |
| Liquidation Bot | ✅ Built |
| Dashboard (React) | 🚧 In progress |
| CLI Tool | 🔲 |
| Deploy & test full lifecycle on devnet | ✅ Verified |

> **Milestone achieved** — Single-asset lending fully working on devnet

## Phase 2: Governance & Markets 📅 (Post-VM Fix)

| Task | Timeline |
|------|----------|
| **VLT Governance Token** — 10M supply, confidential asset | Week 1 |
| **GovernanceVault** — stake VLT, vote on parameters | Week 1 |
| **Timelock** — 48h delay on all parameter changes | Week 2 |
| **Private Lending Marketplace** — multi-pool, multi-collateral | Week 3-4 |
| **Peer-to-Peer Lending** — bilateral confidential loans | Week 5 |
| **Sealed-Bid Auctions** — fully confidential bidding | Week 6 |

> **Milestone** — Decentralized governance live + financial markets operational

## Phase 3: Institutional 📅

| Task | Timeline |
|------|----------|
| **Compliance Module** — ZK KYC/AML verification layer | Week 7-8 |
| **Syndicated Loans** — multi-lender credit pools | Week 8-9 |
| **Treasury Vault** — confidential multi-sig for DAOs/institutions | Week 9-10 |
| **RWA Tokenization Standard** — AssetVault template | Week 10-11 |
| **Private Revenue Sharing** — confidential revenue distribution | Week 12 |
| **Private Payroll** — confidential recurring payments | Week 12 |

> **Milestone** — Institutions can participate with full privacy and compliance

## Phase 4: Expansion 📅

| Task | Timeline |
|------|----------|
| **Private Insurance & Derivatives** — P2P risk markets | Week 13-14 |
| **Multi-Collateral Support** — borrow against any asset | Week 14-15 |
| **Forge DEX Integration** — xUSD/XEL liquidity pool | Week 15-16 |
| **Testnet Launch** — full ecosystem on testnet | Week 16 |

> **Milestone** — Full platform live and tested on testnet

## Phase 5: Mainnet & Beyond 📅

| Task | Timeline |
|------|----------|
| **Security Audit** — professional smart contract audit | Q3 2026 |
| **Bug Bounties** — community security rewards | Q3 2026 |
| **Mainnet Launch** — full protocol on XELIS mainnet | Q3 2026 |
| **Cross-Chain xUSD** — via Trocador bridge | Q3 2026 |
| **Position NFTs** — tradeable debt positions | Q3 2026 |
| **Credit Scores** — under-collateralized lending | Q3 2026 |
| **Full DAO Governance** — on-chain proposal system | Q3 2026 |
| **Institutional API** — programmatic access for funds | Q4 2026 |

> **Milestone** — Live on mainnet with real TVL and institutional adoption

---

## Current Sprint

### Pre-Fix (awaiting VM upgrade May 30)
- [x] Dashboard React (UI components)
- [ ] CLI Tool
- [ ] SDK expansion
- [ ] Deployment scripts

### Post-Fix (immediately after May 30)
- [ ] Deploy secured VaultEngine to testnet
- [ ] Deploy VLT + GovernanceVault + Timelock
- [ ] Validate get_caller/require work correctly
- [ ] Deploy LendingMarket prototype

---

## Legend

- ✅ **Done** — Deployed and verified
- 🚧 **In progress** — Currently being worked on
- 🔲 **Pending** — Not yet started
- 📅 **Planned** — Scheduled for future

---

[⬅ Back to README](../README.md)
