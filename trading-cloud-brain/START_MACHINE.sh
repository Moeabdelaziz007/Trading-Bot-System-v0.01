#!/bin/bash
# ============================================
# 💰 AXIOM MONEY MACHINE - START SCRIPT
# ============================================
# One-click startup for the Axiom Alpha system
#
# This script:
#   1. Starts the background engine (24/7 trading)
#   2. Launches the voice interface (optional)
#
# Usage: ./START_MACHINE.sh
# ============================================

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║     █████╗ ██╗  ██╗██╗ ██████╗ ███╗   ███╗                   ║"
echo "║    ██╔══██╗╚██╗██╔╝██║██╔═══██╗████╗ ████║                   ║"
echo "║    ███████║ ╚███╔╝ ██║██║   ██║██╔████╔██║                   ║"
echo "║    ██╔══██║ ██╔██╗ ██║██║   ██║██║╚██╔╝██║                   ║"
echo "║    ██║  ██║██╔╝ ██╗██║╚██████╔╝██║ ╚═╝ ██║                   ║"
echo "║    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝     ╚═╝                   ║"
echo "║                                                              ║"
echo "║              💰  MONEY MACHINE LAUNCHER  💰                  ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if we're in the right directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found. Please install Python 3.10+${NC}"
    exit 1
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  No .env file found. Creating template...${NC}"
    cat > .env << 'EOF'
# Axiom Alpha Configuration
GROQ_API_KEY=your_groq_api_key_here
BYBIT_API_KEY=your_bybit_api_key
BYBIT_API_SECRET=your_bybit_secret
MT5_BRIDGE_URL=http://localhost:5000
MT5_AUTH_TOKEN=your_mt5_token
PERPLEXITY_API_KEY=your_perplexity_key
EOF
    echo -e "${YELLOW}📝 Please edit .env with your API keys${NC}"
fi

# Parse arguments
MODE="demo"
VOICE="false"

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --live) MODE="live" ;;
        --voice) VOICE="true" ;;
        --help) 
            echo "Usage: $0 [--live] [--voice]"
            echo "  --live   Enable real trading (default: demo mode)"
            echo "  --voice  Start voice interface"
            exit 0
            ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
    shift
done

echo -e "${GREEN}🚀 Starting Axiom Alpha...${NC}"
echo ""

# Start background engine
if [ "$MODE" == "demo" ]; then
    echo -e "${YELLOW}🎮 Running in DEMO MODE (no real trades)${NC}"
    python3 main_engine.py --demo &
    ENGINE_PID=$!
else
    echo -e "${RED}⚡ LIVE TRADING MODE${NC}"
    read -p "Are you sure you want to enable live trading? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Cancelled. Starting in demo mode..."
        python3 main_engine.py --demo &
        ENGINE_PID=$!
    else
        python3 main_engine.py &
        ENGINE_PID=$!
    fi
fi

echo -e "${GREEN}✅ Engine started (PID: $ENGINE_PID)${NC}"

# Optionally start voice interface
if [ "$VOICE" == "true" ]; then
    echo ""
    echo -e "${GREEN}🎙️ Starting Voice Cockpit...${NC}"
    python3 axiom_cli.py
else
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Engine running in background. Options:"
    echo ""
    echo "  • View logs:    tail -f axiom_engine.log"
    echo "  • Voice mode:   python3 axiom_cli.py"
    echo "  • Stop engine:  kill $ENGINE_PID"
    echo ""
    echo "Press Ctrl+C to stop the engine..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Wait for engine
    wait $ENGINE_PID
fi

echo ""
echo -e "${GREEN}👋 Axiom Alpha shutdown complete.${NC}"
