#!/bin/bash
set -e

echo "=== XELIS Vault — Contract Deployment ==="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

DAEMON_URL=${DAEMON_URL:-"http://127.0.0.1:18081"}
WALLET_URL=${WALLET_URL:-"http://127.0.0.1:18082"}
DEV_MODE=${DEV_MODE:-"devnet"}

echo -e "${BLUE}[INFO]${NC} Daemon: $DAEMON_URL"
echo -e "${BLUE}[INFO]${NC} Wallet: $WALLET_URL"
echo -e "${BLUE}[INFO]${NC} Mode: $DEV_MODE"
echo ""

# Function to call wallet RPC
wallet_rpc() {
    local method=$1
    shift
    local params=$@
    curl -s -X POST "$WALLET_URL/json_rpc" \
        -H "Content-Type: application/json" \
        -d "{\"jsonrpc\":\"2.0\",\"id\":\"1\",\"method\":\"$method\",\"params\":{$params}}"
}

# Step 1: Deploy xUSD Contract
echo -e "${YELLOW}[1/4]${NC} Deploying xUSD Savings Stablecoin..."
XUSD_RESULT=$(wallet_rpc "deploy_contract" \
    "\"name\":\"xUSD\",\"path\":\"../contracts/xusd/xUSD.slx\"")
echo "$XUSD_RESULT" | python3 -m json.tool 2>/dev/null || echo "$XUSD_RESULT"
XUSD_CONTRACT=$(echo "$XUSD_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('result',{}).get('contract',''))" 2>/dev/null || echo "")
echo -e "${GREEN}[✓]${NC} xUSD deployed"
echo ""

# Step 2: Deploy PriceOracle
echo -e "${YELLOW}[2/4]${NC} Deploying PriceOracle..."
ORACLE_RESULT=$(wallet_rpc "deploy_contract" \
    "\"name\":\"PriceOracle\",\"path\":\"../contracts/oracle/PriceOracle.slx\"")
echo "$ORACLE_RESULT" | python3 -m json.tool 2>/dev/null || echo "$ORACLE_RESULT"
ORACLE_CONTRACT=$(echo "$ORACLE_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('result',{}).get('contract',''))" 2>/dev/null || echo "")
echo -e "${GREEN}[✓]${NC} PriceOracle deployed"
echo ""

# Step 3: Deploy InterestRateModel
echo -e "${YELLOW}[3/4]${NC} Deploying InterestRateModel..."
INTEREST_RESULT=$(wallet_rpc "deploy_contract" \
    "\"name\":\"InterestRateModel\",\"path\":\"../contracts/interest/InterestRateModel.slx\"")
echo "$INTEREST_RESULT" | python3 -m json.tool 2>/dev/null || echo "$INTEREST_RESULT"
INTEREST_CONTRACT=$(echo "$INTEREST_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('result',{}).get('contract',''))" 2>/dev/null || echo "")
echo -e "${GREEN}[✓]${NC} InterestRateModel deployed"
echo ""

# Step 4: Deploy VaultEngine
echo -e "${YELLOW}[4/4]${NC} Deploying VaultEngine..."
VAULT_RESULT=$(wallet_rpc "deploy_contract" \
    "\"name\":\"VaultEngine\",\"path\":\"../contracts/vault/VaultEngine.slx\"")
echo "$VAULT_RESULT" | python3 -m json.tool 2>/dev/null || echo "$VAULT_RESULT"
VAULT_CONTRACT=$(echo "$VAULT_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('result',{}).get('contract',''))" 2>/dev/null || echo "")
echo -e "${GREEN}[✓]${NC} VaultEngine deployed"
echo ""

echo "=== Deployment Summary ==="
echo -e "${GREEN}xUSD:${NC}          $XUSD_CONTRACT"
echo -e "${GREEN}Oracle:${NC}        $ORACLE_CONTRACT"
echo -e "${GREEN}Interest:${NC}      $INTEREST_CONTRACT"
echo -e "${GREEN}VaultEngine:${NC}   $VAULT_CONTRACT"
echo ""

# Save to .env
cat > ../.env << EOF
DAEMON_URL=$DAEMON_URL
WALLET_URL=$WALLET_URL
VAULT_CONTRACT=$VAULT_CONTRACT
XUSD_ASSET=$XUSD_CONTRACT
ORACLE_CONTRACT=$ORACLE_CONTRACT
INTEREST_CONTRACT=$INTEREST_CONTRACT
EOF

echo -e "${GREEN}Configuration saved to .env${NC}"
echo ""
echo "Next: Initialize xUSD in VaultEngine:"
echo "  Call VaultEngine.set_xusd_asset(\"$XUSD_CONTRACT\")"
echo ""
echo "Then: Set XEL price in Oracle:"
echo "  Call PriceOracle.set_price(\"XEL\", <price>)"
