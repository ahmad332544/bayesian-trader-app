# evidence_modules/kst_evidence.py
import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta

class KstEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "know_sure_thing"
    @property
    def num_states(self) -> int: return 2

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if "KST_10_15_20_30_10_10_10_15" not in data.columns:
            data.ta.kst(append=True)
        return data
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        # --- FIX: استخدام أسماء الأعمدة الصحيحة ---
        kst = data.get("KST_10_15_20_30_10_10_10_15")
        signal = data.get("KSTs_9")
        if kst is None or signal is None: return pd.Series(-1, index=data.index)
        
        return (kst > signal).astype(int)