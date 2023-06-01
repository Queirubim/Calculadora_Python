from PySide6.QtWidgets import QVBoxLayout, QWidget, QMainWindow, QMessageBox


class MainWindow(QMainWindow):
    def __init__(self, parent: QWidget | None = None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        self.cw = QWidget()
        self.vLayout = QVBoxLayout()
        self.cw.setLayout(self.vLayout)

        self.setCentralWidget(self.cw)
        self.setWindowTitle('Calculadora')

    def adjustFixedSize(self) -> None:
        self.adjustSize()
        self.setFixedSize(self.width(), self.height())

    def addToVLayout(self, widget: QWidget) -> None:
        self.vLayout.addWidget(widget)

    def makeMsgBox(self):
        msgBox = QMessageBox(self)
        return msgBox
