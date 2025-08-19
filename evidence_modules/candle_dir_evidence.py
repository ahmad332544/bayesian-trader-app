import pandas as pd
from base_evidence import BaseEvidence

class PrevCandleDirEvidence(BaseEvidence):
    @property
    def name(self) -> str:
        return "prev_candle_direction"

    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        """
        الحالات:
        0: الشمعة السابقة كانت هابطة.
        1: الشمعة السابقة كانت صاعدة.
        """
        return (data['close'] > data['open']).astype(int)
    
    @property
    def num_states(self) -> int: return 2
    @property
    def num_states(self) -> int: return 2
    @property
    def num_states(self) -> int: return 2
    @property
    def num_states(self) -> int: return 3
    @property
    def num_states(self) -> int: return 8