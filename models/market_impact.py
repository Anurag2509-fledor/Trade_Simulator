import numpy as np
from datetime import datetime
import logging
from utils.config import Config

logger = logging.getLogger(__name__)

class AlmgrenChrissModel:
    def __init__(self):
        self.eta = Config.MARKET_IMPACT_PARAMS['eta']  # Temporary market impact parameter
        self.gamma = Config.MARKET_IMPACT_PARAMS['gamma']  # Permanent market impact parameter
        self.sigma = 0.0  # Volatility
        self.risk_aversion = Config.MARKET_IMPACT_PARAMS['risk_aversion']  # Risk aversion parameter
        self.current_price = 0.0
        self.orderbook_data = []
        self.max_history = Config.MAX_ORDERBOOK_HISTORY  # Maximum number of orderbook snapshots to keep
        
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
                
            # Update volatility estimate
            self._update_volatility()
            
        except Exception as e:
            logger.error(f"Error updating market impact model: {str(e)}")
            
    def _update_volatility(self):
        """Update volatility estimate using recent price data"""
        if len(self.orderbook_data) < 2:
            return
            
        prices = [data['price'] for data in self.orderbook_data]
        returns = np.diff(np.log(prices))
        self.sigma = np.std(returns) * np.sqrt(Config.VOLATILITY_WINDOW)  # Annualized volatility
        
    def calculate_market_impact(self, quantity, time_horizon=1.0):
        """
        Calculate market impact using Almgren-Chriss model
        
        Args:
            quantity: Order quantity in base currency
            time_horizon: Trading horizon in days
            
        Returns:
            tuple: (temporary_impact, permanent_impact, total_impact)
        """
        if self.current_price == 0:
            return 0.0, 0.0, 0.0
            
        # Calculate temporary market impact
        temp_impact = self.eta * (quantity / self.current_price) * np.sqrt(quantity / time_horizon)
        
        # Calculate permanent market impact
        perm_impact = self.gamma * (quantity / self.current_price)
        
        # Calculate total market impact
        total_impact = temp_impact + perm_impact
        
        return temp_impact, perm_impact, total_impact
        
    def get_latest_impact(self, quantity=100.0):
        """
        Get the latest market impact estimate for a given quantity
        
        Args:
            quantity: Order quantity in USD
            
        Returns:
            float: Estimated market impact as a percentage
        """
        if self.current_price == 0:
            return 0.0
            
        # Convert USD quantity to base currency
        base_quantity = quantity / self.current_price
        
        # Calculate market impact
        _, _, total_impact = self.calculate_market_impact(base_quantity)
        
        # Convert to percentage
        impact_percentage = total_impact * 100
        
        return impact_percentage
        
    def get_optimal_execution(self, quantity, time_horizon=1.0):
        """
        Calculate optimal execution trajectory using Almgren-Chriss model
        
        Args:
            quantity: Total order quantity
            time_horizon: Trading horizon in days
            
        Returns:
            tuple: (optimal_trajectory, expected_cost)
        """
        if self.current_price == 0:
            return [], 0.0
            
        # Model parameters
        T = time_horizon  # Trading horizon
        N = 100  # Number of time steps
        dt = T / N  # Time step size
        
        # Calculate optimal trajectory
        kappa = np.sqrt(self.risk_aversion * self.sigma**2 / self.eta)
        sinh_kappa_T = np.sinh(kappa * T)
        sinh_kappa_t = np.sinh(kappa * np.arange(0, T + dt, dt))
        
        optimal_trajectory = quantity * (sinh_kappa_t / sinh_kappa_T)
        
        # Calculate expected cost
        expected_cost = (
            self.eta * quantity**2 / T +  # Temporary impact cost
            self.gamma * quantity**2 / 2 +  # Permanent impact cost
            self.risk_aversion * self.sigma**2 * quantity**2 * T / 3  # Risk cost
        )
        
        return optimal_trajectory, expected_cost 