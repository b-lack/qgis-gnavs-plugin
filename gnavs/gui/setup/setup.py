
import os

from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtWidgets import QDialog
from PyQt5 import QtCore
from qgis.PyQt.QtCore import QSettings

from qgis.core import QgsSettings, QgsWkbTypes, QgsMessageLog, QgsGpsDetector, QgsGpsConnection, QgsNmeaConnection


from ...utils.utils import Utils

from ..recording.recording import Recording
from ..navigate.selection import Selection
from ..measurement.aggregation import Aggregation
from ..recording.toggle_buttons import ToggleButtons


UI_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'setup.ui'))

class Setup(QtWidgets.QWidget, UI_CLASS):


    def __init__(self, interface, bestCount=5):
        """Constructor."""

        QDialog.__init__(self, interface.mainWindow())
        self.setupUi(self)

        self.interface = interface
        self.toggleState == 'navigation'
        self.updateView()

        self.rec = self.addRecording()
        self.addToggleButtons()
        self.measurement = self.addMeasurement()
        self.selection = self.addNavigation()

    def __del__(self):
        del self.rec

    def stopTracking(self):
        self.rec.cancelConnection()

    def coordinatesChanged(self, gpsInfo):
        if self.selection is not None:
            self.selection.updateCoordinates(gpsInfo)

    def aggregatedValuesChanged(self, gpsInfos):
        self.measurement.updateAggregatedValues(gpsInfos)
        pass


    def toggleButtonsChanged(self, toggleButtons):
        self.toggleState = toggleButtons
        self.updateView()
        
    def updateView(self):
        if self.toggleState == 'navigation':
            self.selection.show()
            self.measurement.hide()
        else:
            self.selection.hide()
            self.measurement.show()

        self.rec.toggleButtonsChanged(self.toggleState)

    def addToggleButtons(self):
        self.toggleButtons = ToggleButtons(self.interface)
        self.toggleButtons.change.connect(self.toggleButtonsChanged)
        self.lfbSetup.insertWidget(0, self.toggleButtons)

    def addRecording(self):
        rec = Recording(self.interface)
        rec.currentPositionChanged.connect(self.coordinatesChanged)
        rec.aggregatedValuesChanged.connect(self.aggregatedValuesChanged)
        self.lfbSetup.addWidget(rec)
        return rec
    
    def addMeasurement(self):
        selection = Aggregation(self.interface)
        self.lfbSetup.addWidget(selection)
        selection.addToMap.connect(self.addDataToMap)
        return selection

    def addNavigation(self):
        selection = Selection(self.interface)
        self.lfbSetup.addWidget(selection)
        return selection
    
    def addDataToMap(self, aggregatedValues, gpsInfos):
        self.stopTracking()

        Utils.addPointToLayer('lfb-gnavs-aggregated', aggregatedValues, gpsInfos)

    
