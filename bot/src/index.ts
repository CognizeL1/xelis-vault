import { XelisVaultSDK } from '../../sdk/src/index';

interface BotConfig {
    daemonUrl: string;
    walletUrl: string;
    walletAddress: string;
    vaultContract: string;
    xusdAsset: string;
    oracleContract: string;
    interestContract: string;
    insuranceContract: string;
    flashLoanContract: string;
    checkIntervalMs: number;
    minHealthForLiquidation: number;
}

const DEFAULT_CONFIG: BotConfig = {
    daemonUrl: 'http://127.0.0.1:18081',
    walletUrl: 'http://127.0.0.1:18082',
    walletAddress: '',
    vaultContract: '',
    xusdAsset: '',
    oracleContract: '',
    interestContract: '',
    insuranceContract: '',
    flashLoanContract: '',
    checkIntervalMs: 30_000,
    minHealthForLiquidation: 150
};

class LiquidationBot {
    private sdk: XelisVaultSDK;
    private config: BotConfig;
    private running: boolean = false;
    private checkedVaults: Set<string> = new Set();

    constructor(config: Partial<BotConfig> = {}) {
        this.config = { ...DEFAULT_CONFIG, ...config };
        this.sdk = new XelisVaultSDK({
            daemonUrl: this.config.daemonUrl,
            walletUrl: this.config.walletUrl,
            vaultContract: this.config.vaultContract,
            xusdAsset: this.config.xusdAsset,
            oracleContract: this.config.oracleContract,
            interestContract: this.config.interestContract,
            insuranceContract: this.config.insuranceContract,
            flashLoanContract: this.config.flashLoanContract,
        });
    }

    async start(): Promise<void> {
        this.running = true;
        console.log('[LiquidationBot] Started — checking every', this.config.checkIntervalMs, 'ms');
        while (this.running) {
            try {
                await this.checkVaults();
            } catch (err) {
                console.error('[LiquidationBot] Error during check:', err);
            }
            await new Promise(r => setTimeout(r, this.config.checkIntervalMs));
        }
    }

    stop(): void {
        this.running = false;
        console.log('[LiquidationBot] Stopped');
    }

    private async checkVaults(): Promise<void> {
        const price = await this.sdk.getOraclePrice(this.config.walletAddress);
        console.log(`[LiquidationBot] XEL price: ${price}`);

        const height = await this.sdk.getDaemonInfo();
        const topo = height?.result?.topoheight ?? 0;
        const startId = topo > 1000 ? topo - 1000 : 1;

        let liquidated = 0;
        for (let id = startId; id <= topo; id++) {
            const vaultKey = `vault_${id}`;
            if (this.checkedVaults.has(vaultKey)) continue;

            try {
                const liq = await this.sdk.isLiquidatable(String(id));
                if (liq) {
                    console.log(`[LiquidationBot] Vault ${id} is liquidatable! Attempting liquidation...`);
                    const result = await this.sdk.callWallet('contract_call', {
                        contract: this.config.vaultContract,
                        entry: 'liquidate',
                        params: [String(id)]
                    });
                    console.log(`[LiquidationBot] Liquidated vault ${id}:`, result);
                    liquidated++;
                }
            } catch (err) {
                // vault doesn't exist or error
            }
            this.checkedVaults.add(vaultKey);
        }

        if (liquidated > 0) {
            console.log(`[LiquidationBot] Liquidated ${liquidated} vault(s)`);
        }
    }
}

const config: Partial<BotConfig> = {
    daemonUrl: process.env.DAEMON_URL || 'http://127.0.0.1:18081',
    walletUrl: process.env.WALLET_URL || 'http://127.0.0.1:18082',
    walletAddress: process.env.WALLET_ADDRESS || '',
    vaultContract: process.env.VAULT_CONTRACT || '',
    xusdAsset: process.env.XUSD_ASSET || '',
    oracleContract: process.env.ORACLE_CONTRACT || '',
    interestContract: process.env.INTEREST_CONTRACT || '',
    insuranceContract: process.env.INSURANCE_CONTRACT || '',
    flashLoanContract: process.env.FLASHLOAN_CONTRACT || '',
    checkIntervalMs: parseInt(process.env.CHECK_INTERVAL || '30000'),
};

const bot = new LiquidationBot(config);
bot.start().catch(console.error);

process.on('SIGINT', () => { bot.stop(); process.exit(0); });
process.on('SIGTERM', () => { bot.stop(); process.exit(0); });
