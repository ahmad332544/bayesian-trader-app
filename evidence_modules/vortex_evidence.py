import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta

class VortexEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "vortex_trend"
    @property
    def num_states(self) -> int: return 3 # 0=Bearish, 1=Bullish, 2=Transition

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if "VTXP_14" not in data.columns:
            data.ta.vortex(length=14, append=True)
        return data
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        vip = data.get('VTXP_14')
        vim = data.get('VTXM_14')
        if vip is None or vim is None: return pd.Series(-1, index=data.index)

        is_bullish = vip > vim
        states = pd.Series(2, index=data.index) # 2 = Transition (Neutral)
        states[is_bullish] = 1
        states[~is_bullish] = 0
        return states