# evidence_modules/pattern_evidences.py
import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta

class BasePatternEvidence(BaseEvidence):
    """
    قالب داخلي لتبسيط كود نماذج الشموع.
    هذه النسخة المحسنة تضمن عمل الدليل حتى لو لم يتم العثور على نماذج.
    """
    pattern_name: str = ""
    
    @property
    def name(self) -> str: return f"pattern_{self.pattern_name}"
    @property
    def num_states(self) -> int: return 3 # 0=None, 1=Bullish, 2=Bearish

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        # نقوم بإضافة المؤشر هنا. pandas-ta قد لا يضيف العمود إذا لم يجد أي تطابق.
        # لذا، سنتحقق من وجوده في get_state.
        data.ta.cdl_pattern(name=self.pattern_name, append=True)
        return data
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        # البحث عن اسم العمود الصحيح الذي تم إنشاؤه
        target_col = None
        for col in data.columns:
            if col.startswith(f"CDL_{self.pattern_name.upper()}"):
                target_col = col
                break
        
        # --- FIX: التعامل مع حالة عدم العثور على العمود ---
        # إذا لم يقم pandas-ta بإنشاء العمود، فهذا يعني عدم وجود أي نموذج.
        if target_col is None:
            # في هذه الحالة، كل الحالات هي "0" (لا يوجد نموذج)
            return pd.Series(0, index=data.index)
        # --- نهاية التصحيح ---

        signal = data[target_col]
        states = pd.Series(0, index=data.index)
        states[signal > 0] = 1 # Bullish
        states[signal < 0] = 2 # Bearish
        return states

# --- الكلاسات الفرعية (تبقى كما هي تمامًا) ---
class DojiEvidence(BasePatternEvidence):
    pattern_name = "doji"

class HammerEvidence(BasePatternEvidence):
    pattern_name = "hammer"

class InvertedHammerEvidence(BasePatternEvidence):
    pattern_name = "invertedhammer"
    
class HangingManEvidence(BasePatternEvidence):
    pattern_name = "hangingman"

class ShootingStarEvidence(BasePatternEvidence):
    pattern_name = "shootingstar"
    
class MorningStarEvidence(BasePatternEvidence):
    pattern_name = "morningstar"
    
class EveningStarEvidence(BasePatternEvidence):
    pattern_name = "eveningstar"
    
class DragonflyDojiEvidence(BasePatternEvidence):
    pattern_name = "dragonflydoji"
    
class GravestoneDojiEvidence(BasePatternEvidence):
    pattern_name = "gravestonedoji"
    
class MarubozuEvidence(BasePatternEvidence):
    pattern_name = "marubozu"