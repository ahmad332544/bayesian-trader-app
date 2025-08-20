import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta

class PsarEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "psar_trend"
    @property
    def num_states(self) -> int: return 2 # 0=Bearish, 1=Bullish

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if "PSARl_0.02_0.2" not in data.columns:
            data.ta.psar(append=True)
        return data
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        psar_long = data.get("PSARl_0.02_0.2") # يظهر فقط في الاتجاه الصاعد
        # psar_short = data.get("PSARs_0.02_0.2") # يظهر فقط في الاتجاه الهابط
        
        if psar_long is None: return pd.Series(-1, index=data.index)

        # إذا كانت قيمة psar_long ليست NaN، فهذا يعني أننا في اتجاه صاعد
        is_bullish = psar_long.notna()
        
        return is_bullish.astype(int)