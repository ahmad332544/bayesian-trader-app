import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta

class AdlEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "accumulation_distribution_line"
    @property
    def num_states(self) -> int: return 2 # 0=Distribution, 1=Accumulation

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if "AD" not in data.columns:
            data.ta.ad(append=True)
        return data
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        ad = data.get("AD")
        if ad is None: return pd.Series(-1, index=data.index)
        ad_ma = ad.rolling(window=10).mean()
        return (ad > ad_ma).astype(int)