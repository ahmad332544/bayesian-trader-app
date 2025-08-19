import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta

class AboveMASlowEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "above_ma_slow"
    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if "EMA_20" not in data.columns: data.ta.ema(length=20, append=True)
        return data
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        if 'EMA_20' not in data.columns: return pd.Series(-1, index=data.index)
        return (data['close'] > data['EMA_20']).astype(int)

class MACrossEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "ma_cross"
    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if "EMA_10" not in data.columns: data.ta.ema(length=10, append=True)
        if "EMA_20" not in data.columns: data.ta.ema(length=20, append=True)
        return data
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        fast_ma = data.get('EMA_10'); slow_ma = data.get('EMA_20')
        if fast_ma is None or slow_ma is None: return pd.Series(-1, index=data.index)
        bull_cross = (fast_ma > slow_ma) & (fast_ma.shift(1) <= slow_ma.shift(1))
        bear_cross = (fast_ma < slow_ma) & (fast_ma.shift(1) >= slow_ma.shift(1))
        states = pd.Series(0, index=data.index)
        states[bull_cross] = 1; states[bear_cross] = 2
        return states

class AboveEMA50Evidence(BaseEvidence):
    @property
    def name(self) -> str: return "above_ema_50"
    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if "EMA_50" not in data.columns: data.ta.ema(length=50, append=True)
        return data
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        if 'EMA_50' not in data.columns: return pd.Series(-1, index=data.index)
        return (data['close'] > data['EMA_50']).astype(int)

class AboveEMA100Evidence(BaseEvidence):
    @property
    def name(self) -> str: return "above_ema_100"
    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if "EMA_100" not in data.columns: data.ta.ema(length=100, append=True)
        return data
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        if 'EMA_100' not in data.columns: return pd.Series(-1, index=data.index)
        return (data['close'] > data['EMA_100']).astype(int)

class AboveEMA200Evidence(BaseEvidence):
    @property
    def name(self) -> str: return "above_ema_200"
    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if "EMA_200" not in data.columns: data.ta.ema(length=200, append=True)
        return data
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        if 'EMA_200' not in data.columns: return pd.Series(-1, index=data.index)
        return (data['close'] > data['EMA_200']).astype(int)
    
    @property
    def num_states(self) -> int: return 2
    @property
    def num_states(self) -> int: return 3
    @property
    def num_states(self) -> int: return 2
    @property
    def num_states(self) -> int: return 2
    @property
    def num_states(self) -> int: return 2