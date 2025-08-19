import pandas as pd
from base_evidence import BaseEvidence

class UpperWickEvidence(BaseEvidence):
    @property
    def name(self) -> str:
        return "large_upper_wick"

    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        """
        الحالات:
        0: الذيل العلوي ليس كبيرًا.
        1: الذيل العلوي كبير (أكبر من نصف حجم الجسم).
        """
        body = (data['close'] - data['open']).abs()
        # استبدال الأجسام الصفرية بقيمة صغيرة جدًا لتجنب القسمة على صفر
        body[body < 0.00001] = 0.00001
        
        upper_wick = data['high'] - data[['open', 'close']].max(axis=1)
        return (upper_wick > body * 0.5).astype(int)
    
    @property
    def num_states(self) -> int: return 2