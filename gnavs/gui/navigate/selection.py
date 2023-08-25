
import os

from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtWidgets import QDialog
from PyQt5 import QtCore
from PyQt5.QtWidgets import QTableWidgetItem


from qgis.core import  QgsWkbTypes, QgsMessageLog, QgsPoint, QgsPointXY

from ...utils.utils import Utils
from .target import Target


UI_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'selection.ui'))

class Selection(QtWidgets.QWidget, UI_CLASS):
    """
    Selection class.
    Sets up the selection view, shows selected features and updates distances and bearings.
    """

    def __init__(self, interface, selectedFeature=None):
        """Constructor."""

        QDialog.__init__(self, interface.mainWindow())
        self.setupUi(self)

        self.selectedFeatures = []
        self.gpsInfo = None
        self.targets = None
        self.interface = interface

        self.updateToC()

    def updateToC(self):
        """Update the Table of Contents"""

        layers = Utils.selectLayerByType(QgsWkbTypes.PointGeometry)

        for layer in layers:

            try:
                layer.selectionChanged.disconnect(self.layerSelectionChanged)
            except:
                pass

            layer.selectionChanged.connect(self.layerSelectionChanged)

        self.layerSelectionChanged()


    def updateCoordinates(self, gpsInfo):
        """Update the GPS coordinates and list of targets selected by the user"""

        if gpsInfo is None or gpsInfo.latitude is None or gpsInfo.longitude is None:
            return
        
        self.gpsInfo = gpsInfo

        self.targets = self.createTargetList()

        position = QgsPointXY(QgsPoint(self.gpsInfo.longitude, self.gpsInfo.latitude))
        Utils.clearLayer('lfb-tmp-position', 'point')
        Utils.drawPosition('lfb-tmp-position', position)

        self.updateSelectionTargets()

    def createTargetList(self):
        """Create a list of targets selected by the user"""
        targets = []

        
        if self.gpsInfo is not None and self.gpsInfo.latitude is not None and self.gpsInfo.longitude is not None:
            
            endXY = QgsPointXY(QgsPoint(self.gpsInfo.longitude, self.gpsInfo.latitude))

            for element in self.selectedFeatures:
                geom = element['feature'].geometry()
                startXY = QgsPointXY(geom.asPoint())
                if startXY == endXY: 
                    continue
                
                target = {
                    'id': element['feature'].id(),
                    'feature': element['feature'],
                    'layer': element['layer'],
                    'startPoint': startXY,
                    'endPoint': endXY,
                    'distance': Utils.distanceFromPoints(startXY, endXY ),
                    'bearing':  Utils.bearingFromPoints(endXY, startXY )
                }
                targets.append(target)

            targets.sort(key=lambda x: x['distance'], reverse=False)

        return targets
    
    def updateSelectionTargets(self):
        """Update the list of targets selected by the user"""

        while self.lfbSelectedTargets.count():
            child = self.lfbSelectedTargets.takeAt(0)
            if child.widget():
                child.widget().deleteLater()


        Utils.clearLayer('lfb-tmp-distance', 'linestring')
        
        if  self.targets is not None and len(self.targets) > 0:
            for targetElement in self.targets:
                target = Target(self.interface, targetElement)
                self.lfbSelectedTargets.addWidget(target)
                Utils.drawDistance('lfb-tmp-distance',targetElement['startPoint'], targetElement['endPoint'])
                
        else:
            for element in self.selectedFeatures:
                target = Target(self.interface, {
                    'id': element['feature'].id(),
                    'feature': element['feature'],
                    'layer': element['layer'],
                })
                self.lfbSelectedTargets.addWidget(target)

        

    def updateSelectionLabel(self):
        """Update the label showing the number of selected features"""

        _translate = QtCore.QCoreApplication.translate

        if len(self.selectedFeatures) == 0:
            self.lfbSelectionGroup.setTitle(_translate("Form", "Keine Ziel ausgewählt"))
        if len(self.selectedFeatures) == 1:
            self.lfbSelectionGroup.setTitle(str(len(self.selectedFeatures)) + _translate("Form", "Ziel ausgewählt"))
        else:
            self.lfbSelectionGroup.setTitle(str(len(self.selectedFeatures)) + _translate("Form", "Ziele ausgewählt"))

        self.targets = self.createTargetList()
        self.updateSelectionTargets()

    def layerSelectionChanged(self, selected=[''], deselected=[]):
        """Update the list of selected features"""

        self.selectedFeatures = Utils.getSelectedFeaturesFromAllLayers(QgsWkbTypes.PointGeometry)

        self.updateSelectionLabel()
    