
import os

from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtWidgets import QDialog
from PyQt5 import QtCore
from qgis.PyQt.QtCore import QSettings

from qgis.core import QgsSettings, QgsWkbTypes, QgsMessageLog, QgsGpsDetector, QgsGpsConnection, QgsNmeaConnection

import pandas as pd

from ...utils.utils import Utils


UI_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'recording.ui'))

PLUGIN_NAME = "find_location"

class Recording(QtWidgets.QWidget, UI_CLASS):

    inputChanged = QtCore.pyqtSignal(object)
    currentPositionChanged = QtCore.pyqtSignal(object)

    def __init__(self, interface, bestCount=5):
        """Constructor."""

        QDialog.__init__(self, interface.mainWindow())
        self.setupUi(self)
    
        self.bestCount = bestCount
        self.measures = []

        self.gpsCon = None

        try:
            self.lfbGetCoordinatesGtn.clicked.disconnect()
            self.lfbCancelCoordinatesBtn.clicked.disconnect()
            self.lfbSerialPortList.currentIndexChanged.disconnect()
        except:
            pass


        self.lfbGetCoordinatesGtn.clicked.connect(self.connect)
        self.lfbGPSError.setText("")

        self.lfbCancelCoordinatesBtn.clicked.connect(self.cancelConnection)
        self.lfbCancelCoordinatesBtn.setEnabled(False)
        self.lfbCancelCoordinatesBtn.hide()


        self.updateSerialPortSelection()
        self.lfbRefreshSerialListBtn.clicked.connect(self.updateSerialPortSelection)
        self.lfbSerialPortList.currentIndexChanged.connect(self.onSerialPortChanged)
        

        self.lfbRefreshSerialListBtn.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_BrowserReload))

        serialSetting = self.getGPSSettings()
        
        if serialSetting is None:
            self.lfbGPSError.setText("Kein GPS Gerät ausgewählt.")
        else:
            self.selectPort(serialSetting)
        
        #
        #self.portPositionChecked = None
        #self.availablePorts = self.autoSelectPort()
        #self.tryNextPort()

        self.lfbConnectLayout_2.hide()
        self.lfbGPSError.hide()

    def __del__(self):
        print('Destructor called, Employee deleted.')

    def stopTracking(self):
        self.cancelConnection()
    
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

        newPort = self.lfbSerialPortList.itemData(index)
        if newPort is None or newPort == 'None':
            return
        
        self.port = self.lfbSerialPortList.itemData(index)
        self.connectionTest(self.port)
    
        #self.port = self.lfbSerialPortList.itemData(index)
        

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

        self.lfbConnectLayout_2.show()

        try:
            self.gpsDetectorTest.detected.disconnect(self.connectionTestSucceed)
            self.gpsDetectorTest.detectionFailed.disconnect(self.connectionTestFailed)
        except:
            pass

        self.connection_succeed(connection, True)


    
    def connect(self, port):
        QgsSettings().setValue('gps/gpsd-serial-device', self.port)

        if self.port is None:
            self.lfbGPSError.setText('Wähle ein "Serielles Gerät" aus.')
            return
        try:
            self.gpsDetector.detected[QgsGpsConnection].disconnect(self.connection_succeed)
            self.gpsDetector.detectionFailed.disconnect(self.connection_failed)
        except:
            pass
        
        self.lfbGetCoordinatesGtn.setEnabled(False)
        self.lfbGetCoordinatesGtn.hide()

        self.lfbGPSError.setText("")

        self.gpsDetector = QgsGpsDetector(self.port)
        self.gpsDetector.detected[QgsGpsConnection].connect(self.connection_succeed) #
        self.gpsDetector.detectionFailed.connect(self.connection_failed)
        self.gpsDetector.advance()

    def cancelConnection(self):
        QgsMessageLog.logMessage("cancelConnection", 'LFB')

        try:
            
            if self.gpsCon is not None:
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
            #self.lfbGPSError.setText(str(e))

    def connection_succeed(self, connection, closeConnection=False):

        if self.gpsCon is not None:
            self.cancelConnection()

        # https://python.hotexamples.com/examples/PyQt5.QtSerialPort/QSerialPort/setDataBits/python-qserialport-setdatabits-method-examples.html

        if not isinstance(connection, QgsNmeaConnection):
            import sip
            self.gpsCon =  sip.cast(connection, QgsGpsConnection)
            #self.gpsCon = gpsConnection

        elif isinstance(connection, QgsGpsConnection):
            self.gpsCon = gpsConnection
        else:
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
        except Exception as e:
             self.lfbGPSError.setText('connection_succeed:' + str(e))

        

    def connection_failed(self):
        self.lfbGPSError.setText('Es konnte keine Verbindung zum Port "' + self.port + '" hergestellt werden.')
        self.lfbGetCoordinatesGtn.setEnabled(True)
        self.lfbGetCoordinatesGtn.show()

    #def position_changed(self, gpsInfo):
    #    QgsMessageLog.logMessage('position_changed')
    #    QgsMessageLog.logMessage(str(gpsInfo))

    def status_changed(self, gpsInfo):
        

        try:
            self.lfbGPSError.setText('')
            self.emitAggregatedValues(gpsInfo)

        except Exception as e:
           self.lfbGPSError.setText(str(e))
        
    def setMeasurementsCount(self):
        self.lfbGPSCount.setText(str(len(self.measures)))

    def emitAggregatedValues(self, GPSInfo):

        if not GPSInfo.isValid():
            QgsMessageLog.logMessage('GPSInfo is not valid', 'LFB')
            return
        
        self.measures.insert(0, GPSInfo)

        self.measures.sort(key=lambda x: x.satellitesUsed, reverse=False)
        self.measures.sort(key=lambda x: x.pdop, reverse=True)
        self.measures.sort(key=lambda x: x.hdop, reverse=True)


        # Strip the list to 5 elements
        #self.measures = self.measures[:5]

        self.setMeasurementsCount()


        
        if len(self.measures) >= self.bestCount:
            self.inputChanged.emit(self.measures[:self.bestCount])
            #self.cancelConnection()
        else:
            self.currentPositionChanged.emit(GPSInfo)


    