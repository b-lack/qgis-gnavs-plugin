
import os

from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtWidgets import QDialog
from PyQt5 import QtCore
from qgis.PyQt.QtCore import QSettings

from qgis.core import QgsProject, QgsSettings, QgsWkbTypes, QgsMessageLog, QgsGpsDetector, QgsGpsConnection, QgsNmeaConnection
from qgis.gui import QgsMapCanvas

from ...utils.utils import Utils

from ..recording.recording import Recording
from ..navigate.selection import Selection
from ..measurement.aggregation import Aggregation
from ..recording.toggle_buttons import ToggleButtons
from ..recording.focus import Focus


UI_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'setup.ui'))

class Setup(QtWidgets.QWidget, UI_CLASS):

    measurementCountChanged = QtCore.pyqtSignal(int)
    qualityChanged = QtCore.pyqtSignal(int)

    def __init__(self, interface, bestCount=5):
        """Constructor."""

        QDialog.__init__(self, interface.mainWindow())
        self.setupUi(self)

        self.interface = interface
        self.toggleState = 'navigation'
        self.state = 'navigation'

        self.rec = self.addRecording()
        self.followBtn = self.addFocus()
        
        self.measurement = self.addMeasurement()
        self.selection = self.addNavigation()
        #self.toggleButtons = self.addToggleButtons()


        QgsProject.instance().layersAdded.connect( self.updateLayers )
        self.updateView()

    def __del__(self):
        del self.rec


    def stateChanged(self, state):
        self.state = state
        if state == 'point':
            self.measurement.hide()

    def updateLayers(self):
        if self.selection is not None:
            self.selection.updateToC()

            #Utils.layersToTop(['lfb-tmp-position', 'lfb-tmp-distance'])
            

    def stopTracking(self):
        self.rec.cancelConnection()

    def coordinatesChanged(self, gpsInfo):
        if self.toggleState == 'navigation' and self.selection is not None:
            self.selection.updateCoordinates(gpsInfo)

    def aggregatedValuesChanged(self, gpsInfos):
        self.measurementCountChanged.emit(len(gpsInfos))

        if self.toggleState == 'point' and len(gpsInfos) > 0:
            self.measurement.updateAggregatedValues(gpsInfos)

        

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

    #def addToggleButtons(self):
    #    toggleButtons = ToggleButtons(self.interface)
    #    toggleButtons.change.connect(self.toggleButtonsChanged)
    #    self.lfbSetup.insertWidget(0, toggleButtons)
    #    return toggleButtons


    def addRecording(self):
        rec = Recording(self.interface)
        rec.currentPositionChanged.connect(self.coordinatesChanged)
        rec.aggregatedValuesChanged.connect(self.aggregatedValuesChanged)
        self.lfbSetup.addWidget(rec)
        return rec
    
    def addFocus(self):
        focus = Focus(self.interface)
        focus.focus.connect(self.rec.focusQuick)
        focus.toggleFocus.connect(self.rec.toggleFocus)
        self.lfbSetup.addWidget(focus)
        return focus

    def addMeasurement(self):
        selection = Aggregation(self.interface)
        self.lfbSetup.addWidget(selection)
        #selection.addToMap.connect(self.addDataToMap)
        return selection

    def addNavigation(self):
        selection = Selection(self.interface)
        self.lfbSetup.addWidget(selection)
        return selection
    
    def addDataToMap(self):
        self.stopTracking()
        self.measurement.emitData()


    #def addDataToMap(self, aggregatedValues, gpsInfos):
    #    self.stopTracking()
    #    Utils.addPointToLayer('lfb-gnavs-aggregated', aggregatedValues, gpsInfos)

    
