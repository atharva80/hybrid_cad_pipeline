import os
import sys
import glob
import json
import time
import shutil
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path: sys.path.insert(0, _ROOT)

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from gui.styles import C, SS, COMPONENT_COLORS, ML_COMPONENTS
from gui.worker import InferenceWorker
from gui.meshing_page import MeshingPage
from gui.contacts_page import ContactsPage

# ── Segmented nav button ───────────────────────────────────────────────────
class NavBtn(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("seg_btn")
        self.setCursor(Qt.PointingHandCursor)
    def set_active(self, v):
        self.setObjectName("seg_btn_active" if v else "seg_btn")
        self.style().unpolish(self); self.style().polish(self)

# ── Drop zone ──────────────────────────────────────────────────────────────
class DropZone(QWidget):
    path_dropped = Signal(list)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._hover = False
        self._paths = []

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)
        layout.setContentsMargins(32, 48, 32, 48)

        self.main_lbl = QLabel("Select STEP Files")
        self.main_lbl.setFont(QFont("Inter", 16, QFont.Bold))
        self.main_lbl.setAlignment(Qt.AlignCenter)
        self.main_lbl.setStyleSheet(f"color: {C['text']};")

        self.sub_lbl = QLabel("Drag & drop your CAD files here")
        self.sub_lbl.setAlignment(Qt.AlignCenter)
        self.sub_lbl.setFont(QFont("Inter", 13))
        self.sub_lbl.setStyleSheet(f"color: {C['text_dim']};")

        layout.addWidget(self.main_lbl)
        layout.addWidget(self.sub_lbl)
        self._update_style(False)

    def get_paths(self): return self._paths

    def _set_selected(self, paths):
        if not paths: return
        self._paths = paths
        if len(paths) == 1:
            self.main_lbl.setText(os.path.basename(paths[0]))
            self.sub_lbl.setText(paths[0])
        else:
            self.main_lbl.setText(f"{len(paths)} Files Selected")
            self.sub_lbl.setText(f"{os.path.basename(paths[0])} and {len(paths)-1} others")
        
        self.main_lbl.setStyleSheet(f"color: {C['text']};")
        self.path_dropped.emit(paths)

    def mousePressEvent(self, e):
        win = self.window()
        paths, _ = QFileDialog.getOpenFileNames(win, "Select Files", _ROOT, "STEP Files (*.step *.STEP *.stp *.STP)")
        if paths: self._set_selected(paths)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls(): self._hover = True; self._update_style(True); e.accept()
        else: e.ignore()
    def dragLeaveEvent(self, e): self._hover = False; self._update_style(False)
    def dropEvent(self, e):
        self._hover = False; self._update_style(False)
        urls = e.mimeData().urls()
        if urls: self._set_selected([u.toLocalFile() for u in urls])

    def _update_style(self, hovered):
        border = C['text_muted'] if hovered else C['border']
        bg = C['surface'] if hovered else "transparent"
        self.setStyleSheet(f"""
            DropZone {{
                border: 1px dashed {border};
                border-radius: 12px;
                background: {bg};
                min-width: 500px;
            }}
            DropZone:hover {{ background: {C['surface']}; border-color: {C['border_hi']}; }}
        """)
        self.setCursor(Qt.PointingHandCursor)

# ── Import page ────────────────────────────────────────────────────────────
class ConfigCard(QFrame):
    clicked = Signal(int)
    def __init__(self, idx, title, desc, parent=None):
        super().__init__(parent)
        self.idx = idx
        self.setObjectName("form_card")
        self.setCursor(Qt.PointingHandCursor)
        
        cl = QVBoxLayout(self)
        cl.setContentsMargins(12, 12, 12, 12)
        
        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Inter", 11, QFont.Bold))
        lbl_title.setStyleSheet(f"color: {C['accent']};")
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setWordWrap(True)
        
        img_placeholder = QLabel("Cut section view")
        img_placeholder.setAlignment(Qt.AlignCenter)
        img_placeholder.setStyleSheet(f"background: {C['bg']}; color: {C['text_muted']}; border-radius: 8px;")
        img_placeholder.setMinimumHeight(100)
        
        lbl_desc = QLabel(desc)
        lbl_desc.setFont(QFont("Inter", 10))
        lbl_desc.setAlignment(Qt.AlignCenter)
        lbl_desc.setStyleSheet(f"color: {C['text']};")
        
        cl.addWidget(lbl_title)
        cl.addWidget(img_placeholder, 1)
        cl.addWidget(lbl_desc)

    def mousePressEvent(self, ev):
        self.clicked.emit(self.idx)
        
    def set_active(self, active):
        if active:
            self.setStyleSheet(f"QFrame#form_card {{ background: {C['card_hover']}; border: 2px solid {C['accent']}; border-radius: 12px; }}")
        else:
            self.setStyleSheet(f"QFrame#form_card {{ background: {C['surface']}; border: 1px solid {C['border']}; border-radius: 12px; }}")

class MultiSelectDropdown(QPushButton):
    def __init__(self, title, items, parent=None):
        super().__init__(title, parent)
        self.default_title = title
        self.menu = QMenu(self)
        self.menu.setStyleSheet(f"background: {C['surface']}; color: {C['text']}; border: 1px solid {C['border']};")
        self.checkboxes = {}
        self.actions_dict = {}
        
        from PySide6.QtWidgets import QWidgetAction
        for item in items:
            chk = QCheckBox(item)
            chk.setStyleSheet(f"color: {C['text']}; padding: 4px 12px; background: transparent;")
            chk.toggled.connect(self._update_title)
            
            wa = QWidgetAction(self.menu)
            wa.setDefaultWidget(chk)
            self.menu.addAction(wa)
            
            self.checkboxes[item] = chk
            self.actions_dict[item] = wa
            
        self.setMenu(self.menu)
        self.setStyleSheet(f"background: {C['surface']}; color: {C['text']}; border: 1px solid {C['border_hi']}; border-radius: 6px; padding: 6px 12px; text-align: left;")
        
    def _update_title(self):
        selected = self.get_selected()
        if not selected:
            self.setText(self.default_title)
        else:
            self.setText(f"{self.default_title} ({len(selected)})")
            
    def get_selected(self):
        return [item for item, chk in self.checkboxes.items() if chk.isChecked() and self.actions_dict[item].isVisible()]

    def hide_items(self, items_to_hide):
        for item, wa in self.actions_dict.items():
            if item in items_to_hide:
                wa.setVisible(False)
                self.checkboxes[item].setChecked(False)
            else:
                wa.setVisible(True)
        self._update_title()

class ImportPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 32, 48, 32)
        root.setSpacing(24)

        # Config button at top right
        top_layout = QHBoxLayout()
        top_layout.addStretch()
        
        top_layout.addStretch()
        
        info_btn = QPushButton("Core Components")
        info_btn.setObjectName("ghost_btn")
        info_btn.setCursor(Qt.PointingHandCursor)
        info_btn.clicked.connect(self._show_core_components)
        
        cfg_btn = QPushButton("Config.yml")
        cfg_btn.setObjectName("ghost_btn")
        cfg_btn.setCursor(Qt.PointingHandCursor)
        cfg_btn.clicked.connect(self._open_config)
        
        top_layout.addWidget(info_btn)
        top_layout.addWidget(cfg_btn)
        root.addLayout(top_layout)

        # Drop zone
        self.drop = DropZone()
        self.drop.setMaximumHeight(200)
        root.addWidget(self.drop)

        # Select Config Label
        cfg_header = QHBoxLayout()
        lbl_sel = QLabel("Select Config Type")
        lbl_sel.setFont(QFont("Inter", 14, QFont.Bold))
        cfg_header.addWidget(lbl_sel)
        
        cfg_header.addStretch()
        
        non_core = sorted(['PCB_BOX', 'PCB_BRACKET', 'STAYCAP', 'BLADE_BOX', 'FALSE_COVER', 'MASTER_BOX', 'MOTOR_BOX', 'CANOPY', 'SIDE_COVER'])
        self.additional_dropdown = MultiSelectDropdown("Additional Components", non_core)
        cfg_header.addWidget(self.additional_dropdown)
        
        cfg_header.addSpacing(16)
        
        self.run_btn = QPushButton("Process")
        self.run_btn.setObjectName("primary_btn")
        self.run_btn.setEnabled(False)
        self.run_btn.setFixedSize(120, 36)
        cfg_header.addWidget(self.run_btn)
        
        root.addLayout(cfg_header)
        
        self.drop.path_dropped.connect(lambda paths: self.run_btn.setEnabled(len(paths) > 0))

        # Parallel Rectangles
        row_layout = QHBoxLayout()
        row_layout.setSpacing(16)
        
        cards_data = [
            ("Renesa / Hamster / Beaver", "Staycap, Side Body Present"),
            ("Ikano / Canary / Alpaca / Erica", "Staycap, Side Body Absent"),
            ("Pegasus / Sabre / Rhino", "PCB Box"),
            ("Panda / Cougar", "PCB Box, False Cover")
        ]
        
        self.cards = []
        self.selected_config = None
        
        for i, (title, desc) in enumerate(cards_data):
            card = ConfigCard(i, title, desc)
            card.clicked.connect(self._select_config)
            row_layout.addWidget(card)
            self.cards.append(card)
            
        root.addLayout(row_layout, 1)

    def _toggle_batch(self, state):
        self.drop.set_batch(state)

    def _select_config(self, idx):
        if getattr(self, "selected_config", None) == idx:
            self.selected_config = None
        else:
            self.selected_config = idx
            
        for i, card in enumerate(self.cards):
            card.set_active(i == self.selected_config)
            
        config_comps = {
            0: ['STAYCAP', 'SIDE_BODY'],
            1: ['STAYCAP'],
            2: ['PCB_BOX'],
            3: ['PCB_BOX', 'FALSE_COVER']
        }
        
        hide_comps = config_comps.get(self.selected_config, [])
        self.additional_dropdown.hide_items(hide_comps)

    def _show_core_components(self):
        d = QDialog(self)
        d.setWindowTitle("Core Components")
        d.resize(400, 500)
        d.setStyleSheet(f"background: {C['bg']}; color: {C['text']};")
        layout = QVBoxLayout(d)
        
        lbl = QLabel("Always Identified (Core Components):")
        lbl.setFont(QFont("Inter", 14, QFont.Bold))
        layout.addWidget(lbl)
        
        list_w = QListWidget()
        list_w.setStyleSheet(f"background: {C['surface']}; border: 1px solid {C['border']}; border-radius: 8px; padding: 8px; font-size: 13px;")
        
        non_core = {'PCB_BOX', 'PCB_BRACKET', 'STAYCAP', 'BLADE_BOX', 'FALSE_COVER', 'MASTER_BOX', 'MOTOR_BOX', 'SIDE_BODY'}
        core_comps = [c for c in COMPONENT_COLORS.keys() if c not in non_core]
        
        for comp in sorted(core_comps):
            list_w.addItem(comp)
        layout.addWidget(list_w)
        
        btn = QPushButton("Close")
        btn.setObjectName("ghost_btn")
        btn.clicked.connect(d.accept)
        layout.addWidget(btn, alignment=Qt.AlignRight)
        
        d.exec()

    def _open_config(self):
        cfg_path = os.path.join(_ROOT, "config", "heuristics_config.yaml")
        d = ConfigEditorDialog(cfg_path, self)
        d.exec()

    def get_config(self):
        return {
            "in_paths": self.drop.get_paths(), 
            "config_idx": getattr(self, "selected_config", None),
            "additional_comps": self.additional_dropdown.get_selected()
        }

DEFAULT_CONFIG = """# ATLAS Pipeline Heuristics Configuration
# ---------------------------------------
# You can tweak these magic numbers on the fly. The pipeline reloads this file on every run.
# To disable a filter entirely, set its min value to 0 or max value to an extreme (e.g. 99999).

phase1_anchors:
  global_min_vol: 50
  
  stator_min_vol: 3000          # Minimum absolute volume in mm^3
  stator_dia_min: 80.0          # Minimum outer diameter of the stator stack
  stator_dia_max: 120.0         # Maximum outer diameter of the stator stack
  stator_thick_min: 8.0         # Minimum Z-height (thickness) of the stator stack
  stator_thick_max: 35.0        # Maximum Z-height of the stator stack
  stator_aspect_max: 0.35       # Ratio of thickness to diameter
  stator_complex_faces: 100     # Resolves tiebreakers
  
  shaft_len_min: 40.0           # Minimum length of the shaft
  shaft_len_max: 180.0          # Maximum length of the shaft
  shaft_dia_max: 30.0           # Maximum diameter of the shaft
  shaft_rad_dist_max: 5.0       # Maximum distance from the true center of the stator
  
  rotor_inner_len_min: 30.0     # Minimum length to be considered a rotor ring
  rotor_inner_dia_max: 60.0     # Maximum diameter for the inner rotor section
  rotor_inner_rad_dist_max: 5.0 # Must be perfectly centered on the motor axis
  
  rotor_outer_dia_tolerance: 15.0 # Max difference between stator diameter and rotor diameter
  rotor_outer_face_min: 400       # Rotors often have many faces due to magnet slots
  rotor_outer_vol_max: 15000.0    # Prevents classifying the massive outer housing as the rotor
  
  rotor_alt_rad_dist_max: 5.0        # Must be centered
  rotor_alt_dia_min_offset: 1.0      # Rotor must be slightly wider than stator
  rotor_alt_dia_max_offset: 30.0     # Rotor shouldn't be massively wider than stator
  rotor_alt_aspect_max: 0.6          # Aspect ratio (thickness / diameter) limit
  rotor_alt_thick_tolerance: 10.0    # Rotor thickness should match stator thickness closely
  rotor_alt_vol_min: 5000.0          # Must be a substantial metal piece (filters out tiny magnets)

phase2_housing:
  rad_dist_max: 20.0        # Center alignment tolerance
  dia_min_offset: -5.0      # Can be slightly narrower than stator
  dia_max_offset: 120.0     # Can be much wider than stator (some covers flare out)
  face_count_min: 150       # Housings are complex curved surfaces (filters out flat brackets)

phase3_bearings:
  rad_dist_max: 2.0         # Must be perfectly aligned with the shaft axis
  dia_max_mult: 3.0         # Max diameter relative to the shaft diameter
  faces_max: 50             # Bearings are usually modeled as simple smooth toruses in CAD
  height_min: 1.5           # Minimum thickness of a bearing race
  z_center_tolerance: 6.0   # How close the Inner/Outer races must be in Z to be considered one bearing
  cluster_min_nodes: 2      # A valid bearing must have at least an Inner and Outer race modeled

phase4_pcb:
  height_min: 1.4           # Standard FR4 thickness lower bound
  height_max: 2.0           # Standard FR4 thickness upper bound
  dia_min: 40.0             # Must be a wide circular plate
  rad_dist_max: 10.0        # Must be relatively centered in the motor
  faces_min: 30             # PCB CAD usually has holes/cutouts leading to higher face counts

phase5_eps:
  vol_mult_min: 1.5         # Must have a volume 1.5x larger than the massive stator core
  dia_mult_min: 1.5         # Must have an outer diameter 1.5x larger than the stator
  fill_ratio_min: 0.25      # (Volume / Bounding Box Volume) -> Must be a dense block, not a thin shell

phase6_canopies:
  fill_ratio_min: 0.15      # (Volume / Bounding Box Volume) -> Canopies are highly hollow shells
  aspect_ratio_max: 0.30    # Cannot be completely flat (filters out washers/spacers)
  dia_min: 40.0             # Minimum diameter (filters out tiny collars/screws)
"""

class ConfigEditorDialog(QDialog):
    def __init__(self, cfg_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Config Editor - config/heuristics_config.yaml")
        self.resize(700, 700)
        self.setStyleSheet(f"background: {C['bg']}; color: {C['text']};")
        self.cfg_path = cfg_path
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        lbl = QLabel("Heuristics Configuration")
        lbl.setFont(QFont("Inter", 14, QFont.Bold))
        layout.addWidget(lbl)
        
        from PySide6.QtWidgets import QPlainTextEdit
        self.editor = QPlainTextEdit()
        self.editor.setFont(QFont("monospace", 11))
        self.editor.setStyleSheet(f"background: {C['console_bg']}; color: {C['text']}; border: 1px solid {C['border']}; border-radius: 8px; padding: 8px;")
        
        if os.path.exists(cfg_path):
            with open(cfg_path, "r") as f:
                self.editor.setPlainText(f.read())
        else:
            self.editor.setPlainText(DEFAULT_CONFIG)
            
        layout.addWidget(self.editor, 1)
        
        btn_layout = QHBoxLayout()
        reset_btn = QPushButton("Reset Defaults")
        reset_btn.setObjectName("danger_btn")
        reset_btn.clicked.connect(lambda: self.editor.setPlainText(DEFAULT_CONFIG))
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("ghost_btn")
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Save")
        save_btn.setObjectName("primary_btn")
        save_btn.clicked.connect(self._save)
        
        btn_layout.addWidget(reset_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        
    def _save(self):
        with open(self.cfg_path, "w") as f:
            f.write(self.editor.toPlainText())
        self.accept()

# ── Correction Dialog ───────────────────────────────────────────────────────
class CorrectionDialog(QDialog):
    def __init__(self, filename, comp_name, img_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Correct Component Label")
        self.setFixedSize(600, 500)
        self.setStyleSheet(SS)
        
        self.filename = filename
        self.old_comp = comp_name
        self.new_comp = None
        self.img_path = img_path
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        lbl = QLabel(f"Correcting: {comp_name}")
        lbl.setFont(QFont("Inter", 16, QFont.Bold))
        layout.addWidget(lbl)
        
        self.img_lbl = QLabel()
        self.img_lbl.setAlignment(Qt.AlignCenter)
        self.img_lbl.setStyleSheet(f"background: {C['surface']}; border: 1px solid {C['border']}; border-radius: 8px;")
        self.img_lbl.setMinimumHeight(300)
                    
        if self.img_path:
            pix = QPixmap(self.img_path)
            self.img_lbl.setPixmap(pix.scaled(560, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.img_lbl.setText("Render Not Available\nPlease generate renders first.")
            self.img_lbl.setFont(QFont("Inter", 14))
            self.img_lbl.setStyleSheet(f"color: {C['text_dim']}; background: {C['surface']}; border: 1px solid {C['border']}; border-radius: 8px;")
            
        layout.addWidget(self.img_lbl)
        
        form = QFormLayout()
        self.combo = QComboBox()
        self.combo.addItems(sorted(list(COMPONENT_COLORS.keys())))
        self.combo.setCurrentText(comp_name)
        self.combo.setObjectName("form_input")
        self.combo.setFixedHeight(36)
        
        lbl_form = QLabel("New Label:")
        lbl_form.setFont(QFont("Inter", 12))
        form.addRow(lbl_form, self.combo)
        layout.addLayout(form)
        
        btn_layout = QHBoxLayout()
        
        remove_btn = QPushButton("Remove")
        remove_btn.setObjectName("danger_btn")
        remove_btn.clicked.connect(self._remove)
        
        btn_layout.addWidget(remove_btn)
        btn_layout.addStretch()
        cancel = QPushButton("Cancel")
        cancel.setObjectName("ghost_btn")
        cancel.clicked.connect(self.reject)
        
        save = QPushButton("Update Label")
        save.setObjectName("primary_btn")
        save.clicked.connect(self._accept)
        
        btn_layout.addWidget(cancel)
        btn_layout.addWidget(save)
        layout.addLayout(btn_layout)
        
    def _accept(self):
        self.new_comp = self.combo.currentText()
        if self.new_comp == self.old_comp:
            self.reject()
            return
        self.accept()
        
    def _remove(self):
        self.new_comp = "__REMOVE__"
        self.accept()

class ConfigCheckbox(QWidget):
    def __init__(self, text, is_checked=True):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 12, 0)
        self.chk = QCheckBox()
        self.chk.setChecked(is_checked)
        self.btn = QPushButton(text)
        self.btn.setStyleSheet(f"color: {C['text']}; font-weight: bold; text-align: left; background: transparent; border: none; text-decoration: underline;")
        self.btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.chk)
        layout.addWidget(self.btn)
        
        self.path = None
        self.btn.clicked.connect(self._select_path)
        
    def _select_path(self):
        d = QFileDialog.getExistingDirectory(self, f"Select Save Directory for {self.btn.text()}")
        if d:
            self.path = d
            self.btn.setToolTip(f"Save Path: {self.path}")
            self.chk.setChecked(True)
            self.btn.setStyleSheet(f"color: {C['accent']}; font-weight: bold; text-align: left; background: transparent; border: none; text-decoration: underline;")

# ── Results page ───────────────────────────────────────────────────────────
class ImagePreviewDialog(QDialog):
    def __init__(self, name, path, parent=None):
        super().__init__(parent)
        self.setWindowTitle(name)
        self.resize(800, 700)
        self.setStyleSheet(f"background: {C['bg']};")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)

        self.view = QGraphicsView()
        self.view.setStyleSheet("border: none; background: transparent;")
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        
        px = QPixmap(path)
        if not px.isNull():
            self.pixmap_item = self.scene.addPixmap(px)
            self.view.fitInView(self.pixmap_item, Qt.KeepAspectRatio)
        
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        layout.addWidget(self.view)

    def wheelEvent(self, event):
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
        self.view.scale(zoom_factor, zoom_factor)

class ClickableLabel(QLabel):
    clicked = Signal(str, str)
    def __init__(self, comp_name, img_path):
        super().__init__()
        self.comp_name = comp_name
        self.img_path = img_path
        if self.img_path:
            self.setCursor(Qt.PointingHandCursor)
            
    def mouseDoubleClickEvent(self, ev):
        if self.img_path:
            self.clicked.emit(self.comp_name, self.img_path)

class ResultsPage(QWidget):
    correctionRequested = Signal(str, str)
    massRemoveRequested = Signal(str, list)

    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QHBoxLayout(self); main_layout.setContentsMargins(0, 0, 0, 0); main_layout.setSpacing(0)

        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(260)
        self.sidebar.currentRowChanged.connect(self._on_row_changed)
        main_layout.addWidget(self.sidebar)

        content = QWidget()
        layout = QVBoxLayout(content); layout.setContentsMargins(48, 32, 48, 32); layout.setSpacing(24)

        header = QHBoxLayout()
        self.file_lbl = QLabel("—")
        self.file_lbl.setFont(QFont("Inter", 20, QFont.Bold))
        header.addWidget(self.file_lbl)
        
        header.addStretch()
        
        self.save_btn = QPushButton("Save Run")
        self.save_btn.setObjectName("ghost_btn")
        
        self.export_btn = QPushButton("Export CADs")
        self.export_btn.setObjectName("primary_btn")
        
        self.simlab_btn = QPushButton("Open in SimLab")
        self.simlab_btn.setStyleSheet("background: #2E7D52; color: white; border: none; border-radius: 4px; padding: 6px 12px; font-weight: bold; font-size: 12px;")
        
        self.skip_simlab_btn = QPushButton("Open Meshing (Already Open)")
        self.skip_simlab_btn.setStyleSheet("background: #F39C12; color: white; border: none; border-radius: 4px; padding: 6px 12px; font-weight: bold; font-size: 12px;")
        
        self.remove_btn = QPushButton("Remove Selected")
        self.remove_btn.setObjectName("danger_btn")
        self.remove_btn.hide()
        
        header.addWidget(self.save_btn)
        header.addSpacing(8)
        header.addWidget(self.export_btn)
        header.addSpacing(8)
        header.addWidget(self.simlab_btn)
        header.addSpacing(8)
        header.addWidget(self.skip_simlab_btn)
        header.addSpacing(8)
        header.addWidget(self.remove_btn)

        self.topo_layout = QHBoxLayout(); self.topo_layout.setSpacing(8)
        header.addLayout(self.topo_layout)
        header.addStretch()
        layout.addLayout(header)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Component", "Render PNG", "Fix", "Confidence", "Solids"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.setColumnWidth(1, 160)
        
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.setColumnWidth(2, 100)
        
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(120)
        self.table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table.verticalScrollBar().setSingleStep(15)
        self.table.horizontalScrollBar().setSingleStep(15)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setShowGrid(False)
        layout.addWidget(self.table, 1)

        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        self.remove_btn.clicked.connect(self._remove_selected)

        main_layout.addWidget(content, 1)

        self._data_map = {}
        self._renders_map = {}
        self._filenames = []
    def _on_selection_changed(self):
        selected_rows = set([item.row() for item in self.table.selectedItems()])
        if len(selected_rows) > 1:
            self.remove_btn.show()
        else:
            self.remove_btn.hide()

    def _remove_selected(self):
        idx = self.sidebar.currentRow()
        if idx < 0 or idx >= len(self._filenames): return
        filename = self._filenames[idx]
        
        selected_rows = sorted(list(set([item.row() for item in self.table.selectedItems()])), reverse=True)
        if not selected_rows: return
        
        comps_to_remove = []
        for row in selected_rows:
            comp_name = self.table.item(row, 0).data(Qt.UserRole)
            if comp_name: comps_to_remove.append(comp_name)
            
        if not comps_to_remove: return
        
        if filename in self._data_map:
            self._data_map[filename] = [res for res in self._data_map[filename] if res[0] not in comps_to_remove]
        if filename in self._renders_map:
            for comp in comps_to_remove:
                if comp in self._renders_map[filename]: del self._renders_map[filename][comp]
                
        self.massRemoveRequested.emit(filename, comps_to_remove)
        self._on_row_changed(idx)
        self.remove_btn.hide()

    def clear(self):
        if hasattr(self, '_records_map'): self._records_map.clear()
        if hasattr(self, '_paths_map'): self._paths_map.clear()
        self._data_map.clear()
        self._renders_map.clear()
        self._filenames.clear()
        self.sidebar.clear()
        self.table.setRowCount(0)
        while self.topo_layout.count():
            item = self.topo_layout.takeAt(0)
            if item and item.widget(): item.widget().deleteLater()
        self.file_lbl.setText("—")

    def populate(self, step_path, results, records):
        filename = os.path.basename(step_path)
        if not hasattr(self, '_records_map'): self._records_map = {}
        if not hasattr(self, '_paths_map'): self._paths_map = {}
        
        self._records_map[filename] = records
        self._paths_map[filename] = step_path
        
        if filename not in self._data_map:
            self._filenames.append(filename)
            self.sidebar.addItem(filename)
        self._data_map[filename] = results
        if filename not in self._renders_map:
            self._renders_map[filename] = {}
        
        if self.sidebar.count() == 1 or self.sidebar.currentItem().text() == filename:
            self.sidebar.setCurrentRow(self._filenames.index(filename))
            self._on_row_changed(self._filenames.index(filename))

    def add_renders(self, step_path, renders_dict):
        filename = os.path.basename(step_path)
        if filename not in self._renders_map: self._renders_map[filename] = {}
        self._renders_map[filename].update(renders_dict)
        if self.sidebar.currentItem() and self.sidebar.currentItem().text() == filename:
            self._on_row_changed(self._filenames.index(filename))

    def _on_row_changed(self, idx):
        if idx < 0 or idx >= len(self._filenames): return
        filename = self._filenames[idx]
        results = self._data_map[filename]

        self.file_lbl.setText(filename)
        
        v_scroll = self.table.verticalScrollBar().value()
        h_scroll = self.table.horizontalScrollBar().value()
        
        self.table.setRowCount(0)

        while self.topo_layout.count():
            item = self.topo_layout.takeAt(0)
            if item and item.widget(): item.widget().deleteLater()

        comp_map = {res[0]: res[1] for res in results}
        renders_dict = self._renders_map.get(filename, {})

        for res in results:
            comp = res[0]
            nodes = res[1]
            conf = res[2]
            is_fixed = len(res) > 3 and res[3]
            
            if not nodes: continue
            row = self.table.rowCount(); self.table.insertRow(row)

            base = comp.split("_")[0]
            col = COMPONENT_COLORS.get(comp, COMPONENT_COLORS.get(base, C['text']))
            
            is_ml = base in ML_COMPONENTS
            res_str = "Fixed" if is_fixed else ("Model" if is_ml else "Heuristic")
            n_item = QTableWidgetItem(f"{comp}\n({res_str})")
            n_item.setForeground(QColor(col)); n_item.setFont(QFont("Inter", 12, QFont.Bold))
            n_item.setData(Qt.UserRole, comp)
            self.table.setItem(row, 0, n_item)

            # 1: Render PNG
            img_w = QWidget(); img_l = QHBoxLayout(img_w); img_l.setContentsMargins(4,4,4,4)
            img_lbl = ClickableLabel(comp, renders_dict.get(comp))
            img_lbl.clicked.connect(self._open_preview)
            img_lbl.setAlignment(Qt.AlignCenter)
            img_lbl.setStyleSheet(f"background: {C['surface']}; border-radius: 8px;")
            if comp in renders_dict and os.path.exists(renders_dict[comp]):
                px = QPixmap(renders_dict[comp])
                if not px.isNull(): img_lbl.setPixmap(px.scaled(140, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                img_lbl.setText("N/A")
                img_lbl.setStyleSheet(f"color: {C['text_muted']}; background: {C['surface']}; border-radius: 8px;")
            img_l.addWidget(img_lbl)
            self.table.setCellWidget(row, 1, img_w)

            # 2: Fix
            action_w = QWidget()
            action_l = QHBoxLayout(action_w); action_l.setContentsMargins(0,0,0,0)
            action_l.setAlignment(Qt.AlignCenter)
            fix_b = QPushButton("Fix")
            fix_b.setFixedSize(64, 32)
            fix_b.setStyleSheet(f"""
                QPushButton {{
                    color: {C['bg']};
                    background-color: {C['text']};
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background-color: {C['text_dim']};
                }}
            """)
            fix_b.setCursor(Qt.PointingHandCursor)
            fix_b.clicked.connect(lambda _, f=filename, c=comp: self.correctionRequested.emit(f, c))
            action_l.addWidget(fix_b)
            self.table.setCellWidget(row, 2, action_w)

            # 3: Confidence
            conf_str = f"{conf*100:.1f}%"
            c_item = QTableWidgetItem(conf_str)
            if conf >= 0.9: c_item.setForeground(QColor(C['success']))
            elif conf >= 0.7: c_item.setForeground(QColor(C['warning']))
            else: c_item.setForeground(QColor(C['danger']))
            c_item.setFont(QFont("Inter", 12, QFont.Bold))
            self.table.setItem(row, 3, c_item)

            # 4: Solids
            s_item = QTableWidgetItem(f"Count: {len([n for n in nodes if n is not None])}\n" + ", ".join(f"#{n}" for n in nodes if n is not None))
            self.table.setItem(row, 4, s_item)

        self.table.resizeRowsToContents()
        self.table.verticalScrollBar().setValue(v_scroll)
        self.table.horizontalScrollBar().setValue(h_scroll)

    def _open_preview(self, name, path):
        if not path or not os.path.exists(path): return
        d = ImagePreviewDialog(name, path, self.window())
        d.exec()

# ── Debug console ──────────────────────────────────────────────────────────
class DebugConsole(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVisible(False)
        layout = QVBoxLayout(self); layout.setContentsMargins(0,0,0,0); layout.setSpacing(0)
        self.console = QTextEdit(); self.console.setObjectName("console")
        self.console.setReadOnly(True); self.console.setFixedHeight(200)
        layout.addWidget(self.console)

    def append(self, text):
        cur = self.console.textCursor(); cur.movePosition(QTextCursor.End)
        fmt = QTextCharFormat()
        col = C['text'] if "ML" in text else C['text_dim'] if "[Phase" in text else C['danger'] if "" in text else C['text_muted']
        fmt.setForeground(QColor(col))
        cur.insertText(text, fmt)
        self.console.setTextCursor(cur); self.console.ensureCursorVisible()

# ── Load Run Dialog ────────────────────────────────────────────────────────
class LoadRunDialog(QDialog):
    def __init__(self, history_dir, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Run History")
        self.resize(450, 500)
        self.setStyleSheet(f"background: {C['bg']}; color: {C['text']};")
        self.history_dir = history_dir
        self.selected_report = None
        
        layout = QVBoxLayout(self); layout.setContentsMargins(24, 24, 24, 24); layout.setSpacing(16)
        
        lbl = QLabel("Select a run to load:")
        lbl.setFont(QFont("Inter", 13, QFont.Bold))
        layout.addWidget(lbl)
        
        self.list_w = QListWidget()
        layout.addWidget(self.list_w)
        
        self.refresh_list()
        
        btn_layout = QHBoxLayout()
        self.del_btn = QPushButton("Purge Run"); self.del_btn.setObjectName("danger_btn")
        self.load_btn = QPushButton("Load"); self.load_btn.setObjectName("primary_btn")
        btn_layout.addWidget(self.del_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.load_btn)
        layout.addLayout(btn_layout)
        
        self.del_btn.clicked.connect(self._purge)
        self.load_btn.clicked.connect(self._load)
        self.list_w.itemDoubleClicked.connect(self._load)

    def refresh_list(self):
        self.list_w.clear()
        if not os.path.exists(self.history_dir): return
        for f in sorted(glob.glob(os.path.join(self.history_dir, "*.json")), reverse=True):
            item = QListWidgetItem(os.path.basename(f).replace(".json", ""))
            item.setData(Qt.UserRole, f)
            self.list_w.addItem(item)

    def _purge(self):
        item = self.list_w.currentItem()
        if not item: return
        path = item.data(Qt.UserRole)
        
        try:
            with open(path, "r") as f: report = json.load(f)
            for renders in report.get("renders", {}).values():
                if isinstance(renders, dict):
                    for img_path in renders.values():
                        if os.path.exists(img_path): os.remove(img_path)
                elif isinstance(renders, list):
                    for _, img_path in renders:
                        if os.path.exists(img_path): os.remove(img_path)
            os.remove(path)
            self.refresh_list()
        except Exception as e:
            print(f"Error purging: {e}")

    def _load(self):
        item = self.list_w.currentItem()
        if not item: return
        self.selected_report = item.data(Qt.UserRole)
        self.accept()

# ══════════════════════════════════════════════════════════════════════════
# MAIN WINDOW
# ══════════════════════════════════════════════════════════════════════════
class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ATLAS")
        self.resize(1200, 800)
        self.setMinimumSize(900, 600)
        self._worker = None
        self.current_report_path = None
        self._clean_cache()

        central = QWidget(); self.setCentralWidget(central)
        root = QVBoxLayout(central); root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        # Nav bar
        nav = QWidget(); nav.setObjectName("nav_bar"); nav.setFixedHeight(64)
        nav_layout = QHBoxLayout(nav); nav_layout.setContentsMargins(24, 0, 24, 0); nav_layout.setSpacing(0)

        name_lbl = QLabel("ATLAS"); name_lbl.setObjectName("app_name")
        nav_layout.addWidget(name_lbl)
        nav_layout.addSpacing(48)

        self._nav_btns = []
        self._pages_w = QStackedWidget()

        self.import_page  = ImportPage()
        self.results_page = ResultsPage()
        self.meshing_page = MeshingPage()
        self.contacts_page = ContactsPage()
        for p in [self.import_page, self.results_page, self.meshing_page, self.contacts_page]: self._pages_w.addWidget(p)

        for i, label in enumerate(["Import", "Results", "Meshing", "Contacts"]):
            btn = NavBtn(label)
            btn.clicked.connect(lambda _, idx=i: self._switch_page(idx))
            nav_layout.addWidget(btn)
            self._nav_btns.append(btn)
            
        nav_layout.addStretch()
        
        self.opt_render = ConfigCheckbox("Renders", True)

        self.load_btn = QPushButton("Load Run"); self.load_btn.setObjectName("ghost_btn")
        self.debug_toggle = QPushButton("Debug"); self.debug_toggle.setObjectName("ghost_btn"); self.debug_toggle.setCheckable(True)

        self.progress = QProgressBar()
        self.progress.setObjectName("progress")
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(2)
        
        self.progress_lbl = QLabel("")
        self.progress_lbl.setStyleSheet(f"color: {C['text_dim']}; font-style: italic; margin-right: 16px;")

        nav_layout.addWidget(self.progress_lbl)
        nav_layout.addWidget(self.opt_render)
        nav_layout.addWidget(self.load_btn)
        nav_layout.addSpacing(16)
        nav_layout.addWidget(self.debug_toggle)

        root.addWidget(nav)
        root.addWidget(self.progress)
        root.addWidget(self._pages_w, 1)

        self.debug_console = DebugConsole()
        root.addWidget(self.debug_console)

        self.import_page.run_btn.clicked.connect(self._toggle_run)
        self.load_btn.clicked.connect(self._load_run)
        self.results_page.save_btn.clicked.connect(self._save_run)
        self.results_page.export_btn.clicked.connect(self._export_cads)
        self.results_page.simlab_btn.clicked.connect(self._open_in_simlab)
        self.results_page.skip_simlab_btn.clicked.connect(self._skip_to_meshing)
        self.debug_toggle.toggled.connect(self.debug_console.setVisible)
        
        self.results_page.correctionRequested.connect(self._handle_correction)
        self.results_page.massRemoveRequested.connect(self._handle_mass_remove)
        
        self.meshing_page.meshRequested.connect(self._handle_mesh)
        self.meshing_page.meshAllRequested.connect(self._handle_mesh_all)
        
        self.contacts_page.contactRequested.connect(self._handle_contact)
        self.contacts_page.contactAllRequested.connect(self._handle_contact_all)

        # Hide Results, Meshing, and Contacts tabs initially
        self._nav_btns[1].hide()
        self._nav_btns[2].hide()
        self._nav_btns[3].hide()

        self._switch_page(0)
        self._start_api_log_watcher()

    def _toggle_run(self):
        if self._worker and self._worker.isRunning():
            self._stop()
        else:
            self._run()

    def _switch_page(self, idx):
        self._pages_w.setCurrentIndex(idx)
        for i, btn in enumerate(self._nav_btns): btn.set_active(i == idx)

    def _clean_cache(self):
        valid_dirs = set()
        history_dir = os.path.join(_ROOT, "_run_history")
        if os.path.exists(history_dir):
            for f in glob.glob(os.path.join(history_dir, "*.json")):
                try:
                    with open(f, "r") as fh: report = json.load(fh)
                    for renders in report.get("renders", {}).values():
                        if isinstance(renders, dict):
                            for img_path in renders.values():
                                if "_cache" in img_path:
                                    valid_dirs.add(os.path.dirname(os.path.dirname(img_path)))
                        elif isinstance(renders, list):
                            for _, img_path in renders:
                                if "_cache" in img_path:
                                    valid_dirs.add(os.path.dirname(os.path.dirname(img_path)))
                except: pass
                
        cache_dir = os.path.join(_ROOT, "_cache", "renders")
        if os.path.exists(cache_dir):
            for d in os.listdir(cache_dir):
                dir_path = os.path.join(cache_dir, d)
                if dir_path not in valid_dirs:
                    shutil.rmtree(dir_path, ignore_errors=True)

    def _handle_correction(self, filename, old_comp):
        img_path = None
        if filename in self.results_page._renders_map:
            img_path = self.results_page._renders_map[filename].get(old_comp, None)
                    
        dialog = CorrectionDialog(filename, old_comp, img_path, self)
        if dialog.exec() == QDialog.Accepted:
            new_comp = dialog.new_comp
            
            if new_comp == "__REMOVE__":
                if filename in self.results_page._data_map:
                    self.results_page._data_map[filename] = [
                        res for res in self.results_page._data_map[filename] if res[0] != old_comp
                    ]
                
                if filename in self.results_page._renders_map:
                    renders_dict = self.results_page._renders_map[filename]
                    if old_comp in renders_dict:
                        del renders_dict[old_comp]
                
                self.results_page._on_row_changed(self.results_page._filenames.index(filename))
                
                if self.current_report_path and os.path.exists(self.current_report_path):
                    with open(self.current_report_path, "r") as f:
                        data = json.load(f)
                    updated = False
                    if "results" in data and filename in data["results"]:
                        data["results"][filename] = [res for res in data["results"][filename] if res[0] != old_comp]
                        updated = True
                    if "renders" in data and filename in data["renders"]:
                        renders_data = data["renders"][filename]
                        if isinstance(renders_data, dict) and old_comp in renders_data:
                            del renders_data[old_comp]
                            updated = True
                        elif isinstance(renders_data, list):
                            data["renders"][filename] = [r for r in renders_data if r[0] != old_comp]
                            updated = True
                    if updated:
                        with open(self.current_report_path, "w") as f:
                            json.dump(data, f, indent=2)
                return
            
            if filename in self.results_page._data_map:
                res_list = self.results_page._data_map[filename]
                
                # Check for existing labels
                existing_matches = []
                for idx, res in enumerate(res_list):
                    if res[0] == new_comp or res[0].startswith(f"{new_comp}_"):
                        if res[0] != old_comp: # Don't count the one we are changing
                            existing_matches.append(idx)
                            
                new_comp_name = new_comp
                if len(existing_matches) > 0:
                    for idx in existing_matches:
                        if res_list[idx][0] == new_comp:
                            # Rename exact match to _0
                            res_list[idx] = (f"{new_comp}_0", res_list[idx][1], res_list[idx][2], res_list[idx][3] if len(res_list[idx])>3 else False)
                            if filename in self.results_page._renders_map:
                                rd = self.results_page._renders_map[filename]
                                if new_comp in rd:
                                    p = rd[new_comp]
                                    new_p = p.replace(f"_{new_comp}_", f"_{new_comp}_0_")
                                    if os.path.exists(p): os.rename(p, new_p)
                                    rd[f"{new_comp}_0"] = new_p
                                    del rd[new_comp]
                    new_comp_name = f"{new_comp}_{len(existing_matches)}"
                
                for i, res in enumerate(res_list):
                    if res[0] == old_comp:
                        res_list[i] = (new_comp_name, res[1], 1.0, True)
                        break
                self.results_page._on_row_changed(self.results_page._filenames.index(filename))
                
            if filename in self.results_page._renders_map:
                renders_dict = self.results_page._renders_map[filename]
                if old_comp in renders_dict:
                    p = renders_dict[old_comp]
                    new_p = p.replace(f"_{old_comp}_", f"_{new_comp_name}_")
                    if os.path.exists(p):
                        os.rename(p, new_p)
                    del renders_dict[old_comp]
                    renders_dict[new_comp_name] = new_p
                self.results_page._on_row_changed(self.results_page._filenames.index(filename))
                
            if self.current_report_path and os.path.exists(self.current_report_path):
                with open(self.current_report_path, "r") as f:
                    data = json.load(f)
                updated = False
                
                if "results" in data and filename in data["results"]:
                    # Overwrite whole list
                    data["results"][filename] = [list(r) for r in self.results_page._data_map[filename]]
                    updated = True
                if "renders" in data and filename in data["renders"]:
                    data["renders"][filename] = self.results_page._renders_map[filename]
                    updated = True
                    
                if updated:
                    with open(self.current_report_path, "w") as f:
                        json.dump(data, f, indent=2)

    def _handle_mass_remove(self, filename, comps_to_remove):
        if self.current_report_path and os.path.exists(self.current_report_path):
            with open(self.current_report_path, "r") as f:
                data = json.load(f)
            updated = False
            
            if "results" in data and filename in data["results"]:
                data["results"][filename] = [list(r) for r in self.results_page._data_map[filename]]
                updated = True
                
            if "renders" in data and filename in data["renders"]:
                data["renders"][filename] = self.results_page._renders_map[filename]
                updated = True
                
            if updated:
                with open(self.current_report_path, "w") as f:
                    json.dump(data, f, indent=2)

    def _run(self):
        cfg = self.import_page.get_config()
        if not cfg.get("in_paths"): return

        do_render = self.opt_render.chk.isChecked()

        self._clean_cache()
        self.current_report_path = None
        
        r_dir = None
        if do_render:
            base_dir = self.opt_render.path if self.opt_render.path else os.path.join(_ROOT, "_cache", "renders")
            r_dir = os.path.join(base_dir, time.strftime("%Y%m%d_%H%M%S"))
            os.makedirs(r_dir, exist_ok=True)

        self.results_page.clear()
        self.debug_console.console.clear()
        self.progress.setValue(0)
        self.progress.setMaximum(0)
        
        if not self.debug_toggle.isChecked(): self.debug_toggle.setChecked(True)

        self.import_page.run_btn.setText("Stop")
        self.import_page.run_btn.setObjectName("danger_btn")
        self.import_page.run_btn.style().unpolish(self.import_page.run_btn); self.import_page.run_btn.style().polish(self.import_page.run_btn)

        config_comps = {
            0: ['STAYCAP', 'SIDE_BODY'],
            1: ['STAYCAP'],
            2: ['PCB_BOX'],
            3: ['PCB_BOX', 'FALSE_COVER']
        }
        
        expected_components = []
        if cfg["config_idx"] is not None:
            expected_components.extend(config_comps.get(cfg["config_idx"], []))
        if cfg["additional_comps"]:
            expected_components.extend(cfg["additional_comps"])
            
        expected_components = list(set(expected_components))

        self._worker = InferenceWorker(
            step_paths=cfg["in_paths"], 
            render_dir=r_dir,
            export_dir=None,
            expected_components=expected_components, 
            do_render=do_render,
            do_export=False
        )
        self._worker.console_line.connect(self.debug_console.append)
        self._worker.file_started.connect(lambda p: self.progress_lbl.setText(os.path.basename(p)))
        self._worker.batch_progress.connect(lambda c, t: (self.progress.setMaximum(100), self.progress.setValue(int(c/t*100))))
        self._worker.file_done.connect(self._on_done)
        self._worker.finished_all.connect(self._on_finished)
        self._worker.error_occurred.connect(self._on_error)
        self._worker.start()

    def _stop(self):
        if self._worker: self._worker.abort()
        self.import_page.run_btn.setText("Process")
        self.import_page.run_btn.setObjectName("primary_btn")
        self.import_page.run_btn.style().unpolish(self.import_page.run_btn); self.import_page.run_btn.style().polish(self.import_page.run_btn)

    def _on_done(self, step_path, result, render_dir):
        if result and "results" in result:
            self._nav_btns[1].show()
            self.results_page.populate(step_path, result["results"], result.get("records", []))
            self._switch_page(1)
        if render_dir:
            renders_dict = {}
            for img in sorted(glob.glob(os.path.join(render_dir, "*.png"))):
                c_name = os.path.splitext(os.path.basename(img))[0].replace(os.path.splitext(os.path.basename(step_path))[0] + "_", "", 1)
                renders_dict[c_name] = img
            self.results_page.add_renders(step_path, renders_dict)

    def _on_finished(self):
        self.progress.setMaximum(100)
        self.progress.setValue(100)
        self.import_page.run_btn.setText("Process")
        self.import_page.run_btn.setObjectName("primary_btn")
        self.import_page.run_btn.style().unpolish(self.import_page.run_btn); self.import_page.run_btn.style().polish(self.import_page.run_btn)

    def _on_error(self, msg):
        self.import_page.run_btn.setText("Process")
        self.import_page.run_btn.setObjectName("primary_btn")
        self.import_page.run_btn.style().unpolish(self.import_page.run_btn); self.import_page.run_btn.style().polish(self.import_page.run_btn)
        if not self.debug_toggle.isChecked(): self.debug_toggle.setChecked(True)
        self.debug_console.append(f" ERROR:\n{msg}")

    def _start_api_log_watcher(self):
        import os
        self._api_log_path = os.path.join(_ROOT, "_cache", "api_server.log")
        self._api_log_pos = 0
        if os.path.exists(self._api_log_path):
            self._api_log_pos = os.path.getsize(self._api_log_path)
            
        self._api_log_timer = QTimer(self)
        self._api_log_timer.timeout.connect(self._poll_api_log)
        self._api_log_timer.start(500)
        self._active_api_job = None

    def _poll_api_log(self):
        import os, re
        if not os.path.exists(self._api_log_path): return
        
        try:
            size = os.path.getsize(self._api_log_path)
            if size == self._api_log_pos: return
            if size < self._api_log_pos: self._api_log_pos = 0
            
            with open(self._api_log_path, 'r', encoding='utf-8') as f:
                f.seek(self._api_log_pos)
                new_data = f.read()
                self._api_log_pos = f.tell()
                
            for line in new_data.split('\n'):
                line = line.strip()
                if not line: continue
                
                # Check for job start
                match = re.search(r'Processing mesh: (.*?) with', line)
                if match:
                    self._active_api_job = match.group(1).strip()
                    if hasattr(self, 'meshing_page'):
                        self.meshing_page.update_status(self._active_api_job, "Meshing...")
                    self.progress_lbl.setText(f"API: Meshing {self._active_api_job}...")
                
                elif "<- EXECUTION COMPLETED SUCCESSFULLY" in line and self._active_api_job:
                    if hasattr(self, 'meshing_page'):
                        self.meshing_page.update_status(self._active_api_job, "Success")
                    self.progress_lbl.setText(f"API: Success {self._active_api_job}")
                    self._active_api_job = None
                    
                elif "<- EXECUTION FAILED" in line and self._active_api_job:
                    if hasattr(self, 'meshing_page'):
                        self.meshing_page.update_status(self._active_api_job, "Failed")
                    self.progress_lbl.setText(f"API: Failed {self._active_api_job}")
                    self._active_api_job = None
        except:
            pass

    def _save_run(self):
        name, ok = QInputDialog.getText(self, "Save Run", "Run Name:", text=time.strftime("Run_%Y%m%d_%H%M%S"))
        if not ok or not name.strip(): return
        
        history_dir = os.path.join(_ROOT, "_run_history")
        os.makedirs(history_dir, exist_ok=True)
        
        try:
            report = {
                "version": "1.2",
                "results": self.results_page._data_map,
                "renders": self.results_page._renders_map,
                "render_path": self.opt_render.path,
                "paths": getattr(self.results_page, '_paths_map', {})
            }
            report_path = os.path.join(history_dir, f"{name.strip()}.json")
            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)
            self.current_report_path = report_path
            self.progress_lbl.setText("Saved successfully")
        except Exception as e:
            self.progress_lbl.setText(f"Save failed: {e}")

    def _export_cads(self):
        d = QFileDialog.getExistingDirectory(self, "Select Save Directory for CAD Export", _ROOT)
        if not d: return
        
        self.progress.setValue(0)
        self.progress_lbl.setText("Exporting CADs...")
        QApplication.processEvents()
        
        from engine.step_exporter import export_named_step
        total = len(self.results_page._data_map)
        
        exported_count = 0
        for i, (filename, results_list) in enumerate(self.results_page._data_map.items()):
            self.progress.setValue(int((i/total)*100))
            QApplication.processEvents()
            
            records = getattr(self.results_page, '_records_map', {}).get(filename, [])
            original_path = getattr(self.results_page, '_paths_map', {}).get(filename, "")
            if not original_path or not os.path.exists(original_path):
                QMessageBox.warning(self, "Export Failed", "Cannot export CAD from history because the original STEP file was not found on disk.")
                self.progress.setValue(100)
                self.progress_lbl.setText("Export aborted")
                return
                
            if not records:
                self.progress_lbl.setText(f"Re-parsing {filename} geometry...")
                QApplication.processEvents()
                try:
                    from core.step_loader import load_step_xcaf, extract_solids
                    doc, shape_tool = load_step_xcaf(original_path)
                    records = extract_solids(shape_tool)
                except Exception as e:
                    QMessageBox.warning(self, "Parse Failed", f"Failed to parse CAD: {e}")
                    return
            
            res_dict = {"results": results_list, "records": records}
            try:
                export_named_step(res_dict, d, original_path)
                
                if not hasattr(self, 'last_export_path'): self.last_export_path = {}
                basename = os.path.splitext(os.path.basename(original_path))[0]
                self.last_export_path[filename] = os.path.join(d, f"{basename}_NAMED.step")
                
                exported_count += 1
            except Exception as e:
                print(f"Error exporting {filename}: {e}")
                
        self.progress.setValue(100)
        self.progress_lbl.setText(f"Exported {exported_count} CADs")

    def _open_in_simlab(self):
        idx = self.results_page.sidebar.currentRow()
        if idx < 0 or idx >= len(self.results_page._filenames): return
        filename = self.results_page._filenames[idx]
        
        if not hasattr(self, 'last_export_path'): self.last_export_path = {}
        export_path = self.last_export_path.get(filename)
        
        if not export_path or not os.path.exists(export_path):
            export_dir = os.path.join(_ROOT, "exports")
            os.makedirs(export_dir, exist_ok=True)
            
            results_list = self.results_page._data_map.get(filename)
            records = getattr(self.results_page, '_records_map', {}).get(filename, [])
            original_path = getattr(self.results_page, '_paths_map', {}).get(filename, "")
            
            if not original_path or not os.path.exists(original_path):
                QMessageBox.warning(self, "SimLab Failed", "Cannot auto-export CAD from history because the original STEP file was not found on disk.")
                return
                
            if not records:
                self.progress_lbl.setText(f"Re-parsing {filename} geometry...")
                QApplication.processEvents()
                try:
                    from core.step_loader import load_step_xcaf, extract_solids
                    doc, shape_tool = load_step_xcaf(original_path)
                    records = extract_solids(shape_tool)
                except Exception as e:
                    QMessageBox.warning(self, "Parse Failed", f"Failed to parse CAD: {e}")
                    return
                
            from engine.step_exporter import export_named_step
            res_dict = {"results": results_list, "records": records}
            
            self.progress_lbl.setText(f"Auto-exporting {filename} for SimLab...")
            QApplication.processEvents()
            try:
                export_named_step(res_dict, export_dir, original_path)
                basename = os.path.splitext(os.path.basename(original_path))[0]
                expected_path = os.path.join(export_dir, f"{basename}_NAMED.step")
                
                if os.path.exists(expected_path):
                    export_path = expected_path
                    self.last_export_path[filename] = export_path
                else:
                    QMessageBox.warning(self, "SimLab Failed", f"Expected export file not found: {expected_path}")
                    return
            except Exception as e:
                QMessageBox.warning(self, "SimLab Failed", f"Export failed: {e}")
                return
                
        self.progress_lbl.setText("Launching SimLab...")
        QApplication.processEvents()
        
        import subprocess
        simlab_exe = r"E:\Program Files\Altair\SimLab\bin\win64\SimLab.bat"
        if not os.path.exists(simlab_exe):
            QMessageBox.warning(self, "SimLab Not Found", f"Could not find SimLab at:\n{simlab_exe}")
            return
            
        # Write the import macro
        macro_path = os.path.join(_ROOT, "_cache", "simlab_import_macro.py")
        os.makedirs(os.path.dirname(macro_path), exist_ok=True)
        
        macro_code = f'''import simlab

UnitSystem = """ <UnitSystem UUID="3aca8564-4d38-4b0b-887c-6a542d4001c6">
  <SetCurrentDisplaySystem Name="MMKS (mm kg N C s)"/>
</UnitSystem>"""
simlab.execute(UnitSystem)

STEP_Import = """ <STEP_Import CheckBox="ON" Type="STEP" UUID="e88f2fcc-2430-4e47-9455-78b4dea9b064" gda="">
  <FileName HelpStr="File name to be imported." Value="{export_path.replace(chr(92), '/')}" widget="LineEdit"/>
  <Method Value="Convert to Parasolid"/>
  <BodyName Value="1"/>
  <ReadPartName Value="1"/>
  <SketchWireframe Value="0"/>
  <Groups Value="0"/>
  <Imprint Value="0"/>
  <Facets Value="0"/>
  <AssemblyStructure Value="1"/>
  <SaveGeometryInDatabase Value="1"/>
</STEP_Import>"""
simlab.execute(STEP_Import)
'''
        with open(macro_path, "w") as f:
            f.write(macro_code)

        # The API listener is now a permanent standalone script (simlab_api_server.py)
        # which the user will trigger via a custom SimLab dialog/ribbon button.

        try:
            # Launch SimLab passing the macro to execute automatically, fully detaching it 
            # and muting stdout/stderr to prevent Windows pipe buffer deadlocks on large CADs.
            import subprocess
            import copy
            
            clean_env = os.environ.copy()
            for k in list(clean_env.keys()):
                if k.upper() in ["PYTHONHOME", "PYTHONPATH"]:
                    del clean_env[k]
                    
            DETACHED_PROCESS = 0x00000008
            subprocess.Popen(
                [simlab_exe, "-auto", macro_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=DETACHED_PROCESS,
                cwd=os.path.dirname(simlab_exe),
                env=clean_env
            )
            self.progress_lbl.setText(f"Opened {os.path.basename(export_path)} in SimLab")
            
            # Populate and unlock Meshing Tab immediately
            comps = []
            if filename in self.results_page._data_map:
                # Only include components that actually have assigned solids (len(res[1]) > 0)
                comps = [res[0] for res in self.results_page._data_map[filename] if res[1]]
            session_dir = os.path.dirname(self.current_report_path) if self.current_report_path else None
            renders = self.results_page._renders_map.get(filename, {})
            self.meshing_page.populate(comps, session_dir, renders)
            self.contacts_page.populate(comps)
            self._nav_btns[2].show()
            self._nav_btns[3].show()
            self._switch_page(2)

            # Show instruction message box (non-blocking if we prefer, but for now just show it after tab switch)
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Connect Live Meshing")
            msg.setText("SimLab is launching! Once it is fully open and the CAD is loaded, click your custom 'Start ATLAS API' button in the SimLab Ribbon to activate Live Meshing!")
            msg.exec()
            
        except Exception as e:
            QMessageBox.warning(self, "SimLab Failed", f"Failed to launch SimLab: {e}")

    def _skip_to_meshing(self):
        idx = self.results_page.sidebar.currentRow()
        if idx < 0 or idx >= len(self.results_page._filenames): return
        filename = self.results_page._filenames[idx]
        
        self.progress_lbl.setText("Skipping CAD export, opening Meshing Tab...")
        
        comps = []
        if filename in self.results_page._data_map:
            comps = [res[0] for res in self.results_page._data_map[filename] if res[1]]
        
        session_dir = os.path.dirname(self.current_report_path) if self.current_report_path else None
        renders = self.results_page._renders_map.get(filename, {})
        
        self.meshing_page.populate(comps, session_dir, renders)
        self.contacts_page.populate(comps)
        
        self._nav_btns[2].show()
        self._nav_btns[3].show()
        self._switch_page(2)

    def _load_run(self):
        history_dir = os.path.join(_ROOT, "_run_history")
        d = LoadRunDialog(history_dir, self)
        if d.exec() != QDialog.Accepted or not d.selected_report: return
        
        self.results_page.clear()
        self.current_report_path = d.selected_report
        
        self._nav_btns[1].show()
        
        try:
            with open(d.selected_report, "r") as f:
                report = json.load(f)
                
            self.opt_render.path = report.get("render_path")
            if self.opt_render.path:
                self.opt_render.btn.setToolTip(f"Save Path: {self.opt_render.path}")
                self.opt_render.btn.setStyleSheet(f"color: {C['accent']}; font-weight: bold; text-align: left; background: transparent; border: none; text-decoration: underline;")
                
            for filename, results in report.get("results", {}).items():
                flat_results = []
                for res in results:
                    comp = res[0]
                    nodes = res[1]
                    if len([n for n in nodes if n is not None]) > 1:
                        valid_idx = 1
                        for n in nodes:
                            if n is not None:
                                flat_results.append((f"{comp}_{valid_idx}", [n], res[2], res[3] if len(res)>3 else False))
                                valid_idx += 1
                    else:
                        flat_results.append(res)
                
                # Populate expects: populate(self, step_path, results, records)
                original_path = report.get("paths", {}).get(filename, filename)
                self.results_page.populate(original_path, flat_results, [])
                
            for filename, renders in report.get("renders", {}).items():
                valid_renders = {k: v for k, v in renders.items() if isinstance(v, str) and os.path.exists(v)}
                if isinstance(renders, list): # backward compatibility with list of lists
                    valid_renders = {k: v for k, v in renders if os.path.exists(v)}
                self.results_page.add_renders(filename, valid_renders)
                        
            target_page = 1
            self._switch_page(target_page)
        except Exception as e:
            print(f"Error loading report: {e}")

    def _handle_mesh(self, comp_name: str, config: dict):
        """
        Dispatch a mesh job via TCP to the SimLab API server.
        config is a flat dict of param keys -> values from MeshConfigPanel.
        If config is empty (Mesh All), JSON defaults are used.
        """
        script_map = {
            "TOP_COVER":    "mesh_top_cover_complete.py",
            "OUTER_RACE":   "mesh_races.py",
            "MID_RACE":     "mesh_races.py",
            "INNER_RACE":   "mesh_races.py",
            "BEARING_TOP":  "mesh_races.py",
            "BEARING_BOTTOM":"mesh_races.py",
            "SHAFT":        "mesh_shaft.py",
            "STATOR":       "mesh_stator.py",
            "ROTOR_RING":   "mesh_rotor_ring.py",
            "PCB_BRACKET":  "mesh_pcb_bracket.py",
            "DISPLAY_PCB":  "mesh_display_pcb.py",
            "PCB":          "mesh_display_pcb.py",
            "BOTTOM_COVER": "mesh_bottom_cover.py",
            "EPS_PACKAGING":"mesh_EPS.py",
            "FALSE_COVER":  "mesh_false_cover.py",
            "CANOPY":       "mesh_canopies.py",
            "BODY":         "mesh_body.py",
        }

        # Resolve base name (strip numeric suffix e.g. OUTER_RACE_1 -> OUTER_RACE)
        base_name = comp_name
        check_name = comp_name.replace(" ", "_").upper()
        
        script_file = None
        for standard in script_map:
            if check_name == standard or check_name.startswith(standard + "_"):
                script_file = script_map[standard]
                break
                
        # If no standard prefix matched, check for structural patterns
        if not script_file:
            if "BOX" in check_name:
                script_file = "mesh_boxes.py"
            elif "CANOPY" in check_name:
                script_file = "mesh_canopies.py"
            elif "BOTTOM_COVER" in check_name:
                script_file = "mesh_bottom_cover.py"
            else:
                script_file = "mesh_body.py"
        script_path = os.path.join(_ROOT, "mesh_templates", script_file)
        if not os.path.exists(script_path):
            QMessageBox.warning(self, "Mesh Error", f"Mesh script not found: {script_file}")
            return

        try:
            import socket, json
            
            # The SimLab script needs to know the correct path to the temp directory
            temp_dir = os.path.join(_ROOT, "EXISTING_SCRIPTS", "TEMP").replace(chr(92), '/')
            os.makedirs(temp_dir, exist_ok=True)
            config["__temp_dir__"] = temp_dir
            
            payload = json.dumps({
                "script_name": script_file,
                "body_name": comp_name,
                "config": config,
                "scripts_dir": os.path.join(_ROOT, "mesh_templates").replace('\\', '/')
            })
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(5.0)  # Increased from 2.0s
                s.connect(('127.0.0.1', 5050))
                s.sendall(payload.encode('utf-8'))
                s.close()
                self.progress_lbl.setText(f"API: Dispatched mesh job for {comp_name}")
            except ConnectionRefusedError:
                QMessageBox.warning(self, "API Error",
                    "SimLab API listener is not running!\n"
                    "Click the 'ATLAS API' button in SimLab first.")
                return False
            except socket.timeout:
                QMessageBox.warning(self, "API Error",
                    "Connection to SimLab API timed out!\n"
                    "Please close SimLab, restart it, and click 'ATLAS API' again.")
                return False
        except Exception as e:
            QMessageBox.critical(self, "Mesh Error", f"Failed to dispatch mesh script: {e}")
            return False
        
        return True

    def _handle_mesh_all(self, jobs):
        """Dispatch all components using their saved JSON default configs."""
        for comp_name, config in jobs:
            success = self._handle_mesh(comp_name, config)
            if success is False:
                break
            import time
            time.sleep(0.1)
        self.progress_lbl.setText("Dispatched all mesh jobs")

    def _handle_contact(self, contact_name: str, config: dict):
        """Dispatch a contact job via TCP to the SimLab API server."""
        try:
            import socket, json
            
            payload = json.dumps({
                "task_type": "create_contact",
                "contact_name": contact_name,
                "config": config,
                "scripts_dir": os.path.join(_ROOT, "contact_templates").replace('\\', '/')
            })
            
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(5.0)
                s.connect(('127.0.0.1', 5050))
                s.sendall(payload.encode('utf-8'))
                s.close()
                self.progress_lbl.setText(f"API: Dispatched contact job for {contact_name}")
            except ConnectionRefusedError:
                QMessageBox.warning(self, "API Error",
                    "SimLab API listener is not running!\n"
                    "Click the 'ATLAS API' button in SimLab first.")
                return False
            except socket.timeout:
                QMessageBox.warning(self, "API Error",
                    "Connection to SimLab API timed out!")
                return False
        except Exception as e:
            QMessageBox.critical(self, "Contact Error", f"Failed to dispatch contact script: {e}")
            return False
            
        return True

    def _handle_contact_all(self, jobs):
        for contact_name, config in jobs:
            success = self._handle_contact(contact_name, config)
            if success is False:
                break
            import time
            time.sleep(0.1)
        self.progress_lbl.setText("Dispatched all contact jobs")

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("ATLAS")
    app.setStyleSheet(SS)
    p = app.palette(); R = QPalette.ColorRole
    p.setColor(R.Window, QColor(C['bg'])); p.setColor(R.WindowText, QColor(C['text']))
    p.setColor(R.Base, QColor(C['card'])); p.setColor(R.Text, QColor(C['text']))
    p.setColor(R.Button, QColor(C['surface'])); p.setColor(R.ButtonText, QColor(C['text']))
    app.setPalette(p)
    w = App(); w.show()
    sys.exit(app.exec())

if __name__ == "__main__": main()
