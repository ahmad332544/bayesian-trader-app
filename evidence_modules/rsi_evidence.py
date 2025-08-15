import pandas as pd
import numpy as np
from base_evidence import BaseEvidence # نستورد القالب

class RSIEvidence(BaseEvidence):
    """
    دليل يقيس حالة مؤشر RSI (تشبع شرائي، تشبع بيعي، أو عادي).
    """

    @property
    def name(self) -> str:
        return "rsi_14_ob_os" # اسم فريد: مؤشر، فترة، منطق

    def declare_requirements(self) -> list[dict]:
        # هذا الدليل يحتاج فقط إلى مؤشر RSI بفترة 14
        return [
            {"kind": "rsi", "length": 14}
        ]

    def get_state(self, data: pd.DataFrame) -> pd.Series:
        # اسم العمود الذي سيتم إنشاؤه بواسطة DataEngine هو 'RSI_14'
        rsi_column = "RSI_14"

        # التأكد من وجود العمود المطلوب
        if rsi_column not in data.columns:
            # إذا لم يكن العمود موجودًا، نعيد سلسلة من الحالات "غير معروفة" (-1)
            return pd.Series(-1, index=data.index)

        # تعريف الحالات
        # الحالة 0: عادي (Normal)
        # الحالة 1: تشبع شرائي (Overbought)
        # الحالة 2: تشبع بيعي (Oversold)
        
        # استخدام np.select لتطبيق الشروط بكفاءة عالية
        conditions = [
            data[rsi_column] > 70,
            data[rsi_column] < 30
        ]
        choices = [1, 2] # 1 لـ > 70, و 2 لـ < 30
        
        # np.select(شروط, اختيارات, القيمة_الافتراضية)
        states = np.select(conditions, choices, default=0)

        # تحويل النتيجة إلى سلسلة Pandas
        return pd.Series(states, index=data.index)