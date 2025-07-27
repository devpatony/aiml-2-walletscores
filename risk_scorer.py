
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import json

class WalletRiskScorer:
    def __init__(self):
        # Risk factor weights (total = 1.0)
        self.weights = {
            'transaction_volume': 0.20,      # 20% - High volume = lower risk
            'transaction_frequency': 0.15,   # 15% - Regular activity = lower risk
            'protocol_experience': 0.25,     # 25% - DeFi experience = lower risk
            'balance_stability': 0.15,       # 15% - Stable balance = lower risk
            'failure_rate': 0.10,           # 10% - High failure rate = higher risk
            'counterparty_diversity': 0.10,  # 10% - More diverse = lower risk
            'recent_activity': 0.05         # 5% - Recent activity = lower risk
        }
        
        self.risk_params = {
            'min_transaction_volume_eth': 1.0,      # Minimum volume for low risk
            'min_transaction_frequency': 0.1,       # Minimum txs per day
            'min_compound_interactions': 5,         # Minimum Compound txs
            'max_failure_rate': 0.05,              # Maximum acceptable failure rate
            'min_balance_eth': 0.1,                # Minimum balance for activity
            'activity_window_days': 30,            # Recent activity window
            'min_unique_counterparties': 10        # Minimum counterparties
        }
    
    def calculate_transaction_volume_score(self, metrics: Dict) -> float:
        """
        Score based on total transaction volume
        Higher volume = lower risk (more established user)
        """
        volume_eth = metrics.get('total_value_eth', 0)
        
        if volume_eth >= 1000:     # Very high volume
            return 0.1
        elif volume_eth >= 100:    # High volume
            return 0.2
        elif volume_eth >= 10:     # Medium volume
            return 0.4
        elif volume_eth >= 1:      # Low volume
            return 0.6
        else:                      # Very low volume
            return 0.9
    
    def calculate_frequency_score(self, metrics: Dict) -> float:
        frequency = metrics.get('transaction_frequency', 0)
        
        if frequency >= 1.0:       # Daily transactions
            return 0.1
        elif frequency >= 0.5:     # Every 2 days
            return 0.2
        elif frequency >= 0.1:     # Weekly
            return 0.4
        elif frequency > 0:        # Sporadic
            return 0.7
        else:                      # No activity
            return 1.0
    
    def calculate_protocol_experience_score(self, compound_data: Dict) -> float:
        compound_count = compound_data.get('compound_count', 0)
        
        if compound_count >= 50:    # Very experienced
            return 0.05
        elif compound_count >= 20:  # Experienced
            return 0.15
        elif compound_count >= 10:  # Moderate experience
            return 0.3
        elif compound_count >= 5:   # Some experience
            return 0.5
        elif compound_count > 0:    # Minimal experience
            return 0.7
        else:                       # No Compound experience
            return 0.95
    
    def calculate_balance_stability_score(self, balance_data: Dict, metrics: Dict) -> float:
        current_balance = balance_data.get('current_balance_eth', 0)
        
        volume_eth = metrics.get('total_value_eth', 0)
        balance_to_volume_ratio = current_balance / max(volume_eth, 0.001)
        
        if current_balance >= 100:         # Very high balance
            base_score = 0.05
        elif current_balance >= 10:        # High balance
            base_score = 0.15
        elif current_balance >= 1:         # Medium balance
            base_score = 0.3
        elif current_balance >= 0.1:       # Low balance
            base_score = 0.6
        else:                              # Very low balance
            base_score = 0.9
        
        # Adjust based on balance-to-volume ratio
        if balance_to_volume_ratio > 0.1:   # Good balance relative to activity
            adjustment = -0.1
        elif balance_to_volume_ratio < 0.01: # Low balance relative to activity
            adjustment = 0.2
        else:
            adjustment = 0
        
        return max(0, min(1, base_score + adjustment))
    
    def calculate_failure_rate_score(self, metrics: Dict) -> float:
        failure_rate = metrics.get('failed_transaction_rate', 0)
        
        if failure_rate == 0:           # No failures
            return 0.0
        elif failure_rate <= 0.02:      # Very low failure rate
            return 0.1
        elif failure_rate <= 0.05:      # Low failure rate
            return 0.3
        elif failure_rate <= 0.1:       # Moderate failure rate
            return 0.6
        else:                           # High failure rate
            return 1.0
    
    def calculate_counterparty_diversity_score(self, metrics: Dict) -> float:
        unique_counterparties = metrics.get('unique_counterparties', 0)
        total_transactions = metrics.get('total_transactions', 1)
        
        diversity_ratio = unique_counterparties / total_transactions
        
        if unique_counterparties >= 100:    # Very diverse
            return 0.05
        elif unique_counterparties >= 50:   # Diverse
            return 0.15
        elif unique_counterparties >= 20:   # Moderately diverse
            return 0.3
        elif unique_counterparties >= 10:   # Limited diversity
            return 0.5
        elif unique_counterparties > 0:     # Very limited
            return 0.8
        else:                               # No diversity
            return 1.0
    
    def calculate_recent_activity_score(self, metrics: Dict) -> float:
        time_span_days = metrics.get('time_span_days', 0)
        
        if time_span_days <= 30:          # Very recent activity
            return 0.1
        elif time_span_days <= 90:        # Recent activity
            return 0.3
        elif time_span_days <= 180:       # Somewhat recent
            return 0.5
        elif time_span_days <= 365:       # Old activity
            return 0.7
        else:                             # Very old activity
            return 1.0
    
    def calculate_risk_score(self, wallet_address: str, transaction_metrics: Dict, 
                           compound_data: Dict, balance_data: Dict) -> Dict:
        
        # Calculate individual component scores (0-1, where 1 = highest risk)
        scores = {}
        
        scores['transaction_volume'] = self.calculate_transaction_volume_score(transaction_metrics)
        scores['transaction_frequency'] = self.calculate_frequency_score(transaction_metrics)
        scores['protocol_experience'] = self.calculate_protocol_experience_score(compound_data)
        scores['balance_stability'] = self.calculate_balance_stability_score(balance_data, transaction_metrics)
        scores['failure_rate'] = self.calculate_failure_rate_score(transaction_metrics)
        scores['counterparty_diversity'] = self.calculate_counterparty_diversity_score(transaction_metrics)
        scores['recent_activity'] = self.calculate_recent_activity_score(transaction_metrics)
        
        weighted_score = sum(scores[factor] * self.weights[factor] for factor in scores)
        
        risk_score = int(weighted_score * 1000)
        
        if risk_score <= 200:
            risk_category = "Very Low Risk"
        elif risk_score <= 400:
            risk_category = "Low Risk"
        elif risk_score <= 600:
            risk_category = "Medium Risk"
        elif risk_score <= 800:
            risk_category = "High Risk"
        else:
            risk_category = "Very High Risk"
        
        return {
            'wallet_address': wallet_address,
            'risk_score': risk_score,
            'risk_category': risk_category,
            'component_scores': scores,
            'weighted_score': weighted_score,
            'transaction_metrics': transaction_metrics,
            'compound_data': compound_data,
            'balance_data': balance_data
        }
    
    def get_risk_explanation(self, risk_result: Dict) -> str:
        score = risk_result['risk_score']
        components = risk_result['component_scores']
        
        explanation = f"Risk Score: {score}/1000 ({risk_result['risk_category']})\n\n"
        explanation += "Key Risk Factors:\n"
        
        sorted_components = sorted(components.items(), key=lambda x: x[1] * self.weights[x[0]], reverse=True)
        
        for factor, score in sorted_components[:3]:
            weighted_contribution = score * self.weights[factor] * 1000
            explanation += f"- {factor.replace('_', ' ').title()}: {score:.2f} (contributes {weighted_contribution:.0f} points)\n"
        
        return explanation
