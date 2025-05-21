from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFormLayout,
                             QGroupBox, QProgressBar)
from PyQt6.QtCore import Qt

class OutputPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Market Impact
        impact_group = QGroupBox("Market Impact Analysis")
        impact_layout = QFormLayout()
        
        self.impact_label = QLabel("0.00%")
        impact_layout.addRow("Expected Impact:", self.impact_label)
        
        self.impact_bar = QProgressBar()
        self.impact_bar.setRange(0, 100)
        impact_layout.addRow("Impact Level:", self.impact_bar)
        
        impact_group.setLayout(impact_layout)
        layout.addWidget(impact_group)
        
        # Slippage
        slippage_group = QGroupBox("Slippage Analysis")
        slippage_layout = QFormLayout()
        
        self.slippage_label = QLabel("0.00%")
        slippage_layout.addRow("Expected Slippage:", self.slippage_label)
        
        self.slippage_bar = QProgressBar()
        self.slippage_bar.setRange(0, 100)
        slippage_layout.addRow("Slippage Level:", self.slippage_bar)
        
        slippage_group.setLayout(slippage_layout)
        layout.addWidget(slippage_group)
        
        # Fees
        fees_group = QGroupBox("Fee Analysis")
        fees_layout = QFormLayout()
        
        self.fees_label = QLabel("$0.00")
        fees_layout.addRow("Expected Fees:", self.fees_label)
        
        self.fees_bar = QProgressBar()
        self.fees_bar.setRange(0, 100)
        fees_layout.addRow("Fee Level:", self.fees_bar)
        
        fees_group.setLayout(fees_layout)
        layout.addWidget(fees_group)
        
        # Total Cost
        cost_group = QGroupBox("Total Cost Analysis")
        cost_layout = QFormLayout()
        
        self.total_cost_label = QLabel("$0.00")
        cost_layout.addRow("Total Cost:", self.total_cost_label)
        
        self.cost_breakdown_label = QLabel("Impact: $0.00 | Slippage: $0.00 | Fees: $0.00")
        cost_layout.addRow("Cost Breakdown:", self.cost_breakdown_label)
        
        cost_group.setLayout(cost_layout)
        layout.addWidget(cost_group)
        
        # Maker/Taker Analysis
        maker_taker_group = QGroupBox("Maker/Taker Analysis")
        maker_taker_layout = QFormLayout()
        
        self.maker_taker_label = QLabel("50% / 50%")
        maker_taker_layout.addRow("Maker/Taker Ratio:", self.maker_taker_label)
        
        self.maker_taker_bar = QProgressBar()
        self.maker_taker_bar.setRange(0, 100)
        maker_taker_layout.addRow("Maker Proportion:", self.maker_taker_bar)
        
        maker_taker_group.setLayout(maker_taker_layout)
        layout.addWidget(maker_taker_group)
        
        # Performance Metrics
        perf_group = QGroupBox("Performance Metrics")
        perf_layout = QFormLayout()
        
        self.latency_label = QLabel("0.00 ms")
        perf_layout.addRow("Processing Latency:", self.latency_label)
        
        self.tick_rate_label = QLabel("0 ticks/s")
        perf_layout.addRow("Tick Rate:", self.tick_rate_label)
        
        perf_group.setLayout(perf_layout)
        layout.addWidget(perf_group)
        
        # Add stretch to push widgets to the top
        layout.addStretch()
        
        self.setLayout(layout)
        
    def update_values(self, values):
        # Update market impact
        if 'market_impact' in values:
            impact = values['market_impact']
            self.impact_label.setText(f"{impact:.2f}%")
            self.impact_bar.setValue(int(impact * 100))
            
        # Update slippage
        if 'slippage' in values:
            slippage = values['slippage']
            self.slippage_label.setText(f"{slippage:.2f}%")
            self.slippage_bar.setValue(int(slippage * 100))
            
        # Update fees
        if 'fees' in values:
            fees = values['fees']
            self.fees_label.setText(f"${fees:.2f}")
            self.fees_bar.setValue(int(fees * 100))
            
        # Update total cost
        if all(k in values for k in ['market_impact', 'slippage', 'fees']):
            total = values['market_impact'] + values['slippage'] + values['fees']
            self.total_cost_label.setText(f"${total:.2f}")
            self.cost_breakdown_label.setText(
                f"Impact: ${values['market_impact']:.2f} | "
                f"Slippage: ${values['slippage']:.2f} | "
                f"Fees: ${values['fees']:.2f}"
            )
            
        # Update maker/taker
        if 'maker_taker' in values:
            maker, taker = values['maker_taker']
            self.maker_taker_label.setText(f"{maker:.1f}% / {taker:.1f}%")
            self.maker_taker_bar.setValue(int(maker))
            
        # Update performance metrics
        if 'latency' in values:
            self.latency_label.setText(f"{values['latency']:.2f} ms")
        if 'tick_rate' in values:
            self.tick_rate_label.setText(f"{values['tick_rate']:.1f} ticks/s") 