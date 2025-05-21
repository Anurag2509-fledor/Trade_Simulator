import numpy as np
from sklearn.linear_model import LogisticRegression
import logging
from datetime import datetime, timedelta
from utils.config import Config

logger = logging.getLogger(__name__)

class MakerTakerModel:
    def __init__(self):
        self.model = LogisticRegression(max_iter=Config.MAKER_TAKER_PARAMS['max_iter'])
        self.orderbook_data = []
        self.max_history = Config.MAX_ORDERBOOK_HISTORY
        self.current_price = 0.0
        self.volatility = 0.0
        self.last_update = None
        self.update_interval = timedelta(seconds=Config.MAKER_TAKER_PARAMS['update_interval'])
        
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
            logger.error(f"Error updating maker/taker model: {str(e)}")
            
    def _update_volatility(self):
        """Update volatility estimate using recent price data"""
        if len(self.orderbook_data) < 2:
            return
            
        prices = [data['price'] for data in self.orderbook_data]
        returns = np.diff(np.log(prices))
        self.volatility = np.std(returns) * np.sqrt(Config.VOLATILITY_WINDOW)  # Annualized volatility
        
    def _update_model(self):
        """Update the logistic regression model"""
        if len(self.orderbook_data) < 10:
            return
            
        # Prepare features and labels
        X = []
        y = []
        
        for i in range(1, len(self.orderbook_data)):
            prev_data = self.orderbook_data[i-1]
            curr_data = self.orderbook_data[i]
            
            # Calculate features
            price_change = (curr_data['price'] - prev_data['price']) / prev_data['price']
            spread = (curr_data['asks'][0][0] - curr_data['bids'][0][0]) / curr_data['price']
            bid_volume = sum(qty for _, qty in curr_data['bids'])
            ask_volume = sum(qty for _, qty in curr_data['asks'])
            volume_ratio = bid_volume / (bid_volume + ask_volume) if (bid_volume + ask_volume) > 0 else 0.5
            
            # Determine if price moved up (1) or down (0)
            price_direction = 1 if price_change > 0 else 0
            
            X.append([spread, volume_ratio, self.volatility])
            y.append(price_direction)
            
        X = np.array(X)
        y = np.array(y)
        
        # Fit model
        try:
            self.model.fit(X, y)
        except Exception as e:
            logger.error(f"Error fitting maker/taker model: {str(e)}")
            
    def predict_maker_taker(self):
        """
        Predict maker/taker proportion based on current market conditions
        
        Returns:
            tuple: (maker_proportion, taker_proportion)
        """
        if len(self.orderbook_data) < 10:
            return 0.5, 0.5
            
        # Calculate current features
        curr_data = self.orderbook_data[-1]
        spread = (curr_data['asks'][0][0] - curr_data['bids'][0][0]) / self.current_price
        bid_volume = sum(qty for _, qty in curr_data['bids'])
        ask_volume = sum(qty for _, qty in curr_data['asks'])
        volume_ratio = bid_volume / (bid_volume + ask_volume) if (bid_volume + ask_volume) > 0 else 0.5
        
        # Predict probability of price increase
        features = np.array([[spread, volume_ratio, self.volatility]])
        prob_increase = self.model.predict_proba(features)[0][1]
        
        # Convert to maker/taker proportions
        # Higher probability of price increase suggests more maker orders
        maker_proportion = prob_increase
        taker_proportion = 1 - maker_proportion
        
        return maker_proportion, taker_proportion
        
    def get_latest_proportion(self):
        """
        Get the latest maker/taker proportion estimate
        
        Returns:
            tuple: (maker_proportion, taker_proportion)
        """
        if len(self.orderbook_data) < 10:
            return 0.5, 0.5
            
        maker_prop, taker_prop = self.predict_maker_taker()
        
        # Convert to percentages
        maker_pct = maker_prop * 100
        taker_pct = taker_prop * 100
        
        return maker_pct, taker_pct 