
import os
import math

from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtWidgets import QDialog, QTableWidgetItem
from PyQt5 import QtCore

from ...utils.utils import Utils


UI_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'target.ui'))

class Target(QtWidgets.QWidget, UI_CLASS):
    """
    Target class.
    Sets up the target view, shows the selected target and updates distances and bearings.
    """

    def __init__(self, interface, targetElement=None):
        """Constructor."""

        QDialog.__init__(self, interface.mainWindow())
        self.setupUi(self)

        self.interface = interface
        self.targetElement = targetElement

        self.lfbTargetRemoveBtn.clicked.connect(self.removeTargetSelection)
        self.lfbTargetFokusBtn.clicked.connect(self.fokusToTarget)

        self.updateValues()
        self.updateAttributeTableView()

    def removeTargetSelection(self):
        """Deselect target"""
        Utils.deselectFeature(self.targetElement['layer'], self.targetElement['feature'])
    
    def fokusToTarget(self):
        """Center map to target"""
        Utils.centerFeature(self.targetElement['feature'])

    # Deprecated
    #def updateAttributesList(self):
    #    """Show/Update the list of feature attributes"""
    #
    #    feature = self.targetElement['feature']
    #    attrs = feature.attributes()
    #
    #    provider = self.targetElement['layer'].dataProvider()
    #    field_names = [field.name() for field in provider.fields()]
    #
    #    for i, attr in enumerate(attrs):
    #        label = QtWidgets.QLabel(field_names[i] + ': ' + str(attr))
    #        self.lfbAttributeLayout.addWidget(label)

    def updateAttributeTableView(self):
        """Show/Update the table of feature attributes"""
        feature = self.targetElement['feature']
        attrs = feature.attributes()

        provider = self.targetElement['layer'].dataProvider()
        field_names = [field.name() for field in provider.fields()]

        self.lfbAttributeTableWidget.horizontalHeader().setStretchLastSection(True)
        columns = len(field_names)
        self.lfbAttributeTableWidget.setColumnCount(columns)

        for i in range(columns):
            self.lfbAttributeTableWidget.setHorizontalHeaderItem(i, QTableWidgetItem(field_names[i]))

        

        for i, attr in enumerate(attrs):
            item = QTableWidgetItem(str(attr))
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.lfbAttributeTableWidget.setItem(0 , i, item)
    
    def updateValues(self):
        """Update the distance and bearing values"""

        if 'distance' in self.targetElement:
            #self.lfbTargetDetailsWidget.show()
            if self.targetElement['distance'] > 1000:
                self.lfbDistanceEdit.setText(str(round(self.targetElement['distance']/1000, 2)))
                self.lfbDistanceUnit.setText("km")
            elif self.targetElement['distance'] > 1:
                self.lfbDistanceEdit.setText(str(round(self.targetElement['distance'], 0)))
                self.lfbDistanceUnit.setText("m")
            else:
                self.lfbDistanceEdit.setText(str(round(self.targetElement['distance']*100, 0)))
                self.lfbDistanceUnit.setText("cm")
        else:
            #self.lfbTargetDetailsWidget.hide()
            self.lfbDistanceEdit.setText("-")
            self.lfbDistanceUnit.setText("km")


        degUnit = Utils.getSetting('degUnit', 'deg')
        if degUnit == 'deg':
            self.lfbBearingUnit.setText("°")
        elif  degUnit == 'gon':
            self.lfbBearingUnit.setText("gon")
        else:
            self.lfbBearingUnit.setText("rad")
        if 'bearing' in self.targetElement:
            degUnit = Utils.getSetting('degUnit', 'deg')

            rad = self.targetElement['bearing']

            deg = math.degrees(rad)
            deg = deg % 360

            gon = deg * 200 / 180 #self.targetElement['bearing'] * 200 / math.pi

            if degUnit == 'deg':
                self.lfbBearingEdit.setText(str(round(deg, 2)))
            elif  degUnit == 'gon':
                self.lfbBearingEdit.setText(str(round(gon, 2)))
            else:
                self.lfbBearingEdit.setText(str(round(rad, 2)))

            
        else:
            self.lfbBearingEdit.setText("-")
    