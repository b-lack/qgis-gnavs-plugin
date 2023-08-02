
import os
import math

from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtWidgets import QDialog, QScroller
from PyQt5 import QtCore

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

        scroll = QScroller.scroller(self.lfbAttributesLine.viewport())
        scroll.grabGesture(self.lfbAttributesLine.viewport(), QScroller.LeftMouseButtonGesture)

        self.lfbTargetRemoveBtn.clicked.connect(self.removeTargetSelection)
        self.lfbTargetFokusBtn.clicked.connect(self.fokusToTarget)


        self.updateValues()
        self.updateAttributesList()

    def removeTargetSelection(self):
        Utils.deselectFeature(self.targetElement['layer'], self.targetElement['feature'])
    
    def fokusToTarget(self):
        Utils.centerFeature(self.targetElement['feature'])


    def updateAttributesList(self):
        feature = self.targetElement['feature']
        attrs = feature.attributes()

        provider = self.targetElement['layer'].dataProvider()
        field_names = [field.name() for field in provider.fields()]

        for i, attr in enumerate(attrs):
            label = QtWidgets.QLabel(field_names[i] + ': ' + str(attr))
            self.lfbAttributeLayout.addWidget(label)
    
    def updateValues(self):

        if 'distance' in self.targetElement:
            self.lfbDistanceLayout_2.show()
            if self.targetElement['distance'] > 1000:
                self.lfbDistanceEdit.setText(str(round(self.targetElement['distance']/1000, 2)))
                self.lfbDistanceUnit.setText("km")
            else:
                self.lfbDistanceEdit.setText(str(round(self.targetElement['distance'], 0)))
                self.lfbDistanceUnit.setText("m")
        else:
            self.lfbDistanceLayout_2.hide()
            self.lfbDistanceEdit.setText("")
            self.lfbDistanceUnit.setText("")

        if 'bearing' in self.targetElement:
            self.lfbBearingLayout.show()
            deg = math.degrees(self.targetElement['bearing'])
            deg = deg % 360

            gon = deg * 200 / 180 #self.targetElement['bearing'] * 200 / math.pi
            self.lfbBearingEdit.setText(str(round(gon)))
            self.lfbBearingUnit.setText("gon")
        else:
            self.lfbBearingLayout.hide()
            self.lfbBearingEdit.setText("")
            self.lfbBearingUnit.setText("")
    