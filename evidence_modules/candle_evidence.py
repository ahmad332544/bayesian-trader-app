# evidence_modules/candle_evidence.py
import pandas as pd
from base_evidence import BaseEvidence

class PrevCandleDirEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "prev_candle_dir"
    def declare_requirements(self) -> list[dict]: return [] # No indicators needed
    def get_state(self, data: pd.DataFrame) -> pd.Series:
        return (data['close'] > data['open']).astype(int)

class UpperWickEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "upper_wick"
    def declare_requirements(self) -> list[dict]: return []
    def get_state(self, data: pd.DataFrame) -> pd.Series:
        body = (data['close'] - data['open']).abs()
        upper_wick = data['high'] - data[['open', 'close']].max(axis=1)
        return (upper_wick > body * 0.5).astype(int)

class LowerWickEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "lower_wick"
    def declare_requirements(self) -> list[dict]: return []
    def get_state(self, data: pd.DataFrame) -> pd.Series:
        body = (data['close'] - data['open']).abs()
        lower_wick = data[['open', 'close']].min(axis=1) - data['low']
        return (lower_wick > body * 0.5).astype(int)
        
class EngulfingEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "engulfing_pattern"
    def declare_requirements(self) -> list[dict]: return []
    def get_state(self, data: pd.DataFrame) -> pd.Series:
        prev_is_bearish = data['close'].shift(1) < data['open'].shift(1)
        bull_engulf = prev_is_bearish & (data['close'] > data['open'].shift(1)) & (data['open'] < data['close'].shift(1))
        prev_is_bullish = data['close'].shift(1) > data['open'].shift(1)
        bear_engulf = prev_is_bullish & (data['open'] > data['close'].shift(1)) & (data['close'] < data['open'].shift(1))
        states = pd.Series(0, index=data.index) # 0 = None
        states[bull_engulf] = 1
        states[bear_engulf] = 2
        return states
        
class PrevThreeCandlesEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "prev_3_candles"
    def declare_requirements(self) -> list[dict]: return []
    def get_state(self, data: pd.DataFrame) -> pd.Series:
        p1 = (data['close'] > data['open']).astype(int) * 1
        p2 = (data['close'].shift(1) > data['open'].shift(1)).astype(int) * 2
        p3 = (data['close'].shift(2) > data['open'].shift(2)).astype(int) * 4
        return p1 + p2 + p3