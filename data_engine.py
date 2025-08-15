# data_engine.py
import pandas as pd
import pandas_ta as ta
from mt5_connector import MT5Connector
import time

class DataEngine:
    def __init__(self, requirements: list[dict]):
        self.requirements = requirements
        self.connector = MT5Connector()
        self.cache = {}
        self.cache_max_size = 2500
        print("DataEngine: Created with caching enabled.")

    def get_data(self, symbol: str, timeframe: str, count: int) -> pd.DataFrame:
        now = int(time.time())
        key = f"{symbol}_{timeframe}"
        if key not in self.cache or self.cache[key]['data'].shape[0] < count:
            print(f"CACHE MISS/INSUFFICIENT: Fetching data for {key}...")
            df = self.connector.get_ohlcv(symbol, timeframe, max(count, self.cache_max_size))
            if df.empty: return pd.DataFrame()
            self.cache[key] = {'timestamp': now, 'data': df}
        return self.cache[key]['data'].tail(count).copy()

    def add_indicators(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if df.empty: return df
        df_processed = df.copy()
        
        standard_reqs = [req for req in self.requirements if req.get("kind") not in ["daily", "atr_ma"]]
        if standard_reqs:
            strategy = ta.Strategy(name="Bayesian Evidences", ta=standard_reqs)
            df_processed.ta.strategy(strategy, cores=0)
        
        if any(req.get("kind") == "atr_ma" for req in self.requirements):
             if 'ATRr_14' not in df_processed.columns:
                 df_processed.ta.atr(length=14, append=True)
             df_processed['ATRr_14_MA20'] = df_processed['ATRr_14'].rolling(window=20).mean()
        
        if any(req.get("kind") == "daily" for req in self.requirements):
             unique_dates = df_processed.index.to_series().dt.normalize().unique()
             if len(unique_dates) > 0:
                 daily_df = self.connector.get_ohlcv(symbol, "D1", len(unique_dates) + 5)
                 if not daily_df.empty:
                     daily_df = daily_df.rename(columns={'open': 'daily_open'})
                     daily_df.index = daily_df.index.normalize()
                     df_processed = pd.merge_asof(
                         left=df_processed.sort_index(),
                         right=daily_df[['daily_open']],
                         left_index=True,
                         right_index=True,
                         direction='backward'
                     ).reindex(df.index)

        return df_processed

    def shutdown(self):
        self.connector.shutdown()