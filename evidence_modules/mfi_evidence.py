import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta
import numpy as np

class MFI_Evidence(BaseEvidence):
    @property
    def name(self) -> str: return "mfi_ob_os"
    @property
    def num_states(self) -> int: return 3 # 0=Normal, 1=Overbought, 2=Oversold

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if "MFI_14" not in data.columns:
            data.ta.mfi(length=14, append=True)
        return data
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        if "MFI_14" not in data.columns: return pd.Series(-1, index=data.index)
        
        conditions = [data['MFI_14'] > 80, data['MFI_14'] < 20]
        choices = [1, 2]
        return pd.Series(np.select(conditions, choices, default=0), index=data.index)