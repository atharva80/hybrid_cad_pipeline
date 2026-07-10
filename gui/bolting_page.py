import os
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from gui.styles import C

class BoltingRow(QFrame):
    def __init__(self, comp, page, parent=None):
        super().__init__(parent)
        self.comp = comp
        self.page = page
        
        self.setStyleSheet(f"""
            BoltingRow {{
                background: {C['surface']};
                border-radius: 8px;
                border-bottom: 1px solid rgba(255,255,255,0.05);
            }}
            BoltingRow:hover {{
                background: rgba(255,255,255,0.03);
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        
        name = QLabel(comp)
        name.setFont(QFont("Inter", 12, QFont.Bold))
        name.setStyleSheet("color: white;")
        
        btn_isolate = QPushButton("Isolate in SimLab")
        btn_isolate.setCursor(Qt.PointingHandCursor)
        btn_isolate.setStyleSheet("background: #0078D7; color: white; font-weight: bold; padding: 6px 16px; border-radius: 4px;")
        btn_isolate.clicked.connect(self._on_isolate)
        
        layout.addWidget(name, 1)
        layout.addWidget(btn_isolate)

    def _on_isolate(self):
        self.page.isolateRequested.emit(self.comp)

class BoltConfigPanel(QFrame):
    generateRequested = Signal(dict)
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        lbl = QLabel("Solid Bolt Parameters")
        lbl.setFont(QFont("Inter", 16, QFont.Bold))
        layout.addWidget(lbl)
        
        # Presets
        p_lay = QHBoxLayout()
        p_lay.addWidget(QLabel("Preset:"))
        self.preset_cb = QComboBox()
        self.preset_cb.addItems(["Custom", "M3 x 10", "M4 x 15", "M5 x 20"])
        self.preset_cb.currentIndexChanged.connect(self._apply_preset)
        p_lay.addWidget(self.preset_cb, 1)
        layout.addLayout(p_lay)
        
        # Parameters
        self.inputs = {}
        for param, default in [("D1 (Head Dia)", "6.0"), ("D2 (Shaft Dia)", "3.0"), 
                               ("L1 (Head Ht)", "2.0"), ("L2 (Total Len)", "12.0"), ("L5 (Shaft upper)", "10.0"),
                               ("Mesh Size", "2.0"), ("Circum. Elems", "8")]:
            row = QHBoxLayout()
            row.addWidget(QLabel(param))
            inp = QLineEdit(default)
            inp.setFixedWidth(60)
            inp.setStyleSheet(f"background: {C['bg']}; color: white; border: 1px solid {C['border']}; border-radius: 4px; padding: 4px;")
            self.inputs[param] = inp
            row.addWidget(inp)
            layout.addLayout(row)
            
        self.reverse_cb = QCheckBox("Reverse Bolt Direction")
        layout.addWidget(self.reverse_cb)
        
        layout.addStretch()
        
        gen_btn = QPushButton("Generate Bolts at Selected Edges")
        gen_btn.setStyleSheet("background: #2E7D52; color: white; font-weight: bold; font-size: 14px; padding: 12px; border-radius: 6px;")
        gen_btn.setCursor(Qt.PointingHandCursor)
        gen_btn.clicked.connect(self._on_generate)
        layout.addWidget(gen_btn)
        
        # instructions
        inst = QLabel("1. Click 'Isolate' on a component.\n2. Select circular arc edges in SimLab.\n3. Click Generate above.")
        inst.setWordWrap(True)
        inst.setStyleSheet("color: rgba(255,255,255,0.5); font-size: 11px;")
        layout.addWidget(inst)
        
    def _apply_preset(self):
        p = self.preset_cb.currentText()
        if p == "M3 x 10":
            self.inputs["D1 (Head Dia)"].setText("5.5")
            self.inputs["D2 (Shaft Dia)"].setText("3.0")
            self.inputs["L1 (Head Ht)"].setText("3.0")
            self.inputs["L2 (Total Len)"].setText("13.0")
            self.inputs["L5 (Shaft upper)"].setText("10.0")
        elif p == "M4 x 15":
            self.inputs["D1 (Head Dia)"].setText("7.0")
            self.inputs["D2 (Shaft Dia)"].setText("4.0")
            self.inputs["L1 (Head Ht)"].setText("4.0")
            self.inputs["L2 (Total Len)"].setText("19.0")
            self.inputs["L5 (Shaft upper)"].setText("15.0")
        elif p == "M5 x 20":
            self.inputs["D1 (Head Dia)"].setText("8.5")
            self.inputs["D2 (Shaft Dia)"].setText("5.0")
            self.inputs["L1 (Head Ht)"].setText("5.0")
            self.inputs["L2 (Total Len)"].setText("25.0")
            self.inputs["L5 (Shaft upper)"].setText("20.0")

    def _on_generate(self):
        config = {k: v.text() for k, v in self.inputs.items()}
        config["Reverse"] = self.reverse_cb.isChecked()
        self.generateRequested.emit(config)

class BoltingPage(QWidget):
    isolateRequested = Signal(str)
    generateRequested = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(0,0,0,0)
        root_layout.setSpacing(0)
        
        # Left side: Component list
        left = QWidget()
        layout = QVBoxLayout(left)
        layout.setContentsMargins(48, 32, 24, 32)
        
        header = QLabel("Bolting Setup")
        header.setFont(QFont("Inter", 24, QFont.Bold))
        layout.addWidget(header)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.list_container = QWidget()
        self.list_container.setStyleSheet("background: transparent;")
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 8, 16)
        self.list_layout.setSpacing(8)
        self.list_layout.setAlignment(Qt.AlignTop)
        
        self.scroll.setWidget(self.list_container)
        layout.addWidget(self.scroll, 1)
        
        root_layout.addWidget(left, 1)
        
        # Right side: Config panel
        self.config_panel = BoltConfigPanel()
        self.config_panel.setFixedWidth(360)
        self.config_panel.setStyleSheet(f"background: {C['surface']}; border-left: 1px solid {C['border']};")
        self.config_panel.generateRequested.connect(self.generateRequested.emit)
        root_layout.addWidget(self.config_panel)

    def populate(self, components):
        while self.list_layout.count():
            child = self.list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        # Simple flat list for bolting
        for c in components:
            row = BoltingRow(c, self)
            self.list_layout.addWidget(row)
