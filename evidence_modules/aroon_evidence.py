import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta

class AroonEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "aroon_trend"
    @property
    def num_states(self) -> int: return 3 # 0=Bearish, 1=Bullish, 2=Consolidation

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if "AROOND_14" not in data.columns:
            data.ta.aroon(length=14, append=True)
        return data
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        up = data.get("AROONU_14")
        down = data.get("AROOND_14")
        if up is None or down is None: return pd.Series(-1, index=data.index)
        
        bullish = (up > down) & (up > 70)
        bearish = (down > up) & (down > 70)
        
        states = pd.Series(2, index=data.index) # 2=Consolidation
        states[bullish] = 1
        states[bearish] = 0
        return states