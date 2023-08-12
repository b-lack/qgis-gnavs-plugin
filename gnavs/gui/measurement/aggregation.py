
import os
import json
import statistics
import time


from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtWidgets import QDialog
from PyQt5 import QtCore
from qgis.PyQt.QtCore import QSettings, QTimer
from datetime import datetime



from qgis.core import QgsSettings, QgsApplication, QgsMessageLog, QgsGpsDetector, QgsGpsConnection, QgsNmeaConnection

from ...utils.utils import Utils


UI_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'aggregation.ui'))

class Aggregation(QtWidgets.QWidget, UI_CLASS):

    addToMap = QtCore.pyqtSignal(object, list)

    def __init__(self, interface):
        """Constructor."""

        QDialog.__init__(self, interface.mainWindow())
        self.setupUi(self)

        self.lfbAddToMapBtn.clicked.connect(self.emitData)
        self.lfbAddToMapBtn.setEnabled(False)

    def emitData(self):
        self.getTextFields()
        self.lfbAddToMapBtn.setEnabled(False)
        self.addToMap.emit(self.aggregatedValues, self.gpsInfos)
        self.reset()

    def updateAggregatedValues(self, gpsInfos):
        self.lfbAddToMapBtn.setEnabled(True)

        self.gpsInfos = gpsInfos
        self.aggregatedValues = self.aggregate(gpsInfos)
        self.printAggregatedValues(self.aggregatedValues)

    def refreshSettings(self):
        self.settings = {
            "meassurementSetting": Utils.getSetting('meassurementSetting', 100),
            "bestMeassurementSetting": Utils.getSetting('bestMeassurementSetting', 70),
            "aggregationType": Utils.getSetting('aggregationType', 'mean'),
            "sortingValues": json.loads(Utils.getSetting('sortingValues', '[]')),
        }

    def middlePoint(self, list, aggregationType='mean'):
        if aggregationType == 'median':
            return statistics.median(list)
        else:
            return statistics.mean(list)
        
    def reset(self):
        self.aggregatedValues = []
        self.printAggregatedValues(
            {
                'measurementsCount': 0,
                'measurementsUsedCount': 0,
                'aggregationType': '',
                'latitude': 0,
                'latitudeStDev': 0,
                'longitude': 0,
                'longitudeStDev': 0,
                'elevation': 0,
                'elevationStDev': 0,
                'vdop': 0,
                'vdopStDev': 0,
                'pdop': 0,
                'pdopStDev': 0,
                'hdop': 0,
                'hdopStDev': 0,
                'satellitesUsed': 0,
                'satellitesUsedStDev': 0,

                'name': '',
                'description': '',
                'device': '',
            }
        )

    def aggregate(self, GPSInfos):

        #For Realtime Changes
        self.refreshSettings()
        
        if self.settings['sortingValues']:
            for sortObj in reversed(self.settings['sortingValues']):
               GPSInfos.sort(key=lambda x: x[sortObj['value']], reverse=sortObj['direction'])


        measurementLength = len(GPSInfos)
        besteMeasurements = round(measurementLength * int(self.settings['bestMeassurementSetting']) / 100)

        listBestMeasurements = GPSInfos[:besteMeasurements]
        aggregationType = self.settings['aggregationType']

        #self.lfbGPSaggregationType.setText(aggregationType.capitalize())


        latitude = [d['latitude'] for d in listBestMeasurements]
        longitude = [d['longitude'] for d in listBestMeasurements]
        elevation = [d['elevation'] for d in listBestMeasurements]
        vdop = [d['vdop'] for d in listBestMeasurements]
        pdop = [d['pdop'] for d in listBestMeasurements]
        hdop = [d['hdop'] for d in listBestMeasurements]
        satellitesUsed = [d['satellitesUsed'] for d in listBestMeasurements]

        measurementDateTime = [d['utcDateTime'] for d in listBestMeasurements]


        return {
            'measurementStartTime': min(measurementDateTime),
            'measurementEndTime': max(measurementDateTime),

            'measurementsCount': measurementLength,
            'measurementsUsedCount': besteMeasurements,
            'aggregationType': aggregationType,

            'latitude': self.middlePoint(latitude, aggregationType),
            'latitudeStDev': statistics.pstdev(latitude),
            'longitude': self.middlePoint(longitude, aggregationType),
            'longitudeStDev': statistics.pstdev(longitude),
            'elevation': self.middlePoint(elevation, aggregationType),
            'elevationStDev': statistics.pstdev(elevation),
            'pdop': self.middlePoint(pdop, aggregationType),
            'pdopStDev': statistics.pstdev(pdop),
            'vdop': self.middlePoint(vdop, aggregationType),
            'vdopStDev': statistics.pstdev(vdop),
            'hdop': self.middlePoint(hdop, aggregationType),
            'hdopStDev': statistics.pstdev(hdop),
            'satellitesUsed': self.middlePoint(satellitesUsed, aggregationType),
            'satellitesUsedStDev': statistics.pstdev(satellitesUsed),

            'name': self.lfbGPSName.text(),
            'description': self.lfbGPSDescription.toPlainText(),
            'device': self.lfbGPSDevice.text()
        }
    
    def getTextFields(self):
        self.aggregatedValues['device'] = self.lfbGPSDevice.text()
        self.aggregatedValues['name'] = self.lfbGPSName.text()
        self.aggregatedValues['description'] = self.lfbGPSDescription.toPlainText()

    def printAggregatedValues(self, aggregatedValues):
        #self.lfbGPSCount.setText( str(aggregatedValues['measurementLength']) )
        self.lfbGPSCountBest.setText( str(aggregatedValues['measurementsUsedCount']) )
        self.lfbGPSLat.setText( str(round(aggregatedValues['latitude'], 8)) ) # 1.11 mm
        self.lfbGPSLon.setText( str(round(aggregatedValues['longitude'], 8)) ) # 1.11 mm
        self.lfbGPSsatCount.setText( str(round(aggregatedValues['satellitesUsed'])) )

        self.lfbGPSpDop.setText( str(round(aggregatedValues['pdop'], 2)) )
        self.lfbGPSvDop.setText( str(round(aggregatedValues['vdop'], 2)) )
        self.lfbGPShDop.setText( str(round(aggregatedValues['hdop'], 2)) )

        self.lfbGPSDescription.setPlainText( aggregatedValues['description'] )
        self.lfbGPSName.setText( aggregatedValues['name'] )
        self.lfbGPSDevice.setText( aggregatedValues['device'] )