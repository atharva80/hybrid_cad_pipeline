"""
widgets.py — Reusable custom widgets for the Hybrid CAD Pipeline GUI.
"""

import os
from PySide6.QtWidgets import (
    QWidget, QLabel, QHBoxLayout, QVBoxLayout, QFrame,
    QScrollArea, QGridLayout, QSizePolicy, QDialog,
    QVBoxLayout as VBox
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QColor, QPainter, QBrush, QPen, QFont

from gui.styles import C, COMPONENT_COLORS, ML_COMPONENTS


# ── Phase Step Indicator ──────────────────────────────────────────────────
class PhaseStep(QWidget):
    PENDING = 0
    RUNNING = 1
    DONE    = 2
    FAILED  = 3

    def __init__(self, label: str, badge: str, parent=None):
        super().__init__(parent)
        self._state = self.PENDING
        self.setFixedHeight(36)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(10)

        # Circle indicator
        self.dot = QLabel("●")
        self.dot.setFixedWidth(14)
        self.dot.setFont(QFont("Arial", 9))
        self.dot.setAlignment(Qt.AlignCenter)

        # Label
        self.lbl = QLabel(label)
        self.lbl.setFont(QFont("Inter", 11))

        # Badge ([ML] or [HEU])
        self.badge = QLabel(badge)
        self.badge.setFixedWidth(38)
        self.badge.setAlignment(Qt.AlignCenter)
        self.badge.setFont(QFont("Inter", 9, QFont.Bold))
        badge_color = C['ml_blue'] if badge == "[ML]" else C['heu_purple']
        self.badge.setStyleSheet(
            f"color: {badge_color}; background: rgba(255,255,255,0.05);"
            f"border: 1px solid {badge_color}; border-radius: 3px; padding: 1px 3px;"
        )

        layout.addWidget(self.dot)
        layout.addWidget(self.lbl, 1)
        layout.addWidget(self.badge)
        self._apply_state()

    def set_state(self, state: int):
        self._state = state
        self._apply_state()

    def _apply_state(self):
        colors = {
            self.PENDING: (C['text_muted'],  C['text_dim']),
            self.RUNNING: (C['accent_glow'], C['text']),
            self.DONE:    (C['success'],     C['text']),
            self.FAILED:  (C['danger'],      C['text_dim']),
        }
        dot_c, txt_c = colors[self._state]
        self.dot.setStyleSheet(f"color: {dot_c};")
        self.lbl.setStyleSheet(f"color: {txt_c};")
        if self._state == self.RUNNING:
            self.setStyleSheet(
                f"background: rgba(124,109,250,0.08); border-radius:6px;"
            )
        else:
            self.setStyleSheet("")


# ── Render Thumbnail Card ─────────────────────────────────────────────────
class ThumbnailCard(QWidget):
    clicked = Signal(str, str)  # (component_name, image_path)

    def __init__(self, comp_name: str, img_path: str, parent=None):
        super().__init__(parent)
        self.comp_name = comp_name
        self.img_path  = img_path
        self.setFixedSize(150, 170)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(f"Click to expand: {comp_name}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        # Image
        self.img_lbl = QLabel()
        self.img_lbl.setFixedSize(138, 130)
        self.img_lbl.setAlignment(Qt.AlignCenter)
        self.img_lbl.setStyleSheet(
            f"background:{C['console_bg']}; border-radius:6px;"
            f"border:1px solid {C['border_hi']};"
        )
        px = QPixmap(img_path)
        if not px.isNull():
            self.img_lbl.setPixmap(
                px.scaled(138, 130, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )

        # Label
        base = comp_name.split("_")
        color = COMPONENT_COLORS.get(
            "_".join(base[:2]) if len(base) > 2 else comp_name,
            COMPONENT_COLORS.get(base[0], C['accent'])
        )
        self.name_lbl = QLabel(comp_name)
        self.name_lbl.setAlignment(Qt.AlignCenter)
        self.name_lbl.setFont(QFont("Inter", 9, QFont.Bold))
        self.name_lbl.setStyleSheet(f"color: {color};")
        self.name_lbl.setWordWrap(True)

        layout.addWidget(self.img_lbl)
        layout.addWidget(self.name_lbl)

        self.setStyleSheet(
            f"background:{C['card']}; border-radius:8px;"
            f"border:1px solid {C['border']};"
        )

    def mousePressEvent(self, event):
        self.clicked.emit(self.comp_name, self.img_path)

    def enterEvent(self, event):
        self.setStyleSheet(
            f"background:{C['card_hover']}; border-radius:8px;"
            f"border:1px solid {C['accent']};"
        )

    def leaveEvent(self, event):
        self.setStyleSheet(
            f"background:{C['card']}; border-radius:8px;"
            f"border:1px solid {C['border']};"
        )


# ── Full-Screen Image Viewer ──────────────────────────────────────────────
class ImageViewer(QDialog):
    def __init__(self, comp_name: str, img_path: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(comp_name)
        self.setModal(True)
        self.resize(800, 700)
        self.setStyleSheet(f"background:{C['bg']}; color:{C['text']};")

        layout = VBox(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel(comp_name)
        title.setFont(QFont("Inter", 16, QFont.Bold))
        title.setStyleSheet(f"color:{C['accent_glow']};")
        layout.addWidget(title)

        lbl = QLabel()
        px = QPixmap(img_path)
        if not px.isNull():
            lbl.setPixmap(px.scaled(760, 620, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl, 1)

        path_lbl = QLabel(img_path)
        path_lbl.setStyleSheet(f"color:{C['text_dim']}; font-size:10px;")
        layout.addWidget(path_lbl)


# ── Render Gallery ────────────────────────────────────────────────────────
class RenderGallery(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)

        container = QWidget()
        self.grid = QGridLayout(container)
        self.grid.setContentsMargins(8, 8, 8, 8)
        self.grid.setSpacing(8)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.setWidget(container)
        self._cards = []
        self._col = 0
        self._row = 0
        self._max_cols = 3

    def add_render(self, comp_name: str, img_path: str, parent_window):
        card = ThumbnailCard(comp_name, img_path)
        card.clicked.connect(lambda n, p: ImageViewer(n, p, parent_window).exec())
        self.grid.addWidget(card, self._row, self._col)
        self._cards.append(card)
        self._col += 1
        if self._col >= self._max_cols:
            self._col = 0
            self._row += 1

    def clear_renders(self):
        while self._cards:
            card = self._cards.pop()
            self.grid.removeWidget(card)
            card.deleteLater()
        self._col = 0
        self._row = 0


# ── Stat Badge ────────────────────────────────────────────────────────────
class StatBadge(QLabel):
    def __init__(self, text: str, color: str, parent=None):
        super().__init__(text, parent)
        self.setFont(QFont("Inter", 9, QFont.Bold))
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(
            f"color: {color}; background: rgba(255,255,255,0.05);"
            f"border: 1px solid {color}; border-radius: 4px; padding: 2px 6px;"
        )


# ── Separator ─────────────────────────────────────────────────────────────
def make_separator():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)
    line.setStyleSheet(f"color: {C['border_hi']}; margin: 4px 0;")
    return line


# ── Section Header ────────────────────────────────────────────────────────
def section_label(text: str) -> QLabel:
    lbl = QLabel(text.upper())
    lbl.setObjectName("section_label")
    lbl.setFont(QFont("Inter", 9, QFont.Bold))
    lbl.setStyleSheet(
        f"color: {C['text_dim']}; letter-spacing: 2px; padding-bottom: 4px;"
    )
    return lbl
