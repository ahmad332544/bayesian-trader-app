import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta
import numpy as np

class WilliamsREvidence(BaseEvidence):
    @property
    def name(self) -> str: return "williams_r"
    @property
    def num_states(self) -> int: return 3 # 0=Normal, 1=Overbought, 2=Oversold

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if "WILLR_14" not in data.columns:
            data.ta.willr(length=14, append=True)
        return data
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        willr = data.get("WILLR_14")
        if willr is None: return pd.Series(-1, index=data.index)
        
        conditions = [willr > -20, willr < -80]
        choices = [1, 2] # 1=Overbought, 2=Oversold
        return pd.Series(np.select(conditions, choices, default=0), index=data.index)