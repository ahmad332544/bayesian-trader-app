import pandas as pd
from base_evidence import BaseEvidence

class DailyRangeRelationEvidence(BaseEvidence):
    @property
    def name(self) -> str: return "daily_range_relation"
    @property
    def num_states(self) -> int: return 5 # 0=Below Low, 1=Inside Low, 2=Middle, 3=Inside High, 4=Above High
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        # حساب أعلى وأدنى سعر لليوم السابق
        daily_high = data['high'].resample('D').max().shift(1)
        daily_low = data['low'].resample('D').min().shift(1)
        
        # دمج هذه البيانات مع البيانات الحالية
        merged_data = data.copy()
        merged_data['date'] = merged_data.index.date
        daily_high.index = daily_high.index.date
        daily_low.index = daily_low.index.date
        merged_data = pd.merge(merged_data, daily_high.rename('prev_high'), left_on='date', right_index=True, how='left')
        merged_data = pd.merge(merged_data, daily_low.rename('prev_low'), left_on='date', right_index=True, how='left')
        merged_data[['prev_high', 'prev_low']] = merged_data[['prev_high', 'prev_low']].ffill()

        if 'prev_high' not in merged_data.columns: return pd.Series(-1, index=data.index)

        above_high = merged_data['close'] > merged_data['prev_high']
        below_low = merged_data['close'] < merged_data['prev_low']
        
        # تحديد الربع العلوي والسفلي من مدى اليوم السابق
        prev_range = merged_data['prev_high'] - merged_data['prev_low']
        upper_quartile = merged_data['prev_high'] - (prev_range * 0.25)
        lower_quartile = merged_data['prev_low'] + (prev_range * 0.25)
        
        inside_high = (merged_data['close'] <= merged_data['prev_high']) & (merged_data['close'] > upper_quartile)
        inside_low = (merged_data['close'] >= merged_data['prev_low']) & (merged_data['close'] < lower_quartile)
        
        states = pd.Series(2, index=data.index) # 2 = Middle
        states[below_low] = 0
        states[inside_low] = 1
        states[inside_high] = 3
        states[above_high] = 4
        
        return states