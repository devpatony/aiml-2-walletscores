# Wallet Risk Scoring System for Compound Protocol

## Overview

This comprehensive system analyzes Ethereum wallet addresses and assigns risk scores from 0-1000 based on their interaction history with the Compound lending protocol and general DeFi behavior patterns.

## Quick Start

### Demo Mode (No API Keys Required)
```bash
pip install web3 pandas numpy requests python-dotenv matplotlib seaborn

python demo.py
```

### Production Mode (API Keys Required)
```bash
cp .env.example .env

# Edit .env with your API keys:
# - Etherscan API Key (required)

python main.py
```

## API Keys Setup

### Required: Etherscan API Key
1. Visit https://etherscan.io/apis
2. Sign up for a free account
3. Generate an API key
4. Add to `.env` file: `ETHERSCAN_API_KEY=your_key_here`

### Optional: Web3 Provider (Infura or Alchemy)
**Infura:**
1. Visit https://infura.io/
2. Create a free account and project
3. Add to `.env`: `INFURA_API_KEY=your_key_here`

**Alchemy:**
1. Visit https://alchemy.com/
2. Create a free account
3. Add to `.env`: `ALCHEMY_API_KEY=your_key_here`

## File Structure

```
├── Walletid.csv                    # Input: List of wallet addresses
├── main.py                         # Production analysis with real data
├── demo.py                         # Demo with simulated data
├── compound_data_fetcher.py        # Data collection module
├── risk_scorer.py                  # Risk scoring engine
├── METHODOLOGY.md                  # Detailed methodology explanation
├── .env.example                    # Environment variables template
└── README.md                       # This file
```

## Output

The system generates a CSV file with the following columns:

| Column | Description |
|--------|-------------|
| `wallet_id` | Original wallet address |
| `risk_score` | Risk score (0-1000, lower = safer) |
| `risk_category` | Text classification of risk level |
| `total_transactions` | Total transaction count |
| `compound_interactions` | Compound protocol interactions |
| `current_balance_eth` | Current ETH balance |
| `transaction_volume_eth` | Historical transaction volume |
| `transaction_frequency` | Transactions per day |
| `failed_transaction_rate` | Percentage of failed transactions |
| `unique_counterparties` | Number of unique addresses interacted with |
| `error` | Any processing errors |
| `processed_at` | Analysis timestamp |

## Risk Score Interpretation

| Score Range | Risk Level | Description |
|-------------|------------|-------------|
| 0-200 | Very Low Risk | Highly experienced DeFi users with excellent track records |
| 201-400 | Low Risk | Experienced users with good transaction history |
| 401-600 | Medium Risk | Moderate experience with some potential concerns |
| 601-800 | High Risk | Limited experience or concerning behavioral patterns |
| 801-1000 | Very High Risk | New users, poor track record, or analysis errors |

## Risk Factors and Weights

The scoring system considers multiple factors with the following weights:

- **Protocol Experience (25%)**: Compound interaction history
- **Transaction Volume (20%)**: Total ETH transacted
- **Transaction Frequency (15%)**: Regular activity patterns
- **Balance Stability (15%)**: Current ETH holdings
- **Transaction Failure Rate (10%)**: Success rate of transactions
- **Counterparty Diversity (10%)**: Breadth of interactions
- **Recent Activity (5%)**: Current engagement level

## Features

### Data Collection
- **Comprehensive Transaction History**: Fetches complete transaction records
- **Compound Protocol Focus**: Analyzes specific DeFi lending interactions
- **Balance Analysis**: Current and historical balance tracking
- **Multi-Source Support**: Etherscan, Infura, Alchemy APIs

### Risk Analysis
- **Multi-Factor Scoring**: Seven distinct risk factors
- **Weighted Algorithm**: Research-backed factor importance
- **Scalable Processing**: Handles large wallet lists efficiently
- **Error Handling**: Graceful failure recovery

### Output and Reporting
- **CSV Export**: Standard format for further analysis
- **Summary Statistics**: Comprehensive analysis overview
- **Progress Tracking**: Real-time processing updates
- **Incremental Saves**: Prevents data loss during long runs

## Example Usage

### Analyzing a Custom Wallet List
```python
from main import WalletRiskAnalyzer

analyzer = WalletRiskAnalyzer()

results = analyzer.process_wallet_list(
    wallet_file="my_wallets.csv",
    output_file="my_risk_scores.csv",
    delay_seconds=0.5 
)
```

### Single Wallet Analysis
```python
from compound_data_fetcher import CompoundDataFetcher
from risk_scorer import WalletRiskScorer

fetcher = CompoundDataFetcher()
scorer = WalletRiskScorer()

wallet = "0x742d35Cc6aB09a6E4a1a2c45a7b5F52B8C6D5E45"
tx_data = fetcher.get_wallet_transactions(wallet)
compound_data = fetcher.get_compound_interactions(wallet)
balance_data = fetcher.get_wallet_balance_history(wallet)

risk_result = scorer.calculate_risk_score(
    wallet, tx_data, compound_data, balance_data
)
```

## Performance Considerations

### Rate Limiting
- Default 0.5 second delay between API calls
- Configurable via `delay_seconds` parameter
- Respects Etherscan's 5 calls/second limit

### Large Dataset Processing
- Incremental progress saving every 10 wallets
- Memory-efficient streaming processing
- Parallel API calls where possible

### Error Recovery
- Automatic retry on temporary failures
- Graceful degradation for missing data
- Comprehensive error logging

## Troubleshooting

### Common Issues

**"API Key Invalid" Error**
- Verify API key in `.env` file
- Check Etherscan account status
- Ensure no extra spaces in key

**"Rate Limited" Error**
- Increase `delay_seconds` parameter
- Check API key usage limits
- Verify account tier on Etherscan

**"Web3 Connection Failed"**
- Optional for basic analysis
- Check Infura/Alchemy key if needed
- System will fallback to Etherscan only

**"No Transaction Data"**
- Wallet may be new or inactive
- Check wallet address format
- Verify network (system uses Ethereum mainnet)

### Debug Mode
Add verbose logging by modifying the scripts:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Limitations

1. **API Dependencies**: Requires external API access
2. **Ethereum Mainnet Only**: Currently supports ETH mainnet only
3. **Historical Focus**: Emphasizes past behavior over current state
4. **Rate Limits**: Processing speed limited by API constraints

## Future Enhancements

- Multi-chain support (Polygon, BSC, etc.)
- Real-time risk monitoring
- Machine learning-based pattern detection
- Integration with other DeFi protocols
- Advanced visualization dashboard

## Contributing

To contribute improvements:
1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit a pull request

