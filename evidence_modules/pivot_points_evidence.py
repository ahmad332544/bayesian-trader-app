import pandas as pd
from base_evidence import BaseEvidence
import numpy as np

class PivotPointsEvidence(BaseEvidence):
    @property
    def name(self) -> str:
        return "pivot_points"

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        # هذا الدليل سيحسب كل شيء في get_state، لكنه يحتاج ATR
        if "ATRr_14" not in data.columns:
            data.ta.atr(length=14, append=True)
        return data

    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        """
        الحالات:
        0: بعيد عن أي مستوى
        1: قريب من دعم
        2: قريب من مقاومة
        3: ارتد للتو من دعم
        4: ارتد للتو من مقاومة
        """
        # حساب بيانات اليوم السابق
        prev_day = data.resample('D').agg({
            'high': 'max', 'low': 'min', 'close': 'last'
        }).shift(1) # نحصل على بيانات الأمس لكل يوم

        if prev_day.empty: return pd.Series(-1, index=data.index)

        # حساب مستويات البيفوت لكل يوم
        pp = (prev_day['high'] + prev_day['low'] + prev_day['close']) / 3
        s1 = (2 * pp) - prev_day['high']
        r1 = (2 * pp) - prev_day['low']
        s2 = pp - (prev_day['high'] - prev_day['low'])
        r2 = pp + (prev_day['high'] - prev_day['low'])
        s3 = prev_day['low'] - 2 * (prev_day['high'] - pp)
        r3 = prev_day['high'] + 2 * (pp - prev_day['low'])

        # إنشاء DataFrame للمستويات
        pivots_df = pd.DataFrame({
            's3': s3, 's2': s2, 's1': s1, 'pp': pp,
            'r1': r1, 'r2': r2, 'r3': r3
        })

        # دمج مستويات البيفوت مع بيانات الشموع
        # هذا يضمن أن كل شمعة تعرف مستويات البيفوت الخاصة بيومها
        merged_data = pd.merge_asof(
            data.sort_index(), pivots_df,
            left_index=True, right_index=True, direction='backward'
        ).reindex(data.index)

        states = pd.Series(0, index=data.index) # 0 = Away
        proximity = merged_data.get('ATRr_14', 0.001) * 0.25

        pivot_levels = ['s3', 's2', 's1', 'pp', 'r1', 'r2', 'r3']
        for i, level_name in enumerate(pivot_levels):
            level = merged_data[level_name]
            is_support = i <= 3 # S3, S2, S1, PP
            is_resistance = i >= 3 # PP, R1, R2, R3

            # تحقق من الاقتراب
            is_near = (merged_data['close'] - level).abs() < proximity
            
            # تحقق من الارتداد
            rebounded_from_support = is_support & (merged_data['low'] < level) & (merged_data['close'] > level)
            rebounded_from_resistance = is_resistance & (merged_data['high'] > level) & (merged_data['close'] < level)

            states[rebounded_from_support] = 3
            states[rebounded_from_resistance] = 4
            states[is_near & (merged_data['close'] > level)] = 1 # قريب من دعم
            states[is_near & (merged_data['close'] < level)] = 2 # قريب من مقاومة

        return states
    
    @property
    def num_states(self) -> int: return 5