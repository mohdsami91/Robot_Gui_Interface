from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import sys

class GlowingButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._animation = QVariantAnimation()
        self._animation.setStartValue(0.00001)
        self._animation.setEndValue(0.9999)
        self._animation.valueChanged.connect(self._animate)
        self._animation.setDuration(500)
        
        self.color1 = QColor(37, 150, 190)  # Blue
        self.color2 = QColor(85, 255, 255)   # Cyan
        
        # Set initial style
        self.setStyleSheet("""
            QPushButton {
                border-style: solid;
                border-radius: 5px;
                border-width: 2px;
                color: white;
                padding: 5px;
                min-height: 40px;
                background-color: #2596be;
            }
        """)

    def enterEvent(self, event):
        self._animation.setDirection(QAbstractAnimation.Forward)
        self._animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animation.setDirection(QAbstractAnimation.Backward)
        self._animation.start()
        super().leaveEvent(event)

    def _animate(self, value):
        qss = """
            QPushButton {
                border-style: solid;
                border-radius: 5px;
                border-width: 2px;
                color: white;
                padding: 5px;
                min-height: 40px;
            }
        """
        
        grad = f"background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 {self.color1.name()}, stop:{value} {self.color2.name()}, stop:1.0 {self.color1.name()});"
        
        border_style = f"""
            border-top-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.466, stop:{value} {self.color1.name()}, stop:1 {self.color2.name()});
            border-bottom-color: qlineargradient(spread:pad, x1:1, y1:0.5, x2:0, y2:0.5, stop:{value} {self.color1.name()}, stop:1 {self.color2.name()});
            border-right-color: qlineargradient(spread:pad, x1:0.5, y1:0, x2:0.5, y2:1, stop:{value} {self.color1.name()}, stop:1 {self.color2.name()});
            border-left-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:{value} {self.color1.name()}, stop:1 {self.color2.name()});
        """
        
        self.setStyleSheet(qss + grad + border_style)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Glowing Buttons Demo")
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add some glowing buttons
        button1 = GlowingButton("Glowing Button 1")
        button2 = GlowingButton("Glowing Button 2")
        button3 = GlowingButton("Glowing Button 3")
        
        layout.addWidget(button1)
        layout.addWidget(button2)
        layout.addWidget(button3)
        
        # Add some spacing
        layout.addStretch()
        
        # Set window size
        self.setMinimumSize(300, 200)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())