
import os

from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtWidgets import QDialog
from PyQt5 import QtCore

from qgis.core import QgsProject

from ..recording.recording import Recording
from ..navigate.selection import Selection
from ..measurement.aggregation import Aggregation
from ..recording.focus import Focus

from qgis.core import QgsMessageLog

from ..measurement.precision import PrecisionNote

from ..recording.indicator import Indicator


UI_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'setup.ui'))

class Setup(QtWidgets.QWidget, UI_CLASS):
    """
    Setup class.
    Sets up the Navigation and Point-Recording view.
    """

    measurementCountChanged = QtCore.pyqtSignal(int)
    qualityChanged = QtCore.pyqtSignal(int)

    def __init__(self, interface):
        """Constructor."""

        QDialog.__init__(self, interface.mainWindow())
        self.setupUi(self)

        self.interface = interface
        self.toggleState = 'navigation'
        self.state = 'navigation'

        self.rec = self.addRecording()
        self.followBtn = self.addFocus()

        self.precisionNote = self.addPrecisionNote()
        
        self.measurement = self.addMeasurement()
        self.selection = self.addNavigation()

        # Temporary
        #self.addIndicator()

        QgsProject.instance().layersAdded.connect( self.updateLayers ) # on toc change
        self.updateView()

    def __del__(self):
        del self.rec

    def stopTracking(self):
        """Stop the GPS tracking"""
        self.rec.cancelConnection(True)
        

    #def stateChanged(self, state):
    #    self.state = state
    #    if state == 'point':
    #        self.measurement.hide()

    def updateLayers(self):
        """Update one layer to the top of the layer list"""
        # TODO: Put Layer to top of the layer list

        if self.selection is not None:
            self.selection.updateToC()

            #Utils.layersToTop(['lfb-tmp-position', 'lfb-tmp-distance'])
        

    def coordinatesChanged(self, gpsInfo):
        """Update target point distance and bearing"""

        #self.indicator.setColor(gpsInfo)

        #if self.toggleState == 'navigation' and self.selection is not None:
        self.selection.updateCoordinates(gpsInfo, self.toggleState)

        if self.toggleState == 'point':
            self.precisionNote.updateIndicator(gpsInfo)

    def aggregatedValuesChanged(self, gpsInfos):
        """Update the aggregated values"""

        self.measurementCountChanged.emit(len(gpsInfos))

        if self.toggleState == 'point' and len(gpsInfos) > 0:
            aggregated = self.measurement.updateAggregatedValues(gpsInfos)
            self.precisionNote.update(aggregated)

    def toggleButtonsChanged(self, toggleButtons):
        """Toggle between the navigation and point-recording view"""

        self.toggleState = toggleButtons
        self.rec.toggleButtonsChanged(toggleButtons)
        self.updateView()
        
    def updateView(self):
        """Toggle between the navigation and point-recording view"""

        if self.toggleState == 'navigation':
            self.selection.show()
            self.measurement.hide()
            self.precisionNote.hide()
        else:
            self.selection.hide()
            self.measurement.show()
            self.precisionNote.show()

        self.measurement.refreshSettings()
        self.rec.refreshSettings()
        # self.rec.toggleButtonsChanged(self.toggleState) - Deprecated

    def recordingStateChanged(self, state):
        """Update the recording state"""

        if state == False:
            self.selection.stopRecording()
            self.precisionNote.hideGroup()
            #self.indicator.stop()

    def addRecording(self):
        """Add the GPS-recording view"""

        rec = Recording(self.interface)
        rec.currentPositionChanged.connect(self.coordinatesChanged)
        rec.aggregatedValuesChanged.connect(self.aggregatedValuesChanged)

        rec.recordingStateChanged.connect(self.recordingStateChanged)

        self.lfbSetup.addWidget(rec)
        return rec
    
    def addPrecisionNote(self):
        """Add the precision note view"""

        precisionNote = PrecisionNote(self.interface)
        self.lfbSetup.addWidget(precisionNote)
        return precisionNote
    
    def addFocus(self):
        """Add the center map view"""

        focus = Focus(self.interface)
        focus.focus.connect(self.rec.setFocus)
        focus.toggleFocus.connect(self.rec.toggleFocus)
        self.lfbSetup.addWidget(focus)
        return focus

    def addMeasurement(self):
        """Add the aggregation view"""

        selection = Aggregation(self.interface)
        self.lfbSetup.addWidget(selection)
        return selection

    def addNavigation(self):
        """Add the target Point slection view"""

        selection = Selection(self.interface)
        self.lfbSetup.addWidget(selection)

        return selection
    
    def addDataToMap(self):
        """Cancle Recording and add the recorded points to the map"""
    
        self.stopTracking()
        self.measurement.emitData()

    def addIndicator(self):
        """Add the quality indicator"""
        self.indicator = Indicator(self.interface)
        self.lfbSetup.addWidget(self.indicator)

    
