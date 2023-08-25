import os


from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtWidgets import QDialog
from PyQt5 import QtCore


UI_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'focus.ui'))

class Focus(QtWidgets.QWidget, UI_CLASS):
    """
    Focus class.
    Sets up buttons to follow GPS coordinates or one time center map.
    """

    toggleFocus = QtCore.pyqtSignal(bool)
    focus = QtCore.pyqtSignal()

    def __init__(self, interface):
        """Constructor."""

        QDialog.__init__(self, interface.mainWindow())
        self.setupUi(self)

        self.interface = interface

        self.lfbFollowRadioBtn.toggled.connect(self.toggleTheFocus)
        self.lfbFollowQuickBtn.clicked.connect(self.focusQuick)
        self.lfbFollowQuickBtn.hide()

    def focusQuick(self):
        """Focus the map to the current GPS coordinates"""
        self.focus.emit()


    def toggleTheFocus(self, isNavigation):
        """Toggle the focus mode"""
        self.toggleFocus.emit(isNavigation)