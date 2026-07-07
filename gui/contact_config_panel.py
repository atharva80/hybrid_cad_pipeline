import os
import json
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from gui.styles import C, SS

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _load_contact_defaults():
    path = os.path.join(_ROOT, "config", "contact_config", "default_contacts.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

class ContactConfigPanel(QWidget):
    contactRequested = Signal(str, dict) # contact_id, config

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_contact_id = None
        self._current_config = {}
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QWidget()
        header.setStyleSheet(f"background: {C['card']}; border-bottom: 1px solid {C['border']};")
        h_layout = QVBoxLayout(header)
        h_layout.setContentsMargins(24, 24, 24, 24)
        h_layout.setSpacing(4)
        
        self.title_lbl = QLabel("Contact Config")
        self.title_lbl.setFont(QFont("Inter", 16, QFont.Bold))
        self.title_lbl.setWordWrap(True)
        h_layout.addWidget(self.title_lbl)
        
        self.subtitle_lbl = QLabel("Select a contact to edit parameters")
        self.subtitle_lbl.setStyleSheet(f"color: {C['text_dim']}; font-size: 12px;")
        h_layout.addWidget(self.subtitle_lbl)
        
        layout.addWidget(header)
        
        # Scroll area for form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.form_w = QWidget()
        self.form_w.setStyleSheet("background: transparent;")
        self.form_l = QVBoxLayout(self.form_w)
        self.form_l.setContentsMargins(24, 24, 24, 24)
        self.form_l.setSpacing(16)
        self.form_l.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(self.form_w)
        layout.addWidget(scroll, 1)
        
        # Form widgets
        self.inputs = {}
        
        self._add_field("master", "Master Body", "QLineEdit", read_only=True)
        self._add_field("slave", "Slave Body", "QLineEdit", read_only=True)
        self._add_field("contact_type", "Contact Type", "QComboBox", options=["Tied (Type 2)", "Friction (Type 24)", "Slide (Type 7)"])
        self._add_field("solver", "Solver", "QComboBox", options=["Radioss", "OptiStruct"])
        self._add_field("tolerance", "Tolerance (mm)", "QDoubleSpinBox")
        self._add_field("friction", "Friction Coeff", "QDoubleSpinBox")
        
        # Action button
        action_w = QWidget()
        action_w.setStyleSheet(f"background: {C['card']}; border-top: 1px solid {C['border']};")
        a_layout = QVBoxLayout(action_w)
        a_layout.setContentsMargins(24, 24, 24, 24)
        
        self.dispatch_btn = QPushButton("Create Contact")
        self.dispatch_btn.setObjectName("primary_btn")
        self.dispatch_btn.setMinimumHeight(44)
        self.dispatch_btn.clicked.connect(self._on_dispatch)
        self.dispatch_btn.setEnabled(False)
        a_layout.addWidget(self.dispatch_btn)
        
        layout.addWidget(action_w)
        
        # Hide form initially
        self.form_w.setVisible(False)

    def _add_field(self, key, label, widget_type, options=None, read_only=False):
        container = QWidget()
        cl = QVBoxLayout(container)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(6)
        
        lbl = QLabel(label)
        lbl.setFont(QFont("Inter", 11, QFont.Bold))
        cl.addWidget(lbl)
        
        if widget_type == "QLineEdit":
            w = QLineEdit()
            w.setReadOnly(read_only)
            w.setStyleSheet(f"background: {C['surface'] if not read_only else C['bg']}; color: {C['text']}; padding: 8px; border-radius: 4px; border: 1px solid {C['border']};")
        elif widget_type == "QComboBox":
            w = QComboBox()
            if options:
                w.addItems(options)
            w.setStyleSheet(f"background: {C['surface']}; color: {C['text']}; padding: 8px; border-radius: 4px; border: 1px solid {C['border']};")
        elif widget_type == "QDoubleSpinBox":
            w = QDoubleSpinBox()
            w.setDecimals(3)
            w.setSingleStep(0.01)
            w.setRange(0.0, 10.0)
            w.setStyleSheet(f"background: {C['surface']}; color: {C['text']}; padding: 8px; border-radius: 4px; border: 1px solid {C['border']};")
            
        cl.addWidget(w)
        self.form_l.addWidget(container)
        self.inputs[key] = w

    def load_contact(self, contact_id, config):
        self._current_contact_id = contact_id
        self._current_config = config
        
        self.title_lbl.setText(contact_id.replace("_", " "))
        self.subtitle_lbl.setText(f"Master: {config.get('master', '')} | Slave: {config.get('slave', '')}")
        
        # Populate
        self.inputs["master"].setText(config.get("master", ""))
        self.inputs["slave"].setText(config.get("slave", ""))
        
        c_type = config.get("contact_type", "Tied (Type 2)")
        idx = self.inputs["contact_type"].findText(c_type)
        if idx >= 0: self.inputs["contact_type"].setCurrentIndex(idx)
        
        solver = config.get("solver", "Radioss")
        idx = self.inputs["solver"].findText(solver)
        if idx >= 0: self.inputs["solver"].setCurrentIndex(idx)
        
        self.inputs["tolerance"].setValue(float(config.get("tolerance", 0.05)))
        self.inputs["friction"].setValue(float(config.get("friction", 0.0)))
        
        self.form_w.setVisible(True)
        self.dispatch_btn.setEnabled(True)

    def get_current_config(self):
        return {
            "master": self.inputs["master"].text(),
            "slave": self.inputs["slave"].text(),
            "contact_type": self.inputs["contact_type"].currentText(),
            "solver": self.inputs["solver"].currentText(),
            "tolerance": self.inputs["tolerance"].value(),
            "friction": self.inputs["friction"].value()
        }

    def _on_dispatch(self):
        if not self._current_contact_id: return
        self.contactRequested.emit(self._current_contact_id, self.get_current_config())
