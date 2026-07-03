exec(open(r'C:\Users\PranavBhojane\Desktop\New_folder\SIMLAB_AUTOMATION\FINALIZED_GUI_MESH\SIMLAB_AUTOMATION\GUI_SCRIPT\simlab_gui.py').read())

from PyQt5.QtWidgets import QApplication
import sys

app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

window = SimLabGUI()
window.show()