import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta

class VolatilityIncreaseEvidence(BaseEvidence):
    @property
    def name(self) -> str:
        return "volatility_increase"
        
    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if "ATRr_14" not in data.columns:
            data.ta.atr(length=14, append=True)
        return data

    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        atr = data.get('ATRr_14')
        if atr is None: return pd.Series(-1, index=data.index)
        return (atr > atr.shift(1)).astype(int)

class VolatilityRegimeEvidence(BaseEvidence):
    @property
    def name(self) -> str:
        return "volatility_regime"
        
    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        # هذا الدليل يحتاج ATR و MA of ATR
        if 'ATRr_14' not in data.columns:
            data.ta.atr(length=14, append=True)
        if 'ATRr_14_MA20' not in data.columns and 'ATRr_14' in data.columns:
            data['ATRr_14_MA20'] = data['ATRr_14'].rolling(window=20).mean()
        return data

    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        atr = data.get('ATRr_14')
        atr_ma = data.get('ATRr_14_MA20')
        if atr is None or atr_ma is None: return pd.Series(-1, index=data.index)
        return (atr > atr_ma).astype(int)