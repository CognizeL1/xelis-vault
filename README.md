# XELIS Vault — The First Confidential Lending Protocol

> **World's first private overcollateralized lending protocol**, built natively on XELIS BlockDAG with homomorphic encryption.

[![XELIS](https://img.shields.io/badge/XELIS-BlockDAG-blue)](https://xelis.io)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## Vision

XELIS Vault brings **privacy to DeFi lending**. Every position (collateral, debt, liquidation threshold) is encrypted using XELIS native **Twisted ElGamal** homomorphic encryption. Users prove solvency via ZK proofs without ever revealing their actual portfolio.

**No other blockchain can do this natively.** Not Ethereum. Not Solana. Not Monero.

---

## Features

| Feature | Status | Description |
|---------|--------|-------------|
| **Confidential Lending** | ✅ MVP | Deposit XEL → borrow xUSD — all encrypted |
| **xUSD Savings Rate** | ✅ MVP | Auto-yield on xUSD deposits — private |
| **Auto-Remining Loans** | ✅ MVP | Yield pays your loan interest automatically |
| **MEV-Resistant Liquidations** | ✅ MVP | Using XELIS Scheduled Executions |
| **Price Oracle** | ✅ MVP | Admin-set with timelock |
| **Insurance Pool** | 📅 V2 | Community protection against bad debt |
| **Flash Loans** | 📅 V2 | Confidential flash loans |
| **Cross-Chain xUSD** | 📅 V3 | Bridge to Ethereum/Solana via Trocador |
| **Position NFTs** | 📅 V3 | Tradeable debt positions |
| **Credit Scores** | 📅 V4 | Under-collateralized borrowing |

---

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│                     XELIS BLOCKCHAIN                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────┐  │
│  │VaultEngine│  │ xUSD CA  │  │Insurance │  │FlashLoan  │  │
│  │  .slx     │  │  .slx    │  │  .slx    │  │  .slx     │  │
│  └─────┬────┘  └──────────┘  └──────────┘  └───────────┘  │
│        │                                                   │
│  ┌─────▼────┐  ┌──────────┐                                │
│  │Oracle.slx│  │Interest  │                                │
│  │          │  │Rate.slx  │                                │
│  └──────────┘  └──────────┘                                │
└────────────────────────┬───────────────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────────────┐
│                     OFF-CHAIN                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ SDK (TS) │  │Dashboard │  │Liquidation│                  │
│  │          │  │ (React)  │  │ Bot (Rust)│                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Smart Contracts

| Contract | Lang | Description |
|----------|------|-------------|
| `VaultEngine.slx` | Silex | Core lending logic — deposit, borrow, repay, withdraw, liquidate |
| `InterestRateModel.slx` | Silex | Dynamic interest rates with kink model |
| `PriceOracle.slx` | Silex | Price feed with timelock |
| `xUSD.slx` | Silex | Confidential Asset — private stablecoin |
| `InsurancePool.slx` | Silex | Community insurance against bad debt |
| `FlashLoan.slx` | Silex | Confidential flash loans |

---

## Revenue Model

| Source | Rate | Destination |
|--------|------|-------------|
| Borrow fee | 0.5% | Protocol treasury + VLT buyback |
| Interest spread | Variable | xUSD depositors + treasury |
| Liquidation fee | 0.5% | Protocol treasury |
| Insurance premium | 0.1% | Insurance pool |

---

## Governance (VLT)

$VLT$ holders control:
- Risk parameters (collateral ratio, liquidation penalty)
- Interest rate model (base rate, kink, multiplier)
- Asset whitelist (which collaterals to accept)
- Treasury allocation
- Protocol upgrades

---

## Quick Start

```bash
# Clone
git clone https://github.com/xelis-vault
cd xelis-vault

# Setup devnet
chmod +x scripts/setup-devnet.sh
./scripts/setup-devnet.sh

# Deploy contracts
chmod +x scripts/deploy.sh
./scripts/deploy.sh

# Start dashboard
cd dashboard && npm install && npm start
```

---

## Budget

| Item | Cost |
|------|------|
| Smart contract code | $0 (Silex/XVM) |
| Devnet/testnet | $0 |
| Domain (optional) | ~$10/year |
| VPS (optional) | ~$5/month |
| XEL for mainnet deploy | ~$20 |
| **Total runway (6 months)** | **~$50** |

---

## License

MIT
