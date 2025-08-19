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
from future_predictor import FuturePredictor
import uvicorn

class AppState:
    def __init__(self):
        self.bayesian_engine: BayesianEngine = None
        self.mt5_connector: MT5Connector = None
        self.data_engine: DataEngine = None
        self.future_predictor: FuturePredictor = None
        self.config = {}; self.data_cache = {}; self.active_connections = set()
        self.main_loop_task: asyncio.Task = None

state = AppState()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("--- Application Startup ---")
    state.mt5_connector = MT5Connector()
    state.bayesian_engine = BayesianEngine()
    state.future_predictor = FuturePredictor(state.bayesian_engine)
    state.data_engine = DataEngine(state.mt5_connector)
    load_config()
    state.bayesian_engine.threshold = state.config.get('settings', {}).get('evidence_threshold', 0.05)
    
    state.main_loop_task = asyncio.create_task(run_training_and_data_loop())
    asyncio.create_task(broadcast_loop())
    yield
    print("--- Application Shutdown ---")
    if state.main_loop_task: state.main_loop_task.cancel()
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

async def run_training_and_data_loop(retrain=False):
    if retrain:
        state.bayesian_engine.is_trained = {}
        state.data_engine.cache = {}
        await notify_all_clients({"type": "status_update", "payload": "Settings changed. Retraining all models..."})

    lookback = state.config.get('settings', {}).get('history_lookback', 2000)
    timeframes = ["M1", "M5", "M15", "M30", "H1", "H4", "D1"]

    for symbol in state.config.get('watchlist', []):
        for tf in timeframes:
            if not state.bayesian_engine.is_trained.get(symbol, {}).get(tf, False):
                await notify_all_clients({"type": "status_update", "payload": f"Training {symbol} on {tf}..."})
                historical_data = state.data_engine.get_raw_data(symbol, tf, lookback)
                if not historical_data.empty:
                    state.bayesian_engine.train(symbol, tf, historical_data)
    
    await notify_all_clients({"type": "status_update", "payload": "Training complete. Starting live data feed..."})

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
                for tf in timeframes:
                    latest_data_raw = state.data_engine.get_raw_data(symbol, tf, 300)
                    if not latest_data_raw.empty:
                        prediction = state.bayesian_engine.predict(symbol, tf, latest_data_raw)
                        all_predictions[symbol][tf] = prediction
                    else: all_predictions[symbol][tf] = {"error": "No data"}
            state.data_cache = all_predictions
            await asyncio.sleep(10)
        except asyncio.CancelledError: 
            state.bayesian_engine.log_message("Main data loop was cancelled for retrain.", "INFO"); break
        except Exception as e: 
            state.bayesian_engine.log_message(f"Critical error in data loop: {e}", "CRITICAL")

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
    html_content = f"""<!DOCTYPE html><html><head><title>Logs</title><meta http-equiv="refresh" content="3"><style>body{{font-family: monospace; background: #1e1e1e; color: #d4d4d4; font-size: 14px; padding: 10px;}}h1{{color: #569cd6;}} p{{margin: 2px 0; padding: 2px 5px; border-left: 3px solid #444; white-space: pre-wrap;}}.info{{color: #4ec9b0;}} .warning{{color: #dcdcaa;}} .error{{color: #f44747;}}.critical{{background: #f44747; color: #fff; font-weight: bold;}}</style></head><body><h1>Application Logs</h1>{html_content}</body></html>"""
    return HTMLResponse(content=html_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    state.active_connections.add(websocket)
    try:
        initial_data = {"type": "initial_config", "payload": {"watchlist": state.config.get('watchlist',[]), "settings": state.config.get('settings',{})}}
        await websocket.send_text(json.dumps(initial_data))
        while True:
            data_str = await websocket.receive_text()
            data = json.loads(data_str)
            
            if data['type'] == 'update_settings':
                state.config['settings'] = data['payload']
                save_config()
                state.bayesian_engine.threshold = state.config['settings']['evidence_threshold']
                if state.main_loop_task: state.main_loop_task.cancel()
                state.main_loop_task = asyncio.create_task(run_training_and_data_loop(retrain=True))

            elif data['type'] == 'add_symbol':
                symbol = data['payload'].upper()
                if symbol and symbol not in state.config['watchlist']:
                    state.config['watchlist'].append(symbol)
                    save_config()
                    await notify_all_clients({"type": "initial_config", "payload": {"watchlist": state.config['watchlist'], "settings": state.config.get('settings',{})}})
                    if state.main_loop_task: state.main_loop_task.cancel()
                    state.main_loop_task = asyncio.create_task(run_training_and_data_loop(retrain=False))
            
            elif data['type'] == 'predict_future':
                horizon = data['payload']['horizon']
                await notify_all_clients({"type": "status_update", "payload": f"Calculating {horizon}-candle prediction...", "isFuture": True})
                
                future_predictions = {}
                timeframes = ["M1", "M5", "M15", "M30", "H1", "H4", "D1"]
                for symbol in state.config.get("watchlist", []):
                    future_predictions[symbol] = {}
                    daily_data_raw = state.data_engine.get_raw_data(symbol, "D1", 1)
                    future_predictions[symbol]['daily_status'] = 'up' if not daily_data_raw.empty and daily_data_raw.iloc[-1]['close'] > daily_data_raw.iloc[-1]['open'] else 'down'

                    for tf in timeframes:
                        latest_data_raw = state.data_engine.get_raw_data(symbol, tf, 300)
                        if not latest_data_raw.empty:
                            prediction = state.future_predictor.predict_horizon(symbol, tf, latest_data_raw, horizon)
                            future_predictions[symbol][tf] = prediction
                        else:
                            future_predictions[symbol][tf] = {"error": f"No data for {tf}"}

                await notify_all_clients({"type": "future_data_update", "payload": future_predictions})

    except WebSocketDisconnect: state.active_connections.discard(websocket)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)