#!/bin/bash
set -e

echo "=== XELIS Vault — Full Ecosystem Deployment ==="
echo ""

source ../.env 2>/dev/null || true

DAEMON_URL=${DAEMON_URL:-"http://127.0.0.1:18081"}
WALLET_URL=${WALLET_URL:-"http://127.0.0.1:18082"}

wallet_rpc() {
    local method=$1
    shift
    local params=$@
    curl -s -X POST "$WALLET_URL/json_rpc" \
        -H "Content-Type: application/json" \
        -d "{\"jsonrpc\":\"2.0\",\"id\":\"1\",\"method\":\"$method\",\"params\":{$params}}"
}

# Deploy InsurancePool
echo "[1/3] Deploying InsurancePool..."
INSURANCE_RESULT=$(wallet_rpc "deploy_contract" \
    "\"name\":\"InsurancePool\",\"path\":\"../contracts/insurance/InsurancePool.slx\"")
INSURANCE_CONTRACT=$(echo "$INSURANCE_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('result',{}).get('contract',''))" 2>/dev/null || echo "")
echo "InsurancePool: $INSURANCE_CONTRACT"

# Deploy FlashLoan
echo "[2/3] Deploying FlashLoan..."
FLASH_RESULT=$(wallet_rpc "deploy_contract" \
    "\"name\":\"FlashLoan\",\"path\":\"../contracts/flashloan/FlashLoan.slx\"")
FLASH_CONTRACT=$(echo "$FLASH_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('result',{}).get('contract',''))" 2>/dev/null || echo "")
echo "FlashLoan: $FLASH_CONTRACT"

echo ""
echo "=== Full Deployment Complete ==="
echo "InsurancePool: $INSURANCE_CONTRACT"
echo "FlashLoan: $FLASH_CONTRACT"

cat >> ../.env << EOF
INSURANCE_CONTRACT=$INSURANCE_CONTRACT
FLASHLOAN_CONTRACT=$FLASH_CONTRACT
EOF
