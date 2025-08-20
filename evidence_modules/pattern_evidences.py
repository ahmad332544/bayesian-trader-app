# evidence_modules/pattern_evidences.py
import pandas as pd
from base_evidence import BaseEvidence
import pandas_ta as ta

class BasePatternEvidence(BaseEvidence):
    pattern_name: str = ""
    
    @property
    def name(self) -> str: return f"pattern_{self.pattern_name}"
    @property
    def num_states(self) -> int: return 3

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if not any(col.startswith("CDL_") for col in data.columns):
            print("Calculating all candlestick patterns using TA-Lib...")
            # --- FIX: إجبار استخدام TA-Lib ---
            data.ta.cdl_pattern(name="all", append=True, talib=True)
        return data
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        target_col = None
        # البحث عن اسم العمود الصحيح
        for col in data.columns:
            if col.startswith(f"CDL_{self.pattern_name.upper()}"):
                target_col = col
                break
        
        if target_col is None or target_col not in data.columns:
            return pd.Series(0, index=data.index) # إرجاع 0 (لا يوجد نموذج) بدلاً من -1

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