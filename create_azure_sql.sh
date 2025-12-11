#!/bin/bash
set -e

# create_azure_sql.sh
# Purpose: Create a minimal, cost-effective Azure SQL Database via Azure CLI.
# Target: Lowest Tier (Basic 5 DTU or Serverless).
# Output: Secure Connection String.
# Prerequisite: Logged in via `az login`

# Configuration
RESOURCE_GROUP="AxiomTradingResourceGroup"
LOCATION="eastus" # Cheapest region usually
SERVER_NAME="axiom-sql-server-$(date +%s)" # Unique name
DB_NAME="axiom_trading_db"
ADMIN_USER="axiomadmin"
# Generate a random secure password
ADMIN_PASS="Ax$(openssl rand -base64 12 | tr -dc 'a-zA-Z0-9')!"

echo ">> Starting Azure SQL Provisioning..."
echo ">> Resource Group: $RESOURCE_GROUP"
echo ">> Location: $LOCATION"
echo ">> Server Name: $SERVER_NAME"

# 1. Create Resource Group
echo ">> Creating Resource Group..."
az group create --name $RESOURCE_GROUP --location $LOCATION --output none

# 2. Create SQL Server
echo ">> Creating SQL Server (this may take a few minutes)..."
az sql server create \
    --name $SERVER_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --admin-user $ADMIN_USER \
    --admin-password $ADMIN_PASS \
    --enable-public-network true \
    --output none

# 3. Configure Firewall (Allow Azure Services + Current IP)
echo ">> Configuring Firewall..."
# Allow Azure services (internal access)
az sql server firewall-rule create \
    --resource-group $RESOURCE_GROUP \
    --server $SERVER_NAME \
    --name AllowAzureServices \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 0.0.0.0 \
    --output none

# 4. Create Database (Basic Tier - Lowest Cost: ~5 USD/month)
# We use 'Basic' SKU. 'S0' is standard but more expensive. Serverless is 'GeneralPurpose' with 'ComputeModel=Serverless' but minimums might be higher than Basic.
# Basic 5 DTU is the absolute floor for paid tiers.
echo ">> Creating SQL Database (Tier: Basic)..."
az sql db create \
    --resource-group $RESOURCE_GROUP \
    --server $SERVER_NAME \
    --name $DB_NAME \
    --service-objective Basic \
    --output none

# 5. Output Connection String
echo ">> Provisioning Complete!"
echo "========================================================"
echo "SERVER: $SERVER_NAME.database.windows.net"
echo "DATABASE: $DB_NAME"
echo "USER: $ADMIN_USER"
echo "PASSWORD: $ADMIN_PASS"
echo "========================================================"
echo "CONNECTION STRING (ODBC):"
echo "Driver={ODBC Driver 17 for SQL Server};Server=tcp:$SERVER_NAME.database.windows.net,1433;Database=$DB_NAME;Uid=$ADMIN_USER;Pwd=$ADMIN_PASS;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
echo "========================================================"
echo "⚠️  SAVE THIS PASSWORD SECURELY. IT WILL NOT BE SHOWN AGAIN."
