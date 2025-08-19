import pandas as pd
from base_evidence import BaseEvidence

class LowerWickEvidence(BaseEvidence):
    @property
    def name(self) -> str:
        return "large_lower_wick"

    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        """
        الحالات:
        0: الذيل السفلي ليس كبيرًا.
        1: الذيل السفلي كبير (أكبر من نصف حجم الجسم).
        """
        body = (data['close'] - data['open']).abs()
        body[body < 0.00001] = 0.00001
        
        lower_wick = data[['open', 'close']].min(axis=1) - data['low']
        return (lower_wick > body * 0.5).astype(int)