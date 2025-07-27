"""
Compound Protocol Data Fetcher
Fetches transaction history and account data from Compound V2/V3
"""

import requests
import pandas as pd
import json
from web3 import Web3
from typing import Dict, List, Optional
import time
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

class CompoundDataFetcher:
    def __init__(self):
        self.compound_v2_contracts = {
            'cDAI': '0x5d3a536e4d6dbd6114cc1ead35777bab948e3643',
            'cUSDC': '0x39aa39c021dfbae8fac545936693ac917d5e7563',
            'cUSDT': '0xf650c3d88d12db855b8bf7d11be6c55a4e07dcc9',
            'cETH': '0x4ddc2d193948926d02f9b1fe9e1daa0718270ed5',
            'cWBTC': '0xc11b1268c1a384e55c48c2391d8d480264a3a7f4',
            'comptroller': '0x3d9819210a31b4961b30ef54be2aed79b9c9cd3b'
        }
        
        self.compound_v3_contracts = {
            'cUSDCv3': '0xc3d688b66703497daa19211eedff47f25384cdc3',
            'cWETHv3': '0xa17581a9e3356d9a858b789d68b4d866e593ae94'
        }
        
        # Initialize Web3 connection (using Infura - you may need to add your own API key)
        infura_url = f"https://mainnet.infura.io/v3/{os.getenv('INFURA_API_KEY', 'YOUR_INFURA_KEY')}"
        self.w3 = Web3(Web3.HTTPProvider(infura_url))
        
        self.etherscan_api_key = os.getenv('ETHERSCAN_API_KEY', 'YourEtherscanAPIKey')
        
    def get_wallet_transactions(self, wallet_address: str) -> Dict:
        """
        Fetch transaction history for a wallet address using Etherscan API
        """
        url = "https://api.etherscan.io/api"
        params = {
            'module': 'account',
            'action': 'txlist',
            'address': wallet_address,
            'startblock': 0,
            'endblock': 99999999,
            'page': 1,
            'offset': 10000,
            'sort': 'desc',
            'apikey': self.etherscan_api_key
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['status'] == '1':
                return {'success': True, 'transactions': data['result']}
            else:
                return {'success': False, 'error': data.get('message', 'Unknown error')}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_compound_interactions(self, wallet_address: str) -> Dict:
        """
        Filter transactions to find Compound protocol interactions
        """
        tx_data = self.get_wallet_transactions(wallet_address)
        
        if not tx_data['success']:
            return tx_data
            
        compound_txs = []
        all_compound_addresses = {**self.compound_v2_contracts, **self.compound_v3_contracts}
        
        for tx in tx_data['transactions']:
            if (tx['to'].lower() in [addr.lower() for addr in all_compound_addresses.values()] or
                tx['from'].lower() == wallet_address.lower()):
                
                if any(addr.lower() in tx['to'].lower() for addr in all_compound_addresses.values()):
                    compound_txs.append(tx)
        
        return {
            'success': True,
            'compound_transactions': compound_txs,
            'total_transactions': len(tx_data['transactions']),
            'compound_count': len(compound_txs)
        }
    
    def get_current_compound_positions(self, wallet_address: str) -> Dict:
        """
        Get current positions in Compound protocol (if Web3 connection is available)
        """
        try:
            if not self.w3.is_connected():
                return {'success': False, 'error': 'Web3 connection not available'}
            
            return {
                'success': True,
                'positions': {
                    'supplied': {},
                    'borrowed': {},
                    'health_factor': 0,
                    'total_collateral_usd': 0,
                    'total_debt_usd': 0
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_wallet_balance_history(self, wallet_address: str) -> Dict:
        """
        Get ETH balance history for the wallet
        """
        try:
            current_balance = self.w3.eth.get_balance(wallet_address)
            current_balance_eth = self.w3.from_wei(current_balance, 'ether')
            
            return {
                'success': True,
                'current_balance_eth': float(current_balance_eth),
                'current_balance_wei': current_balance
            }
            
        except Exception as e:
            url = "https://api.etherscan.io/api"
            params = {
                'module': 'account',
                'action': 'balance',
                'address': wallet_address,
                'tag': 'latest',
                'apikey': self.etherscan_api_key
            }
            
            try:
                response = requests.get(url, params=params)
                data = response.json()
                
                if data['status'] == '1':
                    balance_wei = int(data['result'])
                    balance_eth = balance_wei / 10**18
                    
                    return {
                        'success': True,
                        'current_balance_eth': balance_eth,
                        'current_balance_wei': balance_wei
                    }
                else:
                    return {'success': False, 'error': data.get('message', 'Unknown error')}
                    
            except Exception as e2:
                return {'success': False, 'error': str(e2)}
    
    def analyze_transaction_patterns(self, transactions: List[Dict]) -> Dict:
        """
        Analyze transaction patterns for risk assessment
        """
        if not transactions:
            return {
                'total_transactions': 0,
                'avg_transaction_value': 0,
                'transaction_frequency': 0,
                'failed_transactions': 0,
                'unique_counterparties': 0,
                'time_span_days': 0
            }
        
        total_txs = len(transactions)
        total_value = sum(float(tx.get('value', 0)) for tx in transactions)
        avg_value = total_value / total_txs if total_txs > 0 else 0
        
        failed_txs = sum(1 for tx in transactions if tx.get('isError') == '1')
        
        counterparties = set()
        for tx in transactions:
            counterparties.add(tx.get('to', ''))
            counterparties.add(tx.get('from', ''))
        
        timestamps = [int(tx.get('timeStamp', 0)) for tx in transactions if tx.get('timeStamp')]
        if timestamps:
            time_span = (max(timestamps) - min(timestamps)) / (24 * 3600)  # days
            frequency = total_txs / max(time_span, 1)  # txs per day
        else:
            time_span = 0
            frequency = 0
        
        return {
            'total_transactions': total_txs,
            'avg_transaction_value': avg_value,
            'transaction_frequency': frequency,
            'failed_transactions': failed_txs,
            'failed_transaction_rate': failed_txs / total_txs if total_txs > 0 else 0,
            'unique_counterparties': len(counterparties),
            'time_span_days': time_span,
            'total_value_eth': total_value / 10**18
        }
