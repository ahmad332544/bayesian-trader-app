# base_evidence.py
from abc import ABC, abstractmethod
import pandas as pd

class BaseEvidence(ABC):
    @property
    @abstractmethod
    def name(self) -> str: pass

    @property
    @abstractmethod
    def num_states(self) -> int: pass

    def add_indicator(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        return data

    @abstractmethod
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series: pass