# evidence_modules/market_structure_evidence.py
import pandas as pd
from base_evidence import BaseEvidence

# هذه نسخة مبسطة لا تعتمد على ZigZag حاليًا لتقليل التعقيد
# يمكن تطويرها لاحقًا لاستخدام ZigZag
class SimpleMarketStructure(BaseEvidence):
    @property
    def name(self) -> str: return "simple_market_structure"
    def declare_requirements(self) -> list[dict]:
        return [{"kind": "ema", "length": 50}, {"kind": "ema", "length": 200}]
    def get_state(self, data: pd.DataFrame) -> pd.Series:
        ema50 = data['EMA_50']
        ema200 = data['EMA_200']
        
        uptrend = (ema50 > ema200)
        downtrend = (ema50 < ema200)
        
        states = pd.Series(2, index=data.index) # 2 = Ranging
        states[uptrend] = 0
        states[downtrend] = 1
        return states