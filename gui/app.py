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
    path_dropped = Signal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._hover = False
        self._batch = False
        self._path  = ""

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)
        layout.setContentsMargins(32, 48, 32, 48)

        self.main_lbl = QLabel("Select STEP File")
        self.main_lbl.setFont(QFont("Inter", 16, QFont.Bold))
        self.main_lbl.setAlignment(Qt.AlignCenter)
        self.main_lbl.setStyleSheet(f"color: {C['text']};")

        self.sub_lbl = QLabel("Drag & drop your CAD file here")
        self.sub_lbl.setAlignment(Qt.AlignCenter)
        self.sub_lbl.setFont(QFont("Inter", 13))
        self.sub_lbl.setStyleSheet(f"color: {C['text_dim']};")

        layout.addWidget(self.main_lbl)
        layout.addWidget(self.sub_lbl)
        self._update_style(False)

    def set_batch(self, batch: bool):
        self._batch = batch
        self._path = ""
        self.main_lbl.setStyleSheet(f"color: {C['text']};")
        self.main_lbl.setText("Select Directory" if batch else "Select STEP File")
        self.sub_lbl.setText("Drag & drop a folder here" if batch else "Drag & drop your CAD file here")

    def get_path(self): return self._path

    def _set_selected(self, path):
        self._path = path
        self.main_lbl.setText(os.path.basename(path))
        self.main_lbl.setStyleSheet(f"color: {C['text']};")
        self.sub_lbl.setText(path)
        self.path_dropped.emit(path)

    def mousePressEvent(self, e):
        win = self.window()
        if self._batch: path = QFileDialog.getExistingDirectory(win, "Select Directory", _ROOT)
        else: path, _ = QFileDialog.getOpenFileName(win, "Select File", _ROOT, "STEP Files (*.step *.STEP *.stp *.STP)")
        if path: self._set_selected(path)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls(): self._hover = True; self._update_style(True); e.accept()
        else: e.ignore()
    def dragLeaveEvent(self, e): self._hover = False; self._update_style(False)
    def dropEvent(self, e):
        self._hover = False; self._update_style(False)
        urls = e.mimeData().urls()
        if urls: self._set_selected(urls[0].toLocalFile())

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
class ImportPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setAlignment(Qt.AlignCenter)

        inner = QWidget(); inner.setMaximumWidth(600)
        fl = QVBoxLayout(inner); fl.setSpacing(24)

        # Drop zone
        self.drop = DropZone()
        fl.addWidget(self.drop)

        # Settings Card
        card = QWidget(); card.setObjectName("form_card")
        cl = QVBoxLayout(card); cl.setContentsMargins(24, 24, 24, 24); cl.setSpacing(20)

        # Checkboxes grid
        chk_grid = QGridLayout(); chk_grid.setSpacing(16)
        self.chk_batch  = QCheckBox("Batch process directory")
        self.chk_box    = QCheckBox("Detect PCB enclosures")
        self.chk_render = QCheckBox("Generate renders"); self.chk_render.setChecked(True)
        self.chk_export_direct = QCheckBox("Export renders directly"); self.chk_export_direct.setChecked(False)
        self.chk_export = QCheckBox("Export labeled parts")
        
        chk_grid.addWidget(self.chk_batch, 0, 0)
        chk_grid.addWidget(self.chk_box, 0, 1)
        chk_grid.addWidget(self.chk_render, 1, 0)
        chk_grid.addWidget(self.chk_export_direct, 1, 1)
        chk_grid.addWidget(self.chk_export, 2, 0)
        cl.addLayout(chk_grid)
        
        self.chk_batch.stateChanged.connect(lambda s: self.drop.set_batch(bool(s)))

        # Dynamic output fields
        self.render_out_w = QWidget(); rl = QHBoxLayout(self.render_out_w); rl.setContentsMargins(0,0,0,0); rl.setSpacing(12)
        r_lbl = QLabel("Renders Dir"); r_lbl.setFixedWidth(80)
        r_lbl.setStyleSheet(f"color: {C['text_muted']}; font-weight: 600; font-size: 11px; text-transform: uppercase; letter-spacing: 1px;")
        self.render_edit = QLineEdit(); self.render_edit.setObjectName("form_input"); self.render_edit.setText(os.path.join(_ROOT, "final_renders"))
        r_btn = QPushButton("Browse"); r_btn.setObjectName("ghost_btn")
        r_btn.clicked.connect(lambda: self.render_edit.setText(QFileDialog.getExistingDirectory(self, "Renders Output", _ROOT) or self.render_edit.text()))
        rl.addWidget(r_lbl); rl.addWidget(self.render_edit, 1); rl.addWidget(r_btn)
        cl.addWidget(self.render_out_w)

        self.export_out_w = QWidget(); el = QHBoxLayout(self.export_out_w); el.setContentsMargins(0,0,0,0); el.setSpacing(12)
        e_lbl = QLabel("Export Dir"); e_lbl.setFixedWidth(80)
        e_lbl.setStyleSheet(f"color: {C['text_muted']}; font-weight: 600; font-size: 11px; text-transform: uppercase; letter-spacing: 1px;")
        self.export_edit = QLineEdit(); self.export_edit.setObjectName("form_input"); self.export_edit.setText(os.path.join(_ROOT, "exported_steps"))
        e_btn = QPushButton("Browse"); e_btn.setObjectName("ghost_btn")
        e_btn.clicked.connect(lambda: self.export_edit.setText(QFileDialog.getExistingDirectory(self, "Export Output", _ROOT) or self.export_edit.text()))
        el.addWidget(e_lbl); el.addWidget(self.export_edit, 1); el.addWidget(e_btn)
        cl.addWidget(self.export_out_w)

        self.render_out_w.setVisible(False)
        self.export_out_w.setVisible(False)
        
        self.chk_export_direct.stateChanged.connect(lambda s: self.render_out_w.setVisible(bool(s) and self.chk_render.isChecked()))
        self.chk_render.stateChanged.connect(lambda s: self.render_out_w.setVisible(bool(s) and self.chk_export_direct.isChecked()))
        self.chk_render.stateChanged.connect(lambda s: self.chk_export_direct.setEnabled(bool(s)))
        self.chk_export.stateChanged.connect(lambda s: self.export_out_w.setVisible(bool(s)))

        fl.addWidget(card)
        root.addWidget(inner)

    def get_config(self):
        return {
            "in_path": self.drop.get_path(),
            "render_dir": self.render_edit.text().strip() if self.chk_export_direct.isChecked() else None,
            "export_direct": self.chk_export_direct.isChecked(),
            "export_dir": self.export_edit.text().strip() if self.chk_export.isChecked() else None,
            "batch": self.chk_batch.isChecked(),
            "box": self.chk_box.isChecked(),
            "do_render": self.chk_render.isChecked(),
            "do_export": self.chk_export.isChecked(),
        }

# ── Results page ───────────────────────────────────────────────────────────
class ResultsPage(QWidget):
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

        self.topo_layout = QHBoxLayout(); self.topo_layout.setSpacing(8)
        header.addLayout(self.topo_layout)
        header.addStretch()
        layout.addLayout(header)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Component", "Solids", "Count", "Confidence", "Resolution"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 5): self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setShowGrid(False)
        layout.addWidget(self.table, 1)

        main_layout.addWidget(content, 1)

        self._data_map = {}
        self._filenames = []

    def clear(self):
        self._data_map.clear()
        self._filenames.clear()
        self.sidebar.clear()
        self.table.setRowCount(0)
        while self.topo_layout.count():
            item = self.topo_layout.takeAt(0)
            if item and item.widget(): item.widget().deleteLater()
        self.file_lbl.setText("—")

    def populate(self, step_path, results, records):
        filename = os.path.basename(step_path)
        if filename not in self._data_map:
            self._filenames.append(filename)
            self.sidebar.addItem(filename)
        self._data_map[filename] = results
        
        if self.sidebar.count() == 1 or self.sidebar.currentItem().text() == filename:
            self.sidebar.setCurrentRow(self._filenames.index(filename))
            self._on_row_changed(self._filenames.index(filename))

    def _on_row_changed(self, idx):
        if idx < 0 or idx >= len(self._filenames): return
        filename = self._filenames[idx]
        results = self._data_map[filename]

        self.file_lbl.setText(filename)
        self.table.setRowCount(0)

        while self.topo_layout.count():
            item = self.topo_layout.takeAt(0)
            if item and item.widget(): item.widget().deleteLater()

        comp_map = {c: n for c, n, _ in results}

        for comp, nodes, conf in results:
            if not nodes: continue
            row = self.table.rowCount(); self.table.insertRow(row)

            base = comp.split("_")[0]
            col = COMPONENT_COLORS.get(comp, COMPONENT_COLORS.get(base, C['text']))
            n_item = QTableWidgetItem(comp); n_item.setForeground(QColor(col)); n_item.setFont(QFont("Inter", 13, QFont.Bold))
            self.table.setItem(row, 0, n_item)

            self.table.setItem(row, 1, QTableWidgetItem(", ".join(f"#{n}" for n in nodes if n is not None)))
            self.table.setItem(row, 2, QTableWidgetItem(str(len([n for n in nodes if n is not None]))))

            conf_str = f"{conf*100:.1f}%"
            c_item = QTableWidgetItem(conf_str)
            if conf >= 0.9: c_item.setForeground(QColor(C['success']))
            elif conf >= 0.7: c_item.setForeground(QColor(C['warning']))
            else: c_item.setForeground(QColor(C['danger']))
            self.table.setItem(row, 3, c_item)

            is_ml = base in ML_COMPONENTS
            m_item = QTableWidgetItem("Model" if is_ml else "Heuristic")
            m_item.setForeground(QColor(C['text_dim']))
            self.table.setItem(row, 4, m_item)

        self.table.resizeRowsToContents()

# ── Render thumbnail ───────────────────────────────────────────────────────
class Thumb(QWidget):
    clicked = Signal(str, str)
    def __init__(self, name, path, parent=None):
        super().__init__(parent)
        self.name = name; self.path = path
        self.setFixedSize(180, 210)
        self.setCursor(Qt.PointingHandCursor)
        layout = QVBoxLayout(self); layout.setContentsMargins(12,12,12,12); layout.setSpacing(12)

        self.img = QLabel()
        self.img.setFixedSize(154, 154)
        self.img.setAlignment(Qt.AlignCenter)
        self.img.setStyleSheet(f"background: {C['bg']}; border-radius: 8px;")
        px = QPixmap(path)
        if not px.isNull(): self.img.setPixmap(px.scaled(154, 154, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        base = name.split("_")[0]
        color = COMPONENT_COLORS.get(name, COMPONENT_COLORS.get(base, C['text']))
        self.lbl = QLabel(name)
        self.lbl.setAlignment(Qt.AlignCenter)
        self.lbl.setFont(QFont("Inter", 11, QFont.Bold))
        self.lbl.setStyleSheet(f"color: {color};")

        layout.addWidget(self.img); layout.addWidget(self.lbl)
        self.setStyleSheet(f"Thumb {{ background: {C['surface']}; border: 1px solid {C['border']}; border-radius: 12px; }} Thumb:hover {{ border-color: {C['border_hi']}; }}")

    def mousePressEvent(self, e): self.clicked.emit(self.name, self.path)

# ── Renders page ───────────────────────────────────────────────────────────
class RendersPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QHBoxLayout(self); main_layout.setContentsMargins(0, 0, 0, 0); main_layout.setSpacing(0)

        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(260)
        self.sidebar.currentRowChanged.connect(self._on_row_changed)
        main_layout.addWidget(self.sidebar)

        content = QWidget()
        layout = QVBoxLayout(content); layout.setContentsMargins(48, 32, 48, 32); layout.setSpacing(24)

        self.file_lbl = QLabel("—")
        self.file_lbl.setFont(QFont("Inter", 20, QFont.Bold))
        
        self.export_btn = QPushButton("Export Renders"); self.export_btn.setObjectName("ghost_btn")
        self.export_btn.clicked.connect(self._export_all)
        
        header_layout = QHBoxLayout()
        header_layout.addWidget(self.file_lbl)
        header_layout.addStretch()
        header_layout.addWidget(self.export_btn)
        
        layout.addLayout(header_layout)

        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        container = QWidget(); self.grid = QGridLayout(container)
        self.grid.setContentsMargins(0,0,0,0); self.grid.setSpacing(16)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        scroll.setWidget(container)
        layout.addWidget(scroll, 1)

        main_layout.addWidget(content, 1)

        self._data_map = {}
        self._filenames = []
        self._row = 0; self._col = 0; self._thumbs = []

    def add_render(self, step_path, comp_name, img_path, win):
        filename = os.path.basename(step_path)
        if filename not in self._data_map:
            self._filenames.append(filename)
            self.sidebar.addItem(filename)
            self._data_map[filename] = []
        
        self._data_map[filename].append((comp_name, img_path))
        
        if self.sidebar.count() == 1 or self.sidebar.currentItem().text() == filename:
            self.sidebar.setCurrentRow(self._filenames.index(filename))
            self._on_row_changed(self._filenames.index(filename))

    def _on_row_changed(self, idx):
        if idx < 0 or idx >= len(self._filenames): return
        self._clear_grid()
        filename = self._filenames[idx]
        self.file_lbl.setText(filename)
        renders = self._data_map[filename]
        
        for comp_name, img_path in renders:
            t = Thumb(comp_name, img_path)
            t.clicked.connect(lambda n, p: self._open(n, p, self.window()))
            self.grid.addWidget(t, self._row, self._col)
            self._thumbs.append(t)
            self._col += 1
            if self._col >= 5: self._col = 0; self._row += 1

    def clear(self):
        self._data_map.clear()
        self._filenames.clear()
        self.sidebar.clear()
        self._clear_grid()
        self.file_lbl.setText("—")

    def _export_all(self):
        if not self._data_map: return
        dest = QFileDialog.getExistingDirectory(self, "Export Renders", _ROOT)
        if not dest: return
        
        old_cache_dirs = set()
        for filename, renders in self._data_map.items():
            for i, (comp_name, img_path) in enumerate(renders):
                if os.path.exists(img_path):
                    target_path = os.path.join(dest, os.path.basename(img_path))
                    try:
                        shutil.move(img_path, target_path)
                        renders[i] = (comp_name, target_path)
                        if "_cache" in img_path:
                            old_cache_dirs.add(os.path.dirname(os.path.dirname(img_path)))
                    except Exception as e: print(f"Export err: {e}")

        win = self.window()
        if hasattr(win, 'current_report_path') and win.current_report_path and os.path.exists(win.current_report_path):
            try:
                with open(win.current_report_path, "r") as f: report = json.load(f)
                report["renders"] = self._data_map
                with open(win.current_report_path, "w") as f: json.dump(report, f, indent=2)
            except Exception as e: print(f"Error updating report: {e}")
            
        for d in old_cache_dirs:
            shutil.rmtree(d, ignore_errors=True)
            
        row = self.sidebar.currentRow()
        if row >= 0: self._on_row_changed(row)

    def _clear_grid(self):
        for t in self._thumbs: self.grid.removeWidget(t); t.deleteLater()
        self._thumbs.clear(); self._row = 0; self._col = 0

    def _open(self, name, path, win):
        d = QDialog(win); d.setWindowTitle(name); d.resize(800, 700)
        d.setStyleSheet(f"background: {C['bg']};")
        layout = QVBoxLayout(d); layout.setContentsMargins(20,20,20,20)
        lbl = QLabel(); px = QPixmap(path)
        if not px.isNull(): lbl.setPixmap(px.scaled(760, 640, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl); d.exec()

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
        col = C['text'] if "ML" in text else C['text_dim'] if "[Phase" in text else C['danger'] if "❌" in text else C['text_muted']
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
        self.renders_page = RendersPage()
        for p in [self.import_page, self.results_page, self.renders_page]: self._pages_w.addWidget(p)

        for i, label in enumerate(["Import", "Results", "Renders"]):
            btn = NavBtn(label)
            btn.clicked.connect(lambda _, idx=i: self._switch_page(idx))
            nav_layout.addWidget(btn)
            self._nav_btns.append(btn)
        self.progress_lbl = QLabel(""); self.progress_lbl.setStyleSheet(f"color: {C['text_muted']}; font-size: 12px; margin-right: 16px;")
        self.load_btn = QPushButton("Load Run"); self.load_btn.setObjectName("ghost_btn")
        self.save_btn = QPushButton("Save Run"); self.save_btn.setObjectName("ghost_btn"); self.save_btn.setEnabled(False)
        self.debug_toggle = QPushButton("Debug"); self.debug_toggle.setObjectName("ghost_btn"); self.debug_toggle.setCheckable(True)
        self.stop_btn = QPushButton("Stop"); self.stop_btn.setObjectName("danger_btn"); self.stop_btn.setEnabled(False)
        self.run_btn = QPushButton("Process"); self.run_btn.setObjectName("primary_btn")

        nav_layout.addWidget(self.load_btn)
        nav_layout.addWidget(self.save_btn)
        nav_layout.addStretch(1)
        nav_layout.addWidget(self.progress_lbl)
        nav_layout.addWidget(self.debug_toggle)
        nav_layout.addSpacing(12)
        nav_layout.addWidget(self.stop_btn)
        nav_layout.addSpacing(12)
        nav_layout.addWidget(self.run_btn)

        self.progress = QProgressBar(); self.progress.setObjectName("progress")
        self.progress.setTextVisible(False)

        root.addWidget(nav)
        root.addWidget(self.progress)
        root.addWidget(self._pages_w, 1)

        self.debug_console = DebugConsole()
        root.addWidget(self.debug_console)

        self.run_btn.clicked.connect(self._run)
        self.stop_btn.clicked.connect(self._stop)
        self.load_btn.clicked.connect(self._load_run)
        self.save_btn.clicked.connect(self._save_run)
        self.debug_toggle.toggled.connect(self.debug_console.setVisible)

        self._switch_page(0)

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

    def _run(self):
        cfg = self.import_page.get_config()
        if not cfg["in_path"]: return
        if cfg["do_render"] and cfg["export_direct"] and not cfg["render_dir"]: return
        if cfg["do_export"] and not cfg["export_dir"]: return

        self._clean_cache()
        self.current_report_path = None
        r_dir = cfg["render_dir"]
        if cfg["do_render"] and not cfg["export_direct"]:
            r_dir = os.path.join(_ROOT, "_cache", "renders", time.strftime("%Y%m%d_%H%M%S"))
            os.makedirs(r_dir, exist_ok=True)

        self.results_page.clear()
        self.renders_page.clear()
        self.debug_console.console.clear()
        self.progress.setValue(0)
        self.run_btn.setEnabled(False); self.stop_btn.setEnabled(True); self.save_btn.setEnabled(False)

        self._worker = InferenceWorker(
            step_path=cfg["in_path"], 
            render_dir=r_dir,
            export_dir=cfg["export_dir"],
            batch=cfg["batch"], 
            box=cfg["box"], 
            do_render=cfg["do_render"],
            do_export=cfg["do_export"]
        )
        self._worker.console_line.connect(self.debug_console.append)
        self._worker.file_started.connect(lambda p: self.progress_lbl.setText(os.path.basename(p)))
        self._worker.batch_progress.connect(lambda c, t: self.progress.setValue(int(c/t*100)))
        self._worker.file_done.connect(self._on_done)
        self._worker.finished_all.connect(self._on_finished)
        self._worker.error_occurred.connect(self._on_error)
        self._worker.start()

    def _stop(self):
        if self._worker: self._worker.abort()
        self.stop_btn.setEnabled(False)

    def _on_done(self, step_path, result, render_dir):
        if result and "results" in result:
            self.results_page.populate(step_path, result["results"], result.get("records", []))
            self._switch_page(1)
        if render_dir:
            for img in sorted(glob.glob(os.path.join(render_dir, "*.png"))):
                c_name = os.path.splitext(os.path.basename(img))[0].replace(os.path.splitext(os.path.basename(step_path))[0] + "_", "", 1)
                self.renders_page.add_render(step_path, c_name, img, self)

    def _on_finished(self):
        self.progress.setValue(100)
        self.run_btn.setEnabled(True); self.stop_btn.setEnabled(False); self.save_btn.setEnabled(True)
        self.progress_lbl.setText("Complete")

    def _on_error(self, msg):
        self.run_btn.setEnabled(True); self.stop_btn.setEnabled(False); self.save_btn.setEnabled(True)
        self.progress_lbl.setText("Failed")
        if not self.debug_toggle.isChecked(): self.debug_toggle.setChecked(True)

    def _save_run(self):
        name, ok = QInputDialog.getText(self, "Save Run", "Run Name:", text=time.strftime("Run_%Y%m%d_%H%M%S"))
        if not ok or not name.strip(): return
        
        history_dir = os.path.join(_ROOT, "_run_history")
        os.makedirs(history_dir, exist_ok=True)
        
        try:
            report = {
                "version": "1.0",
                "results": self.results_page._data_map,
                "renders": self.renders_page._data_map
            }
            report_path = os.path.join(history_dir, f"{name.strip()}.json")
            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)
            self.current_report_path = report_path
            self.progress_lbl.setText("Saved successfully")
        except Exception as e:
            self.progress_lbl.setText(f"Save failed: {e}")

    def _load_run(self):
        history_dir = os.path.join(_ROOT, "_run_history")
        d = LoadRunDialog(history_dir, self)
        if d.exec() != QDialog.Accepted or not d.selected_report: return
        
        self.results_page.clear()
        self.renders_page.clear()
        self.current_report_path = d.selected_report
        
        try:
            with open(d.selected_report, "r") as f:
                report = json.load(f)
                
            for filename, results in report.get("results", {}).items():
                self.results_page.populate(filename, results, [])
                
            for filename, renders in report.get("renders", {}).items():
                for comp_name, img_path in renders:
                    if os.path.exists(img_path):
                        self.renders_page.add_render(filename, comp_name, img_path, self)
                        
            target_page = 2 if self.results_page.sidebar.count() == 0 else 1
            self._switch_page(target_page)
        except Exception as e:
            self.progress_lbl.setText(f"Error loading report: {e}")

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
