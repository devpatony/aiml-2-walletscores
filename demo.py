
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from risk_scorer import WalletRiskScorer

class DemoWalletRiskAnalyzer:
    def __init__(self):
        self.risk_scorer = WalletRiskScorer()
        random.seed(42)
        np.random.seed(42)
    
    def simulate_wallet_data(self, wallet_address: str) -> dict:
        """
        Simulate realistic wallet data for demonstration
        """
        total_transactions = random.randint(10, 500)
        compound_interactions = random.randint(0, min(50, total_transactions // 5))
        
        wallet_hash = hash(wallet_address) % 5
        
        if wallet_hash == 0:  # Low risk wallet
            transaction_volume = random.uniform(50, 1000)
            balance = random.uniform(10, 100)
            failure_rate = random.uniform(0, 0.02)
            frequency = random.uniform(0.5, 2.0)
            counterparties = random.randint(20, 100)
        elif wallet_hash == 1:  # Medium risk wallet
            transaction_volume = random.uniform(10, 100)
            balance = random.uniform(1, 20)
            failure_rate = random.uniform(0.02, 0.08)
            frequency = random.uniform(0.1, 0.8)
            counterparties = random.randint(10, 50)
        elif wallet_hash == 2:  # High risk wallet
            transaction_volume = random.uniform(1, 20)
            balance = random.uniform(0.1, 5)
            failure_rate = random.uniform(0.05, 0.15)
            frequency = random.uniform(0.01, 0.3)
            counterparties = random.randint(3, 20)
        elif wallet_hash == 3:  # New/inexperienced wallet
            transaction_volume = random.uniform(0.5, 10)
            balance = random.uniform(0.1, 2)
            failure_rate = random.uniform(0.1, 0.3)
            frequency = random.uniform(0.1, 0.5)
            counterparties = random.randint(1, 10)
            compound_interactions = random.randint(0, 5)
        else:  # Inactive/old wallet
            transaction_volume = random.uniform(5, 50)
            balance = random.uniform(0.01, 1)
            failure_rate = random.uniform(0, 0.1)
            frequency = random.uniform(0.001, 0.1)
            counterparties = random.randint(5, 30)
        
        avg_transaction_value = transaction_volume / max(total_transactions, 1)
        time_span_days = random.uniform(30, 365)
        failed_transactions = int(total_transactions * failure_rate)
        
        transaction_metrics = {
            'total_transactions': total_transactions,
            'avg_transaction_value': avg_transaction_value,
            'transaction_frequency': frequency,
            'failed_transactions': failed_transactions,
            'failed_transaction_rate': failure_rate,
            'unique_counterparties': counterparties,
            'time_span_days': time_span_days,
            'total_value_eth': transaction_volume
        }
        
        compound_data = {
            'success': True,
            'compound_count': compound_interactions,
            'compound_transactions': []
        }
        
        balance_data = {
            'success': True,
            'current_balance_eth': balance,
            'current_balance_wei': int(balance * 10**18)
        }
        
        return transaction_metrics, compound_data, balance_data
    
    def process_wallet(self, wallet_address: str) -> dict:
        """
        Process a single wallet using simulated data
        """
        print(f"Processing wallet: {wallet_address} (DEMO MODE)")
        
        try:
            tx_metrics, compound_data, balance_data = self.simulate_wallet_data(wallet_address)
            
            risk_result = self.risk_scorer.calculate_risk_score(
                wallet_address, tx_metrics, compound_data, balance_data
            )
            
            print(f"  - Risk Score: {risk_result['risk_score']}/1000 ({risk_result['risk_category']})")
            
            return risk_result
            
        except Exception as e:
            print(f"  - Error processing wallet: {str(e)}")
            return self._create_error_result(wallet_address, str(e))
    
    def _create_error_result(self, wallet_address: str, error_message: str) -> dict:
        """
        Create a result for wallets that couldn't be processed
        """
        return {
            'wallet_address': wallet_address,
            'risk_score': 999,
            'risk_category': 'Error - Unable to Assess',
            'error': error_message,
            'component_scores': {},
            'transaction_metrics': {},
            'compound_data': {},
            'balance_data': {}
        }
    
    def process_wallet_list(self, wallet_file: str, output_file: str = 'demo_wallet_risk_scores.csv') -> pd.DataFrame:
        """
        Process all wallets from CSV file using simulated data
        """
        print(f"Loading wallet addresses from {wallet_file}")
        print("Running in DEMO MODE with simulated data")
    
        wallets_df = pd.read_csv(wallet_file)
        wallet_addresses = wallets_df['wallet_id'].tolist()
        
        print(f"Found {len(wallet_addresses)} wallet addresses to process")
        
        results = []
        
        for i, wallet_address in enumerate(wallet_addresses, 1):
            print(f"\n[{i}/{len(wallet_addresses)}] Processing: {wallet_address}")
            
            try:
                result = self.process_wallet(wallet_address)
                results.append(result)
                
            except Exception as e:
                print(f"  - Critical error: {str(e)}")
                error_result = self._create_error_result(wallet_address, f"Critical error: {str(e)}")
                results.append(error_result)
        
        df_results = self._create_results_dataframe(results)
        
        df_results.to_csv(output_file, index=False)
        print(f"\nDemo results saved to {output_file}")
        
        self._print_summary_statistics(df_results)
        
        return df_results
    
    def _create_results_dataframe(self, results: list) -> pd.DataFrame:
        """
        Convert results to DataFrame with required columns
        """
        processed_results = []
        
        for result in results:
            processed_result = {
                'wallet_id': result['wallet_address'],
                'risk_score': result['risk_score'],
                'risk_category': result['risk_category'],
                'total_transactions': result.get('transaction_metrics', {}).get('total_transactions', 0),
                'compound_interactions': result.get('compound_data', {}).get('compound_count', 0),
                'current_balance_eth': result.get('balance_data', {}).get('current_balance_eth', 0),
                'transaction_volume_eth': result.get('transaction_metrics', {}).get('total_value_eth', 0),
                'transaction_frequency': result.get('transaction_metrics', {}).get('transaction_frequency', 0),
                'failed_transaction_rate': result.get('transaction_metrics', {}).get('failed_transaction_rate', 0),
                'unique_counterparties': result.get('transaction_metrics', {}).get('unique_counterparties', 0),
                'error': result.get('error', ''),
                'processed_at': datetime.now().isoformat(),
                'demo_mode': True
            }
            processed_results.append(processed_result)
        
        return pd.DataFrame(processed_results)
    
    def _print_summary_statistics(self, df: pd.DataFrame):
        """
        Print summary statistics of the risk analysis
        """
        print("\n" + "="*60)
        print("DEMO WALLET RISK ANALYSIS SUMMARY")
        print("="*60)
        
        print(f"Total wallets processed: {len(df)}")
        print(f"Successful analyses: {len(df[df['error'] == ''])}")
        print(f"Failed analyses: {len(df[df['error'] != ''])}")
        
        if len(df[df['error'] == '']) > 0:
            successful_df = df[df['error'] == '']
            
            print(f"\nRisk Score Statistics:")
            print(f"  Average risk score: {successful_df['risk_score'].mean():.1f}")
            print(f"  Median risk score: {successful_df['risk_score'].median():.1f}")
            print(f"  Minimum risk score: {successful_df['risk_score'].min()}")
            print(f"  Maximum risk score: {successful_df['risk_score'].max()}")
            
            print(f"\nRisk Category Distribution:")
            risk_dist = successful_df['risk_category'].value_counts()
            for category, count in risk_dist.items():
                percentage = (count / len(successful_df)) * 100
                print(f"  {category}: {count} ({percentage:.1f}%)")
            
            print(f"\nTransaction Statistics:")
            print(f"  Average transactions per wallet: {successful_df['total_transactions'].mean():.1f}")
            print(f"  Average Compound interactions: {successful_df['compound_interactions'].mean():.1f}")
            print(f"  Average balance (ETH): {successful_df['current_balance_eth'].mean():.4f}")

def main():
    """
    Main demo execution function
    """
    print("DEMO: Wallet Risk Scoring System for Compound Protocol")
    print("Using simulated data for demonstration purposes")
    print("="*60)
    
    analyzer = DemoWalletRiskAnalyzer()
    
    input_file = "Walletid.csv"
    output_file = "demo_wallet_risk_scores.csv"
    
    try:
        results_df = analyzer.process_wallet_list(
            wallet_file=input_file,
            output_file=output_file
        )
        
        print(f"\nDemo processing complete! Results saved to '{output_file}'")
        print("\nNote: This demo uses simulated data. For real analysis, use main.py with proper API keys.")
        
    except KeyboardInterrupt:
        print("\nProcessing interrupted by user")
    except Exception as e:
        print(f"\nCritical error: {str(e)}")

if __name__ == "__main__":
    main()
