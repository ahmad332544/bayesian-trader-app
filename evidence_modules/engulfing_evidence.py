import pandas as pd
from base_evidence import BaseEvidence

class EngulfingEvidence(BaseEvidence):
    @property
    def name(self) -> str:
        return "engulfing_pattern"
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        """
        الحالات:
        0: لا يوجد نمط ابتللاع
        1: نمط ابتللاع صاعد
        2: نمط ابتللاع هابط
        """
        prev_close = data['close'].shift(1)
        prev_open = data['open'].shift(1)
        
        prev_is_bearish = prev_close < prev_open
        bull_engulf = prev_is_bearish & (data['close'] > prev_open) & (data['open'] < prev_close)
        
        prev_is_bullish = prev_close > prev_open
        bear_engulf = prev_is_bullish & (data['open'] > prev_close) & (data['close'] < prev_open)
        
        states = pd.Series(0, index=data.index)
        states[bull_engulf] = 1
        states[bear_engulf] = 2
        return states