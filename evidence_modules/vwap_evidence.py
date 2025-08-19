import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta

class VwapEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "vwap_relation"
    @property
    def num_states(self) -> int: return 3 # 0=Below, 1=Above, 2=Touching

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        # VWAP يتطلب بيانات يومية لحسابه بشكل صحيح
        if "VWAP_D" not in data.columns:
            data.ta.vwap(append=True)
        return data
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        vwap_col = data.get("VWAP_D")
        if vwap_col is None or vwap_col.isnull().all():
            return pd.Series(-1, index=data.index)

        # تحديد مسافة القرب
        proximity = data.get('ATRr_14', 0.001) * 0.1

        is_above = data['close'] > vwap_col
        is_touching = (data['close'] - vwap_col).abs() < proximity
        
        states = pd.Series(0, index=data.index) # 0 = Below
        states[is_above] = 1
        states[is_touching] = 2
        return states