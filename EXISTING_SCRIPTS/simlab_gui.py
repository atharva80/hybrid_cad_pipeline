# -*- coding: utf-8 -*-
# =============================================================================
# SCRIPT  : simlab_gui.py
# PURPOSE : PyQt5 GUI for SimLab component identification and renaming
# USAGE   : Run from SimLab scripting console or as standalone
# =============================================================================

import sys as _sys
#_sys.path.insert(0, r'C:\Users\PranavBhojane\.altair\SimLab_V2025.1\hwx\python\Python38\site-packages')
_sys.path.insert(0, r'C:\Program Files\Altair\2023\common\python\python3.8\win64\Lib\site-packages')


import sys
import os
import threading
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QComboBox, QPushButton, QLabel,
    QHeaderView, QFrame, QProgressBar, QSizePolicy, QMessageBox,
    QLineEdit, QSpinBox, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon

# -- Standard component names list --------------------------------------------
STANDARD_NAMES = [
    "-- Select --",
    "TOP_COVER",
    "OUTER_RACE",
    "OUTER_RACE_1",
    "ROTOR_RING",
    "MID_RACE",
    "MID_RACE_1",
    "MID_RACE_2",
    "MID_RACE_3",
    "INNER_RACE",
    "INNER_RACE_1",
    "SHAFT",
    "STATOR",
    "TOP_INSULATOR",
    "BOTTOM_INSULATOR",
    "PCB_BRACKET",
    "DISPLAY_PCB",
    "UNIDENTIFIED",
]

# -- Colors --------------------------------------------------------------------
CLR_BG          = "#1E2228"
CLR_PANEL       = "#252A32"
CLR_ROW_ODD     = "#2A2F38"
CLR_ROW_EVEN    = "#242930"
CLR_HEADER      = "#1A1F26"
CLR_ACCENT      = "#4A9EFF"
CLR_ACCENT2     = "#2ECC71"
CLR_TEXT        = "#E8EAF0"
CLR_TEXT_DIM    = "#7A8090"
CLR_BORDER      = "#353B47"
CLR_BTN_REVIEW  = "#3D7EAA"
CLR_BTN_RUN     = "#2E7D52"
CLR_BTN_HOVER   = "#5AAFFF"
CLR_IDENTIFIED  = "#2ECC71"
CLR_UNIDENTIFIED= "#E74C3C"
CLR_PENDING     = "#F39C12"


class IdentificationThread(QThread):
    """Runs the component identification script in background."""
    progress      = pyqtSignal(int, str)        # step, message
    component_found = pyqtSignal(str, str)      # original_name, standard_name
    finished      = pyqtSignal(dict)            # {standard_name: original_name}
    error         = pyqtSignal(str)

    def run(self):
        try:
            from hwx import simlab
            results = {}  # standard_name -> original_name

            MODEL = "$Geometry"

            def sel_cyl(body_str, r_min, r_max, grp,
                        full=1, closed=0, open_=0):
                simlab.execute(f'''<SelectFeatures UUID="CF82E8FB-9B3E-4c02-BA93-9466C1342C6E" CheckBox="ON">
  <SupportEntities><Entities><Model>{MODEL}</Model><Body>{body_str}</Body></Entities></SupportEntities>
  <Arcs MaxValue="0 mm" MinValue="0 mm" Value="0"/><ArcsAll Value="2"/>
  <Circles MaxValue="0 mm" MinValue="0 mm" Value="0"/><CirclesAll Value="0"/>
  <Cones MaxValue="0 mm" MinValue="0 mm" Value="0"/><ConeAll Value="0"/>
  <FullCone Value="0"/><ClosedPartialCone Value="0"/><OpenPartialCone Value="0"/>
  <TaperAngle Angle="0 deg" Value="0"/>
  <Dics MaxValue="0 mm" MinValue="0 mm" Value="0"/><DicsAll Value="0"/>
  <HollowDics MaxValue="0 mm" MinValue="0 mm" Value="0"/><HollowDicsAll Value="0"/>
  <Cylinders MaxValue="{r_max} mm" MinValue="{r_min} mm" Value="1"/><CylindersAll Value="0"/>
  <FullCylinder Value="{full}"/><ClosedPartialCylinder Value="{closed}"/><OpenPartialCylinder Value="{open_}"/>
  <Fillets MaxValue="3 mm" MinValue="0.51 mm" Value="0"/><FilletsOption Value="1"/>
  <PlanarFaces Value="0"/><FourEdgedFaces Value="0"/><ConnectedCoaxialFaces Value="0"/>
  <ThroughBoltHole MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <BlindBoltHole MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <BlindBoltHoleDepth MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <SlotEdges MaxValue="0 mm" MinValue="0 mm" Value="0"/><SlotEdgesAll Value="0"/>
  <ArcLengthBased Value=""/><AngleBased Value=""/>
  <SharpEdges Option="" Angle="" Value=""/><ThicknessBased Value=""/>
  <LogosAndDetails Value=""/><LogosAndDetailsThickness Value=""/>
  <CreateGrp Value="1" Name="{grp}"/>
 </SelectFeatures>''')
                return simlab.getSelectedEntities("Face")

            def sel_cone(body_str, r_min, r_max, grp):
                simlab.execute(f'''<SelectFeatures UUID="CF82E8FB-9B3E-4c02-BA93-9466C1342C6E" CheckBox="ON">
  <SupportEntities><Entities><Model>{MODEL}</Model><Body>{body_str}</Body></Entities></SupportEntities>
  <Arcs MaxValue="0 mm" MinValue="0 mm" Value="0"/><ArcsAll Value="2"/>
  <Circles MaxValue="0 mm" MinValue="0 mm" Value="0"/><CirclesAll Value="0"/>
  <Cones MaxValue="{r_max} mm" MinValue="{r_min} mm" Value="1"/><ConeAll Value="0"/>
  <FullCone Value="1"/><ClosedPartialCone Value="1"/><OpenPartialCone Value="1"/>
  <TaperAngle Angle="0 deg" Value="0"/>
  <Dics MaxValue="0 mm" MinValue="0 mm" Value="0"/><DicsAll Value="0"/>
  <HollowDics MaxValue="0 mm" MinValue="0 mm" Value="0"/><HollowDicsAll Value="0"/>
  <Cylinders MaxValue="0 mm" MinValue="0 mm" Value="0"/><CylindersAll Value="0"/>
  <FullCylinder Value="0"/><ClosedPartialCylinder Value="0"/><OpenPartialCylinder Value="0"/>
  <Fillets MaxValue="3 mm" MinValue="0.51 mm" Value="0"/><FilletsOption Value="1"/>
  <PlanarFaces Value="0"/><FourEdgedFaces Value="0"/><ConnectedCoaxialFaces Value="0"/>
  <ThroughBoltHole MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <BlindBoltHole MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <BlindBoltHoleDepth MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <SlotEdges MaxValue="0 mm" MinValue="0 mm" Value="0"/><SlotEdgesAll Value="0"/>
  <ArcLengthBased Value=""/><AngleBased Value=""/>
  <SharpEdges Option="" Angle="" Value=""/><ThicknessBased Value=""/>
  <LogosAndDetails Value=""/><LogosAndDetailsThickness Value=""/>
  <CreateGrp Value="1" Name="{grp}"/>
 </SelectFeatures>''')
                return simlab.getSelectedEntities("Face")

            def get_adj(body_str, grp, exclude):
                simlab.execute(f'''<SelectAdjacentBodies UUID="078de645-1446-470c-9365-d61a1a5c4f47">
  <InputBodies><Entities><Model>{MODEL}</Model><Body>{body_str}</Body></Entities></InputBodies>
  <Tolerance Value="0.000001"/>
  <GroupName Value="{grp}"/>
 </SelectAdjacentBodies>''')
                adj = simlab.getBodiesFromGroup(grp)
                return "".join(f'"{b}",' for b in adj if b not in exclude)

            def face_to_grp(face_str, grp):
                simlab.execute(f'''<SelectFaceAssociatedEntities UUID="4128ad97-7527-4dad-9746-470cfa135434">
  <InputFaces Values=""><Entities><Model>{MODEL}</Model><Face>{face_str}</Face></Entities></InputFaces>
  <Option Value="Bodies"/>
  <Groupname Value="{grp}"/>
 </SelectFaceAssociatedEntities>''')

            def rename_grp(grp, new_name):
                simlab.execute(f'''<RenameBody CheckBox="ON" UUID="78633e0d-3d2f-4e9a-b075-7bff122772d8">
  <SupportEntities><Group>{grp}</Group></SupportEntities>
  <NewName Value="{new_name}"/>
  <AllowDuplicate Value="0"/>
  <Output/>
 </RenameBody>''')

            def cleanup(*grps):
                simlab.execute(f'''<DeleteGroupControl UUID="2a3b5834-9708-4b03-871c-6d05623667bd" CheckBox="ON">
  <tag Value="-1"/>
  <Name Value="{",".join(grps)},"/>
  <Output/>
 </DeleteGroupControl>''')

            def get_orig_name(standard_name):
                """Get original body name before renaming."""
                bodies = simlab.getBodiesWithSubString(MODEL, [standard_name])
                return list(bodies)[0] if bodies else standard_name

            renamed = []
            total_steps = 11
            step = 0

            # 1. TOP_COVER
            step += 1
            self.progress.emit(int(step/total_steps*100), "Identifying TOP_COVER...")
            faces = sel_cyl("<Body></Body>", 53, 54, "TC_CYL", full=1)
            if faces:
                face_str = ",".join(str(f) for f in faces) + ","
                face_to_grp(face_str, "TC_BODY")
                # Get original name from group before rename
                orig = [b for b in simlab.getBodiesFromGroup("TC_BODY")]
                rename_grp("TC_BODY", "TOP_COVER")
                renamed.append("TOP_COVER")
                results["TOP_COVER"] = orig[0] if orig else "NONE"
                self.component_found.emit(orig[0] if orig else "NONE", "TOP_COVER")
                cleanup("TC_CYL", "TC_BODY")

            # 2. OUTER_RACE + OUTER_RACE_1
            step += 1
            self.progress.emit(int(step/total_steps*100), "Identifying OUTER_RACE...")
            adj_str = get_adj('"TOP_COVER",', "ADJ_TC", renamed)
            faces = sel_cyl(adj_str, 17.4, 17.6, "OR_CYL", full=1)
            if faces:
                face_list = list(faces)
                mid = len(face_list) // 2
                for i, chunk in enumerate([face_list[:mid], face_list[mid:]]):
                    face_str = ",".join(str(f) for f in chunk) + ","
                    grp = f"OR_BODY_{i}"
                    face_to_grp(face_str, grp)
                    new_name = "OUTER_RACE" if i == 0 else "OUTER_RACE_1"
                    orig = [b for b in simlab.getBodiesFromGroup(grp)]
                    rename_grp(grp, new_name)
                    renamed.append(new_name)
                    results[new_name] = orig[0] if orig else "NONE"
                    self.component_found.emit(orig[0] if orig else "NONE", new_name)
                    cleanup(grp)
                cleanup("ADJ_TC", "OR_CYL")

            # 3. ROTOR_RING
            step += 1
            self.progress.emit(int(step/total_steps*100), "Identifying ROTOR_RING...")
            adj_str = get_adj('"TOP_COVER",', "ADJ_TC2", renamed)
            faces = sel_cyl(adj_str, 53, 54, "RR_CYL", full=0, closed=1, open_=1)
            if faces:
                face_str = ",".join(str(f) for f in faces) + ","
                face_to_grp(face_str, "RR_BODY")
                orig = [b for b in simlab.getBodiesFromGroup("RR_BODY")]
                rename_grp("RR_BODY", "ROTOR_RING")
                renamed.append("ROTOR_RING")
                results["ROTOR_RING"] = orig[0] if orig else "NONE"
                self.component_found.emit(orig[0] if orig else "NONE", "ROTOR_RING")
                cleanup("ADJ_TC2", "RR_CYL", "RR_BODY")

            # 4. MID_RACE x4
            step += 1
            self.progress.emit(int(step/total_steps*100), "Identifying MID_RACE...")
            adj_str = get_adj('"OUTER_RACE_1",', "ADJ_OR1", renamed)
            faces = sel_cyl(adj_str, 13.4, 13.6, "MR_CYL", full=1)
            if faces:
                face_list = list(faces)
                chunk_size = len(face_list) // 4
                for i in range(4):
                    start = i * chunk_size
                    end   = (i+1)*chunk_size if i < 3 else len(face_list)
                    face_str = ",".join(str(f) for f in face_list[start:end]) + ","
                    grp = f"MR_BODY_{i}"
                    face_to_grp(face_str, grp)
                    new_name = "MID_RACE" if i == 0 else f"MID_RACE_{i}"
                    orig = [b for b in simlab.getBodiesFromGroup(grp)]
                    rename_grp(grp, new_name)
                    renamed.append(new_name)
                    results[new_name] = orig[0] if orig else "NONE"
                    self.component_found.emit(orig[0] if orig else "NONE", new_name)
                    cleanup(grp)
                cleanup("ADJ_OR1", "MR_CYL")

            # 5. INNER_RACE x2
            step += 1
            self.progress.emit(int(step/total_steps*100), "Identifying INNER_RACE...")
            mid_str = '"MID_RACE","MID_RACE_1","MID_RACE_2","MID_RACE_3",'
            adj_str = get_adj(mid_str, "ADJ_MR", renamed)
            faces = sel_cyl(adj_str, 11.4, 11.5, "IR_CYL", full=1)
            if faces:
                face_list = list(faces)
                mid = len(face_list) // 2
                for i, chunk in enumerate([face_list[:mid], face_list[mid:]]):
                    face_str = ",".join(str(f) for f in chunk) + ","
                    grp = f"IR_BODY_{i}"
                    face_to_grp(face_str, grp)
                    new_name = "INNER_RACE" if i == 0 else "INNER_RACE_1"
                    orig = [b for b in simlab.getBodiesFromGroup(grp)]
                    rename_grp(grp, new_name)
                    renamed.append(new_name)
                    results[new_name] = orig[0] if orig else "NONE"
                    self.component_found.emit(orig[0] if orig else "NONE", new_name)
                    cleanup(grp)
                cleanup("ADJ_MR", "IR_CYL")

            # 6. SHAFT
            step += 1
            self.progress.emit(int(step/total_steps*100), "Identifying SHAFT...")
            adj_str = get_adj('"INNER_RACE","INNER_RACE_1",', "ADJ_IR", renamed)
            faces = sel_cyl(adj_str, 7.4, 7.6, "SH_CYL", full=1)
            if faces:
                face_str = ",".join(str(f) for f in faces) + ","
                face_to_grp(face_str, "SH_BODY")
                orig = [b for b in simlab.getBodiesFromGroup("SH_BODY")]
                rename_grp("SH_BODY", "SHAFT")
                renamed.append("SHAFT")
                results["SHAFT"] = orig[0] if orig else "NONE"
                self.component_found.emit(orig[0] if orig else "NONE", "SHAFT")
                cleanup("ADJ_IR", "SH_CYL", "SH_BODY")

            # 7. STATOR
            step += 1
            self.progress.emit(int(step/total_steps*100), "Identifying STATOR...")
            simlab.execute(f'''<SelectAdjacentBodies UUID="078de645-1446-470c-9365-d61a1a5c4f47">
  <InputBodies><Entities><Model>{MODEL}</Model><Body>"SHAFT",</Body></Entities></InputBodies>
  <Tolerance Value="0.000001"/><GroupName Value="ADJ_SH"/>
 </SelectAdjacentBodies>''')
            adj_bodies_st = simlab.getBodiesFromGroup("ADJ_SH")
            adj_str_st = "".join(f'"{b}",' for b in adj_bodies_st if b not in renamed)
            faces = sel_cyl(adj_str_st, 7.6, 7.71, "ST_CYL", full=1, closed=1, open_=1)
            if faces:
                face_str = ",".join(str(f) for f in faces) + ","
                face_to_grp(face_str, "ST_BODY")
                orig = [b for b in simlab.getBodiesFromGroup("ST_BODY")]
                rename_grp("ST_BODY", "STATOR")
                renamed.append("STATOR")
                results["STATOR"] = orig[0] if orig else "NONE"
                self.component_found.emit(orig[0] if orig else "NONE", "STATOR")
                cleanup("ADJ_SH", "ST_CYL", "ST_BODY")

            # 8. TOP_INSULATOR
            step += 1
            self.progress.emit(int(step/total_steps*100), "Identifying TOP_INSULATOR...")
            simlab.execute(f'''<SelectAdjacentBodies UUID="078de645-1446-470c-9365-d61a1a5c4f47">
  <InputBodies><Entities><Model>{MODEL}</Model><Body>"STATOR",</Body></Entities></InputBodies>
  <Tolerance Value="0.000001"/><GroupName Value="ADJ_ST_TI"/>
 </SelectAdjacentBodies>''')
            adj_ti = simlab.getBodiesFromGroup("ADJ_ST_TI")
            adj_str_ti = "".join(f'"{b}",' for b in adj_ti if b not in renamed)
            faces_ti = sel_cone(adj_str_ti, 27.9, 28.0, "CYL_TI")
            if faces_ti:
                face_str = ",".join(str(f) for f in faces_ti) + ","
                face_to_grp(face_str, "BODY_TI")
                orig = [b for b in simlab.getBodiesFromGroup("BODY_TI")]
                rename_grp("BODY_TI", "TOP_INSULATOR")
                renamed.append("TOP_INSULATOR")
                results["TOP_INSULATOR"] = orig[0] if orig else "NONE"
                self.component_found.emit(orig[0] if orig else "NONE", "TOP_INSULATOR")
                cleanup("ADJ_ST_TI", "CYL_TI", "BODY_TI")

            # 9. BOTTOM_INSULATOR
            step += 1
            self.progress.emit(int(step/total_steps*100), "Identifying BOTTOM_INSULATOR...")
            simlab.execute(f'''<SelectAdjacentBodies UUID="078de645-1446-470c-9365-d61a1a5c4f47">
  <InputBodies><Entities><Model>{MODEL}</Model><Body>"STATOR",</Body></Entities></InputBodies>
  <Tolerance Value="0.000001"/><GroupName Value="ADJ_ST_BI"/>
 </SelectAdjacentBodies>''')
            adj_bi = simlab.getBodiesFromGroup("ADJ_ST_BI")
            adj_str_bi = "".join(f'"{b}",' for b in adj_bi if b not in renamed)
            faces_bi = sel_cone(adj_str_bi, 27.5, 29.4, "CYL_BI")
            if faces_bi:
                face_str = ",".join(str(f) for f in faces_bi) + ","
                face_to_grp(face_str, "BODY_BI")
                bodies_bi = [b for b in simlab.getBodiesFromGroup("BODY_BI") if b not in renamed]
                winner_bi = None
                if len(bodies_bi) == 1:
                    winner_bi = bodies_bi[0]
                else:
                    for body in bodies_bi:
                        addon = sel_cone(f'"{body}",', 32, 33, "CYL_BI_ADDON")
                        cleanup("CYL_BI_ADDON")
                        if addon:
                            winner_bi = body
                            break
                    if not winner_bi:
                        winner_bi = bodies_bi[0]
                if winner_bi:
                    rename_grp("BODY_BI", "BOTTOM_INSULATOR")
                    renamed.append("BOTTOM_INSULATOR")
                    results["BOTTOM_INSULATOR"] = winner_bi
                    self.component_found.emit(winner_bi, "BOTTOM_INSULATOR")
                cleanup("ADJ_ST_BI", "CYL_BI", "BODY_BI")

            # 10. PCB_BRACKET
            step += 1
            self.progress.emit(int(step/total_steps*100), "Identifying PCB_BRACKET...")
            simlab.execute(f'''<SelectAdjacentBodies UUID="078de645-1446-470c-9365-d61a1a5c4f47">
  <InputBodies><Entities><Model>{MODEL}</Model><Body>"STATOR",</Body></Entities></InputBodies>
  <Tolerance Value="0.000001"/><GroupName Value="ADJ_ST_PCB"/>
 </SelectAdjacentBodies>''')
            adj_pcb = simlab.getBodiesFromGroup("ADJ_ST_PCB")
            adj_str_pcb = "".join(f'"{b}",' for b in adj_pcb if b not in renamed)
            faces_pcb = sel_cone(adj_str_pcb, 1.9, 2.1, "CYL_PCB")
            if faces_pcb:
                face_str = ",".join(str(f) for f in faces_pcb) + ","
                face_to_grp(face_str, "BODY_PCB")
                orig = [b for b in simlab.getBodiesFromGroup("BODY_PCB")]
                rename_grp("BODY_PCB", "PCB_BRACKET")
                renamed.append("PCB_BRACKET")
                results["PCB_BRACKET"] = orig[0] if orig else "NONE"
                self.component_found.emit(orig[0] if orig else "NONE", "PCB_BRACKET")
                cleanup("ADJ_ST_PCB", "CYL_PCB", "BODY_PCB")

            # 11. DISPLAY_PCB
            step += 1
            self.progress.emit(int(step/total_steps*100), "Identifying DISPLAY_PCB...")
            if "PCB_BRACKET" in renamed:
                simlab.execute(f'''<SelectAdjacentBodies UUID="078de645-1446-470c-9365-d61a1a5c4f47">
  <InputBodies><Entities><Model>{MODEL}</Model><Body>"PCB_BRACKET",</Body></Entities></InputBodies>
  <Tolerance Value="0.000001"/><GroupName Value="ADJ_PCB"/>
 </SelectAdjacentBodies>''')
                adj_dpcb = simlab.getBodiesFromGroup("ADJ_PCB")
                adj_str_dpcb = "".join(f'"{b}",' for b in adj_dpcb if b not in renamed)
                faces_dpcb = sel_cyl(adj_str_dpcb, 2.05, 2.15, "CYL_DPCB", full=1)
                if faces_dpcb:
                    face_str = ",".join(str(f) for f in faces_dpcb) + ","
                    face_to_grp(face_str, "BODY_DPCB")
                    orig = [b for b in simlab.getBodiesFromGroup("BODY_DPCB")]
                    rename_grp("BODY_DPCB", "DISPLAY_PCB")
                    renamed.append("DISPLAY_PCB")
                    results["DISPLAY_PCB"] = orig[0] if orig else "NONE"
                    self.component_found.emit(orig[0] if orig else "NONE", "DISPLAY_PCB")
                    cleanup("ADJ_PCB", "CYL_DPCB", "BODY_DPCB")

            self.progress.emit(100, "Identification complete")
            self.finished.emit(results)

        except Exception as e:
            self.error.emit(str(e))


class SimLabGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.results = {}       # standard_name -> original_name
        self.row_data = []      # list of {original, standard, row_idx}
        self.setWindowTitle("SimLab Component Identifier")
        self.setMinimumSize(820, 560)
        self.setStyleSheet(f"""
            QMainWindow {{ background: {CLR_BG}; }}
            QWidget {{ background: {CLR_BG}; color: {CLR_TEXT}; font-family: 'Segoe UI'; }}
            QLabel {{ color: {CLR_TEXT}; }}
            QScrollBar:vertical {{ background: {CLR_PANEL}; width: 8px; border-radius: 4px; }}
            QScrollBar::handle:vertical {{ background: {CLR_BORDER}; border-radius: 4px; }}
        """)
        self._build_ui()

    def _combo_style(self):
        return f"""
            QComboBox {{
                background: {CLR_PANEL}; color: {CLR_TEXT};
                border: 1px solid {CLR_BORDER}; border-radius: 4px;
                padding: 4px 8px; font-size: 11px;
            }}
            QComboBox:hover {{ border-color: {CLR_ACCENT}; }}
            QComboBox::drop-down {{ border: none; width: 16px; }}
            QComboBox QAbstractItemView {{
                background: {CLR_PANEL}; color: {CLR_TEXT};
                selection-background-color: {CLR_ACCENT};
            }}
        """

    def _apply_defaults_to_all(self):
        mtype = self.global_mesh_type.currentText()
        msize = self.global_mesh_size.currentText()
        for row in range(self.table.rowCount()):
            mt_combo = self.table.cellWidget(row, 3)
            ms_edit  = self.table.cellWidget(row, 4)
            if mt_combo:
                mt_combo.setCurrentText(mtype)
            if ms_edit:
                ms_edit.setText(msize)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # -- Header ------------------------------------------------------------
        header = QWidget()
        header.setFixedHeight(64)
        header.setStyleSheet(f"background: {CLR_HEADER}; border-bottom: 1px solid {CLR_BORDER};")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(20, 0, 20, 0)

        title = QLabel("Component Identification")
        title.setFont(QFont("Segoe UI", 15, QFont.Bold))
        title.setStyleSheet(f"color: {CLR_TEXT}; letter-spacing: 1px;")

        subtitle = QLabel("SimLab Pre-Processor")
        subtitle.setFont(QFont("Segoe UI", 9))
        subtitle.setStyleSheet(f"color: {CLR_TEXT_DIM};")

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        title_box.addWidget(title)
        title_box.addWidget(subtitle)

        self.run_btn = QPushButton(">  Run Identification")
        self.run_btn.setFixedSize(180, 36)
        self.run_btn.setStyleSheet(f"""
            QPushButton {{
                background: {CLR_BTN_RUN}; color: white;
                border: none; border-radius: 6px;
                font-size: 12px; font-weight: bold; letter-spacing: 0.5px;
            }}
            QPushButton:hover {{ background: #3AAA6A; }}
            QPushButton:disabled {{ background: #2A3A30; color: {CLR_TEXT_DIM}; }}
        """)
        self.run_btn.clicked.connect(self._run_identification)

        h_layout.addLayout(title_box)
        h_layout.addStretch()
        h_layout.addWidget(self.run_btn)
        main_layout.addWidget(header)

        # -- Global defaults bar -----------------------------------------------
        defaults_bar = QWidget()
        defaults_bar.setFixedHeight(44)
        defaults_bar.setStyleSheet(f"background: {CLR_PANEL}; border-bottom: 1px solid {CLR_BORDER};")
        d_layout = QHBoxLayout(defaults_bar)
        d_layout.setContentsMargins(16, 0, 16, 0)
        d_layout.setSpacing(8)

        d_label = QLabel("Set all rows:")
        d_label.setStyleSheet(f"color: {CLR_TEXT_DIM}; font-size: 11px;")

        self.global_mesh_type = QComboBox()
        self.global_mesh_type.addItems(["Tet4", "Tet10"])
        self.global_mesh_type.setFixedWidth(80)
        self.global_mesh_type.setStyleSheet(self._combo_style())

        self.global_mesh_size = QComboBox()
        self.global_mesh_size.addItems(["3.5", "4", "4.5", "5"])
        self.global_mesh_size.setEditable(True)
        self.global_mesh_size.setFixedWidth(65)
        self.global_mesh_size.setStyleSheet(self._combo_style())

        apply_all_btn = QPushButton("Apply to All")
        apply_all_btn.setFixedSize(95, 28)
        apply_all_btn.setStyleSheet(f"background: {CLR_BORDER}; color: {CLR_TEXT}; border: none; border-radius: 4px; font-size: 11px;")
        apply_all_btn.clicked.connect(self._apply_defaults_to_all)

        type_lbl = QLabel("Mesh Type:")
        type_lbl.setStyleSheet(f"color: {CLR_TEXT_DIM}; font-size: 11px;")
        size_lbl = QLabel("Size (mm):")
        size_lbl.setStyleSheet(f"color: {CLR_TEXT_DIM}; font-size: 11px;")

        d_layout.addWidget(d_label)
        d_layout.addWidget(type_lbl)
        d_layout.addWidget(self.global_mesh_type)
        d_layout.addWidget(size_lbl)
        d_layout.addWidget(self.global_mesh_size)
        d_layout.addWidget(apply_all_btn)
        d_layout.addStretch()
        self.mesh_selected_btn = QPushButton(">> Mesh Selected")
        self.mesh_selected_btn.setFixedSize(130, 28)
        self.mesh_selected_btn.setStyleSheet("background: #2E7D52; color: white; border: none; border-radius: 4px; font-size: 11px; font-weight: bold;")
        self.mesh_selected_btn.clicked.connect(self._mesh_selected_components)
        d_layout.addWidget(self.mesh_selected_btn)
        main_layout.addWidget(defaults_bar)

        # -- Progress bar ------------------------------------------------------
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(3)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{ background: {CLR_BORDER}; border: none; }}
            QProgressBar::chunk {{ background: {CLR_ACCENT}; }}
        """)
        main_layout.addWidget(self.progress_bar)

        # -- Status label ------------------------------------------------------
        self.status_label = QLabel("  Ready - click Run Identification to begin")
        self.status_label.setFixedHeight(28)
        self.status_label.setStyleSheet(f"""
            color: {CLR_TEXT_DIM}; font-size: 11px;
            background: {CLR_PANEL}; padding-left: 12px;
            border-bottom: 1px solid {CLR_BORDER};
        """)
        main_layout.addWidget(self.status_label)

        # -- Table -------------------------------------------------------------
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["", "Part Name", "Standard Name", "Mesh Type", "Mesh Size", "Review", "Mesh"])
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background: {CLR_ROW_EVEN}; color: {CLR_TEXT};
                gridline-color: {CLR_BORDER}; border: none;
                font-size: 12px;
            }}
            QTableWidget::item {{ padding: 6px 12px; border: none; }}
            QTableWidget::item:selected {{ background: {CLR_ACCENT}; color: white; }}
            QHeaderView::section {{
                background: {CLR_HEADER}; color: {CLR_TEXT_DIM};
                font-size: 11px; font-weight: bold;
                padding: 8px 12px; border: none;
                border-right: 1px solid {CLR_BORDER};
                border-bottom: 1px solid {CLR_BORDER};
                letter-spacing: 1px; text-transform: uppercase;
            }}
        """)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 30)
        self.table.setColumnWidth(2, 170)
        self.table.setColumnWidth(3, 85)
        self.table.setColumnWidth(4, 75)
        self.table.setColumnWidth(5, 75)
        self.table.setColumnWidth(6, 75)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(self.table.styleSheet() + f"""
            QTableWidget {{ alternate-background-color: {CLR_ROW_ODD}; }}
        """)
        main_layout.addWidget(self.table)

        # -- Footer ------------------------------------------------------------
        footer = QWidget()
        footer.setFixedHeight(36)
        footer.setStyleSheet(f"background: {CLR_HEADER}; border-top: 1px solid {CLR_BORDER};")
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(16, 0, 16, 0)
        self.footer_label = QLabel("0 components identified")
        self.footer_label.setStyleSheet(f"color: {CLR_TEXT_DIM}; font-size: 11px;")
        f_layout.addWidget(self.footer_label)
        f_layout.addStretch()
        main_layout.addWidget(footer)

    def _run_identification(self):
        self.run_btn.setEnabled(False)
        self.run_btn.setText("  Running...")
        self.table.setRowCount(0)
        self.row_data.clear()
        self.results.clear()

        # Run identification directly on main thread (required for SimLab)
        try:
            self._run_identification_main()
        except Exception as e:
            self._on_error(str(e))

    def _run_identification_main(self):
        from hwx import simlab
        from PyQt5.QtWidgets import QApplication

        MODEL = "$Geometry"

        def sel_cyl(body_str, r_min, r_max, grp, full=1, closed=0, open_=0):
            simlab.execute(f'''<SelectFeatures UUID="CF82E8FB-9B3E-4c02-BA93-9466C1342C6E" CheckBox="ON">
  <SupportEntities><Entities><Model>{MODEL}</Model><Body>{body_str}</Body></Entities></SupportEntities>
  <Arcs MaxValue="0 mm" MinValue="0 mm" Value="0"/><ArcsAll Value="2"/>
  <Circles MaxValue="0 mm" MinValue="0 mm" Value="0"/><CirclesAll Value="0"/>
  <Cones MaxValue="0 mm" MinValue="0 mm" Value="0"/><ConeAll Value="0"/>
  <FullCone Value="0"/><ClosedPartialCone Value="0"/><OpenPartialCone Value="0"/>
  <TaperAngle Angle="0 deg" Value="0"/>
  <Dics MaxValue="0 mm" MinValue="0 mm" Value="0"/><DicsAll Value="0"/>
  <HollowDics MaxValue="0 mm" MinValue="0 mm" Value="0"/><HollowDicsAll Value="0"/>
  <Cylinders MaxValue="{r_max} mm" MinValue="{r_min} mm" Value="1"/><CylindersAll Value="0"/>
  <FullCylinder Value="{full}"/><ClosedPartialCylinder Value="{closed}"/><OpenPartialCylinder Value="{open_}"/>
  <Fillets MaxValue="3 mm" MinValue="0.51 mm" Value="0"/><FilletsOption Value="1"/>
  <PlanarFaces Value="0"/><FourEdgedFaces Value="0"/><ConnectedCoaxialFaces Value="0"/>
  <ThroughBoltHole MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <BlindBoltHole MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <BlindBoltHoleDepth MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <SlotEdges MaxValue="0 mm" MinValue="0 mm" Value="0"/><SlotEdgesAll Value="0"/>
  <ArcLengthBased Value=""/><AngleBased Value=""/>
  <SharpEdges Option="" Angle="" Value=""/><ThicknessBased Value=""/>
  <LogosAndDetails Value=""/><LogosAndDetailsThickness Value=""/>
  <CreateGrp Value="1" Name="{grp}"/>
 </SelectFeatures>''')
            return simlab.getSelectedEntities("Face")

        def sel_cone(body_str, r_min, r_max, grp):
            simlab.execute(f'''<SelectFeatures UUID="CF82E8FB-9B3E-4c02-BA93-9466C1342C6E" CheckBox="ON">
  <SupportEntities><Entities><Model>{MODEL}</Model><Body>{body_str}</Body></Entities></SupportEntities>
  <Arcs MaxValue="0 mm" MinValue="0 mm" Value="0"/><ArcsAll Value="2"/>
  <Circles MaxValue="0 mm" MinValue="0 mm" Value="0"/><CirclesAll Value="0"/>
  <Cones MaxValue="{r_max} mm" MinValue="{r_min} mm" Value="1"/><ConeAll Value="0"/>
  <FullCone Value="1"/><ClosedPartialCone Value="1"/><OpenPartialCone Value="1"/>
  <TaperAngle Angle="0 deg" Value="0"/>
  <Dics MaxValue="0 mm" MinValue="0 mm" Value="0"/><DicsAll Value="0"/>
  <HollowDics MaxValue="0 mm" MinValue="0 mm" Value="0"/><HollowDicsAll Value="0"/>
  <Cylinders MaxValue="0 mm" MinValue="0 mm" Value="0"/><CylindersAll Value="0"/>
  <FullCylinder Value="0"/><ClosedPartialCylinder Value="0"/><OpenPartialCylinder Value="0"/>
  <Fillets MaxValue="3 mm" MinValue="0.51 mm" Value="0"/><FilletsOption Value="1"/>
  <PlanarFaces Value="0"/><FourEdgedFaces Value="0"/><ConnectedCoaxialFaces Value="0"/>
  <ThroughBoltHole MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <BlindBoltHole MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <BlindBoltHoleDepth MaxValue="0 mm" MinValue="0 mm" Value="0"/>
  <SlotEdges MaxValue="0 mm" MinValue="0 mm" Value="0"/><SlotEdgesAll Value="0"/>
  <ArcLengthBased Value=""/><AngleBased Value=""/>
  <SharpEdges Option="" Angle="" Value=""/><ThicknessBased Value=""/>
  <LogosAndDetails Value=""/><LogosAndDetailsThickness Value=""/>
  <CreateGrp Value="1" Name="{grp}"/>
 </SelectFeatures>''')
            return simlab.getSelectedEntities("Face")

        def get_adj(body_str, grp, exclude):
            simlab.execute(f'''<SelectAdjacentBodies UUID="078de645-1446-470c-9365-d61a1a5c4f47">
  <InputBodies><Entities><Model>{MODEL}</Model><Body>{body_str}</Body></Entities></InputBodies>
  <Tolerance Value="0.000001"/>
  <GroupName Value="{grp}"/>
 </SelectAdjacentBodies>''')
            adj = simlab.getBodiesFromGroup(grp)
            return "".join(f'"{b}",' for b in adj if b not in exclude)

        def face_to_grp(face_str, grp):
            simlab.execute(f'''<SelectFaceAssociatedEntities UUID="4128ad97-7527-4dad-9746-470cfa135434">
  <InputFaces Values=""><Entities><Model>{MODEL}</Model><Face>{face_str}</Face></Entities></InputFaces>
  <Option Value="Bodies"/>
  <Groupname Value="{grp}"/>
 </SelectFaceAssociatedEntities>''')

        def rename_grp(grp, new_name):
            simlab.execute(f'''<RenameBody CheckBox="ON" UUID="78633e0d-3d2f-4e9a-b075-7bff122772d8">
  <SupportEntities><Group>{grp}</Group></SupportEntities>
  <NewName Value="{new_name}"/>
  <AllowDuplicate Value="0"/>
  <Output/>
 </RenameBody>''')

        def cleanup(*grps):
            simlab.execute(f'''<DeleteGroupControl UUID="2a3b5834-9708-4b03-871c-6d05623667bd" CheckBox="ON">
  <tag Value="-1"/>
  <Name Value="{",".join(grps)},"/>
  <Output/>
 </DeleteGroupControl>''')

        def add_row(orig, standard):
            self._on_component_found(orig, standard)
            self.results[standard] = orig
            QApplication.processEvents()

        renamed = []
        total = 11

        # 1. TOP_COVER
        self._on_progress(int(1/total*100), "Identifying TOP_COVER...")
        QApplication.processEvents()
        faces = sel_cyl("<Body></Body>", 53, 54, "TC_CYL", full=1)
        if faces:
            face_str = ",".join(str(f) for f in faces) + ","
            face_to_grp(face_str, "TC_BODY")
            orig = list(simlab.getBodiesFromGroup("TC_BODY"))
            rename_grp("TC_BODY", "TOP_COVER")
            renamed.append("TOP_COVER")
            add_row(orig[0] if orig else "NONE", "TOP_COVER")
            cleanup("TC_CYL", "TC_BODY")

        # 2. OUTER_RACE + OUTER_RACE_1
        self._on_progress(int(2/total*100), "Identifying OUTER_RACE...")
        QApplication.processEvents()
        adj_str = get_adj('"TOP_COVER",', "ADJ_TC", renamed)
        faces = sel_cyl(adj_str, 17.4, 17.6, "OR_CYL", full=1)
        if faces:
            face_list = list(faces)
            mid = len(face_list) // 2
            for i, chunk in enumerate([face_list[:mid], face_list[mid:]]):
                face_str = ",".join(str(f) for f in chunk) + ","
                grp = f"OR_BODY_{i}"
                face_to_grp(face_str, grp)
                new_name = "OUTER_RACE" if i == 0 else "OUTER_RACE_1"
                orig = list(simlab.getBodiesFromGroup(grp))
                rename_grp(grp, new_name)
                renamed.append(new_name)
                add_row(orig[0] if orig else "NONE", new_name)
                cleanup(grp)
            cleanup("ADJ_TC", "OR_CYL")

        # 3. ROTOR_RING
        self._on_progress(int(3/total*100), "Identifying ROTOR_RING...")
        QApplication.processEvents()
        adj_str = get_adj('"TOP_COVER",', "ADJ_TC2", renamed)
        faces = sel_cyl(adj_str, 53, 54, "RR_CYL", full=0, closed=1, open_=1)
        if faces:
            face_str = ",".join(str(f) for f in faces) + ","
            face_to_grp(face_str, "RR_BODY")
            orig = list(simlab.getBodiesFromGroup("RR_BODY"))
            rename_grp("RR_BODY", "ROTOR_RING")
            renamed.append("ROTOR_RING")
            add_row(orig[0] if orig else "NONE", "ROTOR_RING")
            cleanup("ADJ_TC2", "RR_CYL", "RR_BODY")

        # 4. MID_RACE x4
        self._on_progress(int(4/total*100), "Identifying MID_RACE...")
        QApplication.processEvents()
        adj_str = get_adj('"OUTER_RACE_1",', "ADJ_OR1", renamed)
        faces = sel_cyl(adj_str, 13.4, 13.6, "MR_CYL", full=1)
        if faces:
            face_list = list(faces)
            chunk_size = len(face_list) // 4
            for i in range(4):
                start = i * chunk_size
                end = (i+1)*chunk_size if i < 3 else len(face_list)
                face_str = ",".join(str(f) for f in face_list[start:end]) + ","
                grp = f"MR_BODY_{i}"
                face_to_grp(face_str, grp)
                new_name = "MID_RACE" if i == 0 else f"MID_RACE_{i}"
                orig = list(simlab.getBodiesFromGroup(grp))
                rename_grp(grp, new_name)
                renamed.append(new_name)
                add_row(orig[0] if orig else "NONE", new_name)
                cleanup(grp)
            cleanup("ADJ_OR1", "MR_CYL")

        # 5. INNER_RACE x2
        self._on_progress(int(5/total*100), "Identifying INNER_RACE...")
        QApplication.processEvents()
        mid_str = '"MID_RACE","MID_RACE_1","MID_RACE_2","MID_RACE_3",'
        adj_str = get_adj(mid_str, "ADJ_MR", renamed)
        faces = sel_cyl(adj_str, 11.4, 11.5, "IR_CYL", full=1)
        if faces:
            face_list = list(faces)
            mid = len(face_list) // 2
            for i, chunk in enumerate([face_list[:mid], face_list[mid:]]):
                face_str = ",".join(str(f) for f in chunk) + ","
                grp = f"IR_BODY_{i}"
                face_to_grp(face_str, grp)
                new_name = "INNER_RACE" if i == 0 else "INNER_RACE_1"
                orig = list(simlab.getBodiesFromGroup(grp))
                rename_grp(grp, new_name)
                renamed.append(new_name)
                add_row(orig[0] if orig else "NONE", new_name)
                cleanup(grp)
            cleanup("ADJ_MR", "IR_CYL")

        # 6. SHAFT
        self._on_progress(int(6/total*100), "Identifying SHAFT...")
        QApplication.processEvents()
        adj_str = get_adj('"INNER_RACE","INNER_RACE_1",', "ADJ_IR", renamed)
        faces = sel_cyl(adj_str, 7.4, 7.6, "SH_CYL", full=1)
        if faces:
            face_str = ",".join(str(f) for f in faces) + ","
            face_to_grp(face_str, "SH_BODY")
            orig = list(simlab.getBodiesFromGroup("SH_BODY"))
            rename_grp("SH_BODY", "SHAFT")
            renamed.append("SHAFT")
            add_row(orig[0] if orig else "NONE", "SHAFT")
            cleanup("ADJ_IR", "SH_CYL", "SH_BODY")

        # 7. STATOR
        self._on_progress(int(7/total*100), "Identifying STATOR...")
        QApplication.processEvents()
        simlab.execute(f'''<SelectAdjacentBodies UUID="078de645-1446-470c-9365-d61a1a5c4f47">
  <InputBodies><Entities><Model>{MODEL}</Model><Body>"SHAFT",</Body></Entities></InputBodies>
  <Tolerance Value="0.000001"/><GroupName Value="ADJ_SH"/>
 </SelectAdjacentBodies>''')
        adj_st = simlab.getBodiesFromGroup("ADJ_SH")
        adj_str_st = "".join(f'"{b}",' for b in adj_st if b not in renamed)
        faces = sel_cyl(adj_str_st, 7.6, 7.71, "ST_CYL", full=1, closed=1, open_=1)
        if faces:
            face_str = ",".join(str(f) for f in faces) + ","
            face_to_grp(face_str, "ST_BODY")
            orig = list(simlab.getBodiesFromGroup("ST_BODY"))
            rename_grp("ST_BODY", "STATOR")
            renamed.append("STATOR")
            add_row(orig[0] if orig else "NONE", "STATOR")
            cleanup("ADJ_SH", "ST_CYL", "ST_BODY")

        # 8. TOP_INSULATOR
        self._on_progress(int(8/total*100), "Identifying TOP_INSULATOR...")
        QApplication.processEvents()
        simlab.execute(f'''<SelectAdjacentBodies UUID="078de645-1446-470c-9365-d61a1a5c4f47">
  <InputBodies><Entities><Model>{MODEL}</Model><Body>"STATOR",</Body></Entities></InputBodies>
  <Tolerance Value="0.000001"/><GroupName Value="ADJ_ST_TI"/>
 </SelectAdjacentBodies>''')
        adj_ti = simlab.getBodiesFromGroup("ADJ_ST_TI")
        adj_str_ti = "".join(f'"{b}",' for b in adj_ti if b not in renamed)
        faces_ti = sel_cone(adj_str_ti, 27.9, 28.0, "CYL_TI")
        if faces_ti:
            face_str = ",".join(str(f) for f in faces_ti) + ","
            face_to_grp(face_str, "BODY_TI")
            orig = list(simlab.getBodiesFromGroup("BODY_TI"))
            rename_grp("BODY_TI", "TOP_INSULATOR")
            renamed.append("TOP_INSULATOR")
            add_row(orig[0] if orig else "NONE", "TOP_INSULATOR")
            cleanup("ADJ_ST_TI", "CYL_TI", "BODY_TI")

        # 9. BOTTOM_INSULATOR
        self._on_progress(int(9/total*100), "Identifying BOTTOM_INSULATOR...")
        QApplication.processEvents()
        simlab.execute(f'''<SelectAdjacentBodies UUID="078de645-1446-470c-9365-d61a1a5c4f47">
  <InputBodies><Entities><Model>{MODEL}</Model><Body>"STATOR",</Body></Entities></InputBodies>
  <Tolerance Value="0.000001"/><GroupName Value="ADJ_ST_BI"/>
 </SelectAdjacentBodies>''')
        adj_bi = simlab.getBodiesFromGroup("ADJ_ST_BI")
        adj_str_bi = "".join(f'"{b}",' for b in adj_bi if b not in renamed)
        faces_bi = sel_cone(adj_str_bi, 27.5, 29.4, "CYL_BI")
        if faces_bi:
            face_str = ",".join(str(f) for f in faces_bi) + ","
            face_to_grp(face_str, "BODY_BI")
            bodies_bi = [b for b in simlab.getBodiesFromGroup("BODY_BI") if b not in renamed]
            winner_bi = None
            if len(bodies_bi) == 1:
                winner_bi = bodies_bi[0]
            else:
                for body in bodies_bi:
                    addon = sel_cone(f'"{body}",', 32, 33, "CYL_BI_ADDON")
                    cleanup("CYL_BI_ADDON")
                    if addon:
                        winner_bi = body
                        break
                if not winner_bi:
                    winner_bi = bodies_bi[0] if bodies_bi else None
            if winner_bi:
                rename_grp("BODY_BI", "BOTTOM_INSULATOR")
                renamed.append("BOTTOM_INSULATOR")
                add_row(winner_bi, "BOTTOM_INSULATOR")
            cleanup("ADJ_ST_BI", "CYL_BI", "BODY_BI")

        # 10. PCB_BRACKET
        self._on_progress(int(10/total*100), "Identifying PCB_BRACKET...")
        QApplication.processEvents()
        simlab.execute(f'''<SelectAdjacentBodies UUID="078de645-1446-470c-9365-d61a1a5c4f47">
  <InputBodies><Entities><Model>{MODEL}</Model><Body>"STATOR",</Body></Entities></InputBodies>
  <Tolerance Value="0.000001"/><GroupName Value="ADJ_ST_PCB"/>
 </SelectAdjacentBodies>''')
        adj_pcb = simlab.getBodiesFromGroup("ADJ_ST_PCB")
        adj_str_pcb = "".join(f'"{b}",' for b in adj_pcb if b not in renamed)
        faces_pcb = sel_cone(adj_str_pcb, 1.9, 2.1, "CYL_PCB")
        if faces_pcb:
            face_str = ",".join(str(f) for f in faces_pcb) + ","
            face_to_grp(face_str, "BODY_PCB")
            orig = list(simlab.getBodiesFromGroup("BODY_PCB"))
            rename_grp("BODY_PCB", "PCB_BRACKET")
            renamed.append("PCB_BRACKET")
            add_row(orig[0] if orig else "NONE", "PCB_BRACKET")
            cleanup("ADJ_ST_PCB", "CYL_PCB", "BODY_PCB")

        # 11. DISPLAY_PCB
        self._on_progress(int(11/total*100), "Identifying DISPLAY_PCB...")
        QApplication.processEvents()
        if "PCB_BRACKET" in renamed:
            simlab.execute(f'''<SelectAdjacentBodies UUID="078de645-1446-470c-9365-d61a1a5c4f47">
  <InputBodies><Entities><Model>{MODEL}</Model><Body>"PCB_BRACKET",</Body></Entities></InputBodies>
  <Tolerance Value="0.000001"/><GroupName Value="ADJ_PCB"/>
 </SelectAdjacentBodies>''')
            adj_dpcb = simlab.getBodiesFromGroup("ADJ_PCB")
            adj_str_dpcb = "".join(f'"{b}",' for b in adj_dpcb if b not in renamed)
            faces_dpcb = sel_cyl(adj_str_dpcb, 2.05, 2.15, "CYL_DPCB", full=1)
            if faces_dpcb:
                face_str = ",".join(str(f) for f in faces_dpcb) + ","
                face_to_grp(face_str, "BODY_DPCB")
                orig = list(simlab.getBodiesFromGroup("BODY_DPCB"))
                rename_grp("BODY_DPCB", "DISPLAY_PCB")
                renamed.append("DISPLAY_PCB")
                add_row(orig[0] if orig else "NONE", "DISPLAY_PCB")
                cleanup("ADJ_PCB", "CYL_DPCB", "BODY_DPCB")

        self._on_finished(self.results)

    def _on_progress(self, value, message):
        self.progress_bar.setValue(value)
        self.status_label.setText(f"  {message}")

    def _on_component_found(self, original_name, standard_name):
        """Add a row to the table as each component is identified."""
        row = self.table.rowCount()
        self.table.insertRow(row)

        # Checkbox col 0
        chk = QCheckBox()
        chk.setStyleSheet("QCheckBox { margin-left: 8px; }")
        self.table.setCellWidget(row, 0, chk)

        # Part Name col 1
        part_item = QTableWidgetItem(original_name)
        part_item.setForeground(QColor(CLR_TEXT_DIM))
        self.table.setItem(row, 1, part_item)

        # Standard Name dropdown col 2
        combo = QComboBox()
        combo.addItems(STANDARD_NAMES)
        combo.setCurrentText(standard_name)
        combo.setStyleSheet(f"""
            QComboBox {{
                background: {CLR_PANEL}; color: {CLR_TEXT};
                border: 1px solid {CLR_BORDER}; border-radius: 4px;
                padding: 4px 8px; font-size: 12px;
            }}
            QComboBox:hover {{ border-color: {CLR_ACCENT}; }}
            QComboBox::drop-down {{ border: none; width: 20px; }}
            QComboBox QAbstractItemView {{
                background: {CLR_PANEL}; color: {CLR_TEXT};
                selection-background-color: {CLR_ACCENT};
                border: 1px solid {CLR_BORDER};
            }}
        """)
        combo.currentTextChanged.connect(
            lambda text, r=row, orig=original_name: self._on_name_changed(r, orig, text)
        )
        self.table.setCellWidget(row, 2, combo)

        # Mesh Type dropdown
        mt_combo = QComboBox()
        mt_combo.addItems(["Tet4", "Tet10"])
        mt_combo.setStyleSheet(f"""
            QComboBox {{
                background: {CLR_PANEL}; color: {CLR_TEXT};
                border: 1px solid {CLR_BORDER}; border-radius: 4px;
                padding: 2px 4px; font-size: 11px;
            }}
            QComboBox:hover {{ border-color: {CLR_ACCENT}; }}
            QComboBox::drop-down {{ border: none; width: 14px; }}
            QComboBox QAbstractItemView {{
                background: {CLR_PANEL}; color: {CLR_TEXT};
                selection-background-color: {CLR_ACCENT};
            }}
        """)
        self.table.setCellWidget(row, 3, mt_combo)

        # Mesh Size input
        ms_edit = QLineEdit("4")
        ms_edit.setFixedWidth(60)
        ms_edit.setStyleSheet(f"""
            QLineEdit {{
                background: {CLR_PANEL}; color: {CLR_TEXT};
                border: 1px solid {CLR_BORDER}; border-radius: 4px;
                padding: 2px 6px; font-size: 11px;
            }}
            QLineEdit:focus {{ border-color: {CLR_ACCENT}; }}
        """)
        self.table.setCellWidget(row, 4, ms_edit)

        # Review button
        review_btn = QPushButton("Isolate")
        review_btn.setStyleSheet(f"""
            QPushButton {{
                background: {CLR_BTN_REVIEW}; color: white;
                border: none; border-radius: 4px;
                font-size: 11px; font-weight: bold;
                padding: 4px 12px;
            }}
            QPushButton:hover {{ background: {CLR_BTN_HOVER}; }}
        """)
        review_btn.clicked.connect(
            lambda _, sn=standard_name: self._isolate_component(sn)
        )
        self.table.setCellWidget(row, 5, review_btn)

        # Mesh button
        mesh_btn = QPushButton("Mesh")
        mesh_btn.setStyleSheet(f"""
            QPushButton {{
                background: {CLR_BTN_RUN}; color: white;
                border: none; border-radius: 4px;
                font-size: 11px; font-weight: bold;
                padding: 4px 8px;
            }}
            QPushButton:hover {{ background: #3AAA6A; }}
        """)
        # Show mesh button only for first of each race group
        # OUTER_RACE handles all races, hide for sub-components
        # OUTER_RACE is the only active race mesh button
        # All other race components are disabled — one script meshes all 8
        ALL_RACE_DISABLED = [
            "OUTER_RACE_1",
            "MID_RACE", "MID_RACE_1", "MID_RACE_2", "MID_RACE_3",
            "INNER_RACE", "INNER_RACE_1"
        ]
        if standard_name in ALL_RACE_DISABLED:
            mesh_btn.setEnabled(False)
            mesh_btn.setStyleSheet(f"background: {CLR_BORDER}; color: {CLR_TEXT_DIM}; border: none; border-radius: 4px; font-size: 11px; font-weight: bold; padding: 4px 8px;")
        else:
            mesh_btn.clicked.connect(
                lambda _, r=row, sn=standard_name: self._run_mesh(r, sn)
            )
        self.table.setCellWidget(row, 6, mesh_btn)
        self.table.setRowHeight(row, 44)

        # Update footer
        count = self.table.rowCount()
        self.footer_label.setText(f"{count} component{'s' if count != 1 else ''} identified")

    def _on_name_changed(self, row, original_name, new_standard_name):
        """When user changes dropdown - rename body in SimLab."""
        if new_standard_name == "-- Select --":
            return
        try:
            from hwx import simlab
            # Get current name of body (may already be renamed)
            current_standard = None
            for std, orig in self.results.items():
                if orig == original_name:
                    current_standard = std
                    break

            if current_standard and current_standard != new_standard_name:
                simlab.execute(f'''<RenameBody CheckBox="ON"
                   UUID="78633e0d-3d2f-4e9a-b075-7bff122772d8">
  <SupportEntities><Entities>
    <Model>$Geometry</Model>
    <Body>"{current_standard}",</Body>
  </Entities></SupportEntities>
  <NewName Value="{new_standard_name}"/>
  <AllowDuplicate Value="0"/>
  <Output/>
 </RenameBody>''')
                # Update results dict
                del self.results[current_standard]
                self.results[new_standard_name] = original_name
                self.status_label.setText(
                    f"  Renamed '{current_standard}' -> '{new_standard_name}'"
                )
        except Exception as e:
            self.status_label.setText(f"  Error: {str(e)}")

    def _isolate_component(self, standard_name):
        """Isolate component in SimLab viewport."""
        try:
            from hwx import simlab
            # Try geometry model first, then mesh model
            all_models = simlab.getAllRootModelNames("all")
            for model in all_models:
                try:
                    simlab.showOrHideEntities([standard_name], "IsolateShow", model)
                    self.status_label.setText(f"  Isolating '{standard_name}' in viewport")
                    return
                except Exception:
                    continue
            self.status_label.setText(f"  Could not isolate '{standard_name}'")
        except Exception as e:
            self.status_label.setText(f"  Isolate error: {str(e)}")

    def _run_mesh(self, row, standard_name):
        """Run mesh script for the component."""
        mt_combo = self.table.cellWidget(row, 3)
        ms_edit  = self.table.cellWidget(row, 4)
        mesh_type = mt_combo.currentText() if mt_combo else "Tet4"
        mesh_size = float(ms_edit.text()) if ms_edit and ms_edit.text() else 4.0

        # Derive paths dynamically
        GUI_DIR     = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
        BASE_DIR    = os.path.dirname(GUI_DIR)
        SCRIPT_BASE = os.path.join(BASE_DIR, "MESHING")
        TEMP_DIR    = os.path.join(BASE_DIR, "TEMP")
        os.makedirs(TEMP_DIR, exist_ok=True)

        script_map = {
            "TOP_COVER":    os.path.join(SCRIPT_BASE, "mesh_top_cover_complete.py"),
            "OUTER_RACE":   os.path.join(SCRIPT_BASE, "mesh_races.py"),
            "OUTER_RACE_1": os.path.join(SCRIPT_BASE, "mesh_races.py"),
            "MID_RACE":     os.path.join(SCRIPT_BASE, "mesh_races.py"),
            "MID_RACE_1":   os.path.join(SCRIPT_BASE, "mesh_races.py"),
            "MID_RACE_2":   os.path.join(SCRIPT_BASE, "mesh_races.py"),
            "MID_RACE_3":   os.path.join(SCRIPT_BASE, "mesh_races.py"),
            "INNER_RACE":   os.path.join(SCRIPT_BASE, "mesh_races.py"),
            "INNER_RACE_1": os.path.join(SCRIPT_BASE, "mesh_races.py"),
            "SHAFT":        os.path.join(SCRIPT_BASE, "mesh_shaft.py"),
            "STATOR":       os.path.join(SCRIPT_BASE, "mesh_stator.py"),
            "ROTOR_RING":   os.path.join(SCRIPT_BASE, "mesh_rotor_ring.py"),
            "PCB_BRACKET":  os.path.join(SCRIPT_BASE, "mesh_pcb_bracket.py"),
            "DISPLAY_PCB":  os.path.join(SCRIPT_BASE, "mesh_display_pcb.py"),
            "BODY":         os.path.join(SCRIPT_BASE, "mesh_body.py"),
            "BOTTOM_COVER": os.path.join(SCRIPT_BASE, "mesh_bottom_cover.py"),
        }

        script_path = script_map.get(standard_name)
        if not script_path:
            self.status_label.setText(f"  No mesh script for '{standard_name}'")
            return

        self.status_label.setText(f"  Meshing {standard_name} ({mesh_type}, {mesh_size}mm)...")
        QApplication.processEvents()

        try:
            TEMP_FWD = TEMP_DIR.replace("\\", "/")
            with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
                script_code = f.read()
            # Replace hardcoded AREA_CSV paths
            script_code = script_code.replace(
                'C:/Users/PranavBhojane/Desktop/New_folder/SIMLAB_AUTOMATION/TEMP/shaft_area.csv',
                TEMP_FWD + '/shaft_area.csv'
            ).replace(
                'C:/Users/PranavBhojane/Desktop/New_folder/SIMLAB_AUTOMATION/TEMP/stator_area.csv',
                TEMP_FWD + '/stator_area.csv'
            )
            # Override mesh size and type
            import re as _re
            def _replace_val(code, var, val):
                import re as r
                return r.sub(var + r'\s*=\s*[0-9.]+', var + ' = ' + str(val), code)
            script_code = _replace_val(script_code, 'mesh_size', mesh_size)
            script_code = _replace_val(script_code, 'surf_mesh_size', mesh_size)
            script_code = _replace_val(script_code, 'vol_mesh_size', mesh_size)
            script_code = script_code.replace('mesh_type = "Tet4"', 'mesh_type = "' + mesh_type + '"')
            script_code = script_code.replace('mesh_type  = "Tet4"', 'mesh_type  = "' + mesh_type + '"')
            # Write to temp file and execute
            temp_script = os.path.join(TEMP_DIR, "temp_mesh.py")
            with open(temp_script, 'w', encoding='utf-8') as tf:
                tf.write(script_code)
            from hwx import simlab as _sl
            # For SHAFT use executeFile on actual script to preserve GUI context
            if standard_name == "SHAFT":
                _sl.executeFile(script_path)
            else:
                _sl.executeFile(temp_script)
            self.status_label.setText(f"  OK {standard_name} meshed successfully")
        except Exception as e:
            self.status_label.setText(f"  X Mesh error: {str(e)}")
            QMessageBox.critical(self, "Mesh Error", f"{standard_name} meshing failed:\n{str(e)}")

    def _mesh_selected_components(self):
        """Mesh all checked components in sequence."""
        for row in range(self.table.rowCount()):
            chk = self.table.cellWidget(row, 0)
            if chk and chk.isChecked():
                combo = self.table.cellWidget(row, 2)
                standard_name = combo.currentText() if combo else ""
                if standard_name and standard_name != "-- Select --":
                    self.status_label.setText(f"  Meshing {standard_name}...")
                    QApplication.processEvents()
                    self._run_mesh(row, standard_name)
        self.status_label.setText("  Mesh Selected complete")

    def _on_finished(self, results):
        self.results = results
        self.run_btn.setEnabled(True)
        self.run_btn.setText(">  Run Identification")
        self.status_label.setText(
            f"  OK Identification complete - {len(results)} components found"
        )

    def _on_error(self, error_msg):
        self.run_btn.setEnabled(True)
        self.run_btn.setText(">  Run Identification")
        self.status_label.setText(f"  X Error: {error_msg}")
        QMessageBox.critical(self, "Error", f"Identification failed:\n{error_msg}")


def launch_gui():
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    window = SimLabGUI()
    window.show()
    # Note: do NOT call app.exec_() - SimLab has its own Qt event loop


if __name__ == "__main__":
    launch_gui()
