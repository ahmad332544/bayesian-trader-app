import pandas as pd
from base_evidence import BaseEvidence

class MarubozuEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "marubozu_candle"
    @property
    def num_states(self) -> int: return 3 # 0=None, 1=Bullish, 2=Bearish

    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        candle_range = data['high'] - data['low']
        candle_range[candle_range < 0.00001] = 0.00001
        body_size = (data['close'] - data['open']).abs()
        
        # تعتبر ماروبوزو إذا كان الجسم يمثل 95% أو أكثر من مدى الشمعة
        is_marubozu = (body_size / candle_range) >= 0.95
        is_bullish = data['close'] > data['open']
        
        states = pd.Series(0, index=data.index)
        states[is_marubozu & is_bullish] = 1
        states[is_marubozu & ~is_bullish] = 2
        return states