import os
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from gui.styles import C, SS
from gui.mesh_config_panel import MeshConfigPanel

class MeshingPage(QWidget):
    # Emits (comp_name, flat_config_dict) — config is the collected param values
    meshRequested    = Signal(str, dict)
    meshAllRequested = Signal(list)   # list of (comp_name, {}) tuples

    def __init__(self, parent=None):
        super().__init__(parent)
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
        title = QLabel("Live Meshing Engine")
        title.setFont(QFont("Inter", 20, QFont.Bold))
        header.addWidget(title)

        status = QLabel("  (Connected to SimLab)")
        status.setStyleSheet("color: #2ECC71; font-style: italic; font-weight: bold;")
        header.addWidget(status)
        header.addStretch()

        # Global Controls (kept for "Mesh All" fallback)
        header.addWidget(QLabel("Global Type:"))
        self.g_type = QComboBox()
        self.g_type.addItems(["Tet4", "Tet10"])
        self.g_type.setStyleSheet(f"background: {C['surface']}; color: {C['text']}; padding: 6px; border-radius: 4px; min-width: 80px;")
        header.addWidget(self.g_type)

        header.addSpacing(16)
        header.addWidget(QLabel("Size (mm):"))
        self.g_size = QComboBox()
        self.g_size.addItems(["3.5", "4.0", "4.5", "5.0"])
        self.g_size.setEditable(True)
        self.g_size.setStyleSheet(f"background: {C['surface']}; color: {C['text']}; padding: 6px; border-radius: 4px; min-width: 80px;")
        header.addWidget(self.g_size)

        header.addSpacing(16)
        self.apply_btn = QPushButton("Apply to All")
        self.apply_btn.setObjectName("ghost_btn")
        self.apply_btn.clicked.connect(self._apply_all)
        header.addWidget(self.apply_btn)

        layout.addLayout(header)

        # Hint label
        hint = QLabel("Click a component name to open its Mesh Configuration panel")
        hint.setStyleSheet(f"color: {C['text_dim']}; font-size: 11px; font-style: italic;")
        layout.addWidget(hint)

        # Table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Component Name", "Mesh Type", "Mesh Size (mm)", "Action"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.setColumnWidth(1, 140)
        self.table.setColumnWidth(2, 140)
        self.table.setColumnWidth(3, 140)
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
        # Right-clicking row name opens config panel
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._on_right_click)
        layout.addWidget(self.table, 1)

        # Footer
        footer = QHBoxLayout()
        footer.addStretch()
        self.mesh_all_btn = QPushButton("Mesh All Components")
        self.mesh_all_btn.setObjectName("primary_btn")
        self.mesh_all_btn.setStyleSheet("background: #4A9EFF; color: white; font-weight: bold; font-size: 14px; padding: 12px 32px; border-radius: 6px;")
        self.mesh_all_btn.clicked.connect(self._mesh_all)
        footer.addWidget(self.mesh_all_btn)
        layout.addLayout(footer)

        root_layout.addWidget(left, 1)

        # ── Right: Config Panel (hidden until row clicked) ────────
        self.config_panel = MeshConfigPanel()
        self.config_panel.setFixedWidth(340)
        self.config_panel.setStyleSheet(f"background: {C['bg']}; border-left: 1px solid {C['border']};")
        self.config_panel.meshRequested.connect(self._on_panel_mesh)
        root_layout.addWidget(self.config_panel)

    # ── Population ────────────────────────────────────────────────

    def populate(self, components, session_dir=None, renders=None):
        self._session_dir = session_dir
        self._renders = renders or {}
        
        self.table.setRowCount(len(components))
        for row, comp in enumerate(components):
            # Clickable name cell (styled as a link)
            item = QTableWidgetItem(comp)
            item.setFont(QFont("Inter", 12, QFont.Bold))
            item.setToolTip("Right-click to open advanced mesh configuration panel")
            self.table.setItem(row, 0, item)

            c_type = QComboBox()
            c_type.addItems(["Tet4", "Tet10"])
            c_type.setStyleSheet(f"background: {C['bg']}; color: {C['text']}; padding: 6px; border-radius: 4px;")
            self.table.setCellWidget(row, 1, c_type)

            c_size = QComboBox()
            c_size.addItems(["3.5", "4.0", "4.5", "5.0"])
            c_size.setEditable(True)
            c_size.setCurrentText("4.0")
            c_size.setStyleSheet(f"background: {C['bg']}; color: {C['text']}; padding: 6px; border-radius: 4px;")
            self.table.setCellWidget(row, 2, c_size)

            btn_container = QWidget()
            b_layout = QHBoxLayout(btn_container)
            b_layout.setContentsMargins(0, 0, 0, 0)
            btn = QPushButton("Mesh")
            btn.setStyleSheet("background: #2E7D52; color: white; border-radius: 4px; padding: 6px 12px; font-weight: bold;")
            btn.clicked.connect(lambda _, r=row, c=comp: self._direct_mesh(r, c))
            b_layout.addWidget(btn)
            b_layout.setAlignment(Qt.AlignCenter)
            self.table.setCellWidget(row, 3, btn_container)
            self.table.setRowHeight(row, 60)

    # ── Slots ─────────────────────────────────────────────────────

    def _on_right_click(self, pos):
        item = self.table.itemAt(pos)
        if item and item.column() == 0:
            self._open_config(item.text())

    def _direct_mesh(self, row, comp_name):
        c_type = self.table.cellWidget(row, 1).currentText()
        try:
            c_size = float(self.table.cellWidget(row, 2).currentText())
        except ValueError:
            c_size = 4.0
            
        from gui.mesh_config_panel import _load_config, flatten_config
        
        # Load full config (session overrides or default JSON)
        full_json = _load_config(comp_name, self._session_dir) or {}
        flat_config = flatten_config(full_json)
        
        # Apply the quick-overrides from the table row
        flat_config["global.mesh_type"] = c_type
        flat_config["global.mesh_size"] = c_size
        
        self.meshRequested.emit(comp_name, flat_config)

    def _open_config(self, comp_name: str):
        image_path = self._renders.get(comp_name)
        self.config_panel.load_component(comp_name, self._session_dir, image_path)

    def _on_panel_mesh(self, comp_name: str, config: dict):
        self.meshRequested.emit(comp_name, config)

    def _apply_all(self):
        t = self.g_type.currentText()
        s = self.g_size.currentText()
        for row in range(self.table.rowCount()):
            self.table.cellWidget(row, 1).setCurrentText(t)
            self.table.cellWidget(row, 2).setCurrentText(s)

    def _mesh_all(self):
        from gui.mesh_config_panel import _load_config, flatten_config
        jobs = []
        for row in range(self.table.rowCount()):
            comp = self.table.item(row, 0).text()
            
            c_type = self.table.cellWidget(row, 1).currentText()
            try:
                c_size = float(self.table.cellWidget(row, 2).currentText())
            except ValueError:
                c_size = 4.0
                
            full_json = _load_config(comp, self._session_dir) or {}
            flat_config = flatten_config(full_json)
            flat_config["global.mesh_type"] = c_type
            flat_config["global.mesh_size"] = c_size
            
            jobs.append((comp, flat_config))
        self.meshAllRequested.emit(jobs)
