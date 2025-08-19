import pandas as pd
from base_evidence import BaseEvidence

class HTFConfluenceEvidence(BaseEvidence):
    @property
    def name(self) -> str:
        return "htf_confluence"
        
    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        # هذا الدليل سيجلب بيانات H1 بنفسه، لكنه يحتاج إلى DataEngine
        # كحل بسيط ومؤقت، سنستخدم EMA200 كبديل للإطار الزمني الأعلى
        # هذا يضمن عدم وجود تعقيدات إضافية في الوقت الحالي
        if "EMA_200" not in data.columns:
            data.ta.ema(length=200, append=True)
        return data
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        """
        الحالات:
        0: توافق صاعد (السعر فوق EMA200)
        1: توافق هابط (السعر تحت EMA200)
        2: محايد (لا يوجد EMA200)
        """
        if 'EMA_200' not in data.columns:
            return pd.Series(2, index=data.index) # 2 = Neutral

        is_above = data['close'] > data['EMA_200']
        states = pd.Series(2, index=data.index)
        states[is_above] = 0
        states[~is_above] = 1
        return states