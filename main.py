import sys
import asyncio
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import QThread, pyqtSignal
from websocket_client import WebSocketClient
from ui.input_panel import InputPanel
from ui.output_panel import OutputPanel
from models.market_impact import AlmgrenChrissModel
from models.slippage import SlippageModel
from models.maker_taker import MakerTakerModel
from utils.config import Config

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format=Config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TradeSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GoQuant Trade Simulator")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize components
        self.init_ui()
        self.init_models()
        self.init_websocket()
        
    def init_ui(self):
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Create input and output panels
        self.input_panel = InputPanel()
        self.output_panel = OutputPanel()
        
        # Add panels to layout
        layout.addWidget(self.input_panel)
        layout.addWidget(self.output_panel)
        
    def init_models(self):
        self.market_impact_model = AlmgrenChrissModel()
        self.slippage_model = SlippageModel()
        self.maker_taker_model = MakerTakerModel()
        
    def init_websocket(self):
        self.ws_client = WebSocketClient()
        self.ws_client.data_received.connect(self.process_market_data)
        
    def process_market_data(self, data):
        try:
            # Process incoming market data
            self.market_impact_model.update(data)
            self.slippage_model.update(data)
            self.maker_taker_model.update(data)
            
            # Update UI with new calculations
            self.update_output_panel()
            
        except Exception as e:
            logger.error(f"Error processing market data: {str(e)}")
            
    def update_output_panel(self):
        # Get latest calculations from models
        market_impact = self.market_impact_model.get_latest_impact()
        slippage = self.slippage_model.get_latest_slippage()
        maker_taker = self.maker_taker_model.get_latest_proportion()
        
        # Update output panel
        self.output_panel.update_values({
            'market_impact': market_impact,
            'slippage': slippage,
            'maker_taker': maker_taker
        })

def main():
    app = QApplication(sys.argv)
    simulator = TradeSimulator()
    simulator.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 