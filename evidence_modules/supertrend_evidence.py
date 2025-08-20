import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta

class SupertrendEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "supertrend"
    @property
    def num_states(self) -> int: return 2 # 0=Bearish, 1=Bullish

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if "SUPERTd_7_3.0" not in data.columns:
            data.ta.supertrend(length=7, multiplier=3.0, append=True)
        return data
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        direction = data.get("SUPERTd_7_3.0")
        if direction is None: return pd.Series(-1, index=data.index)
        
        # 1 يعني اتجاه صاعد، -1 يعني اتجاه هابط
        is_bullish = direction == 1
        return is_bullish.astype(int)