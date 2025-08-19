# evidence_modules/market_structure_evidence.py
import pandas as pd
from base_evidence import BaseEvidence
from utils import calculate_zigzag # <-- استيراد دالتنا المخصصة

class MarketStructureEvidence(BaseEvidence):
    @property
    def name(self) -> str:
        return "market_structure"
    
    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """
        هذا الدليل يحسب مؤشره المخصص.
        """
        if "zigzag" not in data.columns:
            zigzag_pivots = calculate_zigzag(data, threshold_percent=0.03) # 3% threshold
            # دمج النتائج مع البيانات الأصلية
            data['zigzag'] = zigzag_pivots
        return data
    
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        """
        الحالات:
        0: اتجاه صاعد قوي (HH, HL)
        1: اتجاه هابط قوي (LH, LL)
        2: انحسار / بداية ضعف صاعد (LH, HL)
        3: توسع / بداية ضعف هابط (HH, LL)
        4: حالة عرضية / غير واضحة
        """
        if 'zigzag' not in data.columns or data['zigzag'].dropna().empty:
            return pd.Series(4, index=data.index)

        pivots = data['zigzag'].dropna()
        
        if len(pivots) < 4:
            return pd.Series(4, index=data.index)

        # استخراج آخر 4 نقاط محورية
        last_pivots = pivots.tail(4)
        
        highs = data['high'][last_pivots[last_pivots == 1].index]
        lows = data['low'][last_pivots[last_pivots == -1].index]

        if len(highs) < 2 or len(lows) < 2:
            return pd.Series(4, index=data.index)

        # استخراج قيم آخر قمتين وقاعين
        h2, h1 = highs.iloc[-2], highs.iloc[-1]
        l2, l1 = lows.iloc[-2], lows.iloc[-1]
        
        higherHigh = h1 > h2
        higherLow = l1 > l2
        lowerHigh = h1 < h2
        lowerLow = l1 < l2
        
        state = 4 # Default: Unclear
        if higherHigh and higherLow: state = 0      # Uptrend
        elif lowerHigh and lowerLow: state = 1   # Downtrend
        elif lowerHigh and higherLow: state = 2  # Consolidation
        elif higherHigh and lowerLow: state = 3  # Expansion
        
        # تطبيق الحالة على كل الصفوف
        return pd.Series(state, index=data.index)