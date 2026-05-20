#!/bin/bash
set -e

echo "=== XELIS Vault — Devnet Setup ==="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check for xelis CLI
if ! command -v xelis_daemon &> /dev/null; then
    echo -e "${BLUE}[INFO]${NC} xelis_daemon not found. Setting up local environment..."
    echo "Make sure XELIS binaries are in your PATH."
    echo "Download from: https://github.com/xelis-project/xelis-blockchain/releases"
    exit 1
fi

echo -e "${GREEN}[✓]${NC} xelis_daemon found"

# Create data directory
mkdir -p data

# Generate wallet if needed
if [ ! -f data/wallet.dat ]; then
    echo -e "${BLUE}[INFO]${NC} Generating devnet wallet..."
    xelis_wallet --datadir data --generate
    echo -e "${GREEN}[✓]${NC} Wallet generated"
fi

echo ""
echo "=== Next Steps ==="
echo "1. Start devnet daemon:"
echo "   xelis_daemon --datadir data --devnet"
echo ""
echo "2. In another terminal, start wallet daemon:"
echo "   xelis_wallet --datadir data --daemon http://127.0.0.1:18081"
echo ""
echo "3. Deploy contracts:"
echo "   ./scripts/deploy.sh"
echo ""
echo -e "${GREEN}Ready!${NC}"
