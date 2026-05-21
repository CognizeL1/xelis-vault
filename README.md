# XELIS Vault

### The First Confidential Financial Platform on XELIS BlockDAG

Deposit XEL, borrow xUSD, tokenize real-world assets, manage treasuries, trade privately — all secured by native Twisted ElGamal homomorphic encryption.

[![XELIS](https://img.shields.io/badge/XELIS-BlockDAG-8B5CF6)](https://xelis.io)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## Why XELIS Vault?

Every other platform operates on fully transparent ledgers. Your positions, your strategies, your holdings — visible to everyone.

**XELIS Vault changes that.**

Built on XELIS native homomorphic encryption, XELIS Vault is the first platform where:
- Your **lending position** is encrypted — no one sees your collateral or debt
- Your **stablecoin balance** is private — encrypted transfers by default
- Your **treasury** is confidential — only authorized signers see balances
- Your **auction bids** are sealed — no front-running, no sniping
- Your **compliance** is zero-knowledge — prove eligibility without revealing identity
- Your **governance** is decentralized — VLT holders control protocol parameters

---

## Products

| Product | Description | Status |
|---------|-------------|--------|
| **Confidential Lending** | Overcollateralized loans with private positions | ✅ Live on devnet |
| **xUSD Stablecoin** | Privacy-preserving stablecoin | ✅ Live on devnet |
| **Redemption** | Arbitrage mechanism for xUSD peg via Forge DEX | 🔲 Planned |
| **Private Marketplace** | Multi-pool, multi-collateral lending | 🔲 Planned |
| **RWA Tokenization** | Standard for private real-world asset tokens | 🔲 Planned |
| **Treasury Vault** | Confidential multi-sig for DAOs/institutions | 🔲 Planned |
| **Peer Loans** | Bilateral confidential lending | 🔲 Planned |
| **Syndicated Loans** | Multi-lender credit pools | 🔲 Planned |
| **Sealed-Bid Auctions** | Confidential bidding | 🔲 Planned |
| **Compliance Layer** | ZK KYC/AML verification | 🔲 Planned |
| **Governance (VLT)** | Token-based protocol governance | 🔲 Planned |

---

## Smart Contracts

| Contract | Type | Description |
|----------|------|-------------|
| **VaultEngine** | Core | Deposit, borrow, repay, withdraw, liquidate |
| **xUSD** | Core | Confidential stablecoin |
| **PriceOracle** | Core | XEL price feed |
| **InterestRateModel** | Core | Dynamic kinked rates |
| **Redemption** | Core | Automatic peg support via Forge DEX arbitrage |
| **LendingMarket** | Market | Multi-pool lending marketplace |
| **PeerLoan** | Market | Bilateral P2P loans |
| **SyndicatePool** | Market | Syndicated credit pools |
| **SealedBidAuction** | Market | Confidential auctions |
| **AssetVault** | Tokenization | RWA token standard |
| **TreasuryVault** | Treasury | Multi-sig treasury |
| **RevenueShare** | Treasury | Revenue distribution |
| **Payroll** | Treasury | Recurring payments |
| **InsurancePool** | Insurance | Community insurance |
| **PrivateInsurance** | Insurance | P2P risk markets |
| **FlashLoan** | Core | Confidential flash loans |
| **ComplianceModule** | Compliance | ZK KYC/AML layer |
| **VLT** | Governance | Governance token |
| **GovernanceVault** | Governance | Staking & voting |
| **Timelock** | Governance | 48h execution delay |

---

## How It Works

### For Lenders
```
1. Supply XEL or xUSD → pool
2. Earn interest (dynamic APR)
3. Withdraw anytime
4. Everything is private
```

### For Borrowers
```
1. Deposit XEL as collateral
2. Borrow xUSD against it
3. Repay to unlock collateral
4. Your position is encrypted
```

### For Institutions
```
1. Complete KYC off-chain (once)
2. Receive ZK compliance proof
3. Use any protocol feature privately
4. Regulators see proofs, not positions
```

### For DAOs
```
1. Create a Treasury Vault
2. Add signers with multi-sig
3. Manage budgets confidentially
4. Pay contributors via private payroll
```

---

## Progress

| Phase | Status |
|-------|--------|
| **Core Lending** — deposit, borrow, repay, withdraw | ✅ Live on devnet |
| **xUSD Stablecoin** | ✅ Live on devnet |
| **Price Oracle** | ✅ Live on devnet |
| **Interest Rate Model** | ✅ Live on devnet |
| **Insurance Pool** | ✅ Compiled |
| **Flash Loans** | ✅ Compiled |
| **Dashboard** | 🚧 In progress |
| **TypeScript SDK** | ✅ Built |
| **Liquidation Bot** | ✅ Built |
| **CLI Tool** | 🔲 |
| **Testnet Launch** | 📅 Next |
| **Mainnet** | 📅 Q3 2026 |

---

## Documentation

- [📄 Whitepaper](docs/WHITEPAPER.md) — Full technical specification
- [🗺️ Roadmap](docs/ROADMAP.md) — Development timeline
- [🏗️ Architecture](docs/ARCHITECTURE.md) — System design

---

## Community

XELIS Vault is open-source and community-driven. Privacy in finance should be accessible to everyone.

**How to contribute:**
- **Code** — PRs welcome on contracts, SDK, dashboard, CLI, and bot
- **Security** — Review contracts, report vulnerabilities
- **Build** — Create tools, integrations, and composable products
- **Translate** — Help make XELIS Vault accessible globally
- **Design** — Improve UX, create educational content
- **Run a node** — Help decentralize the XELIS network

---

## Links

[![GitHub](https://img.shields.io/badge/GitHub-XelisVault-181717)](https://github.com/XelisVault/xelis-vault)
[![XELIS](https://img.shields.io/badge/XELIS-BlockDAG-8B5CF6)](https://xelis.io)

---

*XELIS Vault — Confidential Finance for the Privacy Era*
