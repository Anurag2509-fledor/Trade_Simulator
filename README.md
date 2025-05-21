# GoQuant Trade Simulator

A high-performance trade simulator that leverages real-time market data to estimate transaction costs and market impact for cryptocurrency trading.

## Features

- Real-time L2 orderbook data processing
- Market impact analysis using Almgren-Chriss model
- Slippage estimation using regression models
- Fee calculation based on exchange tiers
- Maker/Taker proportion prediction
- Performance metrics and latency monitoring

## Setup

1. Install Python 3.8 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## Project Structure

- `main.py`: Application entry point
- `websocket_client.py`: WebSocket connection and data handling
- `models/`: Contains market impact and regression models
- `ui/`: User interface components
- `utils/`: Utility functions and helpers
- `config/`: Configuration files

## Models

### Almgren-Chriss Model
The market impact model is implemented based on the Almgren-Chriss framework, considering:
- Temporary market impact
- Permanent market impact
- Risk aversion parameter
- Volatility

### Slippage Estimation
Uses quantile regression to estimate expected slippage based on:
- Order size
- Market depth
- Recent price movements
- Volatility

### Maker/Taker Prediction
Logistic regression model to predict the proportion of maker vs taker orders based on:
- Historical order flow
- Market conditions
- Time of day
- Recent trading patterns

## Performance Optimization

The system implements several optimization techniques:
- Asynchronous WebSocket handling
- Efficient data structures for orderbook management
- Optimized regression model calculations
- Memory-efficient data processing
- Multi-threaded UI updates

## License

This project is proprietary and confidential. 