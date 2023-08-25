import os


from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtWidgets import QDialog
from PyQt5 import QtCore
from qgis.PyQt.QtCore import QSettings, QTimer
from datetime import datetime


UI_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'toggle_buttons.ui'))

class ToggleButtons(QtWidgets.QWidget, UI_CLASS):
    """
    ToggleButtons class.
    Styling of navigation buttons to toggle between the views.
    """

    change = QtCore.pyqtSignal(object)

    def __init__(self, interface, isNavigation='navigation'):
        """Constructor."""

        QDialog.__init__(self, interface.mainWindow())
        self.setupUi(self)

        self.lfbPointButton.clicked.connect(self.pointButtonClicked)
        self.lfbNavigationButton.clicked.connect(self.navigationButtonClicked)
        self.lfbSettingsButton.clicked.connect(self.settingsButtonClicked)
        
        self.unactiveStyle = "background-color: rgb(255, 255, 255);border: 1px solid green;padding: 5px;"
        self.activeStyle = "background-color: green;border: 1px solid green;padding: 5px;color: #fff;"

        self.updateButtons(isNavigation)

    def updateButtons(self, selected):
        """Update the buttons to show the selected one"""

        if selected == 'navigation':
            self.lfbNavigationButton.setChecked(True)
            self.lfbPointButton.setChecked(False)
            self.lfbPointButton.setStyleSheet(self.unactiveStyle)
            self.lfbNavigationButton.setStyleSheet(self.activeStyle)
            self.lfbSettingsButton.setStyleSheet(self.unactiveStyle)
        elif selected == 'point':
            self.lfbNavigationButton.setChecked(False)
            self.lfbPointButton.setChecked(True)
            self.lfbNavigationButton.setStyleSheet(self.unactiveStyle)
            self.lfbPointButton.setStyleSheet(self.activeStyle)
            self.lfbSettingsButton.setStyleSheet(self.unactiveStyle)
        else :
            self.lfbNavigationButton.setChecked(False)
            self.lfbPointButton.setChecked(False)
            self.lfbNavigationButton.setStyleSheet(self.unactiveStyle)
            self.lfbPointButton.setStyleSheet(self.unactiveStyle)
            self.lfbSettingsButton.setStyleSheet(self.activeStyle)

    def settingsButtonClicked(self):
        """Emit the change signal and update the button"""
        
        self.updateButtons('settings')
        self.change.emit('settings')

    def pointButtonClicked(self):
        """Emit the change signal and update the button"""
        
        self.updateButtons('point')
        self.change.emit('point')
    
    def navigationButtonClicked(self):
        """Emit the change signal and update the button"""

        self.updateButtons('navigation')
        self.change.emit('navigation')