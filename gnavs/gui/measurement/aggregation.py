
import os
import json
import statistics
import time


from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtWidgets import QDialog
from PyQt5 import QtCore

from ...utils.utils import Utils
from qgis.core import QgsMessageLog


UI_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'aggregation.ui'))

class Aggregation(QtWidgets.QWidget, UI_CLASS):
    """
    Aggregation class.
    Sets up the aggregation view, shows aggregated values.
    """

    addToMap = QtCore.pyqtSignal(object, list)

    def __init__(self, interface):
        """Constructor."""

        QDialog.__init__(self, interface.mainWindow())
        self.setupUi(self)

        self.settings = None

        self.lfbAddToMapBtn.setEnabled(False)

        self.lfbAddToMapWidget.hide()

    def emitData(self):
        """Adds point feature to map and emit the aggregated values to the main view"""

        self.getTextFields()
        self.lfbAddToMapBtn.setEnabled(False)

        Utils.addPointToLayer('GNAVS-Aggregated', self.aggregatedValues, self.gpsInfos)
        self.reset()

    def updateAggregatedValues(self, gpsInfos):
        """Update the aggregated values"""

        self.lfbAddToMapBtn.setEnabled(True)

        self.gpsInfos = gpsInfos
        self.aggregatedValues = self.aggregate(gpsInfos)
        self.printAggregatedValues(self.aggregatedValues)

        return self.aggregatedValues

    def refreshSettings(self):
        """Gets all relevant settings for aggregation"""

        self.settings = {
            "meassurementSetting": Utils.getSetting('meassurementSetting', 100),
            "bestMeassurementSetting": Utils.getSetting('bestMeassurementSetting', 70),
            "aggregationType": Utils.getSetting('aggregationType', 'mean'),
            "sortingValues": json.loads(Utils.getSetting('sortingValues', '[]')),
        }

    def middlePoint(self, list, aggregationType='mean'):
        """Calculates mean or median of values in list"""

        if aggregationType == 'median':
            return statistics.median(list)
        else:
            return statistics.mean(list)
    
    def getDefaultAggregationValues(self):
        return {
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

            'invalid': 0
        }
    
    def reset(self):
        """Resets the aggregation view"""

        self.aggregatedValues = []
        self.printAggregatedValues(self.getDefaultAggregationValues(), True)

    def aggregate(self, GPSInfos):
        """Aggregates the GPSInfos"""

        if self.settings == None:
            self.refreshSettings()

        ## filter valid Data
        validGPSInfos = [d for d in GPSInfos if d['invalid'] == False]

        if self.settings['sortingValues']:
            for sortObj in reversed(self.settings['sortingValues']):
                if 'active' in sortObj and sortObj['active']:
                    validGPSInfos.sort(key=lambda x: x[sortObj['value']], reverse=sortObj['direction'])


        measurementLength = len(GPSInfos)
        validMeasurementLength = len(validGPSInfos)
        besteMeasurements = round(validMeasurementLength * int(self.settings['bestMeassurementSetting']) / 100)

        listBestMeasurements = validGPSInfos[:besteMeasurements]
        aggregationType = self.settings['aggregationType']

        latitude = [d['latitude'] for d in listBestMeasurements]
        longitude = [d['longitude'] for d in listBestMeasurements]
        elevation = [d['elevation'] for d in listBestMeasurements]
        vdop = [d['vdop'] for d in listBestMeasurements]
        pdop = [d['pdop'] for d in listBestMeasurements]
        hdop = [d['hdop'] for d in listBestMeasurements]
        satellitesUsed = [d['satellitesUsed'] for d in listBestMeasurements]

        measurementDateTime = [d['utcDateTime'] for d in listBestMeasurements]

        if len(measurementDateTime) == 0:
            return self.getDefaultAggregationValues()

        return {
            'measurementStartTime': min(measurementDateTime),
            'measurementEndTime': max(measurementDateTime),

            'invalid': len(GPSInfos) - len(validGPSInfos),

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
        """Gets the text from the view"""

        if self.aggregatedValues == None:
            return
        
        self.aggregatedValues['device'] = self.lfbGPSDevice.text()
        self.aggregatedValues['name'] = self.lfbGPSName.text()
        self.aggregatedValues['description'] = self.lfbGPSDescription.toPlainText()

    def printAggregatedValues(self, aggregatedValues, clear=False):
        """Prints the aggregated values to the view"""

        self.lfbGPSCountBest.setText( str(aggregatedValues['measurementsUsedCount']) )
        self.lfbGPSLat.setText( str(round(aggregatedValues['latitude'], 8)) ) # 1.11 mm
        self.lfbGPSLon.setText( str(round(aggregatedValues['longitude'], 8)) ) # 1.11 mm
        self.lfbGPSInvalid.setText( str(aggregatedValues['invalid']) )
        self.lfbGPSsatCount.setText( str(round(aggregatedValues['satellitesUsed'])) )

        self.lfbGPSpDop.setText( str(round(aggregatedValues['pdop'], 2)) )
        self.lfbGPSvDop.setText( str(round(aggregatedValues['vdop'], 2)) )
        self.lfbGPShDop.setText( str(round(aggregatedValues['hdop'], 2)) )

        if clear:
            self.lfbGPSDescription.setPlainText( aggregatedValues['description'] )
            self.lfbGPSName.setText( aggregatedValues['name'] )
            self.lfbGPSDevice.setText( aggregatedValues['device'] )