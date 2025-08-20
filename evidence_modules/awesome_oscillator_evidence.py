import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta

class AwesomeOscillatorEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "awesome_oscillator"
    @property
    def num_states(self) -> int: return 4 # 0=Strong Bear, 1=Weak Bear, 2=Weak Bull, 3=Strong Bull

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if "AO_5_34" not in data.columns:
            data.ta.ao(append=True)
        return data
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        ao = data.get("AO_5_34")
        if ao is None: return pd.Series(-1, index=data.index)
        
        strong_bull = (ao > 0) & (ao > ao.shift(1))
        weak_bull = (ao > 0) & (ao < ao.shift(1))
        strong_bear = (ao < 0) & (ao < ao.shift(1))
        weak_bear = (ao < 0) & (ao > ao.shift(1))

        states = pd.Series(1, index=data.index)
        states[weak_bull] = 2
        states[strong_bull] = 3
        states[strong_bear] = 0
        return states