# evidence_modules/keltner_channels_evidence.py
import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta

class KeltnerChannelsEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "keltner_channels"
    @property
    def num_states(self) -> int: return 3 # 0=Inside, 1=Above Upper, 2=Below Lower

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        # --- FIX: استخدام الأسماء الصحيحة والحديثة للتحقق ---
        upper_col_name = "KCUe_20_2.0"
        lower_col_name = "KCLe_20_2.0"

        if upper_col_name not in data.columns or lower_col_name not in data.columns:
            # append=True سيقوم بإضافة الأعمدة بالأسماء الجديدة تلقائيًا
            data.ta.kc(length=20, scalar=2.0, append=True)
        return data
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        # --- FIX: استخدام الأسماء الصحيحة والحديثة للقراءة ---
        upper_col_name = "KCUe_20_2.0"
        lower_col_name = "KCLe_20_2.0"
        
        upper_channel = data.get(upper_col_name)
        lower_channel = data.get(lower_col_name)
        
        if upper_channel is None or lower_channel is None: 
            return pd.Series(-1, index=data.index)
        
        above_upper = data['close'] > upper_channel
        below_lower = data['close'] < lower_channel

        states = pd.Series(0, index=data.index) # 0 = Inside
        states[above_upper] = 1 # 1 = Above Upper
        states[below_lower] = 2 # 2 = Below Lower
        return states