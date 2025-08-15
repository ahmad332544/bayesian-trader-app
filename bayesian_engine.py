# bayesian_engine.py
import pandas as pd
import numpy as np
import pkgutil
import importlib
import traceback

class BayesianEngine:
    def __init__(self, evidence_strength_threshold: float = 0.05):
        self.evidence_modules = self._load_evidence_modules()
        self.prior_up = 0.5
        self.prior_down = 0.5
        self.likelihoods = {}
        self.is_trained = False
        self.threshold = evidence_strength_threshold
        self.log = []
        self.log_message(f"BayesianEngine: Loaded {len(self.evidence_modules)} evidence modules successfully.")

    def log_message(self, message: str, level: str = "INFO"):
        log_entry = f"[{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}] [{level}] {message}"
        print(log_entry)
        self.log.append(log_entry)
        if len(self.log) > 200: self.log.pop(0)

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

    def get_all_requirements(self) -> list[dict]:
        all_reqs = []
        for module in self.evidence_modules:
            try: all_reqs.extend(module.declare_requirements())
            except Exception: self.log_message(f"Failed to get requirements from '{module.name}'", "ERROR")
        
        unique_reqs = [dict(t) for t in {tuple(sorted(d.items())) for d in all_reqs}]
        return unique_reqs

    def train(self, data: pd.DataFrame):
        self.log_message("Starting training process...")
        if data.empty or len(data) < 50: # Increased minimum size
            self.log_message("Training failed: Not enough data.", "ERROR")
            return
            
        data['next_candle_up'] = (data['close'].shift(-1) > data['open'].shift(-1)).astype(float)
        data.dropna(inplace=True)

        total_up = data['next_candle_up'].sum()
        total_down = len(data) - total_up

        if total_up == 0 or total_down == 0:
            self.log_message("Training failed: No up/down outcomes in historical data.", "ERROR")
            return

        self.prior_up = total_up / len(data)
        self.prior_down = total_down / len(data)
        self.log_message(f"Priors calculated: P(Up)={self.prior_up:.2f}, P(Down)={self.prior_down:.2f}")

        for module in self.evidence_modules:
            try:
                states = module.get_state(data)
                if states is None or states.isnull().all():
                    self.log_message(f"Skipping training for '{module.name}': No valid states returned.", "WARNING")
                    continue

                self.likelihoods[module.name] = {}
                counts = data.groupby(states)['next_candle_up'].value_counts().unstack(fill_value=0)
                all_possible_states = states.dropna().unique()
                num_states = len(all_possible_states)

                for state in all_possible_states:
                    row = counts.loc[state] if state in counts.index else pd.Series([0, 0], index=[0.0, 1.0])
                    p_given_up = (row.get(1.0, 0) + 1) / (total_up + num_states)
                    p_given_down = (row.get(0.0, 0) + 1) / (total_down + num_states)
                    self.likelihoods[module.name][int(state)] = {'p_up': p_given_up, 'p_down': p_given_down}
                
                self.log_message(f"Successfully trained evidence: {module.name}")

            except Exception:
                self.log_message(f"Failed to train evidence '{module.name}'. Error: {traceback.format_exc()}", "ERROR")

        self.is_trained = True
        self.log_message("Training process completed successfully.")

    def predict(self, latest_data: pd.DataFrame) -> dict:
        if not self.is_trained: return {"error": "Engine not trained"}
        if latest_data.empty: return {"error": "No data"}

        posterior_up = self.prior_up
        posterior_down = self.prior_down
        used_count = 0
        ignored_count = 0

        for module in self.evidence_modules:
            try:
                current_state = module.get_state(latest_data).iloc[-1]
                if pd.isna(current_state):
                    ignored_count += 1
                    continue
                
                probs = self.likelihoods.get(module.name, {}).get(int(current_state))
                
                if probs:
                    if abs(probs['p_up'] - probs['p_down']) > self.threshold:
                        posterior_up *= probs['p_up']
                        posterior_down *= probs['p_down']
                        used_count += 1
                    else: ignored_count += 1
                else: ignored_count += 1
            except Exception: ignored_count += 1
        
        total_posterior = posterior_up + posterior_down
        if total_posterior > 1e-12:
            final_up = (posterior_up / total_posterior) * 100
            final_down = (posterior_down / total_posterior) * 100
        else: final_up, final_down = 50.0, 50.0

        return {"up_prob": final_up, "down_prob": final_down, "used_evidence": used_count, "ignored_evidence": ignored_count}