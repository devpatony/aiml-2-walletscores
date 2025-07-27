# Wallet Risk Scoring System for Compound Protocol

## Overview
This system analyzes wallet addresses and assigns risk scores ranging from 0-1000 based on their transaction history, DeFi experience, and behavioral patterns specifically related to the Compound lending protocol.

## Methodology

### Data Collection Methods

#### 1. Transaction History Collection
- **Source**: Etherscan API for comprehensive transaction history
- **Scope**: All historical transactions for each wallet address
- **Data Points**: Transaction value, frequency, success/failure rates, counterparties
- **Alternative**: Web3 direct blockchain queries for real-time data

#### 2. Compound Protocol Interactions
- **Compound V2 Contracts**: cDAI, cUSDC, cUSDT, cETH, cWBTC, Comptroller
- **Compound V3 Contracts**: cUSDCv3, cWETHv3 (Comet protocol)
- **Interaction Types**: Supply, borrow, repay, liquidation events
- **Analysis**: Count and patterns of DeFi protocol usage

#### 3. Balance and Portfolio Analysis
- **Current Balance**: ETH holdings as indicator of financial capacity
- **Balance History**: Stability and growth patterns over time
- **Portfolio Diversity**: Analysis of different token interactions

### Feature Selection Rationale

#### Core Risk Factors (Weighted Scoring System)

1. **Transaction Volume (20% weight)**
   - **Rationale**: Higher transaction volume indicates established user with more experience
   - **Scoring**: 
     - Very High (≥1000 ETH): 0.1 risk multiplier
     - High (≥100 ETH): 0.2 risk multiplier  
     - Medium (≥10 ETH): 0.4 risk multiplier
     - Low (≥1 ETH): 0.6 risk multiplier
     - Very Low (<1 ETH): 0.9 risk multiplier

2. **Protocol Experience (25% weight)**
   - **Rationale**: Experience with Compound protocol indicates understanding of DeFi risks
   - **Metrics**: Number of Compound interactions, complexity of operations
   - **Scoring**:
     - Very Experienced (≥50 interactions): 0.05 risk multiplier
     - Experienced (≥20): 0.15 risk multiplier
     - Moderate (≥10): 0.3 risk multiplier
     - Some (≥5): 0.5 risk multiplier
     - Minimal (1-4): 0.7 risk multiplier
     - None (0): 0.95 risk multiplier

3. **Transaction Frequency (15% weight)**
   - **Rationale**: Regular activity indicates ongoing engagement and monitoring
   - **Calculation**: Transactions per day over activity period
   - **Scoring**: Higher frequency = lower risk

4. **Balance Stability (15% weight)**
   - **Rationale**: Higher balance indicates more "skin in the game"
   - **Metrics**: Current ETH balance, balance-to-volume ratio
   - **Scoring**: Higher stable balance = lower risk

5. **Transaction Failure Rate (10% weight)**
   - **Rationale**: High failure rate indicates poor planning or understanding
   - **Calculation**: Failed transactions / Total transactions
   - **Scoring**: 
     - No failures: 0.0 risk multiplier
     - Very low (≤2%): 0.1 risk multiplier
     - Low (≤5%): 0.3 risk multiplier
     - Moderate (≤10%): 0.6 risk multiplier
     - High (>10%): 1.0 risk multiplier

6. **Counterparty Diversity (10% weight)**
   - **Rationale**: Diverse interactions indicate broader ecosystem participation
   - **Metrics**: Number of unique addresses interacted with
   - **Scoring**: More diversity = lower risk

7. **Recent Activity (5% weight)**
   - **Rationale**: Recent activity indicates current engagement
   - **Metrics**: Time since last transaction, activity in last 30 days
   - **Scoring**: More recent activity = lower risk

### Scoring Method

#### Weighted Risk Calculation
```
Risk Score = Σ(Factor Score × Weight) × 1000
```

Where each factor score ranges from 0-1 (1 = highest risk)

#### Risk Categories
- **0-200**: Very Low Risk (Highly experienced, stable users)
- **201-400**: Low Risk (Experienced users with good track record)
- **401-600**: Medium Risk (Moderate experience, some concerns)
- **601-800**: High Risk (Limited experience, concerning patterns)
- **801-1000**: Very High Risk (New users, poor track record, or errors)

### Risk Indicators Justification

#### Why These Factors Matter for DeFi Lending

1. **Protocol Experience is Heavily Weighted (25%)**
   - DeFi protocols like Compound involve complex financial mechanics
   - Users must understand concepts like collateralization ratios, liquidation risks
   - Historical interaction with Compound demonstrates practical knowledge
   - Experienced users are less likely to make costly mistakes

2. **Transaction Volume Indicates Financial Sophistication (20%)**
   - Higher volume users typically have more resources and experience
   - Larger transactions suggest understanding of gas costs and timing
   - Volume correlates with ability to handle potential losses

3. **Failure Rate Reveals Understanding (10%)**
   - Failed transactions often indicate insufficient gas, wrong parameters, or poor timing
   - High failure rates suggest lack of understanding or preparation
   - Critical for protocols where mistakes can be costly

4. **Balance Stability Shows Commitment (15%)**
   - Users with higher balances have more at stake
   - Stable balances indicate long-term commitment to ecosystem
   - Balance-to-activity ratio shows responsible financial management

5. **Frequency and Recency Indicate Engagement (20% combined)**
   - Regular activity shows ongoing monitoring and engagement
   - Recent activity indicates current awareness of market conditions
   - Inactive users may be out of touch with current protocol changes

### Data Normalization and Edge Cases

#### Handling Missing or Invalid Data
- **No Compound Interactions**: Assigned high risk score (0.95 multiplier)
- **Very New Wallets**: Penalized for lack of history
- **API Failures**: Assigned maximum risk score (999) for safety
- **Zero Balance**: Considered high risk unless justified by recent activity

#### Normalization Techniques
- **Log Scaling**: Applied to transaction volumes to handle extreme outliers
- **Percentile Ranking**: Used for relative scoring within dataset
- **Time Decay**: Recent activity weighted more heavily than historical

### Scalability Considerations

#### System Design for Large-Scale Analysis
1. **Batch Processing**: Processes wallets in configurable batch sizes
2. **Rate Limiting**: Respects API rate limits with configurable delays
3. **Error Recovery**: Handles API failures gracefully with retries
4. **Incremental Processing**: Saves progress to prevent data loss
5. **Modular Architecture**: Easy to update scoring algorithms or add new data sources

#### Performance Optimizations
- **Caching**: Transaction data cached to avoid repeated API calls
- **Parallel Processing**: Multiple wallets processed concurrently when possible
- **Data Compression**: Efficient storage of historical analysis results

### Validation and Backtesting

#### Model Validation Approaches
1. **Historical Analysis**: Compare scores with known good/bad actors
2. **Cross-Validation**: Test scoring consistency across different time periods
3. **Expert Review**: Manual validation of edge cases and outliers
4. **A/B Testing**: Compare different scoring algorithms

### Limitations and Future Improvements

#### Current Limitations
1. **API Dependency**: Relies on external APIs for data collection
2. **Historical Bias**: Heavily weights past behavior over current state
3. **Protocol Specificity**: Focused on Compound; may not capture other DeFi experience
4. **Market Conditions**: Doesn't account for bull/bear market contexts

#### Potential Enhancements
1. **Multi-Protocol Analysis**: Include Aave, Uniswap, other DeFi protocols
2. **Real-Time Monitoring**: Continuous score updates based on new transactions
3. **Machine Learning**: Advanced pattern recognition for fraud detection
4. **Social Analysis**: Include governance participation, community engagement
5. **Market Context**: Adjust scoring based on current market volatility

### Usage Instructions

#### Prerequisites
1. Etherscan API key (free at etherscan.io/apis)
2. Optional: Infura or Alchemy API key for Web3 connections
3. Python 3.8+ with required packages

#### Running the Analysis
```bash
pip install web3 pandas numpy requests python-dotenv

cp .env.example .env

python main.py

python demo.py
```

#### Output Format
The system generates a CSV file with the following columns:
- `wallet_id`: Original wallet address
- `risk_score`: Numerical score (0-1000)
- `risk_category`: Text classification
- `total_transactions`: Count of all transactions
- `compound_interactions`: Count of Compound protocol interactions
- `current_balance_eth`: Current ETH balance
- `transaction_volume_eth`: Total historical volume
- `transaction_frequency`: Average transactions per day
- `failed_transaction_rate`: Percentage of failed transactions
- `unique_counterparties`: Number of unique interaction addresses
- `error`: Any processing errors encountered
- `processed_at`: Timestamp of analysis

This methodology provides a comprehensive, justified, and scalable approach to assessing wallet risk in the context of DeFi lending protocols.
