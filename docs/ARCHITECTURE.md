# XELIS Vault — Architecture

## Directory Structure

```
xelis-vault/
├── contracts/                  # Smart contracts (Silex)
│   ├── vault/
│   │   └── VaultEngine.slx    # Core lending logic
│   ├── oracle/
│   │   └── PriceOracle.slx    # Price feed with timelock
│   ├── interest/
│   │   └── InterestRateModel.slx  # Dynamic interest rates
│   ├── xusd/
│   │   └── xUSD.slx           # Confidential stablecoin
│   ├── insurance/
│   │   └── InsurancePool.slx  # Community insurance
│   └── flashloan/
│       └── FlashLoan.slx      # Confidential flash loans
├── sdk/
│   └── src/
│       └── index.ts           # TypeScript SDK
├── dashboard/
│   └── src/
│       ├── App.tsx            # Main React app
│       ├── components/        # UI components
│       ├── hooks/             # React hooks
│       └── utils/             # Utilities
├── bot/
│   └── src/
│       └── index.ts           # Liquidation keeper bot
├── scripts/
│   ├── setup-devnet.sh        # Devnet environment setup
│   ├── deploy.sh              # Core contract deployment
│   └── deploy-full.sh         # Full ecosystem deployment
├── docs/
│   ├── WHITEPAPER.md          # Technical whitepaper
│   ├── ARCHITECTURE.md        # This file
│   └── ROADMAP.md             # Development roadmap
├── test/                      # Test files
├── README.md                  # Project overview
└── package.json               # Root package
```

## Smart Contract Dependencies

```
VaultEngine
    ├── depends on → PriceOracle (get price data)
    ├── depends on → xUSD (mint/burn stablecoin)
    ├── depends on → InterestRateModel (calculate rates)
    └── called by → LiquidationBot (liquidate positions)

xUSD
    ├── depends on → VaultEngine (mint authorization)
    └── extends → Confidential Asset (native XELIS)

InsurancePool
    ├── depends on → VaultEngine (verify vault status)
    └── depends on → xUSD (payouts)

FlashLoan
    ├── depends on → VaultEngine (liquidity)
    └── depends on → target contracts (callbacks)
```

## Data Flow

### Deposit → Borrow → Repay → Withdraw

```
1. DEPOSIT
   User → [XEL] → VaultEngine
   VaultEngine → store encrypted collateral
   VaultEngine → create VaultSnapshot
   Return: vault_id

2. BORROW
   User → call borrow(vault_id, amount)
   VaultEngine → check health (collateral ≥ debt × 1.5)
   VaultEngine → call xUSD.mint(user, amount)
   VaultEngine → collect 0.5% fee
   VaultEngine → update encrypted debt
   Return: total_debt

3. REPAY
   User → [xUSD] → VaultEngine
   VaultEngine → call xUSD.burn(user, amount)
   VaultEngine → update encrypted debt
   Return: remaining_debt

4. WITHDRAW
   User → call withdraw(vault_id, amount)
   VaultEngine → check health (post-withdrawal)
   VaultEngine → [XEL] → User
   VaultEngine → update encrypted collateral
   Return: remaining_collateral
```

## Privacy Model

| Data | On-Chain | Visibility |
|------|----------|------------|
| Vault owner | Public (Address) | Everyone |
| Collateral amount | Encrypted (Ciphertext) | Owner only |
| Borrow amount | Encrypted (Ciphertext) | Owner only |
| Health factor | Computed (plaintext for VM) | No one (ZK verified) |
| xUSD balance | Encrypted (native) | Owner only |
| Liquidations | Public (event) | Everyone |
| Protocol fees | Public (plaintext) | Everyone |

## Gas Estimates (approximate)

| Operation | Gas Cost |
|-----------|----------|
| deposit() | ~5,000 |
| borrow() | ~15,000 |
| repay() | ~12,000 |
| withdraw() | ~10,000 |
| liquidate() | ~20,000 |
| flash_loan() | ~30,000 |

---

## Deployment Addresses (Mainnet)

*To be filled after mainnet deployment*

| Contract | Address |
|----------|---------|
| VaultEngine | `TBD` |
| xUSD | `TBD` |
| PriceOracle | `TBD` |
| InterestRateModel | `TBD` |
| InsurancePool | `TBD` |
| FlashLoan | `TBD` |
