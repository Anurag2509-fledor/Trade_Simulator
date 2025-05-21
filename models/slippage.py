import numpy as np
from sklearn.linear_model import QuantileRegressor
import logging
from datetime import datetime, timedelta
from utils.config import Config

logger = logging.getLogger(__name__)

class SlippageModel:
    def __init__(self):
        self.model = QuantileRegressor(
            quantile=Config.SLIPPAGE_MODEL_PARAMS['quantile'],
            alpha=Config.SLIPPAGE_MODEL_PARAMS['alpha']
        )
        self.orderbook_data = []
        self.max_history = Config.MAX_ORDERBOOK_HISTORY
        self.current_price = 0.0
        self.volatility = 0.0
        self.last_update = None
        self.update_interval = timedelta(seconds=Config.SLIPPAGE_MODEL_PARAMS['update_interval'])
        
    def update(self, data):
        """Update model with new orderbook data"""
        try:
            # Extract current price from mid price of best bid/ask
            best_bid = float(data['bids'][0][0])
            best_ask = float(data['asks'][0][0])
            self.current_price = (best_bid + best_ask) / 2
            
            # Store orderbook data
            self.orderbook_data.append({
                'timestamp': datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00')),
                'price': self.current_price,
                'bids': [[float(price), float(qty)] for price, qty in data['bids']],
                'asks': [[float(price), float(qty)] for price, qty in data['asks']]
            })
            
            # Keep only recent history
            if len(self.orderbook_data) > self.max_history:
                self.orderbook_data.pop(0)
                
            # Update volatility
            self._update_volatility()
            
            # Update model if enough time has passed
            current_time = datetime.now()
            if (self.last_update is None or 
                current_time - self.last_update >= self.update_interval):
                self._update_model()
                self.last_update = current_time
                
        except Exception as e:
            logger.error(f"Error updating slippage model: {str(e)}")
            
    def _update_volatility(self):
        """Update volatility estimate using recent price data"""
        if len(self.orderbook_data) < 2:
            return
            
        prices = [data['price'] for data in self.orderbook_data]
        returns = np.diff(np.log(prices))
        self.volatility = np.std(returns) * np.sqrt(Config.VOLATILITY_WINDOW)  # Annualized volatility
        
    def _update_model(self):
        """Update the quantile regression model"""
        if len(self.orderbook_data) < 10:
            return
            
        # Prepare features
        X = []
        y = []
        
        for i in range(1, len(self.orderbook_data)):
            prev_data = self.orderbook_data[i-1]
            curr_data = self.orderbook_data[i]
            
            # Calculate features
            price_change = (curr_data['price'] - prev_data['price']) / prev_data['price']
            volume = sum(qty for _, qty in curr_data['bids']) + sum(qty for _, qty in curr_data['asks'])
            spread = (curr_data['asks'][0][0] - curr_data['bids'][0][0]) / curr_data['price']
            
            X.append([volume, spread, self.volatility])
            y.append(price_change)
            
        X = np.array(X)
        y = np.array(y)
        
        # Fit model
        try:
            self.model.fit(X, y)
        except Exception as e:
            logger.error(f"Error fitting slippage model: {str(e)}")
            
    def calculate_slippage(self, quantity):
        """
        Calculate expected slippage for a given quantity
        
        Args:
            quantity: Order quantity in base currency
            
        Returns:
            float: Expected slippage as a percentage
        """
        if self.current_price == 0 or len(self.orderbook_data) < 10:
            return 0.0
            
        # Calculate features for prediction
        volume = sum(qty for _, qty in self.orderbook_data[-1]['bids']) + sum(qty for _, qty in self.orderbook_data[-1]['asks'])
        spread = (self.orderbook_data[-1]['asks'][0][0] - self.orderbook_data[-1]['bids'][0][0]) / self.current_price
        
        # Predict slippage
        features = np.array([[volume, spread, self.volatility]])
        predicted_slippage = self.model.predict(features)[0]
        
        # Adjust for order size
        size_factor = min(1.0, quantity / (volume * 0.1))  # Cap at 10% of volume
        adjusted_slippage = predicted_slippage * size_factor
        
        return abs(adjusted_slippage) * 100  # Convert to percentage
        
    def get_latest_slippage(self, quantity=100.0):
        """
        Get the latest slippage estimate for a given quantity
        
        Args:
            quantity: Order quantity in USD
            
        Returns:
            float: Estimated slippage as a percentage
        """
        if self.current_price == 0:
            return 0.0
            
        # Convert USD quantity to base currency
        base_quantity = quantity / self.current_price
        
        # Calculate slippage
        slippage = self.calculate_slippage(base_quantity)
        
        return slippage 