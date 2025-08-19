import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta

class StochasticEvidence(BaseEvidence):
    @property
    def name(self) -> str:
        return "stochastic_ob_os"

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        # pandas-ta يحسب k و d تلقائيًا
        if "STOCHk_14_3_3" not in data.columns:
            data.ta.stoch(k=14, d=3, smooth_k=3, append=True)
        return data

    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        """
        الحالات: 0=Normal, 1=Overbought, 2=Oversold
        """
        k_col = 'STOCHk_14_3_3'
        d_col = 'STOCHd_14_3_3'
        if k_col not in data.columns or d_col not in data.columns:
            return pd.Series(-1, index=data.index)

        overbought = (data[k_col] > 80) & (data[d_col] > 80)
        oversold = (data[k_col] < 20) & (data[d_col] < 20)
        
        states = pd.Series(0, index=data.index)
        states[overbought] = 1
        states[oversold] = 2
        return states