# future_predictor.py
import pandas as pd

class FuturePredictor:
    def __init__(self, bayesian_engine):
        self.engine = bayesian_engine
        self.log = []
        self.log_message("FuturePredictor initialized.")

    def log_message(self, message: str, level: str = "INFO"):
        log_entry = f"[{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}] [{level}] {message}"
        print(log_entry)
        # self.log.append(log_entry) # Can be added if needed

    def predict_horizon(self, symbol: str, timeframe: str, latest_data: pd.DataFrame, horizon: int) -> dict:
        if not self.engine.is_trained.get(symbol, {}).get(timeframe, False):
            return {"error": f"Engine not trained for {symbol}/{timeframe}"}

        initial_prediction = self.engine.predict(symbol, timeframe, latest_data)
        if "error" in initial_prediction: return initial_prediction

        priors = self.engine.priors.get(symbol, {}).get(timeframe)
        if not priors: return {"error": f"No priors found for {symbol}/{timeframe}"}

        p_up = initial_prediction['up_prob'] / 100.0
        p_down = initial_prediction['down_prob'] / 100.0
        
        up_factor = p_up / priors['up'] if priors['up'] > 0 else 1
        down_factor = p_down / priors['down'] if priors['down'] > 0 else 1

        final_up = priors['up']
        final_down = priors['down']

        for _ in range(horizon):
            final_up *= up_factor
            final_down *= down_factor
            total = final_up + final_down
            if total > 1e-12:
                final_up /= total
                final_down /= total

        return {
            "up_prob": final_up * 100,
            "down_prob": final_down * 100,
            "used_evidence": initial_prediction['used_evidence'],
            "ignored_evidence": initial_prediction['ignored_evidence'],
            "ignored_details": initial_prediction['ignored_details']
        }