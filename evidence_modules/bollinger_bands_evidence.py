import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta

class BollingerBandsEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "bollinger_bands"
    @property
    def num_states(self) -> int: return 5 # 0=Inside, 1=Touching Upper, 2=Touching Lower, 3=Outside Upper, 4=Outside Lower

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if "BBL_20_2.0" not in data.columns:
            data.ta.bbands(length=20, std=2, append=True)
        return data
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        upper_band = data.get('BBU_20_2.0')
        lower_band = data.get('BBL_20_2.0')
        if upper_band is None or lower_band is None: return pd.Series(-1, index=data.index)

        touch_upper = data['high'] >= upper_band
        touch_lower = data['low'] <= lower_band
        outside_upper = data['close'] > upper_band
        outside_lower = data['close'] < lower_band
        
        states = pd.Series(0, index=data.index)
        states[touch_upper] = 1
        states[touch_lower] = 2
        states[outside_upper] = 3
        states[outside_lower] = 4
        return states