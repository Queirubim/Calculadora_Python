from PySide6.QtWidgets import QPushButton, QGridLayout
from math import pow
from PySide6.QtCore import Slot
from variables import MEDIUM_FONT_SIZE
from utils import isNumOrDot, isEmpty, isValid, convertToNumber
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from display import Display
    from info import Info
    from main_window import MainWindow


class Button(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configStyle()

    def configStyle(self):
        font = self.font()
        font.setPixelSize(MEDIUM_FONT_SIZE)
        self.setFont(font)
        self.setMinimumSize(75, 75)


class ButtonsGrid(QGridLayout):
    def __init__(
            self, display: 'Display', info: 'Info',
            window: 'MainWindow', *args, **kwargs
    ):
        super().__init__(*args, **kwargs)

        self._gridMask = [
            ['C', '◀', '^', '/'],
            ['7', '8', '9', '*'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['N',  '0', '.', '='],
        ]

        self.display = display
        self.info = info
        self.window = window
        self._equation = ''
        self._initEquation = 'Calc...'
        self._left = None
        self._op = None
        self._right = None

        self.equation = self._initEquation
        self. _makeGrid()

    @property
    def equation(self):
        return self._equation

    @equation.setter
    def equation(self, value):
        self._equation = value
        self.info.setText(value)

    def _makeGrid(self):
        self.display.enterPressed.connect(self._eq)
        self.display.delPressed.connect(self._backSpace)
        self.display.clearPressed.connect(self._clear)
        self.display.numberPressed.connect(self._insertToDisplay)
        self.display.operatorPressed.connect(self._operatorClicked)

        for rowNum, row in enumerate(self._gridMask):
            for colNum, buttonText in enumerate(row):
                button = Button(buttonText)

                if not isNumOrDot(buttonText) and not isEmpty(buttonText):
                    button.setProperty('cssClass', "specialButton")
                    self._configSpecialButton(button)

                text = button.text()
                self.addWidget(button, rowNum, colNum)
                slot = self._fakeSlot(self._insertToDisplay, text)

                self._connectedClicked(button, slot)

    def _connectedClicked(self, button, slot):
        button.clicked.connect(slot)

    def _configSpecialButton(self, button):
        text = button.text()

        if text == 'C':
            self._connectedClicked(button, self._clear)

        if text == '=':
            self._connectedClicked(button, self._eq)

        if text == '◀':
            slot = self._fakeSlot(self._backSpace)
            self._connectedClicked(button, slot)

        if text == 'N':
            slot = self._fakeSlot(self._invertNumber)
            self._connectedClicked(button, slot)

        if text in '+/-*^':
            self._connectedClicked(button, self._fakeSlot(
                self._operatorClicked, text))

    @Slot()
    def _backSpace(self):
        self.display.setFocus()
        if not (self.display.text() == ''):
            newText = self.display.text()[0:-1]
            self.display.setText(newText)
            return

        if not (self._op is None):
            self._op = None
            self.equation = self._initEquation
            self.display.setText(str(self._left))
            self._left = None

    @Slot()
    def _fakeSlot(self, func, *button, **buttonArgs):
        @Slot(bool)
        def realSlot():
            func(*button, **buttonArgs)
        return realSlot

    @Slot()
    def _insertToDisplay(self, text):
        newDisplayValue = self.display.text() + text
        self.display.setFocus()
        if not isValid(newDisplayValue):
            return
        self.display.insert(text)

    @Slot()
    def _clear(self):
        self._left = None
        self._op = None
        self._right = None
        self.info.setText(self._initEquation)
        self.display.clear()
        self.display.setFocus()

    @Slot()
    def _operatorClicked(self, text):
        buttonText = text
        displayText = self.display.text()
        self.display.clear()
        self.display.setFocus()

        if not isValid(displayText) and self._left is None:
            return

        if self._left is None:
            self._left = convertToNumber(displayText)

        self._op = buttonText
        self.equation = f'{self._left} {self._op} ??'

    @Slot()
    def _eq(self):
        displayText = self.display.text()
        result = 0.0
        self.display.setFocus()

        if not isValid(displayText):
            self._showInfo('invalid number')
            print('invalid number')
            return

        if self._left is None:
            return

        self.display.clear()
        self._right = convertToNumber(displayText)
        self.equation = f'{self._left}{self._op}{self._right}'

        try:
            if '^' in self.equation and self._left is not None:
                result = pow(self._left, self._right)
                result = convertToNumber(str(result))
            else:
                result = eval(self.equation)
        except ZeroDivisionError:
            self.info.setText("can't divide by zero")
            self._showError("can't divide by zero")
            return
        except OverflowError:
            self.info.setText('immense number')
            self._showError('immense number')
            return

        self.info.setText(f'{self._left}{self._op}{self._right}={result}')
        self._left = result
        self._right = None

    @Slot()
    def _invertNumber(self):
        self.display.setFocus()
        displayText = self.display.text()

        if not isValid(displayText):
            return

        number = convertToNumber(displayText) * -1
        self.display.setText(str(number))

    def _makeDialog(self, text):
        msgBox = self.window.makeMsgBox()
        msgBox.setText(text)
        return msgBox

    def _showError(self, text):
        msgBox = self._makeDialog(text)
        msgBox.setIcon(msgBox.Icon.Critical)
        msgBox.setWindowTitle('Error')
        msgBox.setStandardButtons(msgBox.StandardButton.Ok)
        result = msgBox.exec()
        if result == msgBox.StandardButton.Ok:
            self._clear()
        self.display.setFocus()

    def _showInfo(self, text):
        msgBox = self._makeDialog(text)
        msgBox.setWindowTitle('Information')
        msgBox.setIcon(msgBox.Icon.Information)
        msgBox.exec()
        self.display.setFocus()
