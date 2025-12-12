//+------------------------------------------------------------------+
//|                                            AlphaReceiver.mq5     |
//|                        Copyright 2025, AlphaAxiom                |
//|                        https://api.alphaaxiom.com                |
//+------------------------------------------------------------------+
#property copyright "Copyright 2025, AlphaAxiom"
#property link      "https://api.alphaaxiom.com"
#property version   "1.00"
#property description "Signal Receiver for AlphaAxiom API Gateway"
#property strict

#include <Trade/Trade.mqh>

//--- Input Parameters
input string   ApiKey       = "";                                      // Your AlphaAxiom API Key
input string   GatewayUrl   = "https://oracle.axiomid.app/api/v1/signals/latest"; // API Endpoint (Oracle Cloud)
input int      PollingMs    = 5000;                                    // Poll Interval (milliseconds)
input double   RiskPercent  = 1.0;                                     // Risk % per trade
input int      MagicNumber  = 888888;                                  // Magic Number
input bool     EnableTrades = true;                                    // Enable Trade Execution

//--- Global Variables
CTrade trade;
string lastSignalId = "";
int requestTimeout = 5000;

//+------------------------------------------------------------------+
//| Expert initialization function                                     |
//+------------------------------------------------------------------+
int OnInit()
{
    // Validate API Key
    if(StringLen(ApiKey) < 10)
    {
        Print("❌ Error: Please enter a valid API Key in settings");
        return(INIT_PARAMETERS_INCORRECT);
    }
    
    // Configure trade object
    trade.SetExpertMagicNumber(MagicNumber);
    trade.SetDeviationInPoints(10);
    trade.SetTypeFilling(ORDER_FILLING_IOC);
    
    // Start polling timer
    EventSetMillisecondTimer(PollingMs);
    
    Print("✅ AlphaReceiver initialized successfully");
    Print("   Gateway: ", GatewayUrl);
    Print("   Polling: ", PollingMs, " ms");
    Print("   Trading: ", EnableTrades ? "ENABLED" : "DISABLED (View Only)");
    
    return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Timer event handler - Polls for new signals                       |
//+------------------------------------------------------------------+
void OnTimer()
{
    FetchAndProcessSignal();
}

//+------------------------------------------------------------------+
//| Main function to fetch and execute signals                        |
//+------------------------------------------------------------------+
void FetchAndProcessSignal()
{
    //--- Prepare HTTP request
    string headers = "X-API-Key: " + ApiKey + "\r\n";
    headers += "Content-Type: application/json\r\n";
    
    char postData[];
    char result[];
    string resultHeaders;
    
    //--- Send GET request
    int res = WebRequest(
        "GET",
        GatewayUrl,
        headers,
        requestTimeout,
        postData,
        result,
        resultHeaders
    );
    
    //--- Handle errors
    if(res == -1)
    {
        int err = GetLastError();
        if(err == 4060)
        {
            Print("⚠️ Error 4060: Please add URL to Tools > Options > Expert Advisors > Allow WebRequest");
            Print("   Add: ", GatewayUrl);
        }
        else
        {
            Print("⚠️ WebRequest error: ", err);
        }
        return;
    }
    
    //--- Parse response
    string response = CharArrayToString(result);
    
    if(StringLen(response) < 10)
    {
        // Empty or minimal response - no signal available
        return;
    }
    
    //--- Simple JSON parsing (no external library needed)
    string signalId = ExtractJsonValue(response, "signal_id");
    
    // Check if we already processed this signal
    if(signalId == lastSignalId || signalId == "")
    {
        return;
    }
    
    // Update last processed signal
    lastSignalId = signalId;
    
    //--- Extract signal data
    string action   = ExtractJsonValue(response, "action");
    string symbol   = ExtractJsonValue(response, "symbol");
    double price    = StringToDouble(ExtractJsonValue(response, "price"));
    double sl       = StringToDouble(ExtractJsonValue(response, "sl"));
    double tp       = StringToDouble(ExtractJsonValue(response, "tp"));
    double quantity = StringToDouble(ExtractJsonValue(response, "quantity"));
    string reason   = ExtractJsonValue(response, "reason");
    
    //--- Log received signal
    Print("📡 New Signal Received:");
    Print("   ID: ", signalId);
    Print("   Action: ", action);
    Print("   Symbol: ", symbol);
    Print("   Qty: ", quantity);
    Print("   SL: ", sl, " | TP: ", tp);
    Print("   Reason: ", reason);
    
    //--- Execute trade if enabled
    if(!EnableTrades)
    {
        Print("ℹ️ Trading disabled. Signal logged but not executed.");
        return;
    }
    
    ExecuteSignal(action, symbol, quantity, sl, tp, reason);
}

//+------------------------------------------------------------------+
//| Execute the trading signal                                         |
//+------------------------------------------------------------------+
void ExecuteSignal(string action, string symbol, double quantity, double sl, double tp, string reason)
{
    //--- Normalize symbol (some brokers add suffix like .m)
    string tradingSymbol = symbol;
    if(!SymbolSelect(symbol, true))
    {
        // Try with common suffixes
        string suffixes[] = {"m", ".m", "_m", "."};
        bool found = false;
        for(int i = 0; i < ArraySize(suffixes); i++)
        {
            tradingSymbol = symbol + suffixes[i];
            if(SymbolSelect(tradingSymbol, true))
            {
                found = true;
                break;
            }
        }
        if(!found)
        {
            Print("❌ Symbol not found: ", symbol);
            return;
        }
    }
    
    //--- Calculate volume based on account if quantity is 0
    if(quantity <= 0)
    {
        quantity = CalculateLotSize(tradingSymbol, sl);
    }
    
    //--- Normalize lot size
    double minLot = SymbolInfoDouble(tradingSymbol, SYMBOL_VOLUME_MIN);
    double maxLot = SymbolInfoDouble(tradingSymbol, SYMBOL_VOLUME_MAX);
    double lotStep = SymbolInfoDouble(tradingSymbol, SYMBOL_VOLUME_STEP);
    
    quantity = MathMax(minLot, MathMin(maxLot, NormalizeDouble(quantity, 2)));
    quantity = MathRound(quantity / lotStep) * lotStep;
    
    //--- Execute based on action
    bool success = false;
    string comment = "AlphaAxiom: " + StringSubstr(reason, 0, 20);
    
    if(action == "BUY")
    {
        success = trade.Buy(quantity, tradingSymbol, 0, sl, tp, comment);
        if(success)
            Print("🟢 BUY Executed: ", tradingSymbol, " | Qty: ", quantity, " | Ticket: ", trade.ResultOrder());
    }
    else if(action == "SELL")
    {
        success = trade.Sell(quantity, tradingSymbol, 0, sl, tp, comment);
        if(success)
            Print("🔴 SELL Executed: ", tradingSymbol, " | Qty: ", quantity, " | Ticket: ", trade.ResultOrder());
    }
    else
    {
        Print("ℹ️ Action: ", action, " - No trade executed");
    }
    
    if(!success && (action == "BUY" || action == "SELL"))
    {
        Print("❌ Trade failed: ", trade.ResultRetcodeDescription());
    }
}

//+------------------------------------------------------------------+
//| Calculate lot size based on risk percentage                        |
//+------------------------------------------------------------------+
double CalculateLotSize(string symbol, double stopLoss)
{
    double balance = AccountInfoDouble(ACCOUNT_BALANCE);
    double riskAmount = balance * (RiskPercent / 100.0);
    
    double tickValue = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE);
    double tickSize = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_SIZE);
    double currentPrice = SymbolInfoDouble(symbol, SYMBOL_BID);
    
    if(stopLoss <= 0 || tickValue <= 0)
    {
        // Default to minimum lot if can't calculate
        return SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
    }
    
    double stopDistance = MathAbs(currentPrice - stopLoss);
    double stopTicks = stopDistance / tickSize;
    
    double lotSize = riskAmount / (stopTicks * tickValue);
    
    return lotSize;
}

//+------------------------------------------------------------------+
//| Simple JSON value extractor (no external library needed)           |
//+------------------------------------------------------------------+
string ExtractJsonValue(string json, string key)
{
    string searchKey = "\"" + key + "\":";
    int keyStart = StringFind(json, searchKey);
    
    if(keyStart < 0)
        return "";
    
    int valueStart = keyStart + StringLen(searchKey);
    
    // Skip whitespace
    while(valueStart < StringLen(json) && StringGetCharacter(json, valueStart) == ' ')
        valueStart++;
    
    int valueEnd;
    ushort firstChar = StringGetCharacter(json, valueStart);
    
    if(firstChar == '"')
    {
        // String value
        valueStart++;
        valueEnd = StringFind(json, "\"", valueStart);
    }
    else
    {
        // Number or boolean
        valueEnd = valueStart;
        while(valueEnd < StringLen(json))
        {
            ushort c = StringGetCharacter(json, valueEnd);
            if(c == ',' || c == '}' || c == ']' || c == ' ' || c == '\n')
                break;
            valueEnd++;
        }
    }
    
    if(valueEnd <= valueStart)
        return "";
    
    return StringSubstr(json, valueStart, valueEnd - valueStart);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                   |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    EventKillTimer();
    Print("AlphaReceiver stopped. Reason: ", reason);
}

//+------------------------------------------------------------------+
//| OnTick - Not used, using OnTimer for polling                       |
//+------------------------------------------------------------------+
void OnTick()
{
    // Not used - we poll on timer to avoid blocking on every tick
}
