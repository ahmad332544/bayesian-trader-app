# mt5_connector.py
import MetaTrader5 as mt5
import pandas as pd
import time

class MT5Connector:
    def __init__(self):
        if not mt5.initialize():
            print("Failed to initialize MetaTrader 5, error code =", mt5.last_error())
            time.sleep(5)
            if not mt5.initialize(): quit()
        print(f"Python Connector: Connected to MetaTrader 5 build {mt5.version()}")

        self.timeframe_map = {
            "M1": mt5.TIMEFRAME_M1, "M5": mt5.TIMEFRAME_M5, "M15": mt5.TIMEFRAME_M15,
            "M30": mt5.TIMEFRAME_M30, "H1": mt5.TIMEFRAME_H1, "H4": mt5.TIMEFRAME_H4,
            "D1": mt5.TIMEFRAME_D1, "W1": mt5.TIMEFRAME_W1, "MN1": mt5.TIMEFRAME_MN1
        }

    def get_ohlcv(self, symbol: str, timeframe_str: str, count: int) -> pd.DataFrame:
        timeframe = self.timeframe_map.get(timeframe_str.upper())
        if timeframe is None: return pd.DataFrame()
        try: rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
        except Exception: return pd.DataFrame()
        if rates is None or len(rates) == 0: return pd.DataFrame()
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        df.rename(columns={'tick_volume': 'volume'}, inplace=True)
        return df

    # --- FIX: الدالة الجديدة والمهمة ---
    def get_last_bar_time(self, symbol: str, timeframe_str: str) -> int:
        """
        يسحب وقت افتتاح آخر شمعة فقط. عملية سريعة جدًا.
        """
        timeframe = self.timeframe_map.get(timeframe_str.upper())
        if timeframe is None: return 0
        try:
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 1)
            if rates is not None and len(rates) > 0:
                return int(rates[0]['time'])
        except Exception:
            return 0
        return 0

    def shutdown(self):
        mt5.shutdown()
        print("Python Connector: Disconnected from MetaTrader 5.")