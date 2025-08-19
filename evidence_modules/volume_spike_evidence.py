import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta

class VolumeSpikeEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "volume_spike"
    @property
    def num_states(self) -> int: return 3 # 0=Normal, 1=High, 2=Very High

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        # نحتاج لمتوسط حجم التداول للمقارنة
        if "VOLUME_MA_20" not in data.columns:
            data['VOLUME_MA_20'] = data['volume'].rolling(window=20).mean()
        return data
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        if "VOLUME_MA_20" not in data.columns: return pd.Series(-1, index=data.index)
        
        is_very_high = data['volume'] > (data['VOLUME_MA_20'] * 2.5) # أعلى بـ 150% من المتوسط
        is_high = data['volume'] > (data['VOLUME_MA_20'] * 1.5)      # أعلى بـ 50% من المتوسط

        states = pd.Series(0, index=data.index)
        states[is_high] = 1
        states[is_very_high] = 2
        return states