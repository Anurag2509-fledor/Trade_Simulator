class Config:
    # WebSocket Configuration
    WEBSOCKET_URL = "wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP"
    RECONNECT_DELAY = 5  # seconds
    MAX_RECONNECT_ATTEMPTS = 5

    # Model Parameters
    MARKET_IMPACT_PARAMS = {
        'eta': 0.1,  # Temporary market impact parameter
        'gamma': 0.1,  # Permanent market impact parameter
        'risk_aversion': 0.1,  # Risk aversion parameter
    }

    SLIPPAGE_MODEL_PARAMS = {
        'quantile': 0.5,  # Median regression
        'alpha': 0.1,  # Regularization parameter
        'update_interval': 300,  # Update model every 5 minutes
    }

    MAKER_TAKER_PARAMS = {
        'max_iter': 1000,  # Maximum iterations for logistic regression
        'update_interval': 300,  # Update model every 5 minutes
    }

    # Data Management
    MAX_ORDERBOOK_HISTORY = 1000  # Maximum number of orderbook snapshots to keep
    VOLATILITY_WINDOW = 252  # Number of days for annualized volatility calculation

    # Fee Tiers (OKX)
    FEE_TIERS = {
        'Tier 1': {'maker': 0.0008, 'taker': 0.001},  # 0.08% / 0.10%
        'Tier 2': {'maker': 0.0007, 'taker': 0.0009},  # 0.07% / 0.09%
        'Tier 3': {'maker': 0.0006, 'taker': 0.0008},  # 0.06% / 0.08%
        'Tier 4': {'maker': 0.0005, 'taker': 0.0007},  # 0.05% / 0.07%
    }

    # UI Configuration
    UI_REFRESH_RATE = 1000  # milliseconds
    PROGRESS_BAR_MAX = 100

    # Logging Configuration
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = 'trade_simulator.log'

    # Performance Monitoring
    LATENCY_WINDOW = 100  # Number of samples to keep for latency calculation
    TICK_RATE_WINDOW = 60  # Number of seconds to calculate tick rate over 