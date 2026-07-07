import os
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from gui.styles import C, SS
from gui.contact_config_panel import ContactConfigPanel, _load_contact_defaults

class ContactsPage(QWidget):
    contactRequested = Signal(str, dict) # contact_id, config
    contactAllRequested = Signal(list) # list of (contact_id, config)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._active_cid = None
        self._available_comps = []
        self._suggested_pairs = []
        self._defaults = _load_contact_defaults()
        
        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Left: Table area ──────────────────────────────────────
        left = QWidget()
        layout = QVBoxLayout(left)
        layout.setContentsMargins(48, 32, 24, 32)
        layout.setSpacing(24)

        # Header / Global Settings
        header = QHBoxLayout()
        title = QLabel("Auto-Contact Definitions")
        title.setFont(QFont("Inter", 20, QFont.Bold))
        header.addWidget(title)
        
        status = QLabel("  (Connected to SimLab)")
        status.setStyleSheet("color: #2ECC71; font-style: italic; font-weight: bold;")
        header.addWidget(status)
        header.addStretch()
        
        header.addWidget(QLabel("Master:"))
        self.c_master = QComboBox()
        self.c_master.setStyleSheet(f"background: {C['surface']}; color: {C['text']}; padding: 6px; border-radius: 4px; min-width: 120px;")
        header.addWidget(self.c_master)
        
        header.addSpacing(16)
        header.addWidget(QLabel("Slave:"))
        self.c_slave = QComboBox()
        self.c_slave.setStyleSheet(f"background: {C['surface']}; color: {C['text']}; padding: 6px; border-radius: 4px; min-width: 120px;")
        header.addWidget(self.c_slave)

        header.addSpacing(16)
        add_btn = QPushButton("Add Custom")
        add_btn.setObjectName("ghost_btn")
        add_btn.clicked.connect(self._add_custom)
        header.addWidget(add_btn)
        
        layout.addLayout(header)

        # Hint label
        hint = QLabel("Right-click a contact row to toggle its advanced Configuration panel")
        hint.setStyleSheet(f"color: {C['text_dim']}; font-size: 11px; font-style: italic;")
        layout.addWidget(hint)

        # Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Contact Name", "Master", "Slave", "Type", "Action"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.table.setColumnWidth(3, 140)
        self.table.setColumnWidth(4, 120)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table.verticalScrollBar().setSingleStep(15)
        self.table.setStyleSheet(f"""
            QTableWidget {{ background: {C['surface']}; border: none; border-radius: 8px; }}
            QTableWidget::item {{ padding: 8px 16px; border-bottom: 1px solid {C['border']}; cursor: pointer; }}
            QTableWidget::item:selected {{ background: {C['card']}; color: {C['text']}; }}
            QHeaderView::section {{ background: {C['bg']}; color: {C['text_dim']}; font-weight: bold; border: none; padding: 12px; }}
        """)
        
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._on_right_click)
        layout.addWidget(self.table, 1)

        # Footer
        footer = QHBoxLayout()
        footer.addStretch()
        self.create_all_btn = QPushButton("Create All Contacts")
        self.create_all_btn.setObjectName("primary_btn")
        self.create_all_btn.setStyleSheet("background: #2E7D52; color: white; font-weight: bold; font-size: 14px; padding: 12px 32px; border-radius: 6px;")
        self.create_all_btn.clicked.connect(self._create_all)
        footer.addWidget(self.create_all_btn)
        layout.addLayout(footer)

        root_layout.addWidget(left, 1)

        # ── Right: Config Panel (hidden until right-clicked) ────────
        self.config_panel = ContactConfigPanel()
        self.config_panel.setFixedWidth(340)
        self.config_panel.setStyleSheet(f"background: {C['bg']}; border-left: 1px solid {C['border']};")
        self.config_panel.contactRequested.connect(self._on_panel_dispatch)
        self.config_panel.hide()
        root_layout.addWidget(self.config_panel)

    def populate(self, components):
        self._available_comps = components
        self.c_master.clear()
        self.c_slave.clear()
        self.c_master.addItems(components)
        self.c_slave.addItems(components)
        
        # Build suggested pairs
        self._suggested_pairs = []
        for contact_id, config in self._defaults.items():
            # Check if both master and slave exist in available components (ignoring numbering suffixes)
            master_base = config["master"]
            slave_base = config["slave"]
            
            master_match = None
            slave_match = None
            
            for c in components:
                if c == master_base or c.startswith(master_base + "_") or master_base.startswith(c + "_"):
                    master_match = master_base
                if c == slave_base or c.startswith(slave_base + "_") or slave_base.startswith(c + "_"):
                    slave_match = slave_base
                    
            if master_match and slave_match:
                cfg = config.copy()
                cfg["master"] = master_match
                cfg["slave"] = slave_match
                self._suggested_pairs.append((contact_id, cfg))
                
        self._refresh_table()

    def _add_custom(self):
        master = self.c_master.currentText()
        slave = self.c_slave.currentText()
        if not master or not slave or master == slave: return
        
        contact_id = f"CUSTOM_{master}_TO_{slave}"
        cfg = {
            "master": master,
            "slave": slave,
            "tolerance": 0.05,
            "contact_type": "Tied (Type 2)",
            "solver": "Radioss"
        }
        self._suggested_pairs.append((contact_id, cfg))
        self._refresh_table()

    def _refresh_table(self):
        self.table.setRowCount(len(self._suggested_pairs))
        for row, (c_id, cfg) in enumerate(self._suggested_pairs):
            item = QTableWidgetItem(c_id.replace("_", " "))
            item.setFont(QFont("Inter", 11, QFont.Bold))
            item.setToolTip("Right-click to toggle advanced configuration panel")
            item.setData(Qt.UserRole, (c_id, cfg))
            self.table.setItem(row, 0, item)
            
            self.table.setItem(row, 1, QTableWidgetItem(cfg["master"]))
            self.table.setItem(row, 2, QTableWidgetItem(cfg["slave"]))
            self.table.setItem(row, 3, QTableWidgetItem(cfg["contact_type"]))
            
            btn_container = QWidget()
            b_layout = QHBoxLayout(btn_container)
            b_layout.setContentsMargins(0, 0, 0, 0)
            btn = QPushButton("Create")
            btn.setStyleSheet("background: #2E7D52; color: white; border-radius: 4px; padding: 6px 12px; font-weight: bold;")
            btn.clicked.connect(lambda _, r=row: self._direct_create(r))
            b_layout.addWidget(btn)
            b_layout.setAlignment(Qt.AlignCenter)
            self.table.setCellWidget(row, 4, btn_container)
            self.table.setRowHeight(row, 60)

    def _on_right_click(self, pos):
        item = self.table.itemAt(pos)
        if item:
            row = item.row()
            c_id, cfg = self.table.item(row, 0).data(Qt.UserRole)
            if self.config_panel.isVisible():
                if self._active_cid == c_id:
                    self.config_panel.hide()
                    self._active_cid = None
                else:
                    self._active_cid = c_id
                    self.config_panel.load_contact(c_id, cfg)
            else:
                self.config_panel.show()
                self._active_cid = c_id
                self.config_panel.load_contact(c_id, cfg)

    def _direct_create(self, row):
        c_id, cfg = self.table.item(row, 0).data(Qt.UserRole)
        # If the user edited values in the side panel for this contact, grab them live!
        if self.config_panel.isVisible() and self._active_cid == c_id:
            cfg = self.config_panel.get_current_config()
            self.table.item(row, 0).setData(Qt.UserRole, (c_id, cfg))
        self.contactRequested.emit(c_id, cfg)

    def _on_panel_dispatch(self, contact_id, config):
        # Update the table model with new config
        for i, (cid, cfg) in enumerate(self._suggested_pairs):
            if cid == contact_id:
                self._suggested_pairs[i] = (contact_id, config)
                self.table.item(i, 0).setData(Qt.UserRole, (contact_id, config))
                self.table.item(i, 3).setText(config["contact_type"])
                break
        self.contactRequested.emit(contact_id, config)

    def _create_all(self):
        jobs = [(c_id, cfg) for c_id, cfg in self._suggested_pairs]
        self.contactAllRequested.emit(jobs)
