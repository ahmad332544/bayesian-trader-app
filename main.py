# main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
import asyncio
import json
from typing import Set, Dict

from mt5_connector import MT5Connector
from data_engine import DataEngine
from bayesian_engine import BayesianEngine
import uvicorn

# --- 1. تهيئة التطبيق ---
app = FastAPI()
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# --- 2. متغيرات عامة وإدارة الإعدادات ---
CONFIG_FILE = "config.json"
active_connections: Set[WebSocket] = set()
config: Dict = {}
data_cache: Dict = {}
# --- FIX: إنشاء الكائنات في النطاق العام ---
bayesian_engine: BayesianEngine = BayesianEngine()
mt5_connector: MT5Connector = MT5Connector()
data_engine: DataEngine = None # سيتم تهيئته لاحقًا

def load_config():
    global config
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f: config = json.load(f)
    except FileNotFoundError:
        config = {"watchlist": ["EURUSD_", "GBPUSD_", "USDJPY_"], "settings": {"history_lookback": 2000, "evidence_threshold": 0.05}}
        save_config()

def save_config():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(config, f, indent=4)

async def notify_all_clients(message: dict):
    if active_connections:
        for connection in list(active_connections):
            try: await connection.send_text(json.dumps(message))
            except Exception: active_connections.discard(connection)

# --- 3. دوال العمليات الرئيسية (التي تعمل في الخلفية) ---
async def train_and_run_main_loop():
    global data_engine, data_cache
    
    await notify_all_clients({"type": "status_update", "payload": "Gathering requirements..."})
    requirements = bayesian_engine.get_all_requirements()
    data_engine = DataEngine(requirements) # إنشاء data_engine هنا
    
    await notify_all_clients({"type": "status_update", "payload": "Starting initial training..."})
    symbol_to_train = config['watchlist'][0] if config.get('watchlist') else "EURUSD_"
    lookback = config.get('settings', {}).get('history_lookback', 2000)
    
    historical_data = data_engine.get_data(symbol_to_train, "H1", lookback)
    enriched_data = data_engine.add_indicators(historical_data, symbol_to_train)
    bayesian_engine.train(enriched_data)
    
    if bayesian_engine.is_trained:
        await notify_all_clients({"type": "status_update", "payload": "Training complete. Starting live data feed..."})
    else:
        await notify_all_clients({"type": "status_update", "payload": "Training failed. Check logs."})

    while True:
        try:
            current_watchlist = config.get("watchlist", [])
            all_predictions = {}
            timeframes = ["M1", "M5", "M15", "M30", "H1", "H4", "D1"]
            for symbol in current_watchlist:
                all_predictions[symbol] = {}
                daily_data = data_engine.get_data(symbol, "D1", 1)
                all_predictions[symbol]['daily_status'] = 'up' if not daily_data.empty and daily_data.iloc[-1]['close'] > daily_data.iloc[-1]['open'] else 'down'
                for tf in timeframes:
                    latest_data = data_engine.get_data(symbol, tf, 300)
                    enriched_data = data_engine.add_indicators(latest_data, symbol)
                    if not enriched_data.empty:
                        prediction = bayesian_engine.predict(enriched_data)
                        all_predictions[symbol][tf] = prediction
                    else: all_predictions[symbol][tf] = {"error": "No data"}
            data_cache = all_predictions
            await asyncio.sleep(10)
        except asyncio.CancelledError: break
        except Exception as e: bayesian_engine.log_message(f"Critical error in data loop: {e}", "CRITICAL")

async def broadcast_loop():
    while True:
        if active_connections and data_cache:
            await notify_all_clients({"type": "data_update", "payload": data_cache})
        await asyncio.sleep(2)

# --- 4. نقاط نهاية الخادم (API Endpoints) ---
@app.on_event("startup")
async def startup_event():
    load_config()
    bayesian_engine.threshold = config.get('settings', {}).get('evidence_threshold', 0.05)
    asyncio.create_task(train_and_run_main_loop())
    asyncio.create_task(broadcast_loop())

@app.get("/")
async def read_root(): return FileResponse('frontend/index.html')

@app.get("/logs")
async def get_logs():
    log_html = "".join([f"<p>{log.replace('[INFO]', '<span class=info>[INFO]</span>').replace('[WARNING]', '<span class=warning>[WARNING]</span>').replace('[ERROR]', '<span class=error>[ERROR]</span>').replace('[CRITICAL]', '<span class=critical>[CRITICAL]</span>')}</p>" for log in reversed(bayesian_engine.log)])
    html_content = f"""<!DOCTYPE html><html><head><title>Logs</title><meta http-equiv="refresh" content="3"><style>body{{font-family: monospace; background: #1e1e1e; color: #d4d4d4; font-size: 14px; padding: 10px;}}h1{{color: #569cd6;}} p{{margin: 2px 0; padding: 2px 5px; border-left: 3px solid #444; white-space: pre-wrap;}}.info{{color: #4ec9b0;}} .warning{{color: #dcdcaa;}} .error{{color: #f44747;}}.critical{{background: #f44747; color: #fff; font-weight: bold;}}</style></head><body><h1>Application Logs</h1>{log_html}</body></html>"""
    return HTMLResponse(content=html_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    try:
        initial_data = {"type": "initial_config", "payload": {"watchlist": config.get('watchlist',[]), "settings": {"evidenceThreshold": bayesian_engine.threshold}}}
        await websocket.send_text(json.dumps(initial_data))
        while True:
            data_str = await websocket.receive_text()
            data = json.loads(data_str)
            if data['type'] == 'add_symbol':
                symbol = data['payload'].upper()
                if symbol and symbol not in config['watchlist']:
                    config['watchlist'].append(symbol)
                    save_config()
                    await notify_all_clients({"type": "initial_config", "payload": {"watchlist": config['watchlist'], "settings": {"evidenceThreshold": bayesian_engine.threshold}}})
            if data['type'] == 'update_settings':
                new_threshold = float(data['payload']['threshold'])
                config['settings']['evidence_threshold'] = new_threshold
                bayesian_engine.threshold = new_threshold
                save_config()
    except WebSocketDisconnect: active_connections.discard(websocket)

# --- 5. نقطة التشغيل الرئيسية ---
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)