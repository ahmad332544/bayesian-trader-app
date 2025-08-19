# main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
import asyncio
import json
from contextlib import asynccontextmanager

from mt5_connector import MT5Connector
from data_engine import DataEngine
from bayesian_engine import BayesianEngine
import uvicorn

class AppState:
    def __init__(self):
        self.bayesian_engine: BayesianEngine = None
        self.mt5_connector: MT5Connector = None
        self.data_engine: DataEngine = None
        self.config = {}; self.data_cache = {}; self.active_connections = set()

state = AppState()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("--- Application Startup ---")
    state.bayesian_engine = BayesianEngine()
    state.mt5_connector = MT5Connector()
    state.data_engine = DataEngine(state.mt5_connector)
    load_config()
    state.bayesian_engine.threshold = state.config.get('settings', {}).get('evidence_threshold', 0.05)
    asyncio.create_task(train_and_run_main_loop())
    asyncio.create_task(broadcast_loop())
    yield
    print("--- Application Shutdown ---")
    state.mt5_connector.shutdown()

app = FastAPI(lifespan=lifespan)
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

CONFIG_FILE = "config.json"
def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f: state.config = json.load(f)
    except FileNotFoundError:
        state.config = {"watchlist": ["EURUSD_", "GBPUSD_", "USDJPY_"], "settings": {"history_lookback": 2000, "evidence_threshold": 0.05}}
        save_config()
def save_config():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(state.config, f, indent=4)
async def notify_all_clients(message: dict):
    if state.active_connections:
        for connection in list(state.active_connections):
            try: await connection.send_text(json.dumps(message))
            except Exception: state.active_connections.discard(connection)

async def train_and_run_main_loop():
    symbol_to_train = state.config['watchlist'][0] if state.config.get('watchlist') else "EURUSD_"
    lookback = state.config.get('settings', {}).get('history_lookback', 2000)
    timeframes_to_train = ["M1", "M5", "M15", "M30", "H1", "H4", "D1"]

    for tf in timeframes_to_train:
        await notify_all_clients({"type": "status_update", "payload": f"Training for {tf}..."})
        historical_data = state.data_engine.get_raw_data(symbol_to_train, tf, lookback)
        state.bayesian_engine.train(tf, historical_data, symbol_to_train)
    
    await notify_all_clients({"type": "status_update", "payload": "All timeframes trained. Starting live data feed..."})

    while True:
        try:
            current_watchlist = state.config.get("watchlist", [])
            all_predictions = {}
            for symbol in current_watchlist:
                all_predictions[symbol] = {}
                daily_data_raw = state.data_engine.get_raw_data(symbol, "D1", 1)
                if not daily_data_raw.empty:
                    all_predictions[symbol]['daily_status'] = 'up' if daily_data_raw.iloc[-1]['close'] > daily_data_raw.iloc[-1]['open'] else 'down'
                else: all_predictions[symbol]['daily_status'] = 'neutral'
                for tf in timeframes_to_train:
                    latest_data_raw = state.data_engine.get_raw_data(symbol, tf, 300)
                    if not latest_data_raw.empty:
                        prediction = state.bayesian_engine.predict(tf, latest_data_raw, symbol)
                        all_predictions[symbol][tf] = prediction
                    else: all_predictions[symbol][tf] = {"error": "No data"}
            state.data_cache = all_predictions
            await asyncio.sleep(10)
        except asyncio.CancelledError: break
        except Exception as e: state.bayesian_engine.log_message(f"Critical error in data loop: {e}", "CRITICAL")

async def broadcast_loop():
    while True:
        if state.active_connections and state.data_cache:
            await notify_all_clients({"type": "data_update", "payload": state.data_cache})
        await asyncio.sleep(2)

@app.get("/")
async def read_root(): return FileResponse('frontend/index.html')

@app.get("/logs")
async def get_logs():
    log_html = "".join([f"<p>{log.replace('[INFO]', '<span class=info>[INFO]</span>').replace('[WARNING]', '<span class=warning>[WARNING]</span>').replace('[ERROR]', '<span class=error>[ERROR]</span>').replace('[CRITICAL]', '<span class=critical>[CRITICAL]</span>')}</p>" for log in reversed(state.bayesian_engine.log)])
    html_content = f"""<!DOCTYPE html><html><head><title>Logs</title><meta http-equiv="refresh" content="3"><style>body{{font-family: monospace; background: #1e1e1e; color: #d4d4d4; font-size: 14px; padding: 10px;}}h1{{color: #569cd6;}} p{{margin: 2px 0; padding: 2px 5px; border-left: 3px solid #444; white-space: pre-wrap;}}.info{{color: #4ec9b0;}} .warning{{color: #dcdcaa;}} .error{{color: #f44747;}}.critical{{background: #f44747; color: #fff; font-weight: bold;}}</style></head><body><h1>Application Logs</h1>{log_html}</body></html>"""
    return HTMLResponse(content=html_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    state.active_connections.add(websocket)
    try:
        initial_data = {"type": "initial_config", "payload": {"watchlist": state.config.get('watchlist',[]), "settings": {"evidenceThreshold": state.bayesian_engine.threshold}}}
        await websocket.send_text(json.dumps(initial_data))
        while True:
            data_str = await websocket.receive_text()
            data = json.loads(data_str)
            if data['type'] == 'add_symbol':
                symbol = data['payload'].upper()
                if symbol and symbol not in state.config['watchlist']:
                    state.config['watchlist'].append(symbol)
                    save_config()
                    await notify_all_clients({"type": "initial_config", "payload": {"watchlist": state.config['watchlist'], "settings": {"evidenceThreshold": state.bayesian_engine.threshold}}})
            if data['type'] == 'update_settings':
                new_threshold = float(data['payload']['threshold'])
                state.config['settings']['evidence_threshold'] = new_threshold
                state.bayesian_engine.threshold = new_threshold
                save_config()
    except WebSocketDisconnect: state.active_connections.discard(websocket)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)