from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QComboBox,
                             QLineEdit, QFormLayout, QGroupBox)
from PyQt6.QtCore import pyqtSignal

class InputPanel(QWidget):
    input_changed = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Exchange Selection
        exchange_group = QGroupBox("Exchange Settings")
        exchange_layout = QFormLayout()
        
        self.exchange_combo = QComboBox()
        self.exchange_combo.addItem("OKX")
        self.exchange_combo.currentTextChanged.connect(self.on_input_changed)
        exchange_layout.addRow("Exchange:", self.exchange_combo)
        
        self.asset_combo = QComboBox()
        self.asset_combo.addItems(["BTC-USDT", "ETH-USDT", "SOL-USDT"])
        self.asset_combo.currentTextChanged.connect(self.on_input_changed)
        exchange_layout.addRow("Asset:", self.asset_combo)
        
        exchange_group.setLayout(exchange_layout)
        layout.addWidget(exchange_group)
        
        # Order Parameters
        order_group = QGroupBox("Order Parameters")
        order_layout = QFormLayout()
        
        self.order_type_combo = QComboBox()
        self.order_type_combo.addItem("Market")
        self.order_type_combo.currentTextChanged.connect(self.on_input_changed)
        order_layout.addRow("Order Type:", self.order_type_combo)
        
        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("Enter quantity in USD")
        self.quantity_input.textChanged.connect(self.on_input_changed)
        order_layout.addRow("Quantity (USD):", self.quantity_input)
        
        order_group.setLayout(order_layout)
        layout.addWidget(order_group)
        
        # Market Parameters
        market_group = QGroupBox("Market Parameters")
        market_layout = QFormLayout()
        
        self.volatility_input = QLineEdit()
        self.volatility_input.setPlaceholderText("Enter volatility percentage")
        self.volatility_input.textChanged.connect(self.on_input_changed)
        market_layout.addRow("Volatility (%):", self.volatility_input)
        
        self.fee_tier_combo = QComboBox()
        self.fee_tier_combo.addItems(["Tier 1", "Tier 2", "Tier 3", "Tier 4"])
        self.fee_tier_combo.currentTextChanged.connect(self.on_input_changed)
        market_layout.addRow("Fee Tier:", self.fee_tier_combo)
        
        market_group.setLayout(market_layout)
        layout.addWidget(market_group)
        
        # Add stretch to push widgets to the top
        layout.addStretch()
        
        self.setLayout(layout)
        
    def on_input_changed(self):
        try:
            quantity = float(self.quantity_input.text()) if self.quantity_input.text() else 0
            volatility = float(self.volatility_input.text()) if self.volatility_input.text() else 0
        except ValueError:
            quantity = 0
            volatility = 0
            
        input_data = {
            'exchange': self.exchange_combo.currentText(),
            'asset': self.asset_combo.currentText(),
            'order_type': self.order_type_combo.currentText(),
            'quantity': quantity,
            'volatility': volatility,
            'fee_tier': self.fee_tier_combo.currentText()
        }
        
        self.input_changed.emit(input_data)
        
    def get_input_values(self):
        return {
            'exchange': self.exchange_combo.currentText(),
            'asset': self.asset_combo.currentText(),
            'order_type': self.order_type_combo.currentText(),
            'quantity': float(self.quantity_input.text()) if self.quantity_input.text() else 0,
            'volatility': float(self.volatility_input.text()) if self.volatility_input.text() else 0,
            'fee_tier': self.fee_tier_combo.currentText()
        } 