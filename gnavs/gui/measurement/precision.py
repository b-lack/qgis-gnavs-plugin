
import os
import json
import statistics
import time


from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtWidgets import QDialog
from PyQt5 import QtCore

from qgis.core import QgsMessageLog

from ..recording.indicator import Indicator
from ...utils.utils import Utils


UI_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'precision.ui'))

class PrecisionNote(QtWidgets.QWidget, UI_CLASS):
    """
    PrecisionNote class.
    Shows a dialog with a note about the precision of the measurement.
    """

    addToMap = QtCore.pyqtSignal(object, list)

    def __init__(self, interface):
        """Constructor."""

        _translate = QtCore.QCoreApplication.translate

        QDialog.__init__(self, interface.mainWindow())
        self.setupUi(self)

        self.indicator = Indicator(interface, 25, 25)
        self.lfbPrecition.insertWidget(0, self.indicator)

        self.lfbShowPrecitionBad.hide()
        self.lfbShowPrecitionGood.hide()

        
        self.lfbShowPrecitionBad.setText(_translate("Form", "qualityNoteBad"))
        #self.lfbShowPrecitionGoodsetText(self._translate("Form", "qualityNoteGood"))

        self.hide()

    def hideGroup(self):
        """Hides the group"""
        QgsMessageLog.logMessage('Hide precision note', 'gnavs')

        self.hide()

    def updateIndicator(self, gpsInfo):
        """Updates the color indicator"""

        self.indicator.setColor(gpsInfo)

    def update(self, gpsInfos):
        self.show()
        """Updates the note indicator"""
        showNote = self.indicator.getAggregatedNote(gpsInfos)

        if showNote:
            self.lfbShowPrecitionBad.show()
            #self.lfbShowPrecitionGood.hide()
        else:
            self.lfbShowPrecitionBad.hide()
            #self.lfbShowPrecitionGood.show()