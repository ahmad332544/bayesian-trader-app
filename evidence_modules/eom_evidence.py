# evidence_modules/eom_evidence.py
import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta

class EomEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "ease_of_movement"
    @property
    def num_states(self) -> int: return 2

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if "EOM_14_100000000" not in data.columns:
            data.ta.eom(length=14, append=True)
        return data
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        # --- FIX: استخدام اسم العمود الصحيح ---
        eom = data.get("EOM_14_100000000")
        if eom is None: return pd.Series(-1, index=data.index)
        return (eom > 0).astype(int)