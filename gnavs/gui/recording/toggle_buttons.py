import os


from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtWidgets import QDialog
from PyQt5 import QtCore
from qgis.PyQt.QtCore import QSettings, QTimer
from datetime import datetime


UI_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'toggle_buttons.ui'))

class ToggleButtons(QtWidgets.QWidget, UI_CLASS):

    change = QtCore.pyqtSignal(object)

    def __init__(self, interface, isNavigation=True):
        """Constructor."""

        QDialog.__init__(self, interface.mainWindow())
        self.setupUi(self)


        self.lfbPointButton.clicked.connect(self.pointButtonClicked)
        self.lfbNavigationButton.clicked.connect(self.navigationButtonClicked)

        self.updateButtons(isNavigation)

    def updateButtons(self, isNavigation):
        if isNavigation:
            self.lfbNavigationButton.setChecked(True)
            self.lfbPointButton.setChecked(False)
            self.lfbPointButton.setStyleSheet("background-color: rgb(255, 255, 255);padding: 5px;")
            self.lfbNavigationButton.setStyleSheet("background-color: green;padding: 5px;")
        else:
            self.lfbNavigationButton.setChecked(False)
            self.lfbPointButton.setChecked(True)
            self.lfbNavigationButton.setStyleSheet("background-color: rgb(255, 255, 255);padding: 5px;")
            self.lfbPointButton.setStyleSheet("background-color: green;padding: 5px;")


    def pointButtonClicked(self):
        self.updateButtons(False)
        self.change.emit('point')
    
    def navigationButtonClicked(self):
        self.updateButtons(True)
        self.change.emit('navigation')