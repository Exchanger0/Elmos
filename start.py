import sys
from PyQt5.QtWidgets import QApplication
from ui import MainWindow

app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec()
