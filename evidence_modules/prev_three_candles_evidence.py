import pandas as pd
from base_evidence import BaseEvidence

class PrevThreeCandlesEvidence(BaseEvidence):
    @property
    def name(self) -> str:
        return "prev_3_candles"
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        """
        الحالات: 8 حالات (من 0 إلى 7) تمثل كل التركيبات الممكنة
        لـ ↓↓↓, ↓↓↑, ↓↑↓, ...
        """
        p1 = (data['close'] > data['open']).astype(int) * 1
        p2 = (data['close'].shift(1) > data['open'].shift(1)).astype(int) * 2
        p3 = (data['close'].shift(2) > data['open'].shift(2)).astype(int) * 4
        
        # fillna(0) لمعالجة القيم الفارغة في بداية البيانات
        return (p1 + p2 + p3).fillna(0).astype(int)