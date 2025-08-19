import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta
import numpy as np

class MultiStochDivergenceEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "multi_stoch_divergence"
    @property
    def num_states(self) -> int: return 3 # 0=Neutral, 1=Bullish Setup, 2=Bearish Setup

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        # إضافة جميع إعدادات الاستوكاستيك المطلوبة
        data.ta.stoch(k=9, d=3, smooth_k=1, append=True, col_names=("STOCH_k_9_3_1", "STOCH_d_9_3_1"))
        data.ta.stoch(k=14, d=3, smooth_k=1, append=True, col_names=("STOCH_k_14_3_1", "STOCH_d_14_3_1"))
        data.ta.stoch(k=40, d=4, smooth_k=1, append=True, col_names=("STOCH_k_40_4_1", "STOCH_d_40_4_1"))
        data.ta.stoch(k=60, d=10, smooth_k=10, append=True, col_names=("STOCH_k_60_10_10", "STOCH_d_60_10_10"))
        return data
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        s1_d = data.get("STOCH_d_9_3_1")
        s2_d = data.get("STOCH_d_14_3_1")
        s3_d = data.get("STOCH_d_40_4_1")
        s4_d = data.get("STOCH_d_60_10_10")
        
        if any(s is None for s in [s1_d, s2_d, s3_d, s4_d]):
            return pd.Series(-1, index=data.index)

        # --- شروط التشبع ---
        all_oversold = (s1_d < 25) & (s2_d < 25) & (s3_d < 25) & (s4_d < 25)
        all_overbought = (s1_d > 75) & (s2_d > 75) & (s3_d > 75) & (s4_d > 75)

        # --- شروط الدايفرجنس ---
        # البحث عن قيعان في السعر
        lows = data['low']
        # نبحث عن آخر قاعين مهمين (بشكل مبسط، قاع أقل من الشموع المجاورة له)
        prev_low = lows.rolling(5, center=True).min().shift(1)
        
        # دايفرجنس صاعد: قاع جديد في السعر، ولكن قاع أعلى في الاستوكاستيك السريع
        bullish_divergence = (lows < prev_low) & (s1_d > s1_d.rolling(5).min().shift(1))
        
        # البحث عن قمم في السعر
        highs = data['high']
        prev_high = highs.rolling(5, center=True).max().shift(1)
        
        # دايفرجنس هابط: قمة جديدة في السعر، ولكن قمة أدنى في الاستوكاستيك السريع
        bearish_divergence = (highs > prev_high) & (s1_d < s1_d.rolling(5).max().shift(1))

        # --- تجميع الشروط ---
        bullish_setup = all_oversold & bullish_divergence
        bearish_setup = all_overbought & bearish_divergence
        
        states = pd.Series(0, index=data.index) # 0 = Neutral
        states[bullish_setup] = 1
        states[bearish_setup] = 2
        return states