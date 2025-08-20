import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta

class RocEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "rate_of_change"
    @property
    def num_states(self) -> int: return 4 # 0=Bearish Accel, 1=Bearish Decel, 2=Bullish Decel, 3=Bullish Accel

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if "ROC_10" not in data.columns:
            data.ta.roc(length=10, append=True)
        return data
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        roc = data.get("ROC_10")
        if roc is None: return pd.Series(-1, index=data.index)

        bull_accel = (roc > 0) & (roc > roc.shift(1))
        bull_decel = (roc > 0) & (roc < roc.shift(1))
        bear_accel = (roc < 0) & (roc < roc.shift(1))
        bear_decel = (roc < 0) & (roc > roc.shift(1))
        
        states = pd.Series(2, index=data.index) # Default Bullish Decel
        states[bear_decel] = 1
        states[bear_accel] = 0
        states[bull_accel] = 3
        return states