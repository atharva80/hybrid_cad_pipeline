"""
mesh_config_panel.py — Clickable component config side-panel for the Meshing Tab.
When the user clicks a component row, this panel slides in and shows all tunable
mesh parameters loaded from config/mesh_config/<script>.json.

Signals
-------
meshRequested : (comp_name: str, config: dict)
    Emitted when the user clicks the Mesh button on the panel.
"""

import os
import json
import copy

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QLineEdit, QComboBox, QSizePolicy,
    QSpacerItem
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QDoubleValidator, QIntValidator

from gui.styles import C, SS

_CONFIGS_DIR = os.path.join(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
    "config", "mesh_config"
)

# Map component base names → config JSON filenames
_COMP_CONFIG_MAP = {
    "SHAFT":        "mesh_shaft",
    "STATOR":       "mesh_stator",
    "OUTER_RACE":   "mesh_races",
    "MID_RACE":     "mesh_races",
    "INNER_RACE":   "mesh_races",
    "ROTOR_RING":   "mesh_rotor_ring",
    "TOP_COVER":    "mesh_top_cover_complete",
    "BOTTOM_COVER": "mesh_bottom_cover",
    "BODY":         "mesh_body",
    "PCB_BRACKET":  "mesh_pcb_bracket",
    "DISPLAY_PCB":  "mesh_display_pcb",
    "EPS_PACKAGING":"mesh_EPS",
    "BEARING_TOP":  "mesh_races",
    "BEARING_BOTTOM":"mesh_races",
    "PCB_BOX":      "mesh_pcb_box",
}


def _get_config_key(comp_name: str) -> str | None:
    """Strip numeric suffixes (_1, _2) and look up the config key."""
    base = comp_name
    for key in _COMP_CONFIG_MAP:
        if comp_name == key or comp_name.startswith(key + "_"):
            base = key
            break
    return _COMP_CONFIG_MAP.get(base)


def _load_config(comp_name: str, session_dir: str = None) -> dict | None:
    key = _get_config_key(comp_name)
    if not key:
        return None
    # If session_dir is provided, check there first
    if session_dir:
        session_path = os.path.join(session_dir, "mesh_configs", f"{key}.json")
        if os.path.exists(session_path):
            with open(session_path, "r", encoding="utf-8") as f:
                return json.load(f)
    
    # Fallback to defaults
    path = os.path.join(_CONFIGS_DIR, f"{key}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def flatten_config(config: dict) -> dict:
    """Flatten a hierarchical JSON config into a 1D dict for the meshing scripts."""
    flat = {}
    
    for k, v in config.get("global", {}).items():
        flat[f"global.{k}"] = v.get("value") if isinstance(v, dict) else v

    for mc in config.get("mesh_controls", []):
        for k, v in mc.get("params", {}).items():
            flat[f"mc.{mc['name']}.{k}"] = v.get("value") if isinstance(v, dict) else v

    for k, v in config.get("quality", {}).items():
        flat[f"quality.{k}"] = v.get("value") if isinstance(v, dict) else v

    for k, v in config.get("volume", {}).items():
        flat[f"volume.{k}"] = v.get("value") if isinstance(v, dict) else v

    for k, v in config.get("special", {}).items():
        flat[f"special.{k}"] = v.get("value") if isinstance(v, dict) else v

    return flat


def _save_config(comp_name: str, config: dict, session_dir: str = None):
    key = _get_config_key(comp_name)
    if not key:
        return
    # If session_dir is provided, save there. Otherwise save to defaults.
    if session_dir:
        save_dir = os.path.join(session_dir, "mesh_configs")
        os.makedirs(save_dir, exist_ok=True)
    else:
        save_dir = _CONFIGS_DIR
        
    path = os.path.join(save_dir, f"{key}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


class _SectionHeader(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFont(QFont("Inter", 8, QFont.Bold))
        self.setStyleSheet(
            f"color: {C['text_dim']}; text-transform: uppercase; "
            f"letter-spacing: 1px; padding: 8px 0px 4px 0px; "
            f"border-bottom: 1px solid {C['border']};"
        )


class _ParamRow(QWidget):
    """A single labelled editable field (float or int or combo)."""

    def __init__(self, label: str, param_def: dict, parent=None):
        super().__init__(parent)
        self._def = param_def
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(8)

        lbl = QLabel(label)
        lbl.setFont(QFont("Inter", 9))
        lbl.setStyleSheet(f"color: {C['text']};")
        lbl.setMinimumWidth(160)
        layout.addWidget(lbl)

        if "options" in param_def:
            self.widget = QComboBox()
            self.widget.addItems(param_def["options"])
            self.widget.setCurrentText(str(param_def["value"]))
            self.widget.setStyleSheet(
                f"background: {C['surface']}; color: {C['text']}; "
                f"padding: 4px; border-radius: 4px; min-width: 80px;"
            )
        else:
            self.widget = QLineEdit(str(param_def["value"]))
            self.widget.setStyleSheet(
                f"background: {C['surface']}; color: {C['text']}; "
                f"padding: 4px 6px; border-radius: 4px; min-width: 70px; "
                f"border: 1px solid {C['border']};"
            )
            unit = param_def.get("unit", "")
            if unit == "count":
                self.widget.setValidator(QIntValidator(1, 9999))
            else:
                self.widget.setValidator(QDoubleValidator(0.0, 9999.0, 4))
        layout.addWidget(self.widget)

        unit = param_def.get("unit", "")
        if unit and unit != "count":
            ul = QLabel(unit)
            ul.setStyleSheet(f"color: {C['text_dim']}; font-size: 9px;")
            layout.addWidget(ul)

        layout.addStretch()

    def get_value(self):
        if isinstance(self.widget, QComboBox):
            return self.widget.currentText()
        raw = self.widget.text()
        unit = self._def.get("unit", "")
        if unit == "count":
            try:
                return int(raw)
            except ValueError:
                return self._def["value"]
        else:
            try:
                return float(raw)
            except ValueError:
                return self._def["value"]


class MeshConfigPanel(QWidget):
    """
    Side-panel that shows the JSON-driven mesh configuration for a component.
    """
    meshRequested = Signal(str, dict)   # (comp_name, resolved_config)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._comp_name = None
        self._session_dir = None
        self._orig_config = None
        self._param_rows: dict[str, _ParamRow] = {}   # key → widget

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Header bar ────────────────────────────────────────────
        self._header = QWidget()
        self._header.setStyleSheet(f"background: {C['surface']}; border-bottom: 1px solid {C['border']};")
        h_layout = QHBoxLayout(self._header)
        h_layout.setContentsMargins(16, 10, 16, 10)

        self._title_lbl = QLabel("— Select a component —")
        self._title_lbl.setFont(QFont("Inter", 13, QFont.Bold))
        self._title_lbl.setStyleSheet(f"color: {C['text']};")
        
        # We will add an image label below the title in the header layout
        title_vbox = QVBoxLayout()
        title_vbox.setContentsMargins(0, 0, 0, 0)
        title_vbox.addWidget(self._title_lbl)
        
        self._image_lbl = QLabel()
        self._image_lbl.setFixedSize(120, 120)
        self._image_lbl.setStyleSheet(f"border: 1px solid {C['border']}; border-radius: 4px;")
        self._image_lbl.hide()
        title_vbox.addWidget(self._image_lbl)
        
        h_layout.addLayout(title_vbox)
        h_layout.addStretch()

        self._close_btn = QPushButton("✕")
        self._close_btn.setFixedSize(28, 28)
        self._close_btn.setObjectName("ghost_btn")
        self._close_btn.clicked.connect(self.hide)
        h_layout.addWidget(self._close_btn)

        outer.addWidget(self._header)

        # ── Scrollable body ────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self._body = QWidget()
        self._body.setStyleSheet(f"background: {C['bg']};")
        self._body_layout = QVBoxLayout(self._body)
        self._body_layout.setContentsMargins(16, 12, 16, 12)
        self._body_layout.setSpacing(4)
        self._body_layout.addStretch()

        scroll.setWidget(self._body)
        outer.addWidget(scroll, 1)

        # ── Footer ─────────────────────────────────────────────────
        footer = QWidget()
        footer.setStyleSheet(f"background: {C['surface']}; border-top: 1px solid {C['border']};")
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(16, 10, 16, 10)
        f_layout.setSpacing(8)

        self._reset_btn = QPushButton("Reset Defaults")
        self._reset_btn.setObjectName("ghost_btn")
        self._reset_btn.clicked.connect(self._reset_defaults)
        f_layout.addWidget(self._reset_btn)

        self._save_btn = QPushButton("Save Config")
        self._save_btn.setObjectName("ghost_btn")
        self._save_btn.clicked.connect(self._save_config)
        f_layout.addWidget(self._save_btn)

        f_layout.addStretch()

        self._mesh_btn = QPushButton("▶  Mesh")
        self._mesh_btn.setObjectName("primary_btn")
        self._mesh_btn.setStyleSheet(
            "background: #4A9EFF; color: white; font-weight: bold; "
            "font-size: 13px; padding: 8px 24px; border-radius: 6px;"
        )
        self._mesh_btn.clicked.connect(self._dispatch_mesh)
        f_layout.addWidget(self._mesh_btn)

        outer.addWidget(footer)
        self.hide()

    # ── Public API ────────────────────────────────────────────────

    def load_component(self, comp_name: str, session_dir: str = None, image_path: str = None):
        """Load JSON config for comp_name and rebuild the form."""
        config = _load_config(comp_name, session_dir)
        self._comp_name = comp_name
        self._session_dir = session_dir
        self._orig_config = config
        self._param_rows.clear()
        self._title_lbl.setText(f"  {comp_name}")
        
        if image_path and os.path.exists(image_path):
            from PySide6.QtGui import QPixmap
            pixmap = QPixmap(image_path)
            self._image_lbl.setPixmap(pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self._image_lbl.show()
        else:
            self._image_lbl.hide()

        # Clear existing body widgets
        while self._body_layout.count():
            item = self._body_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if config is None:
            no_cfg = QLabel("No config file found for this component.\nUsing global mesh settings.")
            no_cfg.setStyleSheet(f"color: {C['text_dim']}; font-style: italic;")
            no_cfg.setWordWrap(True)
            self._body_layout.addWidget(no_cfg)
            self._body_layout.addStretch()
            self.show()
            return

        # ── GLOBAL section ─────────────────────────────────────
        self._body_layout.addWidget(_SectionHeader("Global"))
        for key, pdef in config.get("global", {}).items():
            row = _ParamRow(pdef["label"], pdef)
            self._param_rows[f"global.{key}"] = row
            self._body_layout.addWidget(row)

        # ── MESH CONTROLS section ──────────────────────────────
        controls = config.get("mesh_controls", [])
        if controls:
            self._body_layout.addWidget(_SectionHeader("Mesh Controls"))
            for mc in controls:
                grp_lbl = QLabel(f"  {mc['label']}")
                grp_lbl.setFont(QFont("Inter", 9, QFont.Bold))
                grp_lbl.setStyleSheet(f"color: {C['text']}; padding-top: 6px;")
                self._body_layout.addWidget(grp_lbl)
                for pkey, pdef in mc.get("params", {}).items():
                    row = _ParamRow(pdef["label"], pdef)
                    self._param_rows[f"mc.{mc['name']}.{pkey}"] = row
                    self._body_layout.addWidget(row)

        # ── QUALITY section ────────────────────────────────────
        quality = config.get("quality", {})
        if quality:
            self._body_layout.addWidget(_SectionHeader("Quality"))
            for key, pdef in quality.items():
                row = _ParamRow(pdef["label"], pdef)
                self._param_rows[f"quality.{key}"] = row
                self._body_layout.addWidget(row)

        # ── VOLUME section ─────────────────────────────────────
        volume = config.get("volume", {})
        if volume:
            self._body_layout.addWidget(_SectionHeader("Volume Mesher"))
            for key, pdef in volume.items():
                row = _ParamRow(pdef["label"], pdef)
                self._param_rows[f"volume.{key}"] = row
                self._body_layout.addWidget(row)

        # ── SPECIAL section ────────────────────────────────────
        special = config.get("special", {})
        if special:
            self._body_layout.addWidget(_SectionHeader("Advanced"))
            for key, pdef in special.items():
                row = _ParamRow(pdef["label"], pdef)
                self._param_rows[f"special.{key}"] = row
                self._body_layout.addWidget(row)

        self._body_layout.addStretch()
        self.show()

    # ── Internal slots ─────────────────────────────────────────────

    def _collect_config(self) -> dict:
        """Build a flat {key: value} dict from all current widget values."""
        return {k: row.get_value() for k, row in self._param_rows.items()}

    def _reset_defaults(self):
        if self._orig_config is None:
            return
        # Load from default directory, ignoring session
        config = _load_config(self._comp_name, session_dir=None)
        if config:
            self._orig_config = config
            # We can't re-call load_component directly because it would read from session again
            # We must just re-populate the UI with the default config.
            # But the easiest way is to temporarily delete the session config if we want to reset!
            if self._session_dir:
                key = _get_config_key(self._comp_name)
                session_path = os.path.join(self._session_dir, "mesh_configs", f"{key}.json")
                if os.path.exists(session_path):
                    os.remove(session_path)
        self.load_component(self._comp_name, self._session_dir)

    def _save_config(self):
        if self._orig_config is None or self._comp_name is None:
            return
        updated = copy.deepcopy(self._orig_config)
        for flat_key, row in self._param_rows.items():
            parts = flat_key.split(".")
            section = parts[0]
            if section == "global" and len(parts) == 2:
                updated["global"][parts[1]]["value"] = row.get_value()
            elif section == "mc" and len(parts) == 3:
                mc_name, pkey = parts[1], parts[2]
                for mc in updated.get("mesh_controls", []):
                    if mc["name"] == mc_name:
                        mc["params"][pkey]["value"] = row.get_value()
            elif section in ("quality", "volume", "special") and len(parts) == 2:
                updated[section][parts[1]]["value"] = row.get_value()
        _save_config(self._comp_name, updated, self._session_dir)
        self._orig_config = updated

    def _dispatch_mesh(self):
        if self._comp_name is None:
            return
        self.meshRequested.emit(self._comp_name, self._collect_config())
