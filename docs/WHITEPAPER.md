# XELIS Vault — Technical Whitepaper

> **Version 1.0 — Confidential Lending on XELIS BlockDAG**
>
> *World's first private overcollateralized lending protocol using native homomorphic encryption*

---

## Abstract

XELIS Vault is a decentralized, non-custodial lending protocol built on the XELIS BlockDAG. It leverages XELIS native **Twisted ElGamal homomorphic encryption** to provide the first truly confidential lending market in blockchain history. Users can deposit XEL as collateral, borrow xUSD (a privacy-preserving stablecoin), earn yield on xUSD savings, and access flash loans — all while keeping their positions completely private.

No existing lending protocol (Aave, Compound, Morpho) offers this level of privacy. XELIS Vault fills this gap by building directly on XELIS unique cryptographic primitives.

---

## 1. Introduction

### 1.1 The Privacy Gap in DeFi Lending

Current DeFi lending protocols operate on fully transparent ledgers:

- **Aave**: $20B+ TVL — every position, liquidation, and interest payment is public
- **Compound**: $3B+ TVL — same transparent model
- **Morpho**: $1.5B+ TVL — peer-to-peer but fully visible

This transparency creates problems:
- **Front-running**: MEV bots watch for large deposits or liquidation opportunities
- **Institutional reluctance**: Funds cannot reveal their positions publicly
- **Privacy loss**: Anyone can track your financial activities forever
- **Competitive disadvantage**: Traders expose their strategies and leverage

### 1.2 Why XELIS

XELIS is uniquely positioned to solve this because:

1. **Native Homomorphic Encryption**: Twisted ElGamal over Ristretto255 enables computation on encrypted data at the protocol level
2. **Confidential Assets**: Any token on XELIS has the same privacy guarantees as XEL
3. **XVM + Silex**: A powerful smart contract environment capable of handling complex DeFi logic
4. **Scheduled Executions**: Protocol-level cron jobs enabling MEV-resistant operations
5. **BlockDAG Architecture**: 5-second block times with high throughput (2500+ TPS theoretical)

---

## 2. Protocol Architecture

### 2.1 Smart Contracts

The protocol consists of six core smart contracts:

| Contract | Language | Purpose |
|----------|----------|---------|
| `VaultEngine.slx` | Silex | Core lending: deposit, borrow, repay, withdraw, liquidate |
| `InterestRateModel.slx` | Silex | Dynamic rate calculation with kinked model |
| `PriceOracle.slx` | Silex | Price feed with timelock mechanism |
| `xUSD.slx` | Silex | Confidential stablecoin with savings rate |
| `InsurancePool.slx` | Silex | Community-backed insurance against bad debt |
| `FlashLoan.slx` | Silex | Confidential uncollateralized flash loans |

### 2.2 System Flow

```
User Wallet
    │
    ├── 1. Deposit XEL → VaultEngine
    │      ├── Balance encrypted with Twisted ElGamal
    │      └── Vault position created (Ciphertext on-chain)
    │
    ├── 2. Borrow xUSD ← VaultEngine
    │      ├── xUSD minted as Confidential Asset
    │      ├── ZK RangeProof: collateral ≥ debt × 1.5
    │      └── 0.5% protocol fee collected
    │
    ├── 3. Repay xUSD → VaultEngine
    │      ├── xUSD burned
    │      └── Debt reduced (encrypted update)
    │
    ├── 4. Withdraw XEL ← VaultEngine
    │      ├── Health check (ZK) before withdrawal
    │      └── Collateral reduced (encrypted update)
    │
    ├── 5. Save xUSD → xUSD Savings
    │      └── Auto-yield accrues per block
    │
    ├── 6. Insurance Pool
    │      ├── Stake XEL, earn premiums
    │      └── Submit/execute claims
    │
    └── 7. Flash Loans
           └── Borrow, execute callback, repay (same TX)
```

---

## 3. Core Mechanics

### 3.1 Vault Positions

Each vault position is a `VaultSnapshot` struct stored on-chain:

```
VaultSnapshot {
    owner: Address,
    collateral_asset: Hash,
    borrow_asset: Hash,
    collateral_cipher: Ciphertext,   // Encrypted balance
    borrow_cipher: Ciphertext,       // Encrypted debt
    collateral_plain: u64,           // Decrypted (for VM logic)
    borrow_plain: u64,               // Decrypted (for VM logic)
    last_update_topo: u64,
    liquidated: bool,
    created_at: u64,
    id: u64
}
```

**Privacy design**: The `_cipher` fields store the actual encrypted amounts using XELIS native `Ciphertext` type. The `_plain` fields are used internally by the VM for health checks and liquidation logic. From a third-party perspective, the `_cipher` values are unreadable.

### 3.2 Collateral Ratio

```
Minimum Collateral Ratio: 150%
Liquidation Penalty:      5%
Protocol Fee:             0.5%

Health Factor = collateral_value × 100 / borrow_value
Liquidation at: health_factor < 150
```

### 3.3 Interest Rate Model

The protocol uses a **kinked interest rate model**, similar to Aave V2:

```
If utilization ≤ kink (80%):
    borrow_rate = base_rate + (utilization × multiplier / kink)

If utilization > kink (80%):
    borrow_rate = base_rate + multiplier + (excess × jump_multiplier / (100 - kink))
```

Where:
- `base_rate`: 0.5% APR
- `multiplier`: 10% APR (slope before kink)
- `jump_multiplier`: 50% APR (slope after kink)
- `kink`: 80% utilization

Supply rate: `borrow_rate × utilization × (1 - reserve_factor)`

### 3.4 Liquidation Mechanism

Liquidations are **MEV-resistant** through XELIS Scheduled Executions:

1. A keeper bot monitors vault health using the `is_liquidatable()` entry function
2. When a vault becomes underwater, anyone can call `liquidate()`
3. The liquidator repays the debt and receives collateral minus a 5% penalty
4. The 5% penalty is burned, reducing total supply
5. Scheduled Executions at block-end can batch liquidate multiple vaults atomically

---

## 4. xUSD — Privacy-Preserving Stablecoin

### 4.1 Design

xUSD is a **Confidential Asset** on XELIS, managed by the VaultEngine contract:

- **Minted** when users borrow against XEL collateral
- **Burned** when users repay their debt
- **All transfers are encrypted** via XELIS native Twisted ElGamal
- **No maximum supply** — fully elastic based on demand

### 4.2 Peg Mechanism

xUSD maintains its $1 peg through:

1. **Arbitrage**: Users can borrow xUSD when price > $1, or repay debt when price < $1
2. **Savings Rate**: Adjustable yield incentivizes holding or spending xUSD
3. **Overcollateralization**: Every xUSD is backed by at least $1.50 of XEL

### 4.3 Savings Rate

The xUSD Savings Rate is a **protocol-level yield** paid to xUSD depositors:

- Depositors lock xUSD in the savings contract
- Interest accrues automatically per block
- Current rate is adjustable via governance
- Allows users to earn yield on stablecoins privately

```
Example:
Deposit:      10,000 xUSD
Savings APR:  8%
Time:         30 days
Earned:       ~65.75 xUSD
Total:        10,065.75 xUSD
```

---

## 5. Key Innovations

### 5.1 MEV-Resistant Liquidations

Using XELIS **Scheduled Executions**, we can batch-process liquidations at block boundaries:

```
1. Keeper identifies underwater vaults
2. Deposits xUSD to repay debt
3. Scheduled execution at block-end:
   a. Processes all pending liquidations
   b. Sorts by health factor (worst first)
   c. Atomic execution — all or nothing
4. No front-running possible within block
```

### 5.2 Confidential Flash Loans

Flash loans that preserve privacy:

```
1. Borrow XEL or xUSD (amount encrypted)
2. Execute arbitrary contract call (callback)
3. Repay loan + 0.09% fee (same TX)
4. Amounts are encrypted at every step
```

### 5.3 Auto-Remining Loans

Users can opt-in to automatic loan repayment:

```
1. User deposits XEL and borrows xUSD
2. Auto-remine flag = true
3. Each block:
   a. Protocol checks if yield from XEL mining ≥ interest due
   b. If yes, auto-repays interest from mining rewards
   c. Position stays healthy automatically
4. User never needs to manually manage position
```

### 5.4 Insurance Pool

Community-backed protection against bad debt:

- Users stake XEL to earn insurance premiums (0.1% of all borrows)
- When a vault cannot be liquidated (e.g., oracle failure), claims can be submitted
- Claims are approved by governance/guardians
- Payouts come from the pooled stake

---

## 6. Governance

### 6.1 VLT Token

VLT is the governance token of XELIS Vault:

- **Total Supply**: 10,000,000 VLT
- **Distribution**:
  - 40% Liquidity providers (farm VLT)
  - 20% Core team (2-year vesting)
  - 15% Protocol treasury
  - 10% XELIS ecosystem fund
  - 10% Early user airdrop
  - 5% Audits & security

### 6.2 Governance Powers

| Parameter | Scope | Initial Value |
|-----------|-------|---------------|
| Min Collateral Ratio | Risk | 150% |
| Liquidation Penalty | Risk | 5% |
| Reserve Factor | Treasury | 10% |
| Base Rate | Interest | 0.5% |
| Kink | Interest | 80% |
| Multiplier | Interest | 10% |
| Jump Multiplier | Interest | 50% |
| Borrow Fee | Protocol | 0.5% |
| Insurance Premium | Insurance | 0.1% |
| Savings Rate | xUSD | Configurable |
| Asset Whitelist | Expansion | Vault vote |
| Oracle Source | Risk | Vault vote |
| Emergency Pause | Security | Guardians |

---

## 7. Revenue Model

### 7.1 Protocol Revenue

| Source | Rate | Annualized (est. $5M TVL) |
|--------|------|--------------------------|
| Borrow fees | 0.5% upfront | $25,000 |
| Interest spread | ~2% avg | $100,000 |
| Liquidation fees | 0.5% | $5,000 |
| Flash loan fees | 0.09% | $2,000 |
| **Total** | | **~$132,000** |

### 7.2 Revenue Allocation

```
Revenue → Treasury
    ├── 50% → VLT token buyback & burn
    ├── 30% → Development fund
    ├── 10% → Insurance pool
    └── 10% → XELIS ecosystem partnerships
```

---

## 8. Security

### 8.1 Risk Mitigations

| Risk | Mitigation |
|------|-----------|
| Oracle manipulation | Timelock (1h), multiple sources (future) |
| Flash loan attacks | Fee + callback verification |
| Bad debt | Insurance pool + reserve fund |
| Smart contract bugs | Open source, audit, bug bounties |
| Governance attack | Timelock on all parameter changes |
| Liquidation cascade | Gradual liquidation, Scheduled Executions |

### 8.2 Emergency Procedures

1. **Pause**: Guardians can pause borrowing/liquidations
2. **Recover**: Admin functions for extreme scenarios (timelocked)
3. **Upgrade**: Contracts are not upgradeable — new versions deployed via governance

---

## 9. Roadmap

```
Phase 1 ──── MVP (Weeks 1-6)
    Core VaultEngine (deposit/borrow/repay/withdraw)
    xUSD Confidential Asset
    Basic PriceOracle
    InterestRateModel
    Devnet → Testnet deployment

Phase 2 ──── Growth (Weeks 7-10)
    xUSD Savings Rate (auto-yield)
    MEV-resistant Liquidation Bot
    Auto-Remining Loans
    Dashboard + SDK
    Mainnet launch

Phase 3 ──── Scale (Weeks 11-16)
    Insurance Pool
    Flash Loans
    Multi-collateral support
    Forge DEX integration

Phase 4 ──── Dominance (Q3-Q4 2026)
    Cross-chain xUSD (Trocador bridge)
    Position NFTs (tradeable debt)
    Credit scores (under-collateralized)
    Full DAO governance
```

---

## 10. Conclusion

XELIS Vault is the first protocol to bring **true privacy to DeFi lending**. By building on XELIS native homomorphic encryption, we enable:

- **Confidential positions**: No one sees your collateral or debt
- **MEV-resistant operations**: Fair liquidations and order execution
- **Private stablecoin**: xUSD with encrypted balances and transfers
- **Auto-yield savings**: Earn interest without exposing your wealth
- **Community protection**: Insurance pool for peace of mind

In a world where financial privacy is increasingly valued, XELIS Vault provides the infrastructure for the next generation of decentralized lending.

---

## References

1. [XELIS Whitepaper V2](https://whitepaper.xelis.io/)
2. [XELIS BlockDAG Documentation](https://docs.xelis.io/features/scalability/blockdag)
3. [XELIS Homomorphic Encryption](https://docs.xelis.io/features/privacy/homomorphic-encryption)
4. [Silex Language Reference](https://docs.xelis.io/features/smart-contracts/silex)
5. [Aave Protocol Whitepaper](https://github.com/aave/aave-v3-core)
6. [MakerDAO DAI Documentation](https://makerdao.com/en/whitepaper/)

---

*XELIS Vault — Confidential Lending for the Privacy Era*
