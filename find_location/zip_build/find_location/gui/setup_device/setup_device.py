
import os

from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtWidgets import QDialog

from ...utils.utils import Utils

from qgis.core import QgsSettings, QgsApplication, QgsMessageLog

UI_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'setup_device.ui'))

PLUGIN_NAME = "lfb_regeneration_wildlife_impact" #lfb_regeneration_wildlife_impact/pb_tool.cfg

class SetupDevice(QtWidgets.QWidget, UI_CLASS):

    def __init__(self, interface):
        """Constructor."""

        QDialog.__init__(self, interface.mainWindow())
        self.setupUi(self)

        self.pushButton.clicked.connect(self.test)

        s=QgsSettings()
        val=s.value(PLUGIN_NAME+"/layername_fieldname_a")
        QgsMessageLog.logMessage(str(val), "FindLocation")

        
        #GPSInfo = connectionList[0].currentGPSInformation()

        #s.setValue(PLUGIN_NAME+"/layername_fieldname_a", 66)


        if Utils.checkPluginExists(PLUGIN_NAME):
            self.geSetupLabel.setText("Plugin FOUND")
            plugin = Utils.getPluginByName(PLUGIN_NAME)

            results = plugin.tr('fromm')

            #results = plugin.run()
            
            QgsMessageLog.logMessage(str(results), "FindLocation")
        else:
            self.geSetupLabel.setText("Plugin NOT FOUND")
    
    def status_changed(self, gpsInfo):

        QgsMessageLog.logMessage('Status:' + str(self.gpsCon.status()), "FindLocation")

        if self.gpsCon.status() == 3: #data received
            QgsMessageLog.logMessage(gpsInfo.longitude, "FindLocation")
            QgsMessageLog.logMessage(gpsInfo.status, "FindLocation")
           

    def test(self):
        # https://qgis.org/pyqgis/3.2/core/Gps/QgsGpsInformation.html
        # https://gis.stackexchange.com/questions/307209/accessing-gps-via-pyqgis

        connectionRegistry = QgsApplication.gpsConnectionRegistry()
        connectionList = connectionRegistry.connectionList()
        if len(connectionList) > 0:
            # QgsGpsConnection
            self.gpsCon = connectionList[0]
            self.gpsCon.stateChanged.connect(self.status_changed)
            
            QgsMessageLog.logMessage(str('state.change'), "FindLocation")

        else:
            QgsMessageLog.logMessage(str('no.gps'), "FindLocation")

    