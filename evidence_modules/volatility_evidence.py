# evidence_modules/volatility_evidence.py
import pandas as pd
from base_evidence import BaseEvidence

class VolatilityIncreaseEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "volatility_increase"
    def declare_requirements(self) -> list[dict]:
        return [{"kind": "atr", "length": 14}]
    def get_state(self, data: pd.DataFrame) -> pd.Series:
        return (data['ATRr_14'] > data['ATRr_14'].shift(1)).astype(int)

class VolatilityRegimeEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "volatility_regime"
    def declare_requirements(self) -> list[dict]:
        return [{"kind": "atr_ma", "atr_length": 14, "ma_length": 20}] # Special
    def get_state(self, data: pd.DataFrame) -> pd.Series:
        return (data['ATRr_14'] > data['ATRr_14_MA20']).astype(int)