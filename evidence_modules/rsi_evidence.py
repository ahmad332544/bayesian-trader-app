import pandas as pd
import numpy as np
from base_evidence import BaseEvidence
import pandas_ta as ta

class RSIEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "rsi_14_ob_os"
    
    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if "RSI_14" not in data.columns:
            data.ta.rsi(length=14, append=True)
        return data
    


    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        if "RSI_14" not in data.columns: return pd.Series(-1, index=data.index)
        conditions = [data["RSI_14"] > 70, data["RSI_14"] < 30]
        choices = [1, 2] # 1=Overbought, 2=Oversold
        return pd.Series(np.select(conditions, choices, default=0), index=data.index)
    
    @property
    def num_states(self) -> int: return 3