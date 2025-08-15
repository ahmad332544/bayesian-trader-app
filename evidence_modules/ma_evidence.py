# evidence_modules/ma_evidence.py
import pandas as pd
from base_evidence import BaseEvidence

class AboveMASlowEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "above_ma_slow"
    def declare_requirements(self) -> list[dict]:
        return [{"kind": "ema", "length": 20}]
    def get_state(self, data: pd.DataFrame) -> pd.Series:
        return (data['close'] > data['EMA_20']).astype(int)

class MACrossEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "ma_cross"
    def declare_requirements(self) -> list[dict]:
        return [{"kind": "ema", "length": 10}, {"kind": "ema", "length": 20}]
    def get_state(self, data: pd.DataFrame) -> pd.Series:
        fast_ma = data['EMA_10']
        slow_ma = data['EMA_20']
        bull_cross = (fast_ma > slow_ma) & (fast_ma.shift(1) <= slow_ma.shift(1))
        bear_cross = (fast_ma < slow_ma) & (fast_ma.shift(1) >= slow_ma.shift(1))
        states = pd.Series(0, index=data.index) # 0 = No Cross
        states[bull_cross] = 1 # 1 = Bullish Cross
        states[bear_cross] = 2 # 2 = Bearish Cross
        return states