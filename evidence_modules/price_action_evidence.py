import pandas as pd
from base_evidence import BaseEvidence
import numpy as np

class PinBarEvidence(BaseEvidence):
    @property
    def name(self) -> str:
        return "pin_bar"

    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        """
        الحالات: 0=Not Pin Bar, 1=Bullish Pin Bar, 2=Bearish Pin Bar
        """
        body = (data['open'] - data['close']).abs()
        upper_wick = data['high'] - data[['open', 'close']].max(axis=1)
        lower_wick = data[['open', 'close']].min(axis=1) - data['low']
        
        # يجب أن يكون هناك جسم صغير لتجنب الدوجي
        has_body = body > 0.00001
        
        bullish_pin = has_body & (lower_wick > body * 2) & (upper_wick < body)
        bearish_pin = has_body & (upper_wick > body * 2) & (lower_wick < body)
        
        states = pd.Series(0, index=data.index)
        states[bullish_pin] = 1
        states[bearish_pin] = 2
        return states

class CandleCharacterEvidence(BaseEvidence):
    @property
    def name(self) -> str:
        return "candle_character"

    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        """
        الحالات: 0=زخم قوي, 1=تردد/دوجي, 2=رفض علوي, 3=رفض سفلي, 4=عادي
        """
        candle_range = data['high'] - data['low']
        candle_range[candle_range < 0.00001] = 0.00001 # تجنب القسمة على صفر
        
        body_size = (data['close'] - data['open']).abs()
        upper_wick = data['high'] - data[['open', 'close']].max(axis=1)
        lower_wick = data[['open', 'close']].min(axis=1) - data['low']
        body_ratio = body_size / candle_range

        conditions = [
            body_ratio > 0.7,                   # زخم قوي
            body_ratio < 0.3,                   # تردد
            upper_wick > lower_wick * 2,        # رفض علوي
            lower_wick > upper_wick * 2         # رفض سفلي
        ]
        choices = [0, 1, 2, 3]
        
        states = np.select(conditions, choices, default=4)
        return pd.Series(states, index=data.index)