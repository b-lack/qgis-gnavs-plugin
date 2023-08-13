import os


from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtWidgets import QDialog
from PyQt5 import QtCore
from qgis.PyQt.QtCore import QSettings, QTimer
from datetime import datetime


UI_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'toggle_buttons.ui'))

class ToggleButtons(QtWidgets.QWidget, UI_CLASS):

    change = QtCore.pyqtSignal(object)

    def __init__(self, interface, isNavigation='navigation'):
        """Constructor."""

        QDialog.__init__(self, interface.mainWindow())
        self.setupUi(self)


        self.lfbPointButton.clicked.connect(self.pointButtonClicked)
        self.lfbNavigationButton.clicked.connect(self.navigationButtonClicked)
        self.lfbSettingsButton.clicked.connect(self.settingsButtonClicked)

        self.updateButtons(isNavigation)

    def updateButtons(self, selected):
        if selected == 'navigation':
            self.lfbNavigationButton.setChecked(True)
            self.lfbPointButton.setChecked(False)
            self.lfbPointButton.setStyleSheet("background-color: rgb(255, 255, 255);padding: 5px;")
            self.lfbNavigationButton.setStyleSheet("background-color: green;padding: 5px;")
        elif selected == 'point':
            self.lfbNavigationButton.setChecked(False)
            self.lfbPointButton.setChecked(True)
            self.lfbNavigationButton.setStyleSheet("background-color: rgb(255, 255, 255);padding: 5px;")
            self.lfbPointButton.setStyleSheet("background-color: green;padding: 5px;")
        else :
            self.lfbNavigationButton.setChecked(False)
            self.lfbPointButton.setChecked(False)
            self.lfbNavigationButton.setStyleSheet("background-color: rgb(255, 255, 255);padding: 5px;")
            self.lfbPointButton.setStyleSheet("background-color: rgb(255, 255, 255);padding: 5px;")

    def settingsButtonClicked(self):
        self.updateButtons('settings')
        self.change.emit('settings')

    def pointButtonClicked(self):
        self.updateButtons('point')
        self.change.emit('point')
    
    def navigationButtonClicked(self):
        self.updateButtons('navigation')
        self.change.emit('navigation')