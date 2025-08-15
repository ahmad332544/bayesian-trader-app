# evidence_modules/price_action_evidence.py
import pandas as pd
from base_evidence import BaseEvidence

class PinBarEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "pin_bar"
    def declare_requirements(self) -> list[dict]: return []
    def get_state(self, data: pd.DataFrame) -> pd.Series:
        body = (data['open'] - data['close']).abs()
        upper_wick = data['high'] - data[['open', 'close']].max(axis=1)
        lower_wick = data[['open', 'close']].min(axis=1) - data['low']
        
        is_pin = (body > 0.00001) # Must have a body
        bearish_pin = is_pin & (upper_wick > body * 2) & (lower_wick < body)
        bullish_pin = is_pin & (lower_wick > body * 2) & (upper_wick < body)
        
        states = pd.Series(0, index=data.index) # 0 = Not a pin bar
        states[bullish_pin] = 1
        states[bearish_pin] = 2
        return states

class CandleCharacterEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "candle_character"
    def declare_requirements(self) -> list[dict]: return []
    def get_state(self, data: pd.DataFrame) -> pd.Series:
        candle_range = data['high'] - data['low']
        body_size = (data['close'] - data['open']).abs()
        
        # تجنب القسمة على صفر
        candle_range[candle_range < 0.00001] = 0.00001

        body_ratio = body_size / candle_range
        
        strong_momentum = body_ratio > 0.7
        indecision = body_ratio < 0.3
        
        states = pd.Series(4, index=data.index) # 4 = Normal
        states[strong_momentum] = 0
        states[indecision] = 1
        return states