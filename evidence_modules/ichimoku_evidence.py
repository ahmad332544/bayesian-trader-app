# evidence_modules/ichimoku_evidence.py
import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta

class IchimokuEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "ichimoku_cloud"
    @property
    def num_states(self) -> int: return 3

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        # --- FIX: استخدام الأسماء الصحيحة للتحقق ---
        if "ISA_9" not in data.columns:
            # استخدام الإعدادات الافتراضية
            data.ta.ichimoku(append=True)
        return data
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        # --- FIX: استخدام أسماء الأعمدة الصحيحة ---
        span_a = data.get("ISA_9")
        span_b = data.get("ISB_26")
        
        if span_a is None or span_b is None: return pd.Series(-1, index=data.index)
        
        cloud_top = pd.concat([span_a, span_b], axis=1).max(axis=1)
        cloud_bottom = pd.concat([span_a, span_b], axis=1).min(axis=1)
        
        above_cloud = data['close'] > cloud_top
        below_cloud = data['close'] < cloud_bottom
        
        states = pd.Series(2, index=data.index) # 2=Inside
        states[above_cloud] = 1
        states[below_cloud] = 0
        return states