import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta

class TsiEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "tsi_trend"
    @property
    def num_states(self) -> int: return 4 # 0=Strong Bear, 1=Weak Bear, 2=Weak Bull, 3=Strong Bull

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if "TSI_13_25_13" not in data.columns:
            data.ta.tsi(fast=13, slow=25, signal=13, append=True)
        return data
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        tsi_line = data.get('TSI_13_25_13')
        signal_line = data.get('TSIs_13_25_13')
        if tsi_line is None or signal_line is None: return pd.Series(-1, index=data.index)
        
        strong_bull = (tsi_line > signal_line) & (tsi_line > 0)
        weak_bull = (tsi_line > signal_line) & (tsi_line < 0)
        strong_bear = (tsi_line < signal_line) & (tsi_line < 0)
        weak_bear = (tsi_line < signal_line) & (tsi_line > 0)

        states = pd.Series(1, index=data.index) # Default Weak Bear
        states[weak_bull] = 2
        states[strong_bull] = 3
        states[strong_bear] = 0
        return states