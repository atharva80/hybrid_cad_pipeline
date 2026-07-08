import os
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from gui.styles import C, SS
from gui.mesh_config_panel import MeshConfigPanel

class MeshRow(QFrame):
    """A clean, standalone row for a single component"""
    def __init__(self, comp, page, parent=None, is_child=False):
        super().__init__(parent)
        self.comp = comp
        self.page = page
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(lambda pos: self.page._on_right_click_comp(self.comp))
        
        # If it's a child row inside a group, make it slightly lighter/indented
        bg_color = "transparent" if is_child else C['surface']
        radius = "0px" if is_child else "8px"
        margin_left = 24 if is_child else 0
        
        self.setStyleSheet(f"""
            MeshRow {{
                background: {bg_color};
                border-radius: {radius};
                border-bottom: 1px solid rgba(255,255,255,0.05);
            }}
            MeshRow:hover {{
                background: rgba(255,255,255,0.03);
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(margin_left + 16, 8, 16, 8)
        
        name = QLabel(comp)
        name.setFont(QFont("Inter", 12, QFont.Bold))
        name.setStyleSheet("color: white;")
        name.setToolTip("Right-click to open configuration panel")
        
        self.c_type = QComboBox()
        if "BOX" in comp.upper() and "PCB" not in comp.upper():
            self.c_type.addItems(["Hex"])
        else:
            self.c_type.addItems(["Tet4", "Tet10", "Hex"])
        self.c_type.setStyleSheet("background: rgba(255,255,255,0.1); color: white; border: none; padding: 6px; border-radius: 4px; min-width: 70px;")
        
        self.c_size = QComboBox()
        self.c_size.addItems(["3.5", "4.0", "4.5", "5.0"])
        self.c_size.setEditable(True)
        self.c_size.setCurrentText("4.0")
        self.c_size.setStyleSheet("background: rgba(255,255,255,0.1); color: white; border: none; padding: 6px; border-radius: 4px; min-width: 60px;")
        
        status = QLabel("Ready")
        status.setFixedWidth(80)
        status.setAlignment(Qt.AlignCenter)
        status.setStyleSheet("color: rgba(255,255,255,0.5); font-weight: bold; font-size: 11px;")
        
        btn = QPushButton("Mesh")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("background: #2E7D52; color: white; font-weight: bold; padding: 6px 16px; border-radius: 4px;")
        btn.clicked.connect(self._on_mesh_click)
        
        self.page.status_labels[comp] = status
        self.page.all_inputs[comp] = (self.c_type, self.c_size)
        
        layout.addWidget(name, 1)
        layout.addWidget(self.c_type)
        layout.addWidget(self.c_size)
        layout.addWidget(status)
        layout.addWidget(btn)

    def _on_mesh_click(self):
        self.page._direct_mesh_by_name(self.comp, self.c_type.currentText(), self.c_size.currentText())


class GroupHeader(QFrame):
    clicked = Signal()
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
            event.accept()
        else:
            super().mousePressEvent(event)

class MeshGroup(QFrame):
    """An accordion group for multiple components"""
    def __init__(self, title, components, page, parent=None):
        super().__init__(parent)
        self.title = title
        self.components = components
        self.page = page
        self.expanded = False
        
        # Virtual component name for group configs
        self.group_comp_name = f"GROUP_{title.replace(' ', '_').upper()}"
        
        self.setStyleSheet(f"""
            MeshGroup {{
                background: {C['surface']};
                border-radius: 8px;
                border: 1px solid rgba(255,255,255,0.05);
            }}
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Header
        self.header = GroupHeader()
        self.header.setCursor(Qt.PointingHandCursor)
        self.header.setContextMenuPolicy(Qt.CustomContextMenu)
        self.header.customContextMenuRequested.connect(lambda pos: self.page._on_right_click_comp(self.group_comp_name))
        
        self.header.setStyleSheet("""
            GroupHeader { background: transparent; border-radius: 8px; }
            GroupHeader:hover { background: rgba(255,255,255,0.02); }
        """)
        
        hl = QHBoxLayout(self.header)
        hl.setContentsMargins(16, 12, 16, 12)
        
        self.arrow = QLabel("▶")
        self.arrow.setStyleSheet(f"color: {C['text_dim']}; font-size: 12px; font-weight: bold;")
        
        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Inter", 14, QFont.Bold))
        lbl_title.setStyleSheet("color: white;")
        
        lbl_count = QLabel(f"{len(components)} items")
        lbl_count.setStyleSheet(f"color: {C['text_dim']}; font-size: 12px;")
        
        btn_mesh_group = QPushButton("Mesh Group")
        btn_mesh_group.setCursor(Qt.PointingHandCursor)
        # Use the exact same green as the standalone "Mesh" button for consistency
        btn_mesh_group.setStyleSheet("background: #2E7D52; color: white; font-weight: bold; padding: 6px 16px; border-radius: 4px;")
        btn_mesh_group.clicked.connect(self._mesh_entire_group)
        
        # Group-wise mesh options
        lbl_type = QLabel("Type:")
        lbl_type.setStyleSheet(f"color: {C['text_dim']}; font-size: 11px;")
        
        self.g_type = QComboBox()
        if title == "Boxes":
            self.g_type.addItems(["Hex"])
        else:
            self.g_type.addItems(["Tet4", "Tet10", "Hex"])
        self.g_type.setStyleSheet("background: rgba(255,255,255,0.05); color: white; border: 1px solid rgba(255,255,255,0.1); padding: 4px; border-radius: 4px; min-width: 60px;")
        
        lbl_size = QLabel("Size:")
        lbl_size.setStyleSheet(f"color: {C['text_dim']}; font-size: 11px;")
        
        self.g_size = QComboBox()
        self.g_size.addItems(["3.5", "4.0", "4.5", "5.0"])
        self.g_size.setEditable(True)
        self.g_size.setCurrentText("4.0")
        self.g_size.setStyleSheet("background: rgba(255,255,255,0.05); color: white; border: 1px solid rgba(255,255,255,0.1); padding: 4px; border-radius: 4px; min-width: 50px;")
        
        btn_apply = QPushButton("Apply")
        btn_apply.setCursor(Qt.PointingHandCursor)
        btn_apply.setStyleSheet(f"background: transparent; color: {C['text_dim']}; border: 1px solid rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 4px;")
        btn_apply.clicked.connect(self._apply_to_group)
        
        hl.addWidget(self.arrow)
        hl.addWidget(lbl_title)
        hl.addSpacing(8)
        hl.addWidget(lbl_count)
        hl.addStretch()
        
        hl.addWidget(lbl_type)
        hl.addWidget(self.g_type)
        hl.addSpacing(8)
        hl.addWidget(lbl_size)
        hl.addWidget(self.g_size)
        hl.addSpacing(4)
        hl.addWidget(btn_apply)
        hl.addSpacing(16)
        
        hl.addWidget(btn_mesh_group)
        
        self.layout.addWidget(self.header)
        
        # Content Widget
        self.content = QWidget()
        self.content.hide()
        
        cl = QVBoxLayout(self.content)
        cl.setContentsMargins(0, 0, 0, 8)
        cl.setSpacing(0)
        
        # Handle subgroups for Bearings and Insulators
        if title == "Bearings":
            top = [c for c in components if "TOP" in c.upper()]
            bot = [c for c in components if "BOTTOM" in c.upper() or "BOT" in c.upper()]
            oth = [c for c in components if c not in top and c not in bot]
            if top: self._add_subheader(cl, "Top Bearing"); self._add_rows(cl, top)
            if bot: self._add_subheader(cl, "Bottom Bearing"); self._add_rows(cl, bot)
            if oth: self._add_subheader(cl, "Other Races"); self._add_rows(cl, oth)
        elif title == "Insulators":
            top = [c for c in components if "TOP" in c.upper()]
            bot = [c for c in components if "BOTTOM" in c.upper() or "BOT" in c.upper()]
            oth = [c for c in components if c not in top and c not in bot]
            if top: self._add_subheader(cl, "Top Insulator"); self._add_rows(cl, top)
            if bot: self._add_subheader(cl, "Bottom Insulator"); self._add_rows(cl, bot)
            if oth: self._add_rows(cl, oth)
        else:
            self._add_rows(cl, components)
            
        self.layout.addWidget(self.content)
        self.header.clicked.connect(self.toggle)

    def _add_subheader(self, layout, text):
        lbl = QLabel(text)
        lbl.setFont(QFont("Inter", 11, QFont.Bold))
        lbl.setStyleSheet("color: rgba(255,255,255,0.4); padding-left: 40px; padding-top: 8px; padding-bottom: 2px;")
        layout.addWidget(lbl)

    def _add_rows(self, layout, comps):
        for c in comps:
            row = MeshRow(c, self.page, is_child=True)
            layout.addWidget(row)

    def toggle(self):
        self.expanded = not self.expanded
        self.content.setVisible(self.expanded)
        self.arrow.setText("▼" if self.expanded else "▶")

    def _apply_to_group(self):
        t = self.g_type.currentText()
        s = self.g_size.currentText()
        for comp in self.components:
            if comp in self.page.all_inputs:
                c_type_w, c_size_w = self.page.all_inputs[comp]
                c_type_w.setCurrentText(t)
                c_size_w.setCurrentText(s)

    def _mesh_entire_group(self):
        from gui.mesh_config_panel import _load_config, flatten_config
        # Load the group-level config if it exists
        full_json = _load_config(self.group_comp_name, self.page._session_dir) or {}
        flat_config = flatten_config(full_json)
        
        # Dispatch a mesh request for every component in this group
        jobs = []
        for comp in self.components:
            # Overwrite with row-level UI overrides
            c_type_w, c_size_w = self.page.all_inputs[comp]
            cfg = flat_config.copy()
            cfg["global.mesh_type"] = c_type_w.currentText()
            try:
                cfg["global.mesh_size"] = float(c_size_w.currentText())
            except:
                cfg["global.mesh_size"] = 4.0
            jobs.append((comp, cfg))
            
        self.page.meshAllRequested.emit(jobs)


class MeshingPage(QWidget):
    meshRequested    = Signal(str, dict)
    meshAllRequested = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._active_comp = None
        self.status_labels = {}
        self.all_inputs = {}
        
        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Left: Main List Area ─────────────────────────────
        left = QWidget()
        left.setStyleSheet(f"background: {C['bg']};")
        layout = QVBoxLayout(left)
        layout.setContentsMargins(32, 24, 16, 24)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("Live Meshing Engine")
        title.setFont(QFont("Inter", 20, QFont.Bold))
        header.addWidget(title)
        
        status = QLabel("  (Connected to SimLab)")
        status.setStyleSheet("color: #2ECC71; font-style: italic; font-weight: bold;")
        header.addWidget(status)
        header.addStretch()

        header.addWidget(QLabel("Global Type:"))
        self.g_type = QComboBox()
        self.g_type.addItems(["Tet4", "Tet10", "Hex"])
        self.g_type.setStyleSheet(f"background: {C['surface']}; color: {C['text']}; padding: 6px; border-radius: 4px; min-width: 70px;")
        header.addWidget(self.g_type)

        header.addSpacing(12)
        header.addWidget(QLabel("Size (mm):"))
        self.g_size = QComboBox()
        self.g_size.addItems(["3.5", "4.0", "4.5", "5.0"])
        self.g_size.setEditable(True)
        self.g_size.setStyleSheet(f"background: {C['surface']}; color: {C['text']}; padding: 6px; border-radius: 4px; min-width: 60px;")
        header.addWidget(self.g_size)

        header.addSpacing(12)
        self.apply_btn = QPushButton("Apply to All")
        self.apply_btn.setObjectName("ghost_btn")
        self.apply_btn.clicked.connect(self._apply_all)
        header.addWidget(self.apply_btn)

        layout.addLayout(header)

        hint = QLabel("Right-click any component or group header to open its Configuration Panel.")
        hint.setStyleSheet(f"color: rgba(255,255,255,0.4); font-size: 12px; font-style: italic;")
        layout.addWidget(hint)

        # Scroll Area for List
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

        # ── Right: Config Panel ──────────────────────────────────
        self.config_panel = MeshConfigPanel()
        self.config_panel.setFixedWidth(360)
        self.config_panel.setStyleSheet(f"background: {C['surface']}; border-left: 1px solid {C['border']};")
        self.config_panel.meshRequested.connect(self._on_panel_mesh)
        self.config_panel.hide()
        root_layout.addWidget(self.config_panel)

    def populate(self, components, session_dir=None, renders=None):
        self._session_dir = session_dir
        self._renders = renders or {}
        
        while self.list_layout.count():
            child = self.list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        self.status_labels.clear()
        self.all_inputs.clear()

        # Group components exactly as requested
        groups = {
            "Bearings": [],
            "Canopies": [],
            "Boxes": [],
            "EPS Packaging": [],
            "Insulators": [],
            "Bottom Covers": [],
            "PCBs": []
        }
        standalone = []

        for c in components:
            cu = c.upper()
            if "RACE" in cu or "BEARING" in cu:
                groups["Bearings"].append(c)
            elif "CANOPY" in cu:
                groups["Canopies"].append(c)
            elif "BOX" in cu and "PCB" not in cu:
                groups["Boxes"].append(c)
            elif "EPS" in cu:
                groups["EPS Packaging"].append(c)
            elif "INSULATOR" in cu:
                groups["Insulators"].append(c)
            elif "BOTTOM_COVER" in cu:
                groups["Bottom Covers"].append(c)
            elif "PCB" in cu:
                groups["PCBs"].append(c)
            else:
                standalone.append(c)

        # Move Bottom Covers and PCBs to standalone if len <= 1
        if len(groups["Bottom Covers"]) <= 1:
            standalone.extend(groups["Bottom Covers"])
            groups["Bottom Covers"] = []
            
        if len(groups["PCBs"]) <= 1:
            standalone.extend(groups["PCBs"])
            groups["PCBs"] = []

        # 1. Build Standalone rows first (Core parts)
        for c in standalone:
            row = MeshRow(c, self)
            self.list_layout.addWidget(row)

        # 2. Build Groups
        for title, items in groups.items():
            if items:
                group_widget = MeshGroup(title, items, self)
                self.list_layout.addWidget(group_widget)

    def update_status(self, comp_name, status):
        lbl = self.status_labels.get(comp_name)
        if lbl:
            lbl.setText(status)
            if status == "Meshing...":
                lbl.setStyleSheet("color: #F39C12; font-weight: bold; font-size: 11px;")
            elif status == "Success":
                lbl.setStyleSheet("color: #2ECC71; font-weight: bold; font-size: 11px;")
            elif status == "Failed":
                lbl.setStyleSheet("color: #E74C3C; font-weight: bold; font-size: 11px;")
            else:
                lbl.setStyleSheet("color: rgba(255,255,255,0.5); font-weight: bold; font-size: 11px; font-style: italic;")

    def _on_right_click_comp(self, comp_name):
        if self.config_panel.isVisible():
            if self._active_comp == comp_name:
                self.config_panel.hide()
                self._active_comp = None
            else:
                self._active_comp = comp_name
                self._open_config(comp_name)
        else:
            self.config_panel.show()
            self._active_comp = comp_name
            self._open_config(comp_name)

    def _direct_mesh_by_name(self, comp_name, c_type, c_size_str):
        try:
            c_size = float(c_size_str)
        except ValueError:
            c_size = 4.0
            
        from gui.mesh_config_panel import _load_config, flatten_config
        full_json = _load_config(comp_name, self._session_dir) or {}
        flat_config = flatten_config(full_json)
        
        flat_config["global.mesh_type"] = c_type
        flat_config["global.mesh_size"] = c_size
        
        self.meshRequested.emit(comp_name, flat_config)

    def _open_config(self, comp_name: str):
        # Render image lookup (won't find anything for GROUP_*)
        image_path = self._renders.get(comp_name)
        self.config_panel.load_component(comp_name, self._session_dir, image_path)

    def _on_panel_mesh(self, comp_name: str, config: dict):
        # If the user clicks 'Mesh' from inside the panel on a GROUP, we should broadcast it
        if comp_name.startswith("GROUP_"):
            # We need to find which group this is, and extract the components
            target_group = None
            for idx in range(self.list_layout.count()):
                w = self.list_layout.itemAt(idx).widget()
                if isinstance(w, MeshGroup) and w.group_comp_name == comp_name:
                    target_group = w
                    break
            
            if target_group:
                jobs = []
                for c in target_group.components:
                    # Apply the group config directly to all parts
                    c_type_w, c_size_w = self.all_inputs[c]
                    cfg = config.copy()
                    cfg["global.mesh_type"] = c_type_w.currentText()
                    try:
                        cfg["global.mesh_size"] = float(c_size_w.currentText())
                    except:
                        cfg["global.mesh_size"] = 4.0
                    jobs.append((c, cfg))
                self.meshAllRequested.emit(jobs)
        else:
            self.meshRequested.emit(comp_name, config)

    def _apply_all(self):
        t = self.g_type.currentText()
        s = self.g_size.currentText()
        for c_type, c_size in self.all_inputs.values():
            c_type.setCurrentText(t)
            c_size.setCurrentText(s)

    def _mesh_all(self):
        from gui.mesh_config_panel import _load_config, flatten_config
        jobs = []
        for comp, (c_type_w, c_size_w) in self.all_inputs.items():
            c_type = c_type_w.currentText()
            try:
                c_size = float(c_size_w.currentText())
            except ValueError:
                c_size = 4.0
                
            full_json = _load_config(comp, self._session_dir) or {}
            flat_config = flatten_config(full_json)
            flat_config["global.mesh_type"] = c_type
            flat_config["global.mesh_size"] = c_size
            
            jobs.append((comp, flat_config))
        self.meshAllRequested.emit(jobs)
