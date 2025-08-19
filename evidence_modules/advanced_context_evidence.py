import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta
import numpy as np

class ADXStrengthEvidence(BaseEvidence):
    @property
    def name(self) -> str:
        return "adx_strength"
        
    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if "ADX_14" not in data.columns:
            data.ta.adx(length=14, append=True)
        return data

    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        """
        الحالات: 0=Ranging, 1=Emerging Trend, 2=Strong Trend
        """
        adx = data.get('ADX_14', 0)
        conditions = [adx > 25, adx > 20]
        choices = [2, 1]
        states = np.select(conditions, choices, default=0)
        return pd.Series(states, index=data.index)

class RoundNumbersEvidence(BaseEvidence):
    @property
    def name(self) -> str:
        return "round_numbers"
        
    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if "ATRr_14" not in data.columns:
            data.ta.atr(length=14, append=True)
        return data
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        """
        الحالات: 0=Away, 1=Near Resistance, 2=Near Support
        """
        point = 0.001 if "JPY" in symbol.upper() else 0.00001
        
        level_00 = (data['close'] / (100 * point)).round() * (100 * point)
        level_50 = (data['close'] / (50 * point)).round() * (50 * point)
        
        dist_00 = (data['close'] - level_00).abs()
        dist_50 = (data['close'] - level_50).abs()
        
        nearest_level = level_00.where(dist_00 < dist_50, level_50)
        proximity = data.get('ATRr_14', 0.001) * 0.1
        
        is_near = (data['close'] - nearest_level).abs() < proximity
        is_above = data['close'] > nearest_level
        
        states = pd.Series(0, index=data.index)
        states[is_near & ~is_above] = 1
        states[is_near & is_above] = 2
        return states