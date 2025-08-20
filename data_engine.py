# data_engine.py
import pandas as pd
from mt5_connector import MT5Connector
import time

class DataEngine:
    def __init__(self, connector: MT5Connector):
        self.connector = connector
        self.cache = {}
        self.cache_max_size = 2500
        print("DataEngine: Created with Candle-Aware Caching.")

    def get_raw_data(self, symbol: str, timeframe: str, count: int) -> pd.DataFrame:
        key = f"{symbol}_{timeframe}"

        # --- FIX: نظام Caching ذكي يعتمد على وقت آخر شمعة ---
        
        # 1. الحصول على وقت آخر شمعة من MT5
        latest_bar_time_mt5 = self.connector.get_last_bar_time(symbol, timeframe)
        if latest_bar_time_mt5 == 0: # إذا فشل الطلب
            return self.cache.get(key, {}).get('data', pd.DataFrame())

        # 2. التحقق مما إذا كان يجب تحديث البيانات
        needs_update = False
        if key not in self.cache:
            needs_update = True
            print(f"CACHE MISS: Fetching initial data for {key}...")
        else:
            last_cached_bar_time = self.cache[key].get('last_bar_time', 0)
            if latest_bar_time_mt5 > last_cached_bar_time:
                needs_update = True
                print(f"NEW BAR DETECTED: Refreshing data for {key}...")

        # 3. سحب البيانات فقط عند الحاجة
        if needs_update:
            df = self.connector.get_ohlcv(symbol, timeframe, self.cache_max_size)
            if df.empty:
                return self.cache.get(key, {}).get('data', pd.DataFrame())
            
            # تخزين البيانات مع وقت آخر شمعة
            self.cache[key] = {
                'last_bar_time': int(df.index[-1].timestamp()), 
                'data': df
            }
        
        # 4. إرجاع أحدث 'count' شمعة من البيانات المحدثة
        return self.cache.get(key, {}).get('data', pd.DataFrame()).tail(count).copy()

    def shutdown(self):
        self.connector.shutdown()