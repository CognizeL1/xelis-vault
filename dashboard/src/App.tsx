import React, { useState, useEffect, useCallback } from 'react';
import { XelisVaultSDK, VaultSnapshot, HealthInfo, SavingsBalance } from '../../sdk/src/index';

const CONFIG = {
    daemonUrl: process.env.REACT_APP_DAEMON_URL || 'http://127.0.0.1:18081',
    walletUrl: process.env.REACT_APP_WALLET_URL || 'http://127.0.0.1:18082',
    vaultContract: process.env.REACT_APP_VAULT_CONTRACT || '',
    xusdAsset: process.env.REACT_APP_XUSD_ASSET || '',
    oracleContract: process.env.REACT_APP_ORACLE_CONTRACT || '',
    interestContract: process.env.REACT_APP_INTEREST_CONTRACT || '',
    insuranceContract: process.env.REACT_APP_INSURANCE_CONTRACT || '',
    flashLoanContract: process.env.REACT_APP_FLASHLOAN_CONTRACT || '',
};

function App() {
    const [sdk] = useState(() => new XelisVaultSDK(CONFIG));
    const [address, setAddress] = useState('');
    const [vaults, setVaults] = useState<{ id: string; health: HealthInfo }[]>([]);
    const [savings, setSavings] = useState<SavingsBalance | null>(null);
    const [price, setPrice] = useState('0');
    const [tab, setTab] = useState<'vault' | 'savings' | 'stats'>('vault');
    const [depositAmount, setDepositAmount] = useState('');
    const [borrowAmount, setBorrowAmount] = useState('');
    const [selectedVault, setSelectedVault] = useState<string | null>(null);

    const loadData = useCallback(async () => {
        if (!address) return;
        try {
            const p = await sdk.getOraclePrice(CONFIG.xusdAsset);
            setPrice(p);
        } catch { }
    }, [address, sdk]);

    useEffect(() => {
        loadData();
        const interval = setInterval(loadData, 15000);
        return () => clearInterval(interval);
    }, [loadData]);

    const handleDeposit = async () => {
        if (!depositAmount || !address) return;
        try {
            const result = await sdk.callWallet('contract_call', {
                contract: CONFIG.vaultContract,
                entry: 'deposit',
                params: [CONFIG.xusdAsset, depositAmount]
            });
            console.log('Deposit result:', result);
            setDepositAmount('');
            loadData();
        } catch (err) {
            console.error('Deposit error:', err);
        }
    };

    const handleBorrow = async (vaultId: string) => {
        if (!borrowAmount) return;
        try {
            const result = await sdk.callWallet('contract_call', {
                contract: CONFIG.vaultContract,
                entry: 'borrow',
                params: [vaultId, borrowAmount]
            });
            console.log('Borrow result:', result);
            setBorrowAmount('');
            loadData();
        } catch (err) {
            console.error('Borrow error:', err);
        }
    };

    const VaultTab = () => (
        <div>
            <h2>Vault Dashboard</h2>
            <div>
                <h3>Deposit XEL</h3>
                <input
                    type="text"
                    value={depositAmount}
                    onChange={e => setDepositAmount(e.target.value)}
                    placeholder="Amount (atomic units)"
                />
                <button onClick={handleDeposit}>Deposit</button>
            </div>
            <div>
                <h3>Borrow xUSD</h3>
                <input
                    type="text"
                    value={borrowAmount}
                    onChange={e => setBorrowAmount(e.target.value)}
                    placeholder="Amount (atomic units)"
                />
                <input
                    type="text"
                    value={selectedVault || ''}
                    onChange={e => setSelectedVault(e.target.value)}
                    placeholder="Vault ID"
                />
                <button onClick={() => handleBorrow(selectedVault || '')}>Borrow</button>
            </div>
            <div>
                <h3>Your Vaults</h3>
                {vaults.length === 0 ? (
                    <p>No vaults found. Deposit XEL to create one.</p>
                ) : (
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Collateral</th>
                                <th>Borrow</th>
                                <th>Health</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {vaults.map(v => (
                                <tr key={v.id}>
                                    <td>{v.id}</td>
                                    <td>{v.health.collateralValue}</td>
                                    <td>{v.health.borrowValue}</td>
                                    <td style={{ color: v.health.health < 150 ? 'red' : 'green' }}>
                                        {v.health.health}%
                                    </td>
                                    <td>{v.health.isLiquidatable ? '⚠️ LIQUIDATABLE' : 'Healthy'}</td>
                                    <td>
                                        <button onClick={() => handleBorrow(v.id)}>Borrow</button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
            <div>
                <h3>Interest Rates</h3>
                <p>XEL Price: ${(Number(price) / 100_000_000).toFixed(4)}</p>
                <p>Current Utilization: --</p>
                <p>Borrow APR: --</p>
                <p>Supply APR: --</p>
            </div>
        </div>
    );

    const SavingsTab = () => (
        <div>
            <h2>xUSD Savings</h2>
            {savings ? (
                <div>
                    <p>Deposited: {savings.amount} xUSD</p>
                    <p>Accumulated Yield: {savings.accumulated} xUSD</p>
                    <p>Total: {String(Number(savings.amount) + Number(savings.accumulated))} xUSD</p>
                </div>
            ) : (
                <p>Connect wallet to see savings</p>
            )}
            <div>
                <h3>Deposit to Savings</h3>
                <input type="text" placeholder="Amount" />
                <button>Deposit</button>
            </div>
            <div>
                <h3>Withdraw from Savings</h3>
                <input type="text" placeholder="Amount" />
                <button>Withdraw</button>
            </div>
        </div>
    );

    const StatsTab = () => (
        <div>
            <h2>Protocol Stats</h2>
            <p>Total Value Locked: --</p>
            <p>Total Borrowed: --</p>
            <p>Total Insurance Staked: --</p>
            <p>xUSD Supply: --</p>
            <p>Active Vaults: --</p>
            <p>Current Price: ${(Number(price) / 100_000_000).toFixed(4)}</p>
        </div>
    );

    return (
        <div>
            <h1>XELIS Vault</h1>
            <p>Confidential Lending Protocol</p>
            <div>
                <input
                    type="text"
                    value={address}
                    onChange={e => setAddress(e.target.value)}
                    placeholder="Your XELIS address"
                />
                <button onClick={loadData}>Connect</button>
            </div>
            <nav>
                <button onClick={() => setTab('vault')} style={{ fontWeight: tab === 'vault' ? 'bold' : 'normal' }}>
                    Vault
                </button>
                <button onClick={() => setTab('savings')} style={{ fontWeight: tab === 'savings' ? 'bold' : 'normal' }}>
                    Savings
                </button>
                <button onClick={() => setTab('stats')} style={{ fontWeight: tab === 'stats' ? 'bold' : 'normal' }}>
                    Stats
                </button>
            </nav>
            {tab === 'vault' && <VaultTab />}
            {tab === 'savings' && <SavingsTab />}
            {tab === 'stats' && <StatsTab />}
        </div>
    );
}

export default App;
