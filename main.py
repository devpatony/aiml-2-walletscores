
import pandas as pd
import numpy as np
import json
import time
from datetime import datetime
import os
from compound_data_fetcher import CompoundDataFetcher
from risk_scorer import WalletRiskScorer

class WalletRiskAnalyzer:
    def __init__(self):
        self.data_fetcher = CompoundDataFetcher()
        self.risk_scorer = WalletRiskScorer()
        self.results = []
        
    def process_wallet(self, wallet_address: str) -> dict:
        """
        Process a single wallet and return risk analysis
        """
        print(f"Processing wallet: {wallet_address}")
        
        try:
            print("  - Fetching transaction history...")
            tx_data = self.data_fetcher.get_wallet_transactions(wallet_address)
            
            if not tx_data['success']:
                print(f"  - Error fetching transactions: {tx_data['error']}")
                return self._create_error_result(wallet_address, f"Transaction fetch error: {tx_data['error']}")
            
            print("  - Analyzing transaction patterns...")
            tx_metrics = self.data_fetcher.analyze_transaction_patterns(tx_data['transactions'])
            
            print("  - Fetching Compound interactions...")
            compound_data = self.data_fetcher.get_compound_interactions(wallet_address)
            
            if not compound_data['success']:
                print(f"  - Error fetching Compound data: {compound_data['error']}")
                compound_data = {'success': True, 'compound_count': 0, 'compound_transactions': []}
            
            print("  - Fetching balance information...")
            balance_data = self.data_fetcher.get_wallet_balance_history(wallet_address)
            
            if not balance_data['success']:
                print(f"  - Error fetching balance: {balance_data['error']}")
                balance_data = {'success': True, 'current_balance_eth': 0}

            print("  - Calculating risk score...")
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
    
    def process_wallet_list(self, wallet_file: str, output_file: str = 'wallet_risk_scores.csv', 
                          delay_seconds: float = 0.5) -> pd.DataFrame:
        """
        Process all wallets from CSV file and save results
        """
        print(f"Loading wallet addresses from {wallet_file}")
        
        wallets_df = pd.read_csv(wallet_file)
        wallet_addresses = wallets_df['wallet_id'].tolist()
        
        print(f"Found {len(wallet_addresses)} wallet addresses to process")
        
        results = []
        
        for i, wallet_address in enumerate(wallet_addresses, 1):
            print(f"\n[{i}/{len(wallet_addresses)}] Processing wallet: {wallet_address}")
            
            try:
                result = self.process_wallet(wallet_address)
                results.append(result)
                
                if i % 10 == 0: 
                    self._save_intermediate_results(results, f"temp_{output_file}")
                    print(f"  - Saved intermediate results ({i} wallets processed)")
 
                if delay_seconds > 0:
                    time.sleep(delay_seconds)
                    
            except Exception as e:
                print(f"  - Critical error processing wallet {wallet_address}: {str(e)}")
                error_result = self._create_error_result(wallet_address, f"Critical error: {str(e)}")
                results.append(error_result)
        
        df_results = self._create_results_dataframe(results)
        
        df_results.to_csv(output_file, index=False)
        print(f"\nFinal results saved to {output_file}")
        
        self._print_summary_statistics(df_results)
        
        return df_results
    
    def _save_intermediate_results(self, results: list, filename: str):
        """
        Save intermediate results to avoid data loss
        """
        df = self._create_results_dataframe(results)
        df.to_csv(filename, index=False)
    
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
                'processed_at': datetime.now().isoformat()
            }
            processed_results.append(processed_result)
        
        return pd.DataFrame(processed_results)
    
    def _print_summary_statistics(self, df: pd.DataFrame):
        """
        Print summary statistics of the risk analysis
        """
        print("\n" + "="*60)
        print("WALLET RISK ANALYSIS SUMMARY")
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
    Main execution function
    """
    print("Wallet Risk Scoring System for Compound Protocol")
    print("="*50)
    
    analyzer = WalletRiskAnalyzer()
    
    input_file = "Walletid.csv"
    output_file = "wallet_risk_scores.csv"
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found!")
        return
    
    try:
        results_df = analyzer.process_wallet_list(
            wallet_file=input_file,
            output_file=output_file,
            delay_seconds=0.5  
        )
        
        print(f"\nProcessing complete! Results saved to '{output_file}'")
        
    except KeyboardInterrupt:
        print("\nProcessing interrupted by user")
    except Exception as e:
        print(f"\nCritical error: {str(e)}")

if __name__ == "__main__":
    main()
