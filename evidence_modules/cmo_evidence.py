import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta
import numpy as np

class CmoEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "cmo_strength"
    @property
    def num_states(self) -> int: return 5 # Very Bearish, Bearish, Neutral, Bullish, Very Bullish

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if "CMO_14" not in data.columns:
            data.ta.cmo(length=14, append=True)
        return data
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        cmo = data.get("CMO_14")
        if cmo is None: return pd.Series(-1, index=data.index)

        conditions = [
            cmo > 50,  # Very Bullish
            cmo > 0,   # Bullish
            cmo < -50, # Very Bearish
            cmo < 0    # Bearish
        ]
        choices = [4, 3, 0, 1]
        return pd.Series(np.select(conditions, choices, default=2), index=data.index) # 2=Neutral