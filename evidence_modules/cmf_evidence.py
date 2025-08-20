import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta
import numpy as np

class CmfEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "chaikin_money_flow"
    @property
    def num_states(self) -> int: return 3 # 0=Bearish Flow, 1=Bullish Flow, 2=Neutral

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if "CMF_20" not in data.columns:
            data.ta.cmf(length=20, append=True)
        return data
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        cmf = data.get("CMF_20")
        if cmf is None: return pd.Series(-1, index=data.index)
        
        # نستخدم عتبة صغيرة (e.g., 0.05) لتحديد التدفق القوي
        is_bullish = cmf > 0.05
        is_bearish = cmf < -0.05

        states = pd.Series(2, index=data.index) # 2=Neutral
        states[is_bullish] = 1
        states[is_bearish] = 0
        return states