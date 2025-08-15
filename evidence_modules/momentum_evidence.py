# evidence_modules/momentum_evidence.py
import pandas as pd
from base_evidence import BaseEvidence

class StochasticEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "stochastic_ob_os"
    def declare_requirements(self) -> list[dict]:
        return [{"kind": "stoch", "k": 14, "d": 3, "smooth_k": 3}]
    def get_state(self, data: pd.DataFrame) -> pd.Series:
        overbought = (data['STOCHk_14_3_3'] > 80) & (data['STOCHd_14_3_3'] > 80)
        oversold = (data['STOCHk_14_3_3'] < 20) & (data['STOCHd_14_3_3'] < 20)
        states = pd.Series(0, index=data.index)
        states[overbought] = 1
        states[oversold] = 2
        return states

class ADXStrengthEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "adx_strength"
    def declare_requirements(self) -> list[dict]:
        return [{"kind": "adx", "length": 14}]
    def get_state(self, data: pd.DataFrame) -> pd.Series:
        strong_trend = data['ADX_14'] > 25
        emerging_trend = data['ADX_14'] > 20
        states = pd.Series(0, index=data.index) # 0 = Ranging
        states[emerging_trend] = 1
        states[strong_trend] = 2
        return states