import pandas as pd
from base_evidence import BaseEvidence
import numpy as np

class SessionEvidence(BaseEvidence):
    @property
    def name(self) -> str:
        return "trading_session"
    
    @property
    def num_states(self) -> int: return 5
        
    def get_state(self, data: pd.DataFrame, symbol: str) -> pd.Series:
        """
        الحالات:
        0: Tokyo, 1: London, 2: New York, 3: Overlap, 4: Outside
        """
        hour = data.index.hour
        
        conditions = [
            (hour >= 0) & (hour < 8),    # Tokyo
            (hour >= 8) & (hour < 13),   # London
            (hour >= 17) & (hour < 22),  # New York
            (hour >= 13) & (hour < 17)   # Overlap
        ]
        choices = [0, 1, 2, 3]
        
        states = np.select(conditions, choices, default=4)
        return pd.Series(states, index=data.index)