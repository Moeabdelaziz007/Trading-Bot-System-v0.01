import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    print("⚠️ MetaTrader5 package not found (Mac/Linux detected). Running in SIMULATION MODE.")
    
    # Mock Class for Mac Development
    class MockMT5:
        def initialize(self): return True
        def shutdown(self): pass
        def terminal_info(self): 
            return type('Info', (object,), {'trade_allowed': True})()
        def account_info(self): 
            return type('Account', (object,), {'_asdict': lambda self: {'login': 123456, 'balance': 10000.0, 'equity': 10050.0}})()
    
    mt5 = MockMT5()

# Initialize Logic
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if not mt5.initialize():
        print("❌ Failed to initialize MT5")
    else:
        status = "✅ MT5 Initialized" if MT5_AVAILABLE else "⚠️ Mock MT5 Initialized (Sim Mode)"
        print(status)
        # Ensure Algo Trading is enabled
        info = mt5.terminal_info()
        if info and not info.trade_allowed:
            print("⚠️ WARNING: Algo Trading is NOT enabled in MT5!")
    yield
    # Shutdown
    mt5.shutdown()

app = FastAPI(lifespan=lifespan)

# Allow PWA to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In prod, restrict to app.alphaaxiom.com
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    print("🔗 New Client Connected")
    try:
        while True:
            data = await websocket.receive_text()
            cmd = json.loads(data)
            response = await process_command(cmd)
            if response:
                await websocket.send_json(response)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("🔌 Client Disconnected")
    except Exception as e:
        print(f"⚠️ Error: {e}")

async def process_command(cmd):
    action = cmd.get("action")
    
    if action == "STATUS_CHECK":
        terminal_info = mt5.terminal_info()
        return {
            "type": "STATUS", 
            "mt5_connected": terminal_info is not None,
            "algo_enabled": terminal_info.trade_allowed if terminal_info else False,
            "account": mt5.account_info()._asdict() if mt5.account_info() else None
        }

    elif action == "TRADE":
        # Handle Trade Execution Logic Here
        return {"type": "TRADE_ACK", "ticket": 0, "msg": "Simulation Mode"}
    
    return None

if __name__ == "__main__":
    print("👻 STARTING GHOST CONNECTOR...")
    # Try to import cert_manager
    try:
        from cert_manager import CertManager
        cm = CertManager()
        ssl_ctx = cm.get_ssl_context()
        # Run Secure WSS
        uvicorn.run(app, host="0.0.0.0", port=8765, ssl_keyfile=cm.key_path, ssl_certfile=cm.cert_path)
    except ImportError:
        print("⚠️ CertManager not found or failed. Running INSECURE (ws://).")
        uvicorn.run(app, host="0.0.0.0", port=8765)
    except Exception as e:
        print(f"⚠️ SSL Error: {e}. Running INSECURE.")
        uvicorn.run(app, host="0.0.0.0", port=8765)
