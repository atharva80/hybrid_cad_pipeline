"""
styles.py — Premium Dark Theme for ATLAS
"""
import os
_GUI_DIR = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')

C = {
    'bg':          '#09090B', # Zinc 950
    'surface':     '#18181B', # Zinc 900
    'card':        '#18181B', # Zinc 900
    'card_hover':  '#27272A', # Zinc 800
    'border':      '#27272A', # Zinc 800
    'border_hi':   '#3F3F46', # Zinc 700
    'accent':      '#FFFFFF', # White for primary
    'accent_dim':  '#A1A1AA', # Zinc 400
    'accent_glow': '#F4F4F5', # Zinc 100
    'ml_blue':     '#38BDF8', # Sky 400
    'heu':         '#A78BFA', # Violet 400
    'success':     '#34D399', # Emerald 400
    'warning':     '#FBBF24', # Amber 400
    'danger':      '#F87171', # Red 400
    'text':        '#FAFAFA', # Zinc 50
    'text_dim':    '#A1A1AA', # Zinc 400
    'text_muted':  '#52525B', # Zinc 600
    'console_bg':  '#000000', # Pure black
}

ML_COMPONENTS  = {'STATOR','SHAFT','ROTOR_RING','TOP_COVER',
                  'BOTTOM_COVER','TOP_INSULATOR','BOTTOM_INSULATOR'}

COMPONENT_COLORS = {
    'STATOR':           C['text'],
    'SHAFT':            C['text'],
    'ROTOR_RING':       C['text'],
    'TOP_COVER':        C['text'],
    'BOTTOM_COVER':     C['text'],
    'TOP_INSULATOR':    C['text'],
    'BOTTOM_INSULATOR': C['text'],
    'BEARING_TOP':      C['text'],
    'BEARING_BOTTOM':   C['text'],
    'PCB':              C['text'],
    'PCB_BOX':          C['text'],
    'PCB_BRACKET':      C['text'],
    'EPS_PACKAGING':    C['text'],
    'CANOPY':           C['text'],
    'STAYCAP':          C['text'],
    'MASTER_BOX':       C['text'],
    'MOTOR_BOX':        C['text'],
    'BLADE_BOX':        C['text'],
    'FALSE_COVER':      C['text'],
    'SIDE_COVER':       C['text'],
}

SS = f"""
QMainWindow, QDialog {{
    background: {C['bg']};
}}

QWidget {{
    color: {C['text']};
    font-family: 'Inter', '-apple-system', 'Segoe UI', sans-serif;
    font-size: 13px;
}}

QSplitter::handle {{ background: {C['border']}; }}

/* Nav bar */
#nav_bar {{
    background: {C['bg']};
    border-bottom: 1px solid {C['border']};
}}
#app_name {{
    color: {C['text']};
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 2px;
}}

/* Page segment control */
#seg_btn {{
    background: transparent;
    color: {C['text_dim']};
    border: none;
    border-radius: 6px;
    padding: 6px 16px;
    font-size: 13px;
    font-weight: 500;
    margin: 4px;
}}
#seg_btn:hover {{ color: {C['text']}; background: {C['surface']}; }}
#seg_btn_active {{
    background: {C['card_hover']};
    color: {C['text']};
    border: 1px solid {C['border']};
    border-radius: 6px;
    padding: 6px 16px;
    font-size: 13px;
    font-weight: 600;
    margin: 4px;
}}

/* Buttons */
QPushButton {{
    background: {C['surface']};
    color: {C['text']};
    border: 1px solid {C['border']};
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 500;
}}
QPushButton:hover  {{ background: {C['card_hover']}; border-color: {C['border_hi']}; }}
QPushButton:pressed {{ background: {C['border']}; }}
QPushButton:disabled {{ color: {C['text_muted']}; border-color: {C['border']}; background: {C['surface']}; }}

#primary_btn {{
    background: {C['accent']};
    color: {C['bg']};
    border: 1px solid {C['accent_glow']};
    border-radius: 6px;
    padding: 8px 24px;
    font-size: 13px;
    font-weight: 600;
}}
#primary_btn:hover {{
    background: {C['accent_glow']};
}}
#primary_btn:disabled {{
    background: {C['border_hi']};
    color: {C['text_muted']};
    border: none;
}}

#ghost_btn {{
    background: transparent;
    color: {C['text_dim']};
    border: 1px solid {C['border']};
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 12px;
}}
#ghost_btn:hover {{ color: {C['text']}; border-color: {C['border_hi']}; background: {C['surface']}; }}

#danger_btn {{
    background: transparent;
    color: {C['danger']};
    border: 1px solid {C['border']};
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 13px;
}}
#danger_btn:hover {{ background: rgba(248,113,113,0.10); border-color: {C['danger']}; }}

/* Inputs */
#form_input {{
    background: {C['bg']};
    color: {C['text']};
    border: 1px solid {C['border']};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    selection-background-color: {C['border_hi']};
}}
#form_input:focus {{ border-color: {C['accent_dim']}; }}

/* Ensure text elements don't draw a black background box on top of cards */
QLabel, QCheckBox, QRadioButton {{
    background: transparent;
}}

/* Checkboxes */
QCheckBox {{ color: {C['text']}; spacing: 10px; font-size: 13px; font-weight: 500; }}
QCheckBox::indicator {{
    width: 16px; height: 16px; border-radius: 4px;
    border: 1px solid {C['border_hi']}; background: {C['bg']};
}}
QCheckBox::indicator:hover {{ border-color: {C['text_dim']}; }}
QCheckBox::indicator:checked {{
    background: {C['accent']};
    border: 1px solid {C['accent']};
    image: url({_GUI_DIR}/check.svg);
}}

/* Sidebar List */
QListWidget {{
    background: {C['surface']};
    border: none;
    border-right: 1px solid {C['border']};
    outline: none;
    font-size: 13px;
}}
QListWidget::item {{
    color: {C['text_dim']};
    padding: 16px 20px;
    border-bottom: 1px solid {C['border']};
}}
QListWidget::item:selected {{
    background: {C['card_hover']};
    color: {C['text']};
    font-weight: 600;
    border-left: 3px solid {C['accent']};
}}
QListWidget::item:hover:!selected {{
    background: {C['bg']};
    color: {C['text']};
}}

/* Form Card */
#form_card {{
    background: {C['surface']};
    border: 1px solid {C['border']};
    border-radius: 12px;
}}

/* Console */
#console {{
    background: {C['console_bg']};
    color: {C['text_dim']};
    border: none;
    border-top: 1px solid {C['border']};
    font-family: 'JetBrains Mono', 'Menlo', 'Consolas', monospace;
    font-size: 12px;
    padding: 12px 16px;
    selection-background-color: {C['border']};
}}

/* Table */
QTableWidget {{
    background: {C['bg']};
    color: {C['text']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    gridline-color: transparent;
    font-size: 13px;
    selection-background-color: {C['surface']};
    outline: none;
}}
QTableWidget::item {{ padding: 12px 16px; border-bottom: 1px solid {C['border']}; }}
QTableWidget::item:selected {{ background: {C['surface']}; color: {C['text']}; }}
QTableWidget::item:focus {{ border: none; outline: none; }}
QHeaderView {{
    background: {C['surface']};
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}}
QHeaderView::section {{
    background: {C['surface']};
    color: {C['text_dim']};
    padding: 12px 16px;
    border: none;
    border-bottom: 1px solid {C['border']};
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* Scrollbars */
QScrollBar:vertical {{ background: transparent; width: 8px; margin: 0; }}
QScrollBar::handle:vertical {{ background: {C['border_hi']}; border-radius: 4px; min-height: 30px; margin: 2px; }}
QScrollBar::handle:vertical:hover {{ background: {C['text_muted']}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{ background: transparent; height: 8px; margin: 0; }}
QScrollBar::handle:horizontal {{ background: {C['border_hi']}; border-radius: 4px; min-width: 30px; margin: 2px; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
QScrollArea {{ border: none; background: transparent; }}
QScrollArea > QWidget > QWidget {{ background: transparent; }}

/* Progress */
QProgressBar {{
    background: transparent; border: none; height: 2px;
}}
QProgressBar::chunk {{
    background: {C['text']};
}}

/* Status bar */
QStatusBar {{
    background: {C['bg']};
    color: {C['text_dim']};
    border-top: 1px solid {C['border']};
    font-size: 12px;
    padding: 0 16px;
}}
QStatusBar::item {{ border: none; }}

/* File Dialog overrides to fix dark system icons */
QFileDialog QToolButton {{
    background: {C['border_hi']};
    border-radius: 4px;
}}
QFileDialog QToolButton:hover {{
    background: {C['text_muted']};
}}
"""
