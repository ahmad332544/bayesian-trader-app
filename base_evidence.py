from abc import ABC, abstractmethod
import pandas as pd

class BaseEvidence(ABC):
    """
    الكلاس الأساسي المجرد (القالب) الذي يجب أن يرث منه كل دليل.
    إنه يفرض على كل دليل جديد توفير الدوال الأساسية اللازمة ليعمل
    النظام بشكل صحيح.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """يعيد اسمًا فريدًا للدليل (يُستخدم كمعرف)."""
        pass

    @abstractmethod
    def declare_requirements(self) -> list[dict]:
        """
        يعيد قائمة بالبيانات التي يحتاجها هذا الدليل.
        كل عنصر في القائمة هو قاموس يصف مؤشرًا معينًا.
        مثال: [{"kind": "rsi", "length": 14}, {"kind": "ema", "length": 50}]
        """
        pass

    @abstractmethod
    def get_state(self, data: pd.DataFrame) -> pd.Series:
        """
        يأخذ DataFrame غني بالبيانات ويحسب "الحالة" لكل شمعة.
        يجب أن يعيد سلسلة Pandas (عمود واحد) بنفس طول الـ DataFrame،
        تحتوي على أرقام صحيحة تمثل الحالات (0, 1, 2, ...).
        """
        pass