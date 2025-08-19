# utils.py
import pandas as pd
import numpy as np

def calculate_zigzag(data: pd.DataFrame, threshold_percent: float = 0.05) -> pd.Series:
    """
    تحسب نقاط ZigZag بناءً على نسبة تغير مئوية.
    هذه النسخة محسنة للعمل مع Pandas ومصممة لإرجاع سلسلة 
    يمكن دمجها بسهولة مع البيانات الأصلية.
    
    :param data: DataFrame يجب أن يحتوي على عمود 'close'.
    :param threshold_percent: النسبة المئوية للتغير المطلوبة لتحديد نقطة محورية.
    :return: pd.Series تحتوي على قيم ZigZag (1 للقمة، -1 للقاع، و NaN للباقي).
    """
    if 'close' not in data.columns or data.empty:
        return pd.Series(dtype=float)

    pivots = []
    last_pivot_price = data['close'].iloc[0]
    last_pivot_time = data.index[0]
    trend = 0  # 0: Undefined, 1: Up, -1: Down

    # تحديد ما إذا كانت أول نقطة قمة أم قاع
    first_change = (data['close'] - last_pivot_price) / last_pivot_price
    initial_pivots = first_change[first_change.abs() > threshold_percent]
    if not initial_pivots.empty:
        first_significant_time = initial_pivots.index[0]
        first_significant_price = data['close'].loc[first_significant_time]
        
        if first_significant_price > last_pivot_price:
            pivots.append({'time': last_pivot_time, 'pivot': -1}) # قاع
            trend = 1
        else:
            pivots.append({'time': last_pivot_time, 'pivot': 1}) # قمة
            trend = -1
        
        last_pivot_price = first_significant_price
        last_pivot_time = first_significant_time

    # المرور على بقية البيانات
    for time, price in data['close'].loc[last_pivot_time:].items():
        if trend == 0: # إذا لم يتم تحديد الاتجاه بعد
            change = (price - last_pivot_price) / last_pivot_price
            if abs(change) > threshold_percent:
                trend = np.sign(change)
                pivots.append({'time': last_pivot_time, 'pivot': -trend})
                last_pivot_price = price
                last_pivot_time = time
        elif trend == 1: # في اتجاه صاعد
            if price > last_pivot_price:
                last_pivot_price = price
                last_pivot_time = time
            elif (price - last_pivot_price) / last_pivot_price < -threshold_percent:
                pivots.append({'time': last_pivot_time, 'pivot': 1}) # قمة
                trend = -1
                last_pivot_price = price
                last_pivot_time = time
        elif trend == -1: # في اتجاه هابط
            if price < last_pivot_price:
                last_pivot_price = price
                last_pivot_time = time
            elif (price - last_pivot_price) / last_pivot_price > threshold_percent:
                pivots.append({'time': last_pivot_time, 'pivot': -1}) # قاع
                trend = 1
                last_pivot_price = price
                last_pivot_time = time

    if not pivots:
        return pd.Series(index=data.index, dtype=float)

    # تحويل قائمة النقاط إلى Series
    pivot_df = pd.DataFrame(pivots).set_index('time')
    return pivot_df['pivot']