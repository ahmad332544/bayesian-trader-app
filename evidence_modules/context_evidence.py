# evidence_modules/context_evidence.py
import pandas as pd
from base_evidence import BaseEvidence

class SessionEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "trading_session"
    def declare_requirements(self) -> list[dict]: return []
    def get_state(self, data: pd.DataFrame) -> pd.Series:
        hour = data.index.hour
        states = pd.Series(4, index=data.index) # 4 = Outside
        states[(hour >= 0) & (hour < 8)] = 0 # Tokyo
        states[(hour >= 8) & (hour < 13)] = 1 # London
        states[(hour >= 17) & (hour < 22)] = 2 # NY
        states[(hour >= 13) & (hour < 17)] = 3 # Overlap
        return states

class DayOfWeekEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "day_of_week"
    def declare_requirements(self) -> list[dict]: return []
    def get_state(self, data: pd.DataFrame) -> pd.Series:
        return data.index.dayofweek # Monday=0, Tuesday=1, ...

class DailyOpenRelationEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "daily_open_relation"
    def declare_requirements(self) -> list[dict]:
        return [{"kind": "daily"}] # A special requirement
    def get_state(self, data: pd.DataFrame) -> pd.Series:
        # DataEngine needs to be updated to handle this 'daily' requirement
        daily_open = data['open'].resample('D').first().ffill()
        return (data['close'] > daily_open).astype(int)