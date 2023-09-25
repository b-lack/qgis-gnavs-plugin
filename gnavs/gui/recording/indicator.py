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

    def __init__(self, interface, width=100, height=100):
        """Constructor."""

        QDialog.__init__(self, interface.mainWindow())
        self.setupUi(self)

        self.lfbIndicatorFrame.setFixedSize(width, height)

        self.lfbHelpBtn.clicked.connect(self.getHelp)


    def getHelp(self):
        QgsMessageLog.logMessage('Help', 'gnavs')

    def stop(self, size):
        """Sets the size of the widget"""

        self.lfbIndicatorFrame.setStyleSheet("background-color:#ddd;")

    def setColor(self, gpsInfo):
        """Sets the color of the indicator"""
        color = self.getColor(gpsInfo)

        self.lfbIndicatorFrame.setStyleSheet("background-color: " + color + ";")

        return color

    def getAggregatedNote(self, gpsInfos):
        """Show a note about the aggregated precision of the measurement"""
        
        longitudeStDev = gpsInfos['longitudeStDev']
        latitudeStDev = gpsInfos['latitudeStDev']

        
        if gpsInfos is None or gpsInfos['pdop'] is None or gpsInfos['satellitesUsed'] is None:
            return True
        elif gpsInfos['pdop'] > 6 or gpsInfos['satellitesUsed'] < 6 or longitudeStDev > 0.00002 or latitudeStDev > 0.00002:
            return True

        return False
        
    def getColor(self, gpsInfo):
        """Returns the color of the indicator"""

        if gpsInfo is None or gpsInfo.latitude is None or gpsInfo.longitude is None:
            return 'red'
        elif str(gpsInfo.qualityIndicator) == 'GpsQualityIndicator.RTK' and gpsInfo.pdop < 2 and gpsInfo.satellitesUsed >= 10:
            return 'green'
        elif str(gpsInfo.qualityIndicator) == 'GpsQualityIndicator.FloatRTK' and gpsInfo.pdop < 6 and gpsInfo.satellitesUsed >= 6:
            return 'yellow'
        elif str(gpsInfo.qualityIndicator) == 'GpsQualityIndicator.GPS' and gpsInfo.pdop < 10 and gpsInfo.satellitesUsed >= 6:
            return 'orange'
        else:
            return 'red'