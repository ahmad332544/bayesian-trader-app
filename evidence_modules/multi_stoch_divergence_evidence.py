# evidence_modules/multi_stoch_divergence_evidence.py
import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta
import numpy as np

class MultiStochDivergenceEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "multi_stoch_divergence"
    @property
    def num_states(self) -> int: return 3

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        # --- FIX: تغيير smooth_k من 1 إلى 3 لتجنب خطأ TA-Lib ---
        # وتحديث أسماء الأعمدة لتكون فريدة
        data.ta.stoch(k=9, d=3, smooth_k=3, append=True, col_names=("STOCHk_9_3_3", "STOCHd_9_3_3"))
        data.ta.stoch(k=14, d=3, smooth_k=3, append=True, col_names=("STOCHk_14_3_3", "STOCHd_14_3_3"))
        data.ta.stoch(k=40, d=4, smooth_k=4, append=True, col_names=("STOCHk_40_4_4", "STOCHd_40_4_4"))
        data.ta.stoch(k=60, d=10, smooth_k=10, append=True, col_names=("STOCHk_60_10_10", "STOCHd_60_10_10"))
        return data
            
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        s1_d = data.get("STOCHd_9_3_3")
        s2_d = data.get("STOCHd_14_3_3")
        s3_d = data.get("STOCHd_40_4_4")
        s4_d = data.get("STOCHd_60_10_10")
        
        if any(s is None for s in [s1_d, s2_d, s3_d, s4_d]):
            return pd.Series(-1, index=data.index)

        all_oversold = (s1_d < 25) & (s2_d < 25) & (s3_d < 25) & (s4_d < 25)
        all_overbought = (s1_d > 75) & (s2_d > 75) & (s3_d > 75) & (s4_d > 75)

        lows = data['low']
        prev_lows = lows.rolling(5, center=True).min().shift(1)
        bullish_divergence = (lows < prev_lows) & (s1_d > s1_d.rolling(5).min().shift(1))
        
        highs = data['high']
        prev_highs = highs.rolling(5, center=True).max().shift(1)
        bearish_divergence = (highs > prev_highs) & (s1_d < s1_d.rolling(5).max().shift(1))

        bullish_setup = all_oversold & bullish_divergence
        bearish_setup = all_overbought & bearish_divergence
        
        states = pd.Series(0, index=data.index)
        states[bullish_setup] = 1
        states[bearish_setup] = 2
        return states