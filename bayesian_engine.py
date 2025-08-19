# bayesian_engine.py
import pandas as pd
import numpy as np
import traceback
import pkgutil
import importlib

class BayesianEngine:
    def __init__(self, evidence_strength_threshold: float = 0.05):
        self.log = []
        self.evidence_modules = self._load_evidence_modules()
        self.priors = {}
        self.likelihoods = {}
        self.is_trained = {}
        self.threshold = evidence_strength_threshold
        self.log_message(f"BayesianEngine: Loaded {len(self.evidence_modules)} evidence modules.")

    def log_message(self, message: str, level: str = "INFO"):
        log_entry = f"[{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}] [{level}] {message}"
        print(log_entry)
        self.log.append(log_entry)
        if len(self.log) > 500: self.log.pop(0)

    def _load_evidence_modules(self) -> list:
        modules = []
        try:
            from base_evidence import BaseEvidence
            import evidence_modules
            for _, module_name, _ in pkgutil.iter_modules(evidence_modules.__path__, "evidence_modules."):
                try:
                    module = importlib.import_module(module_name)
                    for attribute_name in dir(module):
                        attribute = getattr(module, attribute_name)
                        if isinstance(attribute, type) and issubclass(attribute, BaseEvidence) and attribute is not BaseEvidence:
                            modules.append(attribute())
                except Exception as e:
                    self.log_message(f"Failed to load module {module_name}. Error: {e}", "ERROR")
        except Exception as e:
            self.log_message(f"Could not load evidence modules package. Error: {e}", "CRITICAL")
        return modules

    def get_enriched_data(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        enriched_df = data.copy()
        for module in self.evidence_modules:
            try:
                enriched_df = module.add_indicator(enriched_df, symbol)
            except Exception:
                self.log_message(f"Error in add_indicator for '{module.name}'. Details: {traceback.format_exc()}", "ERROR")
        return enriched_df

    def train(self, symbol: str, timeframe: str, data: pd.DataFrame):
        self.log_message(f"Starting training for SYMBOL: {symbol}, TIMEFRAME: {timeframe}")
        enriched_data = self.get_enriched_data(data, symbol)
        if enriched_data.empty or len(enriched_data) < 50:
            self.log_message(f"Training failed for {symbol}/{timeframe}: Not enough data.", "ERROR"); return
        
        enriched_data['next_candle_up'] = (enriched_data['close'].shift(-1) > enriched_data['open'].shift(-1)).astype(float)
        enriched_data.dropna(subset=['next_candle_up'], inplace=True)
        total_up = enriched_data['next_candle_up'].sum(); total_down = len(enriched_data) - total_up
        if total_up == 0 or total_down == 0:
            self.log_message(f"Training failed for {symbol}/{timeframe}: No up/down outcomes.", "ERROR"); return

        if symbol not in self.priors: self.priors[symbol] = {}
        if symbol not in self.likelihoods: self.likelihoods[symbol] = {}
        if symbol not in self.is_trained: self.is_trained[symbol] = {}

        self.priors[symbol][timeframe] = {'up': total_up / len(enriched_data), 'down': total_down / len(enriched_data)}
        self.likelihoods[symbol][timeframe] = {}

        for module in self.evidence_modules:
            try:
                num_states = module.num_states
                states = module.get_state(enriched_data, symbol)
                if states is None or states.isnull().all(): continue
                self.likelihoods[symbol][timeframe][module.name] = {}
                temp_df = pd.DataFrame({'state': states, 'outcome': enriched_data['next_candle_up']}).dropna()
                counts = temp_df.groupby('state')['outcome'].value_counts().unstack(fill_value=0)
                for state in range(num_states):
                    if state == -1: continue
                    row = counts.loc[state] if state in counts.index else pd.Series([0, 0], index=[0.0, 1.0])
                    p_given_up = (row.get(1.0, 0) + 1) / (total_up + num_states)
                    p_given_down = (row.get(0.0, 0) + 1) / (total_down + num_states)
                    self.likelihoods[symbol][timeframe][module.name][int(state)] = {'p_up': p_given_up, 'p_down': p_given_down}
            except Exception:
                self.log_message(f"Failed to train evidence '{module.name}' on {symbol}/{timeframe}. Details: {traceback.format_exc()}", "ERROR")

        self.is_trained[symbol][timeframe] = True
        self.log_message(f"Training for {symbol}/{timeframe} completed successfully.")

    def predict(self, symbol: str, timeframe: str, latest_data: pd.DataFrame) -> dict:
        if not self.is_trained.get(symbol, {}).get(timeframe, False): return {"error": f"Engine not trained for {symbol}/{timeframe}"}
        if latest_data.empty: return {"error": "No data"}
        
        enriched_data = self.get_enriched_data(latest_data, symbol)
        posterior_up = self.priors[symbol][timeframe]['up']; posterior_down = self.priors[symbol][timeframe]['down']
        used_count = 0; ignored_count = 0; ignored_reasons = []

        for module in self.evidence_modules:
            reason = None
            try:
                current_state = module.get_state(enriched_data, symbol).iloc[-1]
                if pd.isna(current_state) or current_state == -1: reason = "No valid state (NaN or -1)"
                else:
                    probs = self.likelihoods.get(symbol, {}).get(timeframe, {}).get(module.name, {}).get(int(current_state))
                    if probs:
                        if abs(probs['p_up'] - probs['p_down']) > self.threshold:
                            posterior_up *= probs['p_up']; posterior_down *= probs['p_down']; used_count += 1
                        else: reason = "Weak signal"
                    else: reason = "Untrained state"
            except Exception as e:
                reason = "Execution error"; self.log_message(f"Prediction error in '{module.name}' on {symbol}/{timeframe}: {e}", "ERROR")
            if reason: ignored_count += 1; ignored_reasons.append(f"{module.name}: {reason}")
        
        total_posterior = posterior_up + posterior_down
        final_up, final_down = (50.0, 50.0)
        if total_posterior > 1e-30:
            final_up = (posterior_up / total_posterior) * 100
            final_down = (posterior_down / total_posterior) * 100
        return {"up_prob": final_up, "down_prob": final_down, "used_evidence": used_count, "ignored_evidence": ignored_count, "ignored_details": ignored_reasons}