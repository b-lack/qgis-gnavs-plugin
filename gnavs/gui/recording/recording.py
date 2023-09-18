
import os
import json
import random

from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtWidgets import QDialog
from PyQt5 import QtCore
from qgis.PyQt.QtCore import QTimer

from qgis.core import QgsSettings, QgsApplication, QgsMessageLog, QgsGpsDetector, QgsGpsConnection, QgsNmeaConnection, QgsPointXY, QgsPoint

from ...utils.utils import Utils



UI_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'recording.ui'))

class Recording(QtWidgets.QWidget, UI_CLASS):
    """
    Recording class.
    Gets GPS Info from selected serial port.
    """

    aggregatedValuesChanged = QtCore.pyqtSignal(object)
    currentPositionChanged = QtCore.pyqtSignal(object)
    recordingStateChanged = QtCore.pyqtSignal(bool)

    def __init__(self, interface, aggregate=True):
        """Constructor."""

        QDialog.__init__(self, interface.mainWindow())
        self.setupUi(self)

        self.refreshSettings()
        self.interface = interface

        self.measures = []
        self.measurementStart = None
        self.measurementEnd = None

        self.gpsCon = None
        self.lastGPSInfo = None
        self.keepFocus = False

        self._translate = QtCore.QCoreApplication.translate

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
        #self.lfbRefreshSerialListBtn.hide()
        self.lfbSerialPortList.currentIndexChanged.connect(self.onSerialPortChanged)
        

        self.lfbRefreshSerialListBtn.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_BrowserReload))

        serialSetting = self.getGPSSettings()
        
        if serialSetting is not None:
            self.selectPort(serialSetting)

        self.lfbValidIndicator.hide()
        self.lfbValidIndicator.setStyleSheet("background-color: gray; border-radius: 5px;")

        self.lfbRecordingPercent.setRange(0, 100)
        self.lfbRecordingPercent.setContentsMargins(0,0,0,0)
        self.lfbRecordingPercent.setValue(0)
        
        
    def toggleButtonsChanged(self, value):
        self.recordingStyle = value
        self.setMeasurementsCount()
        #self.cangeState()

    # Deprecated: Replaced by setFocus
    #def focusQuick(self):
    #       self.setFocus()
    
    def toggleFocus(self, isNavigation):
        """Toggle between the tracking and not tracking """
        self.keepFocus = isNavigation

    def setFocus(self):
        """Set the center of the map canvas to last GPS position"""
        if self.lastGPSInfo is not None:
            Utils.focusToXY(self.lastGPSInfo.longitude, self.lastGPSInfo.latitude)

#   Deprecated: unnecessary
#   def cangeState(self):
#        return
#        if self.recordingStyle == 'navigation':
#            self.lfbGetCoordinatesGtn.setText("NAVIGIEREN")
#            self.lfbCancelCoordinatesBtn.setText("BEENDEN")
#        else:
#            self.lfbGetCoordinatesGtn.setText("AUFZEICHNEN")
#            self.lfbCancelCoordinatesBtn.setText("BEENDEN")

    def refreshSettings(self):
        """Set default QGIS settings"""
        self.settings = {
            "meassurementSetting": Utils.getSetting('meassurementSetting', 100),
            "bestMeassurementSetting": Utils.getSetting('bestMeassurementSetting', 70),
            "aggregationType": Utils.getSetting('aggregationType', 'mean'),
            "sortingValues": json.loads(Utils.getSetting('sortingValues', '[]')),
        }
    
    def updateSerialPortSelection(self):
        """Update the serial port List"""
        self.ports = Utils.getSerialPorts()

        self.lfbSerialPortList.clear()
        for port in self.ports:
            self.lfbSerialPortList.addItem(port[0], port[0])

    def selectPort(self, port):
        """Select a serial port"""
        index = self.lfbSerialPortList.findData(port)
        if index != -1 :
            self.lfbSerialPortList.setCurrentIndex(index)
        else:
            self.lfbSerialPortList.setCurrentIndex(0)

        self.onSerialPortChanged(self.lfbSerialPortList.currentIndex())

    def getGPSSettings(self):
        """Get the selected and saved serial port from Settings"""
        return QgsSettings().value('gps/gpsd-serial-device')
    
    def onSerialPortChanged(self, index):
        """Update the serial port selection"""

        self.geConnectionInfoLabel.setText("")

        newPort = self.lfbSerialPortList.itemData(index)
        if newPort is None or newPort == 'None':
            self.geConnectionInfoLabel.setText("Wähle ein 'Serielles Gerät' aus.")
            return
        
        self.port = self.lfbSerialPortList.itemData(index)
    
    def connectionEstablished(self):
        """Check if a connection already exists and return it"""
        connectionRegistry = QgsApplication.gpsConnectionRegistry()
        connectionList = connectionRegistry.connectionList()

        if len(connectionList) > 0:
            return connectionList[0]

        return None

    # Not yet implemented
    def connectionTest(self, port):
        """Test the connection before starting the tracking"""
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

    # Not yet implemented
    def connectionTestFailed(self):
        """Connection test fail before starting the tracking"""
        
        self.geConnectionInfoLabel.setText(self._translate("Form", "Verbindung fehlgeschlagen."))
        self.geConnectionInfoLabel.setStyleSheet("color: red;")
        self.lfbSerialPortList.setEnabled(True)
        self.lfbGetCoordinatesGtn.setEnabled(False)
        
        try:
            self.gpsDetectorTest.detected.disconnect(self.connectionTestSucceed)
            self.gpsDetectorTest.detectionFailed.disconnect(self.connectionTestFailed)
        except:
            pass

    # Not yet implemented
    def connectionTestSucceed(self, connection):
        """Connection test succeed before starting the tracking"""
        self.geConnectionInfoLabel.setText(self._translate("Form", "Verbindung erfolgreich."))
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
        """Delay the connection to the GPS device by 100 ms"""

        self.geConnectionInfoLabel.setText(self._translate("Form", "Port wird gestestet..."))
        self.geConnectionInfoLabel.setStyleSheet("color: gray;")

        
        self.lfbGetCoordinatesGtn.setEnabled(False)

        self.lfbCancelCoordinatesBtn.setEnabled(True)
        self.lfbCancelCoordinatesBtn.hide()

        self.lfbSerialPortList.setEnabled(False)

        #QgsSettings().setValue('gps/gpsd-serial-device', self.port)


        self.connectionTimer = QTimer()
        self.connectionTimer.setSingleShot(True)
        self.connectionTimer.timeout.connect(self.connect)
        self.connectionTimer.start(100)

    def connect(self):
        """Setup connection to the GPS device"""

        connection = self.connectionEstablished()
        
        if connection is not None:
            self.connection_succeed(connection, False)
            self.geConnectionInfoLabel.setText('Connection exists.')
            return

        if self.port is None:
            self.geConnectionInfoLabel.setText(self._translate("Form", 'Wähle ein Gerät aus.'))
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


    def cancelConnection(self, reset=True):
        """Cancel an existing connection to the GPS device"""

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

                self.recordingStateChanged.emit(False)
           

            self.gps_active = False
            self.lfbCancelCoordinatesBtn.setEnabled(False)
            self.lfbCancelCoordinatesBtn.hide()

            self.lfbGetCoordinatesGtn.setEnabled(True)
            self.lfbGetCoordinatesGtn.show()

            self.measures = []

            if reset:
                self.setMeasurementsCount()
                self.getProgress()

            

        except Exception as e:
            pass

    def connection_succeed(self, connection, closeConnection=False):
        """Connection succeed to the GPS device"""

        self.geConnectionInfoLabel.setText('Tracking...')
        self.geConnectionInfoLabel.setStyleSheet("color: green;")

        if self.gpsCon is not None:
            self.cancelConnection(False)

        # https://python.hotexamples.com/examples/PyQt5.QtSerialPort/QSerialPort/setDataBits/python-qserialport-setdatabits-method-examples.html

        if not isinstance(connection, QgsNmeaConnection):
            import sip
            self.gpsCon =  sip.cast(connection, QgsGpsConnection)

        elif isinstance(connection, QgsGpsConnection):
            self.gpsCon = connection
        else:
            QgsMessageLog.logMessage("not isinstance: " + str(connection), 'LFB')   
            return
        
        if closeConnection:
            self.cancelConnection(False)
            return

        try:
            self.lfbCancelCoordinatesBtn.setEnabled(True)
            self.lfbCancelCoordinatesBtn.show()

            self.gpsCon.stateChanged.connect(self.status_changed)
            self.recordingStateChanged.emit(True)
            
            self.gps_active = True

            connectionRegistry = QgsApplication.gpsConnectionRegistry()
            connectionRegistry.registerConnection(self.gpsCon)
        except Exception as e:
            QgsMessageLog.logMessage('Exception:' + str(e))

    def connection_failed(self):
        """Connection to the GPS device failed"""

        portStr1 = self._translate("Form", "noConnection1")
        portStr2 = self._translate("Form", "noConnection2")

        self.geConnectionInfoLabel.setText(portStr1 + ' ' + self.port + ' ' + portStr2)
        self.geConnectionInfoLabel.setStyleSheet("color: red;")

        self.lfbGetCoordinatesGtn.setEnabled(True)
        self.lfbGetCoordinatesGtn.show()
        self.lfbCancelCoordinatesBtn.hide()
        self.lfbCancelCoordinatesBtn.setEnabled(False)

        self.lfbSerialPortList.setEnabled(True)

    # not yet implemented
    def getQualityColor(self):
        """Get the quality indicator color of the last GPS position"""
        if self.lastGPSInfo is None:
            return
        
        quaityIndicator =  self.lastGPSInfo.qualityIndicator
        pdop = self.lastGPSInfo.pdop
        satellitesUsed = self.lastGPSInfo.satellitesUsed


        if pdop <= 2 and satellitesUsed >= 10 and quaityIndicator == 'GpsQualityIndicator.RTK':
            return 'green'
        elif pdop > 2 and pdop <= 6 and satellitesUsed and quaityIndicator == 'GpsQualityIndicator.FloatRTK':
            return 'yellow'
        else:
            return 'red'

        if str(quaityIndicator) == 'GpsQualityIndicator.RTK':
            return 1
        elif str(quaityIndicator) == 'GpsQualityIndicator.FloatRTK':
            return 2
        elif str(quaityIndicator) == 'GpsQualityIndicator.GPS':
            return 3
        else:
            return 10
            

    def status_changed(self, gpsInfo):
        
        """Update the GPS position and emit values"""
        quality = gpsInfo.quality

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
                
            self.createGPSObject(gpsInfo)
        except Exception as e:
           self.geConnectionInfoLabel.setText(str(e))

    def getProgress(self):
        meassurementSetting = Utils.getSetting('meassurementSetting', 100)
        self.lfbGPSCountSeperator.setText('/')
        self.lfbGPSCountTotal.setText(str(meassurementSetting))

        val = round(len(self.measures) / int(meassurementSetting) * 100)

        self.lfbRecordingPercent.setValue(val)
        self.lfbRecordingPercent.show()

        return val
        
    def setMeasurementsCount(self):
        """Set the number of measurements"""
        self.lfbGPSCount.setText(str(len(self.measures)))

        if self.recordingStyle == 'navigation':
            self.lfbGPSCountTotal.hide()
            self.lfbGPSCountSeperator.hide()
            #self.lfbGPSCount.hide()
            #self.label_2.hide()
            self.lfbRecordingPercent.hide()
        else:
            self.lfbGPSCountTotal.show()
            self.lfbGPSCountSeperator.show()
            self.lfbGPSCount.show()
            self.label_2.show()

    def createGPSObject(self, GPSInfo):
        """Create a GPS object and emit values"""

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
            'qualityIndicator': random.randint(0,10) #TODO: self.getQualityColor(GPSInfo),
        })

        self.setMeasurementsCount()


        self.aggregatedValuesChanged.emit(self.measures)
        self.currentPositionChanged.emit(GPSInfo)

        val = self.getProgress()
        
        if val >= 100:
            self.cancelConnection(False)