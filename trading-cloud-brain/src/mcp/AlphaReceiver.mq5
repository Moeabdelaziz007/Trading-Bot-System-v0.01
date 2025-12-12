//+------------------------------------------------------------------+
//|                                            AlphaReceiver.mq5     |
//|                            AlphaAxiom - Cloud Signal Bridge      |
//|                                   https://alphaaxiom.com         |
//+------------------------------------------------------------------+
#property copyright "AlphaAxiom"
#property link      "https://alphaaxiom.com"
#property version   "1.00"
#property strict

#include <Trade\Trade.mqh>

//--- Input Parameters
input string   API_URL       = "https://your-cloudflare-worker.workers.dev/api/v1/signals/latest";
input string   API_KEY       = "YOUR_API_KEY_HERE";  // Get from AlphaAxiom Dashboard
input int      POLL_INTERVAL = 5;                    // Seconds between API checks
input double   LOT_SIZE      = 0.01;                 // Default lot size
input int      SLIPPAGE      = 10;                   // Max slippage in points
input bool     AUTO_EXECUTE  = true;                 // Execute trades automatically

//--- Global Variables
CTrade         trade;
string         lastSignalId  = "";
datetime       lastCheckTime = 0;

//+------------------------------------------------------------------+
//| Expert initialization function                                     |
//+------------------------------------------------------------------+
int OnInit()
{
   //--- Validate API URL is whitelisted
   Print("🚀 AlphaReceiver v1.0 Initializing...");
   Print("📡 API Endpoint: ", API_URL);
   
   //--- Set timer for polling
   EventSetTimer(POLL_INTERVAL);
   
   //--- Configure trade settings
   trade.SetExpertMagicNumber(123456);
   trade.SetDeviationInPoints(SLIPPAGE);
   trade.SetTypeFilling(ORDER_FILLING_IOC);
   
   Print("✅ AlphaReceiver Ready! Polling every ", POLL_INTERVAL, " seconds.");
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                   |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   EventKillTimer();
   Print("🛑 AlphaReceiver Stopped.");
}

//+------------------------------------------------------------------+
//| Timer function - Polls API for new signals                         |
//+------------------------------------------------------------------+
void OnTimer()
{
   FetchSignal();
}

//+------------------------------------------------------------------+
//| Fetch Signal from Cloud API                                        |
//+------------------------------------------------------------------+
void FetchSignal()
{
   string headers = "Content-Type: application/json\r\nX-API-Key: " + API_KEY + "\r\n";
   char   post[];
   char   result[];
   string resultHeaders;
   
   //--- Make GET request
   int res = WebRequest(
      "GET",           // Method
      API_URL,         // URL (must be whitelisted in MT5 Options)
      headers,         // Headers
      5000,            // Timeout (5 seconds)
      post,            // POST data (empty for GET)
      result,          // Response body
      resultHeaders    // Response headers
   );
   
   //--- Check response
   if(res == -1)
   {
      int error = GetLastError();
      if(error == 4014) // ERR_WEBREQUEST_INVALID_ADDRESS
         Print("❌ ERROR: URL not whitelisted! Add to Tools > Options > Expert Advisors");
      else
         Print("❌ WebRequest Error: ", error);
      return;
   }
   
   if(res != 200)
   {
      Print("⚠️ API returned status: ", res);
      return;
   }
   
   //--- Parse JSON response
   string response = CharArrayToString(result);
   ProcessSignal(response);
}

//+------------------------------------------------------------------+
//| Process Signal JSON                                                |
//+------------------------------------------------------------------+
void ProcessSignal(string json)
{
   //--- Simple JSON parsing (for production, use CJAVal library)
   //--- Expected format: {"action":"BUY","symbol":"XAUUSD","signal_id":"abc123"}
   
   //--- Check for "no_signal" status
   if(StringFind(json, "\"status\":\"no_signal\"") >= 0)
   {
      // No new signal, normal state
      return;
   }
   
   //--- Extract signal_id to prevent duplicate execution
   string signalId = ExtractValue(json, "signal_id");
   if(signalId == lastSignalId && signalId != "")
   {
      // Already processed this signal
      return;
   }
   
   //--- Extract trade parameters
   string action = ExtractValue(json, "action");
   string symbol = ExtractValue(json, "symbol");
   
   if(action == "" || symbol == "")
   {
      Print("⚠️ Invalid signal format");
      return;
   }
   
   //--- Update last signal ID
   lastSignalId = signalId;
   
   //--- Log signal
   Print("📡 NEW SIGNAL: ", action, " ", symbol);
   
   //--- Execute if auto mode enabled
   if(AUTO_EXECUTE)
   {
      ExecuteTrade(action, symbol);
   }
   else
   {
      Alert("🔔 Signal Received: ", action, " ", symbol);
   }
}

//+------------------------------------------------------------------+
//| Execute Trade                                                      |
//+------------------------------------------------------------------+
void ExecuteTrade(string action, string symbol)
{
   //--- Normalize symbol (e.g., "XAUUSD" might need suffix like "XAUUSDm")
   string tradingSymbol = symbol;
   if(!SymbolSelect(symbol, true))
   {
      // Try with common suffixes
      if(SymbolSelect(symbol + "m", true))
         tradingSymbol = symbol + "m";
      else if(SymbolSelect(symbol + ".r", true))
         tradingSymbol = symbol + ".r";
      else
      {
         Print("❌ Symbol not found: ", symbol);
         return;
      }
   }
   
   //--- Get current price
   double ask = SymbolInfoDouble(tradingSymbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(tradingSymbol, SYMBOL_BID);
   
   //--- Execute based on action
   bool success = false;
   
   if(action == "BUY")
   {
      success = trade.Buy(LOT_SIZE, tradingSymbol, ask, 0, 0, "AlphaAxiom Signal");
   }
   else if(action == "SELL")
   {
      success = trade.Sell(LOT_SIZE, tradingSymbol, bid, 0, 0, "AlphaAxiom Signal");
   }
   else if(action == "CLOSE")
   {
      CloseAllPositions(tradingSymbol);
      success = true;
   }
   
   if(success)
      Print("✅ Trade executed: ", action, " ", tradingSymbol, " @ ", (action == "BUY" ? ask : bid));
   else
      Print("❌ Trade failed: ", trade.ResultRetcode(), " - ", trade.ResultRetcodeDescription());
}

//+------------------------------------------------------------------+
//| Close all positions for a symbol                                   |
//+------------------------------------------------------------------+
void CloseAllPositions(string symbol)
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong ticket = PositionGetTicket(i);
      if(PositionGetString(POSITION_SYMBOL) == symbol)
      {
         trade.PositionClose(ticket);
      }
   }
}

//+------------------------------------------------------------------+
//| Simple JSON value extractor                                        |
//+------------------------------------------------------------------+
string ExtractValue(string json, string key)
{
   string search = "\"" + key + "\":\"";
   int start = StringFind(json, search);
   if(start < 0) return "";
   
   start += StringLen(search);
   int end = StringFind(json, "\"", start);
   if(end < 0) return "";
   
   return StringSubstr(json, start, end - start);
}

//+------------------------------------------------------------------+
//| Tick function (optional - for price-based logic)                   |
//+------------------------------------------------------------------+
void OnTick()
{
   // Main logic handled in OnTimer()
   // OnTick can be used for trailing stops or real-time adjustments
}
//+------------------------------------------------------------------+
