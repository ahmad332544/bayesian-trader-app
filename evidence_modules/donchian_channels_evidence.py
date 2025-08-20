import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta

class DonchianChannelsEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "donchian_channels"
    @property
    def num_states(self) -> int: return 3 # 0=Inside, 1=Breakout Up, 2=Breakout Down

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if "DCU_20_20" not in data.columns:
            data.ta.donchian(lower_length=20, upper_length=20, append=True)
        return data
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        upper = data.get("DCU_20_20")
        lower = data.get("DCL_20_20")
        if upper is None or lower is None: return pd.Series(-1, index=data.index)
        
        breakout_up = data['close'] >= upper.shift(1)
        breakout_down = data['close'] <= lower.shift(1)
        
        states = pd.Series(0, index=data.index)
        states[breakout_up] = 1
        states[breakout_down] = 2
        return states