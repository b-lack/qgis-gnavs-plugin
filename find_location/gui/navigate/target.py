
import os
import math

from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtWidgets import QDialog
from PyQt5 import QtCore
from qgis.PyQt.QtCore import QSettings

from qgis.core import QgsSettings, QgsApplication, QgsMessageLog, QgsGpsDetector, QgsGpsConnection, QgsNmeaConnection

from ...utils.utils import Utils


UI_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'target.ui'))

class Target(QtWidgets.QWidget, UI_CLASS):

    def __init__(self, interface, targetElement=None):
        """Constructor."""

        QDialog.__init__(self, interface.mainWindow())
        self.setupUi(self)

        self.interface = interface
        self.targetElement = targetElement

        self.updateValues()
        

    
    def updateValues(self):
        if 'distance' in self.targetElement:
            if self.targetElement['distance'] > 1000:
                self.lfbDistanceEdit.setText(str(round(self.targetElement['distance']/1000, 2)))
                self.lfbDistanceUnit.setText("km")
            else:
                self.lfbDistanceEdit.setText(str(round(self.targetElement['distance'], 0)))
                self.lfbDistanceUnit.setText("m")
        if 'bearing' in self.targetElement:
            deg = math.degrees(self.targetElement['bearing'])
            deg = deg % 360
            QgsMessageLog.logMessage(str(deg), 'LFB')
            gon = deg * 200 / 180 #self.targetElement['bearing'] * 200 / math.pi
            self.lfbBearingEdit.setText(str(round(gon)))
            self.lfbBearingUnit.setText("gon")
    