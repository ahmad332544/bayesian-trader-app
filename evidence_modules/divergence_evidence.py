# evidence_modules/divergence_evidence.py
import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta

class RsiDivergenceEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "rsi_divergence"
    @property
    def num_states(self) -> int: return 3 # 0=None, 1=Bullish, 2=Bearish

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if "RSI_14" not in data.columns:
            data.ta.rsi(length=14, append=True)
        return data
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        if "RSI_14" not in data.columns: return pd.Series(-1, index=data.index)
        
        price = data['close']
        indicator = data['RSI_14']
        
        # البحث عن القيعان (بشكل مبسط)
        lows_price = price.rolling(5, center=True).min()
        lows_indicator = indicator.rolling(5, center=True).min()
        
        # دايفرجنس صاعد: قاع أدنى في السعر، وقاع أعلى في المؤشر
        bullish_div = (lows_price < lows_price.shift(1)) & (lows_indicator > lows_indicator.shift(1))

        # البحث عن القمم
        highs_price = price.rolling(5, center=True).max()
        highs_indicator = indicator.rolling(5, center=True).max()

        # دايفرجنس هابط: قمة أعلى في السعر، وقمة أدنى في المؤشر
        bearish_div = (highs_price > highs_price.shift(1)) & (highs_indicator < highs_indicator.shift(1))
        
        states = pd.Series(0, index=data.index)
        states[bullish_div] = 1
        states[bearish_div] = 2
        return states


class MacdDivergenceEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "macd_divergence"
    @property
    def num_states(self) -> int: return 3 # 0=None, 1=Bullish, 2=Bearish

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        # MACD يضيف 3 أعمدة (MACD, Histogram, Signal)
        if "MACDh_12_26_9" not in data.columns:
            data.ta.macd(fast=12, slow=26, signal=9, append=True)
        return data
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        # سنستخدم الهيستوجرام للكشف عن الدايفرجنس
        if "MACDh_12_26_9" not in data.columns: return pd.Series(-1, index=data.index)

        price = data['close']
        indicator = data['MACDh_12_26_9'] # استخدام الهيستوجرام

        lows_price = price.rolling(5, center=True).min()
        lows_indicator = indicator.rolling(5, center=True).min()
        bullish_div = (lows_price < lows_price.shift(1)) & (lows_indicator > lows_indicator.shift(1))

        highs_price = price.rolling(5, center=True).max()
        highs_indicator = indicator.rolling(5, center=True).max()
        bearish_div = (highs_price > highs_price.shift(1)) & (highs_indicator < highs_indicator.shift(1))
        
        states = pd.Series(0, index=data.index)
        states[bullish_div] = 1
        states[bearish_div] = 2
        return states