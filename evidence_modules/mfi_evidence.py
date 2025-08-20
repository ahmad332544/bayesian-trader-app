# evidence_modules/mfi_evidence.py
import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta
import numpy as np

class MfiEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "mfi_ob_os"
    @property
    def num_states(self) -> int: return 3

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        # --- FIX: استخدام الطريقة الصريحة لتجنب تحذيرات dtype ---
        if "MFI_14" not in data.columns:
            mfi_series = ta.mfi(high=data['high'], low=data['low'], close=data['close'], volume=data['volume'], length=14)
            data = data.join(mfi_series) # .join أكثر أمانًا من append=True في بعض الحالات
        return data
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        if "MFI_14" not in data.columns: return pd.Series(-1, index=data.index)
        
        conditions = [
            data['MFI_14'] > 80, # Overbought
            data['MFI_14'] < 20  # Oversold
        ]
        choices = [1, 2]
        
        return pd.Series(np.select(conditions, choices, default=0), index=data.index)