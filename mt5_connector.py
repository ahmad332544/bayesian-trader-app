import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import time

class MT5Connector:
    def __init__(self):
        """
        يقوم بتهيئة الاتصال المباشر مع منصة MetaTrader 5.
        """
        if not mt5.initialize():
            print("فشل تهيئة الاتصال مع MetaTrader 5, error code =", mt5.last_error())
            # حاول مرة أخرى بعد 5 ثوانٍ
            time.sleep(5)
            if not mt5.initialize():
                 quit() # إذا فشل مرة أخرى، أغلق البرنامج

        print(f"Python Connector: متصل بـ MetaTrader 5 build {mt5.version()}")

    def get_ohlcv(self, symbol: str, timeframe_str: str, count: int) -> pd.DataFrame:
        """
        يسحب بيانات الشموع الخام مباشرة من منصة MT5.
        """
        # تحويل اسم الإطار الزمني النصي إلى كائن MT5 timeframe
        timeframe_map = {
            "M1": mt5.TIMEFRAME_M1, "M5": mt5.TIMEFRAME_M5, "M15": mt5.TIMEFRAME_M15,
            "M30": mt5.TIMEFRAME_M30, "H1": mt5.TIMEFRAME_H1, "H4": mt5.TIMEFRAME_H4,
            "D1": mt5.TIMEFRAME_D1, "W1": mt5.TIMEFRAME_W1, "MN1": mt5.TIMEFRAME_MN1
        }
        timeframe = timeframe_map.get(timeframe_str.upper())
        if timeframe is None:
            print(f"Python Connector: الإطار الزمني '{timeframe_str}' غير صالح.")
            return pd.DataFrame()

        # طلب البيانات من MT5
        try:
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
        except Exception as e:
            print(f"Python Connector: حدث خطأ أثناء طلب البيانات لـ {symbol}: {e}")
            return pd.DataFrame()

        if rates is None or len(rates) == 0:
            print(f"Python Connector: لم يتم العثور على بيانات لـ {symbol}. تأكد من أن الرمز متاح في Market Watch.")
            return pd.DataFrame()
        
        # تحويل البيانات إلى DataFrame
        df = pd.DataFrame(rates)
        # MT5 يعيد الوقت كـ Unix timestamp, نحوله إلى صيغة قابلة للقراءة
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        # إعادة تسمية الأعمدة لتكون متوافقة مع بقية الكود
        df.rename(columns={'tick_volume': 'volume'}, inplace=True)
        
        return df

    def shutdown(self):
        """
        يقوم بإغلاق الاتصال مع منصة MT5.
        """
        mt5.shutdown()
        print("Python Connector: تم إغلاق الاتصال مع MetaTrader 5.")


# --- مثال للاختبار ---
if __name__ == "__main__":
    print("Starting connector test...")
    
    # تأكد من أن منصة MT5 مفتوحة قبل تشغيل هذا السكريبت
    connector = MT5Connector()
    
    print("\n--- Requesting EURUSD, M1 data ---")
    eurusd_df = connector.get_ohlcv(symbol="EURUSD_", timeframe_str="M1", count=5)
    
    if not eurusd_df.empty:
        print("\nSuccessfully received data:")
        print(eurusd_df)
    else:
        print("\nFailed to receive data or data was empty.")
        
    connector.shutdown()
    print("\nTest finished.")