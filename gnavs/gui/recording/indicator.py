import os


from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtWidgets import QDialog
from PyQt5 import QtCore
from qgis.PyQt.QtCore import QSettings, QTimer
from datetime import datetime
from qgis.core import QgsMessageLog


UI_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'indicator.ui'))

# TODO: Not implemented yet

class Indicator(QtWidgets.QWidget, UI_CLASS):
    """
    Indicator class.
    Sets up a colored indicator view, shows the current GPS coordinates and accuracy.
    """

    toggleFocus = QtCore.pyqtSignal(bool)
    focus = QtCore.pyqtSignal()

    def __init__(self, interface):
        """Constructor."""

        QDialog.__init__(self, interface.mainWindow())
        self.setupUi(self)

    def getColor(self, gpsInfo):
        """Returns the color of the indicator"""

        if gpsInfo is None or gpsInfo.latitude is None or gpsInfo.longitude is None:
            return 'red'

        if gpsInfo.accuracy < 10:
            return 'green'
        elif gpsInfo.accuracy < 20:
            return 'yellow'
        else:
            return 'red'