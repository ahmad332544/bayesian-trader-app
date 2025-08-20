import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta

class QqeEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "qqe_trend"
    @property
    def num_states(self) -> int: return 2 # 0=Bearish, 1=Bullish

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if "QQE_14_5_4.236" not in data.columns:
            data.ta.qqe(length=14, smooth=5, factor=4.236, append=True)
        return data
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        qqe = data.get("QQE_14_5_4.236")
        qqe_signal = data.get("QQEl_14_5_4.236")
        if qqe is None or qqe_signal is None: return pd.Series(-1, index=data.index)
        
        return (qqe > qqe_signal).astype(int)