import pandas as pd
from base_evidence import BaseEvidence

class DayOfWeekEvidence(BaseEvidence):
    @property
    def name(self) -> str:
        return "day_of_week"
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        """
        الحالات: 0=Monday, 1=Tuesday, ..., 4=Friday
        """
        # dayofweek يتجاهل السبت (5) والأحد (6)
        return pd.Series(data.index.dayofweek, index=data.index)