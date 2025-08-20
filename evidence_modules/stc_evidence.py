import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta
import numpy as np

class StcEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "schaff_trend_cycle"
    @property
    def num_states(self) -> int: return 3

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if "STC_10_23_50" not in data.columns:
            # FIX: نمرر close بشكل صريح
            stc = ta.stc(close=data['close'], tclength=10, fast=23, slow=50)
            data = data.join(stc)
        return data
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        stc_col = "STC_10_23_50_0.5" # الاسم الصحيح للعمود
        stc = data.get(stc_col)
        if stc is None: return pd.Series(-1, index=data.index)
        
        trending_up = (stc > 75) | ((stc > 25) & (stc > stc.shift(1)))
        trending_down = (stc < 25) | ((stc < 75) & (stc < stc.shift(1)))
        
        states = pd.Series(2, index=data.index)
        states[trending_up] = 1
        states[trending_down] = 0
        return states