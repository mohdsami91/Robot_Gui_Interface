## Fullscreen & Kiosk Mode Setup ##

from PyQt5 import QtWidgets, QtCore
import sys

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # Removes minimize/maximize buttons
        self.showFullScreen()  # Forces full screen
        self.setCursor(QtCore.Qt.BlankCursor)  # (Optional) Hide cursor for clean UI

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
