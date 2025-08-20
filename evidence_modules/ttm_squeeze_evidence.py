import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta

class TtmSqueezeEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "ttm_squeeze"
    @property
    def num_states(self) -> int: return 2 # 0=Squeezed (low volatility), 1=Released (high volatility)

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if "SQZ_ON" not in data.columns:
            data.ta.squeeze(lazy_bear=True, append=True) # lazy_bear=True يعطي نتائج أبسط
        return data
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        squeeze_on = data.get("SQZ_ON")
        if squeeze_on is None: return pd.Series(-1, index=data.index)
        
        # 1 يعني أن الانضغاط مفعل، 0 يعني أنه تم إطلاقه
        is_squeezed = squeeze_on == 1
        return (~is_squeezed).astype(int) # نعكسها، 0 = انضغاط، 1 = إطلاق