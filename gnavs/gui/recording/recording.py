
import os
import json
import statistics
import time
import random


from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtWidgets import QDialog
from PyQt5 import QtCore
from qgis.PyQt.QtCore import QTimer
from datetime import datetime



from qgis.core import QgsSettings, QgsApplication, QgsMessageLog, QgsGpsDetector, QgsGpsConnection, QgsNmeaConnection

from ...utils.utils import Utils



UI_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'recording.ui'))

class Recording(QtWidgets.QWidget, UI_CLASS):

    aggregatedValuesChanged = QtCore.pyqtSignal(object)
    currentPositionChanged = QtCore.pyqtSignal(object)

    def __init__(self, interface, aggregate=True):
        """Constructor."""

        QDialog.__init__(self, interface.mainWindow())
        self.setupUi(self)

        self.refreshSettings()
    
        self.measures = []
        self.measurementStart = None
        self.measurementEnd = None

        self.gpsCon = None
        self.lastGPSInfo = None
        self.keepFocus = False

        if aggregate:
            self.recordingStyle = 'point'
            self.lfbGetCoordinatesGtn.setText("START")
            self.lfbCancelCoordinatesBtn.setText("BEENDEN")
        else:
            self.recordingStyle = 'navigation'
            self.lfbGetCoordinatesGtn.setText("START")
            self.lfbCancelCoordinatesBtn.setText("BEENDEN")

        try:
            self.lfbGetCoordinatesGtn.clicked.disconnect()
            self.lfbCancelCoordinatesBtn.clicked.disconnect()
            self.lfbSerialPortList.currentIndexChanged.disconnect()
        except:
            pass

        
        self.lfbGetCoordinatesGtn.clicked.connect(self.delayConnection)

        self.lfbCancelCoordinatesBtn.clicked.connect(self.cancelConnection)
        self.lfbCancelCoordinatesBtn.setEnabled(False)
        self.lfbCancelCoordinatesBtn.hide()


        self.updateSerialPortSelection()
        self.lfbRefreshSerialListBtn.clicked.connect(self.updateSerialPortSelection)
        self.lfbRefreshSerialListBtn.hide()
        self.lfbSerialPortList.currentIndexChanged.connect(self.onSerialPortChanged)
        

        self.lfbRefreshSerialListBtn.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_BrowserReload))

        serialSetting = self.getGPSSettings()
        
        if serialSetting is not None:
            self.selectPort(serialSetting)

        self.lfbValidIndicator.setStyleSheet("background-color: gray; border-radius: 5px;")
        

    def __del__(self):
        pass

    def toggleButtonsChanged(self, value):
        self.recordingStyle = value
        self.cangeState()

    def focusQuick(self):
        self.setFocus()
    
    def toggleFocus(self, isNavigation):
        self.keepFocus = isNavigation

    def setFocus(self):
        if self.lastGPSInfo is not None:
            Utils.focusToXY(self.lastGPSInfo.longitude, self.lastGPSInfo.latitude)

    def cangeState(self):
        return
        if self.recordingStyle == 'navigation':
            self.lfbGetCoordinatesGtn.setText("NAVIGIEREN")
            self.lfbCancelCoordinatesBtn.setText("BEENDEN")
        else:
            self.lfbGetCoordinatesGtn.setText("AUFZEICHNEN")
            self.lfbCancelCoordinatesBtn.setText("BEENDEN")

    def refreshSettings(self):
        self.settings = {
            "meassurementSetting": Utils.getSetting('meassurementSetting', 100),
            "bestMeassurementSetting": Utils.getSetting('bestMeassurementSetting', 70),
            "aggregationType": Utils.getSetting('aggregationType', 'mean'),
            "sortingValues": json.loads(Utils.getSetting('sortingValues', '[]')),
        }
    
    def updateSerialPortSelection(self):

        self.ports = Utils.getSerialPorts()

        self.lfbSerialPortList.clear()
        for port in self.ports:
            self.lfbSerialPortList.addItem(port[0], port[0])

    def selectPort(self, port):
        index = self.lfbSerialPortList.findData(port)
        if index != -1 :
            self.lfbSerialPortList.setCurrentIndex(index)
        else:
            self.lfbSerialPortList.setCurrentIndex(0)

        self.onSerialPortChanged(self.lfbSerialPortList.currentIndex())

    def getGPSSettings(self):
        return QgsSettings().value('gps/gpsd-serial-device')
    
    def onSerialPortChanged(self, index):
        self.geConnectionInfoLabel.setText("")

        newPort = self.lfbSerialPortList.itemData(index)
        if newPort is None or newPort == 'None':
            self.geConnectionInfoLabel.setText("Wähle ein 'Serielles Gerät' aus.")
            return
        
        self.port = self.lfbSerialPortList.itemData(index)
        
        #self.connectionTest(self.port)
    
        #self.port = self.lfbSerialPortList.itemData(index)
    
    def connectionEstablished(self):
        connectionRegistry = QgsApplication.gpsConnectionRegistry()
        connectionList = connectionRegistry.connectionList()

        if len(connectionList) > 0:
            return connectionList[0]

        return None
        
        #GPSInfo = connectionList[0].currentGPSInformation()

        if len(connectionList) > 0:
            #self.connection_succeed(connectionList[0], False)
            return True

    def connectionTest(self, port):
        if port is None:
            self.geConnectionInfoLabel.setText('Wähle ein "Serielles Gerät" aus.')
            self.geConnectionInfoLabel.setStyleSheet("color: red;")
            return
        
        self.geConnectionInfoLabel.setText("Teste Verbindung...")
        self.geConnectionInfoLabel.setStyleSheet("color: gray;")
        self.lfbSerialPortList.setEnabled(False)

        try:
            self.gpsDetectorTest.detected.disconnect(self.connectionTestSucceed)
            self.gpsDetectorTest.detectionFailed.disconnect(self.connectionTestFailed)
        except:
            pass

        self.gpsDetectorTest = QgsGpsDetector(port)
        self.gpsDetectorTest.detected[QgsGpsConnection].connect(self.connectionTestSucceed)
        self.gpsDetectorTest.detectionFailed.connect(self.connectionTestFailed)
       
        self.gpsDetectorTest.advance()


    def connectionTestFailed(self):
        
        self.geConnectionInfoLabel.setText("Verbindung fehlgeschlagen.")
        self.geConnectionInfoLabel.setStyleSheet("color: red;")
        self.lfbSerialPortList.setEnabled(True)
        self.lfbGetCoordinatesGtn.setEnabled(False)
        
        try:
            self.gpsDetectorTest.detected.disconnect(self.connectionTestSucceed)
            self.gpsDetectorTest.detectionFailed.disconnect(self.connectionTestFailed)
        except:
            pass

    def connectionTestSucceed(self, connection):
        self.geConnectionInfoLabel.setText("Verbindung erfolgreich.")
        self.geConnectionInfoLabel.setStyleSheet("color: green;")
        self.lfbSerialPortList.setEnabled(True)
        self.lfbGetCoordinatesGtn.setEnabled(True)

        try:
            self.gpsDetectorTest.detected.disconnect(self.connectionTestSucceed)
            self.gpsDetectorTest.detectionFailed.disconnect(self.connectionTestFailed)
        except:
            pass

        self.connection_succeed(connection, True)


    def delayConnection(self, connection):
        self.geConnectionInfoLabel.setText("Port wird gestestet...")
        self.geConnectionInfoLabel.setStyleSheet("color: gray;")

        
        self.lfbGetCoordinatesGtn.setEnabled(False)

        self.lfbCancelCoordinatesBtn.setEnabled(True)
        self.lfbCancelCoordinatesBtn.hide()

        self.lfbSerialPortList.setEnabled(False)

        QgsSettings().setValue('gps/gpsd-serial-device', self.port)


        self.connectionTimer = QTimer()
        self.connectionTimer.setSingleShot(True)
        self.connectionTimer.timeout.connect(self.connect)
        self.connectionTimer.start(100)
        #self.connect()

    def connect(self):

        connection = self.connectionEstablished()
        
        if connection is not None:
            self.connection_succeed(connection, False)
            self.geConnectionInfoLabel.setText('Connection exists.')
            return

        if self.port is None:
            self.geConnectionInfoLabel.setText('Wähle ein "Serielles Gerät" aus.')
            return
        
        try:
            self.gpsDetector.detected[QgsGpsConnection].disconnect(self.connection_succeed)
            self.gpsDetector.detectionFailed.disconnect(self.connection_failed)
        except:
            pass
        
        self.lfbGetCoordinatesGtn.setEnabled(False)
        self.lfbGetCoordinatesGtn.hide()
        self.lfbCancelCoordinatesBtn.show()
        self.lfbCancelCoordinatesBtn.setEnabled(True)

        self.gpsDetector = QgsGpsDetector(self.port)
        self.gpsDetector.detected[QgsGpsConnection].connect(self.connection_succeed) #
        self.gpsDetector.detectionFailed.connect(self.connection_failed)
        self.gpsDetector.advance()


    def cancelConnection(self):
        self.geConnectionInfoLabel.setText('Stopped')
        self.lfbValidIndicator.setStyleSheet("background-color: grey; border-radius: 5px;")

        self.lfbSerialPortList.setEnabled(True)

        Utils.removeLayer(['lfb-tmp-position', 'lfb-tmp-distance'])

        try:
            
            if self.gpsCon is not None:
                connectionRegistry = QgsApplication.gpsConnectionRegistry()
                connectionRegistry.unregisterConnection(self.gpsCon)

                self.gpsCon.stateChanged.disconnect(self.status_changed)

                self.gpsCon.close()
                self.gpsCon = None

           

            self.gps_active = False
            self.lfbCancelCoordinatesBtn.setEnabled(False)
            self.lfbCancelCoordinatesBtn.hide()

            self.lfbGetCoordinatesGtn.setEnabled(True)
            self.lfbGetCoordinatesGtn.show()

            self.measures = []
            self.setMeasurementsCount()

        except Exception as e:
            pass

    def connection_succeed(self, connection, closeConnection=False):
        self.geConnectionInfoLabel.setText('Tracking...')
        self.geConnectionInfoLabel.setStyleSheet("color: green;")

        if self.gpsCon is not None:
            self.cancelConnection()

        # https://python.hotexamples.com/examples/PyQt5.QtSerialPort/QSerialPort/setDataBits/python-qserialport-setdatabits-method-examples.html

        if not isinstance(connection, QgsNmeaConnection):
            import sip
            self.gpsCon =  sip.cast(connection, QgsGpsConnection)
            #self.gpsCon = gpsConnection

        elif isinstance(connection, QgsGpsConnection):
            self.gpsCon = connection
        else:
            QgsMessageLog.logMessage("not isinstance: " + str(connection), 'LFB')   
            return
        
        if closeConnection:
            self.cancelConnection()
            return

        try:
            self.lfbCancelCoordinatesBtn.setEnabled(True)
            self.lfbCancelCoordinatesBtn.show()

            self.gpsCon.stateChanged.connect(self.status_changed)
            #self.gpsCon.positionChanged.connect(self.position_changed)
            
            self.gps_active = True

            connectionRegistry = QgsApplication.gpsConnectionRegistry()
            connectionRegistry.registerConnection(self.gpsCon)
        except Exception as e:
            QgsMessageLog.logMessage('Exception:' + str(e))

    def connection_failed(self):
        self.geConnectionInfoLabel.setText('Es konnte keine Verbindung zum Port "' + self.port + '" hergestellt werden.')
        self.geConnectionInfoLabel.setStyleSheet("color: red;")

        self.lfbGetCoordinatesGtn.setEnabled(True)
        self.lfbGetCoordinatesGtn.show()
        self.lfbCancelCoordinatesBtn.hide()
        self.lfbCancelCoordinatesBtn.setEnabled(False)

        self.lfbSerialPortList.setEnabled(True)

    def getQualityColor(self):
        if self.lastGPSInfo is None:
            return
        
        quaityIndicator =  self.lastGPSInfo.qualityIndicator
        #qualityDescription =  self.lastGPSInfo.constellationFixStatus()
        pdop = self.lastGPSInfo.pdop
        satellitesUsed = self.lastGPSInfo.satellitesUsed

        QgsMessageLog.logMessage('getQualityColor: ' + str(quaityIndicator), 'LFB')
        QgsMessageLog.logMessage(str( str(quaityIndicator) == 'GpsQualityIndicator.GPS' ), 'LFB')
        #QgsMessageLog.logMessage('getQualityColor: ' + str(qualityDescription), 'LFB')

        if pdop <= 2 and satellitesUsed >= 10 and quaityIndicator == 'GpsQualityIndicator.RTK':
            return 'green'
        elif pdop > 2 and pdop <= 6 and satellitesUsed and quaityIndicator == 'GpsQualityIndicator.FloatRTK':
            return 'yellow'
        else:
            return 'red'
            

    def status_changed(self, gpsInfo):

        quality = gpsInfo.quality
        
        #self.getQualityColor()

        try:
            if quality == 0:
                self.lfbValidIndicator.setStyleSheet("background-color: red; border-radius: 5px;")
                return
            elif quality == -1:
                self.lfbValidIndicator.setStyleSheet("background-color: yellow; border-radius: 5px;")
            else:
                self.lfbValidIndicator.setStyleSheet("background-color: green; border-radius: 5px;")

            self.lastGPSInfo = gpsInfo
            

            if self.keepFocus:
                self.setFocus()
                
            self.emitAggregatedValues(gpsInfo)
        except Exception as e:
           self.geConnectionInfoLabel.setText(str(e))

        #self.getQualityColor()
        
    def setMeasurementsCount(self):
        self.lfbGPSCount.setText(str(len(self.measures)))

    def getQualityColor(self, gpsInfo):

        quaityIndicator = gpsInfo.qualityIndicator

        if str(quaityIndicator) == 'GpsQualityIndicator.RTK':
            return 1
        elif str(quaityIndicator) == 'GpsQualityIndicator.FloatRTK':
            return 2
        elif str(quaityIndicator) == 'GpsQualityIndicator.GPS':
            return 3
        else:
            return 10

    def emitAggregatedValues(self, GPSInfo):
        
        self.measures.insert(0, {
            'utcDateTime': GPSInfo.utcDateTime.currentMSecsSinceEpoch(),
            'latitude': GPSInfo.latitude,
            'longitude': GPSInfo.longitude,
            'elevation': GPSInfo.elevation,
            'vdop': GPSInfo.vdop,
            'pdop': GPSInfo.pdop,
            'hdop': GPSInfo.hdop,
            'satellitesUsed': GPSInfo.satellitesUsed,
            'quality': GPSInfo.quality,
            'qualityIndicator': random.randint(0,10) #self.getQualityColor(GPSInfo),
        })

        self.setMeasurementsCount()

        self.aggregatedValuesChanged.emit(self.measures)
        self.currentPositionChanged.emit(GPSInfo)