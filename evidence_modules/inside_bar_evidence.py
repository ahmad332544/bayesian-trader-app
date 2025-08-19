import pandas as pd
from base_evidence import BaseEvidence

class InsideBarEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "inside_bar"
    @property
    def num_states(self) -> int: return 2 # 0=No, 1=Yes

    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        prev_high = data['high'].shift(1)
        prev_low = data['low'].shift(1)
        
        is_inside_bar = (data['high'] < prev_high) & (data['low'] > prev_low)
        return is_inside_bar.astype(int)