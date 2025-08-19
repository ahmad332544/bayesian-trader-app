# data_engine.py
import pandas as pd
from mt5_connector import MT5Connector
import time

class DataEngine:
    def __init__(self, connector: MT5Connector):
        self.connector = connector
        self.cache = {}
        self.cache_max_size = 2500
        print("DataEngine: Created with caching enabled.")

    def get_raw_data(self, symbol: str, timeframe: str, count: int) -> pd.DataFrame:
        now = int(time.time())
        key = f"{symbol}_{timeframe}"
        
        if key not in self.cache or self.cache[key]['data'].shape[0] < count:
            df = self.connector.get_ohlcv(symbol, timeframe, max(count, self.cache_max_size))
            if df.empty: return pd.DataFrame()
            self.cache[key] = {'timestamp': now, 'data': df}
        
        return self.cache[key]['data'].tail(count).copy()