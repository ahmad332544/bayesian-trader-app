import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta

class MeanReversionEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "mean_reversion"
    @property
    def num_states(self) -> int: return 5 # 0=Very Overextended, 1=Overextended, 2=Normal, 3=Oversold, 4=Very Oversold

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if "EMA_20" not in data.columns: data.ta.ema(length=20, append=True)
        if "ATRr_14" not in data.columns: data.ta.atr(length=14, append=True)
        return data
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        ema = data.get('EMA_20')
        atr = data.get('ATRr_14')
        if ema is None or atr is None: return pd.Series(-1, index=data.index)
        
        distance = data['close'] - ema
        
        very_overextended = distance > (atr * 2)
        overextended = distance > atr
        very_oversold = distance < -(atr * 2)
        oversold = distance < -atr
        
        states = pd.Series(2, index=data.index) # 2 = Normal
        states[oversold] = 3
        states[very_oversold] = 4
        states[overextended] = 1
        states[very_overextended] = 0
        return states