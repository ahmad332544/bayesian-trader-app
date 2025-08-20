import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta

class ForceIndexEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "force_index"
    @property
    def num_states(self) -> int: return 2 # 0=Bearish Force, 1=Bullish Force

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if "EFI_13" not in data.columns:
            data.ta.efi(length=13, append=True)
        return data
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        efi = data.get("EFI_13")
        if efi is None: return pd.Series(-1, index=data.index)
        return (efi > 0).astype(int)