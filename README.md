# XELIS Vault

### *The First Confidential Financial Platform on XELIS BlockDAG*

Deposit XEL, borrow xUSD, tokenize real-world assets, manage treasuries, trade privately — all secured by native Twisted ElGamal homomorphic encryption on the XELIS BlockDAG.

[![XELIS](https://img.shields.io/badge/XELIS-BlockDAG-8B5CF6)](https://xelis.io)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## Why XELIS Vault?

Every other DeFi platform operates on fully transparent ledgers. Your positions, your strategies, your holdings — visible to everyone, including bots, competitors, and regulators.

**XELIS Vault changes that.**

Built on XELIS native homomorphic encryption, XELIS Vault is the first platform where:

- Your **lending position** is encrypted — nobody sees your collateral or debt
- Your **stablecoin balance** is private — encrypted transfers by default
- Your **treasury** is confidential — only authorized signers see balances
- Your **auction bids** are sealed — no front-running, no sniping
- Your **compliance** is zero-knowledge — prove eligibility without revealing identity
- Your **governance** is decentralized — VLT holders control protocol parameters

---

## What We're Building

XELIS Vault is a complete suite of **19 smart contracts** covering every major DeFi primitive — all with built-in confidentiality via XELIS native Twisted ElGamal encryption.

### Core Lending

| Product | Description |
|---------|-------------|
| **VaultEngine** | Overcollateralized lending: deposit XEL, borrow xUSD (50% LTV max) |
| **xUSD Stablecoin** | Confidential stablecoin minted one-to-one against XEL collateral |
| **PriceOracle** | XEL price feed with timelock, callable from any contract |
| **InterestRateModel** | Kinked interest rates (80% utilization kink) |
| **Redemption** | Fair-queue arbitrage mechanism that keeps xUSD pegged to $1 |
| **FlashLoan** | Uncollateralized flash loans with reentrancy protection |

### Financial Markets

| Product | Description |
|---------|-------------|
| **LendingMarket** | Multi-pool, multi-collateral private lending marketplace |
| **PeerLoan** | Bilateral confidential P2P loans with custom terms |
| **SyndicatePool** | Multi-lender, single-borrower syndicated credit pools |
| **SealedBidAuction** | Confidential bidding with commit/reveal/settle |

### Tokenization & Treasury

| Product | Description |
|---------|-------------|
| **AssetVault** | Standard template for issuing confidential RWA tokens |
| **TreasuryVault** | Multi-signature confidential treasury management |
| **RevenueShare** | Confidential revenue distribution to holders |
| **Payroll** | Private recurring payments with time-based accrual |

### Insurance & Derivatives

| Product | Description |
|---------|-------------|
| **InsurancePool** | Community-backed insurance pool (stake → earn premiums → claim) |
| **PrivateInsurance** | Peer-to-peer insurance and derivatives markets |

### Compliance & Governance

| Product | Description |
|---------|-------------|
| **ComplianceModule** | ZK-based KYC/AML verification layer (MiCA/MiFID compatible) |
| **VLT Token** | Governance token (10M supply, confidential asset) |
| **GovernanceVault** | Stake VLT, earn boosted voting power, control protocol parameters |
| **Timelock** | 48-hour delay on all parameter changes with guardian veto |

---

## How It Works

### Borrow xUSD Against XEL

1. **Deposit** XEL into VaultEngine (encrypted, private).
2. **Borrow** xUSD up to 50% Loan-To-Value.
3. **Interest** accrues dynamically based on pool utilization (kinked model).
4. **Repay** xUSD → unlock your XEL collateral.
5. If LTV exceeds the maximum (150% collateral ratio), anyone can **liquidate** the position.

### xUSD Peg Mechanism

xUSD is designed to trade at $1 through four mechanisms:

- **Redemption** (primary) — Anyone can burn xUSD and claim XEL at face value via a fair queue. When xUSD trades below $1 on external DEXes (XELIS Forge), arbitrageurs buy and redeem for profit.
- **Borrow arbitrage** — When xUSD trades above $1, vault holders can borrow xUSD at face value and sell it for profit.
- **Overcollateralization** — Every xUSD is backed by at least $1.50 of XEL collateral.
- **Savings Rate** — Adjustable APY incentivizes holding or spending.

### Governance (VLT)

- **VLT** is the governance token (10M supply, confidential asset).
- **GovernanceVault**: stake VLT, earn up to 2x voting power via timelock commitments.
- VLT holders control: collateral ratios, liquidation penalties, interest rate parameters, asset whitelist, oracle sources, compliance verifiers.
- All parameter changes pass through a 48-hour **Timelock**.

---

## Current Status

| Phase | Status |
|-------|--------|
| **19 Smart Contracts** — all compiled, bug-fixed, hex-generated | ✅ Complete |
| **Bug Fixes Applied** — 18+ static analysis & compilation fixes | ✅ Complete |
| **TypeScript SDK** | ✅ Built |
| **Liquidation Bot** | ✅ Built |
| **Dashboard (React)** | 🚧 In progress |
| **VM Storage Bug Fix** — syscall ID mismatch between compiler and daemon | 🔧 In progress |
| **Testnet Deployment** | 📅 Post-VM-fix |
| **Mainnet Launch** | 📅 Q3 2026 |

### Current Blocker: VM Syscall ID Mismatch

We identified that the silex-compiler's environment registration order differs from the daemon's runtime environment. Because all native functions share a single flat ID space, even one registration difference shifts every subsequent syscall ID. Key findings:

- `iterator::register` is included in silex-cli's `EnvironmentBuilder::default()` but only registered by the daemon for V1+ contracts
- Several opaque type methods have different names (`generate` vs `new` for Ciphertext)
- Several contract functions differ between compiler stubs and daemon registrations

**We're fixing this by rewriting the silex-cli environment to exactly mirror the daemon's `build_environment()` registration order.** Once fixed, storage operations (`storage_store`, `storage_load`) will reach the daemon's handlers and contracts can be deployed with persistent state.

---

## Documentation

- [📄 Whitepaper](docs/WHITEPAPER.md) — Full technical specification
- [🗺️ Roadmap](docs/ROADMAP.md) — Development timeline and current sprint
- [🏗️ Architecture](docs/ARCHITECTURE.md) — System design and contract dependencies

## Quick Start

```bash
# Prerequisites: XELIS daemon, wallet, miner running on testnet

# Compile a contract
git clone git@github.com:XelisVault/xelis-vault.git
cd xelis-vault

# Use our silex-cli fork to compile
/path/to/silex-cli contracts/vault/VaultEngine.slx > vault_hex.txt

# Deploy via wallet RPC
curl -u ":password" -X POST http://127.0.0.1:18082/json_rpc \
  -H "Content-Type: application/json" \
  -d '{
    "method": "deploy_contract",
    "params": {
      "data": "'$(cat vault_hex.txt)'",
      "version": 0,
      "fees": 1000000000,
      "entries": [{"name": "init", "args": []}]
    }
  }'
```

---

## Community

XELIS Vault is open-source and community-driven. Privacy in finance should be accessible to everyone.

- **Build** — PRs welcome on contracts, SDK, dashboard, CLI, and bot
- **Security** — Review contracts, report vulnerabilities
- **Translate** — Help make XELIS Vault accessible globally
- **Run a node** — Help decentralize the XELIS network

---

## Links

[![GitHub](https://img.shields.io/badge/GitHub-XelisVault-181717)](https://github.com/XelisVault/xelis-vault)
[![XELIS](https://img.shields.io/badge/XELIS-BlockDAG-8B5CF6)](https://xelis.io)

---

*XELIS Vault — Confidential Finance for the Privacy Era*
