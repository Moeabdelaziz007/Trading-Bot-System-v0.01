#!/bin/bash

# Cleanup script for Trading System workspace
# Removes artifacts from previous AI agent ("Roo Code") crash

echo "=== Trading System Workspace Cleanup Script ==="
echo "Removing artifacts from previous AI agent ('Roo Code') crash..."
echo

# 1. Kill any lingering Node.js processes related to VS Code extensions or the previous agent
echo "1. Killing lingering Node.js processes..."
NODE_PROCESSES=$(ps aux | grep -i "node" | grep -i "vscode\|roo\|extension" | grep -v grep | awk '{print $2}')
if [ ! -z "$NODE_PROCESSES" ]; then
    echo "Found Node.js processes: $NODE_PROCESSES"
    kill -9 $NODE_PROCESSES 2>/dev/null || echo "Some processes may have already terminated"
else
    echo "No suspicious Node.js processes found"
fi
echo

# 2. Remove hidden directories created by AI agents
echo "2. Removing AI agent directories..."
if [ -d ".roo" ]; then
    echo "Removing .roo directory..."
    rm -rf .roo
else
    echo ".roo directory not found"
fi

# Check for other potential AI agent directories
for dir in .cline .shadow .ai_agent .mcp; do
    if [ -d "$dir" ]; then
        echo "Removing $dir directory..."
        rm -rf "$dir"
    fi
done
echo

# 3. Clean temporary directories
echo "3. Cleaning temporary directories..."
if [ -d "trading-cloud-brain/.wrangler/tmp" ]; then
    echo "Cleaning trading-cloud-brain/.wrangler/tmp..."
    rm -rf trading-cloud-brain/.wrangler/tmp/*
else
    echo "trading-cloud-brain/.wrangler/tmp directory not found"
fi
echo

# 4. Reset file permissions
echo "4. Resetting file permissions..."
# Ensure current user has full access to the workspace
chmod -R u+rwx . 2>/dev/null || echo "Some files could not be chmodded (possibly due to ownership)"
echo

# 5. Clean Python cache directories
echo "5. Cleaning Python cache directories..."
if [ -d ".mypy_cache" ]; then
    echo "Removing .mypy_cache..."
    rm -rf .mypy_cache
fi

if [ -d ".venv" ]; then
    echo "Removing .venv..."
    rm -rf .venv
fi

# Find and remove __pycache__ directories
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || echo "Some __pycache__ directories could not be removed"
echo

# 6. Clean Node.js modules and lock files
echo "6. Cleaning Node.js artifacts..."
# Find and remove node_modules directories
find . -type d -name "node_modules" -prune -exec rm -rf {} + 2>/dev/null || echo "Some node_modules directories could not be removed"

# Find and remove package-lock.json and yarn.lock files
find . -type f \( -name "package-lock.json" -o -name "yarn.lock" \) -exec rm -f {} + 2>/dev/null || echo "Some lock files could not be removed"
echo

# 7. Check for any remaining lock files
echo "7. Checking for remaining lock files..."
LOCK_FILES=$(find . -type f \( -name "*.lock" -o -name "*.pid" \) -not -path "./frontend_legacy/*" -not -path "./frontend/*")
if [ ! -z "$LOCK_FILES" ]; then
    echo "Found lock files:"
    echo "$LOCK_FILES"
    echo "Removing lock files..."
    echo "$LOCK_FILES" | xargs rm -f
else
    echo "No additional lock files found"
fi
echo

echo "=== Cleanup Complete ==="
echo "The workspace has been cleaned of artifacts from the previous AI agent."
echo "You can now restart your development environment."