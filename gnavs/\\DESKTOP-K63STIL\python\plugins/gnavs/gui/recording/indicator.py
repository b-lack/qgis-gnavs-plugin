import os


from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from PyQt5 import QtCore
from qgis.PyQt.QtCore import QSettings, QTimer
from datetime import datetime



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
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)

        msgBox.setWindowTitle("Precision Indicator States")
        msgBox.setTextFormat(QtCore.Qt.RichText)
        msgBox.setText('''
                        <p>
                            The colored box shows the precision state of the current GPS signal.
                            The following states are possible:
                        </p>
                        <hr/>
                        <p style="width:30px;height:30px; background-color:green; color:green">I</p>
                        <ul>
                            <li>Quality Indicator: RTK (Fixed)</li>
                            <li>Pdop: &lt; 2</li>
                            <li>Satellites used: &gt; 10</li>
                        </ul>
                        <hr/>
                        <br/>
                        <p style="width:30px;height:30px; background-color:yellow; color:yellow">I</p>
                        <ul>
                            <li>Quality Indicator: RTK (Float)</li>
                            <li>Pdop: &lt; 6</li>
                            <li>Satellites used: &gt; 6</li>
                        </ul>
                        <br/>
                        <p style="width:30px;height:30px; background-color:orange; color:orange">I</p>
                        <ul>
                            <li>Quality Indicator: GPS</li>
                            <li>Pdop: &lt; 10</li>
                            <li>Satellites used: &gt; 4</li>
                        </ul>
                        <br/>
                        <p style="width:30px;height:30px; background-color:red; color:red">I</p>
                        <p style="text-align:center;">none of the above</p>
                        <br/>
                        <p style="width:30px;height:30px; background-color:grey; color:grey">I</p>
                        <p style="text-align:center;">not active</p>
                    ''')


        msgBox.exec()


    def stop(self):
        """Sets the size of the widget"""

        self.lfbIndicatorFrame.setStyleSheet("background-color:grey;")

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
        elif str(gpsInfo.qualityIndicator) == 'GpsQualityIndicator.RTK' and gpsInfo.pdop < 2 and gpsInfo.satellitesUsed > 10:
            return 'green'
        elif str(gpsInfo.qualityIndicator) == 'GpsQualityIndicator.FloatRTK' and gpsInfo.pdop < 6 and gpsInfo.satellitesUsed > 6:
            return 'yellow'
        elif str(gpsInfo.qualityIndicator) == 'GpsQualityIndicator.GPS' and gpsInfo.pdop < 10 and gpsInfo.satellitesUsed > 4:
            return 'orange'
        else:
            return 'red'