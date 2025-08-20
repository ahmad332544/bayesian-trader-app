# evidence_modules/coppock_curve_evidence.py
import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta

class CoppockCurveEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "coppock_curve"
    @property
    def num_states(self) -> int: return 2

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if "COPC_11_14_10" not in data.columns:
            data.ta.coppock(length=10, fast=11, slow=14, append=True)
        return data
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        # --- FIX: استخدام اسم العمود الصحيح ---
        coppock = data.get("COPC_11_14_10")
        if coppock is None: return pd.Series(-1, index=data.index)
        return (coppock > 0).astype(int)