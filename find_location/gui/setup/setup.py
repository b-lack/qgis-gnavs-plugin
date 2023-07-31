
import os

from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtWidgets import QDialog
from PyQt5 import QtCore
from qgis.PyQt.QtCore import QSettings

from qgis.core import QgsSettings, QgsWkbTypes, QgsMessageLog, QgsGpsDetector, QgsGpsConnection, QgsNmeaConnection

import pandas as pd

from ...utils.utils import Utils

from ..recording.recording import Recording
from ..navigate.selection import Selection


UI_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'setup.ui'))

PLUGIN_NAME = "find_location"

class Setup(QtWidgets.QWidget, UI_CLASS):

    inputChanged = QtCore.pyqtSignal(object)

    def __init__(self, interface, bestCount=5):
        """Constructor."""

        QDialog.__init__(self, interface.mainWindow())
        self.setupUi(self)

        self.interface = interface

        self.addRecording()
        self.addNavigation()

    def coordinatesChanged(self, gpsInfo):
        if self.selection is not None:
            self.selection.updateCoordinates(gpsInfo)

    def addRecording(self):
        rec = Recording(self.interface)
        rec.currentPositionChanged.connect(self.coordinatesChanged)
        self.lfbSetup.addWidget(rec)

    def addNavigation(self):
        self.selection = Selection(self.interface)
        self.lfbSetup.addWidget(self.selection)