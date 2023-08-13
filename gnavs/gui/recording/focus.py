import os


from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtWidgets import QDialog
from PyQt5 import QtCore
from qgis.PyQt.QtCore import QSettings, QTimer
from datetime import datetime
from qgis.core import QgsMessageLog


UI_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'focus.ui'))

class Focus(QtWidgets.QWidget, UI_CLASS):

    toggleFocus = QtCore.pyqtSignal(bool)
    focus = QtCore.pyqtSignal()

    def __init__(self, interface):
        """Constructor."""

        QDialog.__init__(self, interface.mainWindow())
        self.setupUi(self)

        self.interface = interface

        self.lfbFollowRadioBtn.toggled.connect(self.toggleTheFocus)
        self.lfbFollowQuickBtn.clicked.connect(self.focusQuick)

    def focusQuick(self):
        self.focus.emit()


    def toggleTheFocus(self, isNavigation):
       self.toggleFocus.emit(isNavigation)