import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta

class ObvEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "obv_trend"
    @property
    def num_states(self) -> int: return 2 # 0=OBV Falling, 1=OBV Rising

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if "OBV" not in data.columns:
            data.ta.obv(append=True)
        return data
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        obv = data.get("OBV")
        if obv is None: return pd.Series(-1, index=data.index)
        # نقارن OBV بمتوسطه المتحرك لتحديد اتجاهه
        obv_ma = obv.rolling(window=10).mean()
        return (obv > obv_ma).astype(int)