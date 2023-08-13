import json

from qgis import qgis
from qgis.core import QgsSettings, QgsLayerTreeLayer, QgsPoint, QgsPointXY, QgsProject, QgsMessageLog, QgsGpsDetector, QgsDistanceArea, QgsCoordinateTransform, QgsExpressionContextUtils, QgsFeature, QgsMapLayer, QgsFields, QgsStyle, QgsGeometry, QgsField, QgsVectorLayer, QgsCoordinateReferenceSystem
from qgis.utils import iface
from qgis.PyQt.QtCore import QVariant, QDateTime
from PyQt5.QtGui import QColor

PLUGIN_NAME = "find_location"

class Utils(object):

    point_fields = [
        

        ("name", QVariant.String),
        ("device", QVariant.String),
        ("description", QVariant.String),

        ("measurementEndTime", QVariant.DateTime),
        ("measurementStartTime", QVariant.DateTime),

        ("measurementsCount", QVariant.Int),
        ("measurementsUsedCount", QVariant.Int),
        ("aggregationType", QVariant.String),

        ("longitude", QVariant.Double),
        ("latitude", QVariant.Double),
        ("longitudeStDev", QVariant.Double),
        ("latitudeStDev", QVariant.Double),

        ("elevation", QVariant.Double),
        ("elevationStDev", QVariant.Double),

        ("hdop", QVariant.Double),
        ("hdopStDev", QVariant.Double),
        ("vdop", QVariant.Double),
        ("vdopStDev", QVariant.Double),
        ("pdop", QVariant.Double),
        ("pdopStDev", QVariant.Double),

        ("quality", QVariant.Int),

        ("satellitesUsed", QVariant.Double),
        
        ("raw", QVariant.String),
    ]

    def getPluginByName(plugin_name):
        return qgis.utils.plugins[plugin_name]

    def checkPluginExists(plugin_name):
        return plugin_name in qgis.utils.plugins
    
    def getPosition(self, name):
        return 'position: ' + name
    
    #Settings
    def getSerialPortSettings(self):
        s=QgsSettings()
        return s.value(Utils.getPluginName()+"/serialPort")
    
    def setSerialPortSettings(self, serialPort):
        s=QgsSettings()
        return s.setValue(Utils.getPluginName()+"/serialPort", serialPort)
    
    def getSetting(name, default=None):
        setting = QgsSettings().value(Utils.getPluginName()+"/" + name)
        if setting == None:
            if default is not None:
                Utils.setSetting(name, default)
            return default
        return setting
    
    def setSetting(name, value):
        QgsSettings().setValue(Utils.getPluginName()+"/" + name, value)
        return
    
    def getPluginName():
        return PLUGIN_NAME
    
    def getSerialPorts():
        ports = QgsGpsDetector.availablePorts()
        return ports
    
    def distanceFromPoints(point1, point2):
        distance = QgsDistanceArea()
        units = distance.lengthUnits()
        distance.setEllipsoid('WGS84')
        return distance.measureLine(point1, point2)
    
    def bearingFromPoints(point1, point2):
        distance = QgsDistanceArea()
        units = distance.lengthUnits()
        distance.setEllipsoid('WGS84')
        return distance.bearing(point1, point2)
        
    def deselectFeature(layer, feature):
        layer.deselect(feature.id())

    def fokusToFeature(feature):
        iface.mapCanvas().zoomToFeatureExtent(feature.geometry().boundingBox())
    
    def focusToXY(x, y, zoom = 150000):
        iface.mapCanvas().setCenter(QgsPointXY(x, y))
        #current_scale =  iface.mapCanvas().scale()
        #iface.mapCanvas().zoomScale(min(zoom, current_scale))

    def transformCoordinates(geom):
        crs = QgsProject.instance().crs().authid()
    
        sourceCrs = QgsCoordinateReferenceSystem.fromEpsgId(4326)
        destCrs = QgsCoordinateReferenceSystem(crs)

        tr = QgsCoordinateTransform(sourceCrs, destCrs, QgsProject.instance())
        geom.transform(tr)
        return geom

    def centerFeature(feature, zoom = 150000):
        geom = feature.geometry()
        coordinates = geom.asPoint()

        geom = Utils.transformCoordinates(geom)

        coordinates = geom.asPoint()
        iface.mapCanvas().setCenter(coordinates)
        
        current_scale =  iface.mapCanvas().scale()
        iface.mapCanvas().zoomScale(min(zoom, current_scale))

    # QgsWkbTypes.PointGeometry
    def getSelectedFeaturesFromAllLayers(geometryType):

        features = []

        layers = Utils.selectLayerByType(geometryType)
        
        for layer in layers:
            if layer.selectedFeatureCount() > 0:
                for feature in layer.selectedFeatures():
                    features.append({
                        'layer': layer,
                        'feature': feature
                    })
                #features = features + layer.selectedFeatures()
                #features.append(layer.selectedFeatures())

        return features
    
    # QgsWkbTypes.PointGeometry
    def selectLayerByType(geometryType):

        layerList = []

        layers = QgsProject.instance().mapLayers().values()

        for layer in layers:

            try:
                if layer.geometryType() == geometryType:
                    layerList.append(layer)
            except:
                pass
            
        return layerList
    
    def setFields(self):
        fields = QgsFields()
        fields.append(QgsField("id", QVariant.String))
        return fields
    
    def setStyle(layer, type):
        renderer = layer.renderer()
        symbol = renderer.symbol()

        get_styles = QgsStyle.defaultStyle()

        if type == 'point':

            style = get_styles.symbol('topo pop capital')
            renderer.setSymbol(style)
        
        elif type == 'linestring':
            symbol.setColor(QColor(255,255,1, 155))
            symbol.setWidth(1)

        #symbol.symbolLayer(0).setStrokeColor(QColor(255,255,1))
        #symbol.symbolLayer(0).setStrokeWidth(3)

        layer.triggerRepaint()
    
    def getPrivateLayers(layerName, type, private=True, addStyle=True, fields=None):

        names = [layer for layer in QgsProject.instance().mapLayers().values()]

        for i in names:
            if QgsExpressionContextUtils.layerScope(i).variable('LFB-NAME') == layerName :
                #Utils.setStyle(i)
                return i

        vl = QgsVectorLayer(type, layerName, "memory")
        QgsExpressionContextUtils.setLayerVariable(vl, 'LFB-NAME', layerName)

        if private:
            vl.setFlags(QgsMapLayer.Private)
        
        if fields is not None:
            fields = Utils.getGPSInfoFields()
            dp = vl.dataProvider()
            dp.addAttributes(fields)
            vl.updateFields()

        QgsProject.instance().addMapLayer(vl)

        if addStyle:
            Utils.setStyle(vl, type)

        return vl
    
    def clearLayer(layerName, type='point'):
        layer = Utils.getPrivateLayers(layerName, type)

        if layer is None:
            return
        
        layer.startEditing()
        
        listOfIds = [feat.id() for feat in layer.getFeatures()]
        layer.deleteFeatures( listOfIds )

        layer.commitChanges()
        layer.endEditCommand()

    def removeLayer(layerNames):
        layers = QgsProject.instance().mapLayers().values()

        for layer in layers:
            if QgsExpressionContextUtils.layerScope(layer).variable('LFB-NAME') in layerNames :
                QgsProject.instance().removeMapLayer(layer.id())

    def layersToTop(layerNames):

        return

        registry = QgsProject.instance()

        layers = list(registry.mapLayers().values())

        root = registry.layerTreeRoot()

        for layer in layers:
            if QgsExpressionContextUtils.layerScope(layer).variable('LFB-NAME') in layerNames :
                QgsMessageLog.logMessage(str(layer.id()), 'LFB')
                clone_layer = layer.clone()
                QgsProject.instance().removeMapLayer(layer.id())
                root.insertLayer(0, clone_layer)

       # root.insertLayer(0, layers[0])

        return

        layers = QgsProject.instance().mapLayers().values()

        root = QgsProject.instance().layerTreeRoot()

        for layer in layers:
            if QgsExpressionContextUtils.layerScope(layer).variable('LFB-NAME') in layerNames :
                layerClone = layer.clone()
                id = layer.id()
                root.insertChildNode(0, QgsLayerTreeLayer(layerClone))
                QgsProject.instance().removeMapLayer(id)
        
        return

        rg = iface.layerTreeCanvasBridge().rootGroup()
        if rg.hasCustomLayerOrder():
            QgsMessageLog.logMessage(str('hasCustomLayerOrder'), 'LFB')
            order = rg.customLayerOrder()
            for layer in layers: # How many layers we need to move
                QgsMessageLog.logMessage(str(layer.id()), 'LFB')
                if QgsExpressionContextUtils.layerScope(layer).variable('LFB-NAME') in layerNames :
                    order.insert( 0, order.pop( order.index( layer.id() ) ) )

            rg.setCustomLayerOrder( order )
        return
        layers = QgsProject.instance().mapLayers().values()

        bridge = iface.layerTreeCanvasBridge()
       

        for layer in layers:
            if QgsExpressionContextUtils.layerScope(layer).variable('LFB-NAME') in layerNames :
                
                order = bridge.rootGroup().customLayerOrder()
                order.insert( 0, order.pop( order.index( layer.id() ) ) ) # vlayer to the top
                bridge.setCustomLayerOrder( order )
                #order.insert(0, layerClone )
                #QgsProject.instance().removeMapLayer(layer.id())
                #QgsProject.instance().layerTreeRoot().moveLayer(layer, 0)

        iface.layerTreeCanvasBridge().setCustomLayerOrder( order )

    def drawDistance(layerName, startPoint, endPoint):
        layer = Utils.getPrivateLayers(layerName, 'linestring')

        if layer is None:
            return
        
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPolylineXY([startPoint, endPoint]))

        layer.startEditing()
        layer.addFeature(feature)
        layer.commitChanges()
        layer.endEditCommand()
    
    def drawPosition(layerName, startPoint):
        layer = Utils.getPrivateLayers(layerName, 'point')

        if layer is None:
            return
        
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPointXY(startPoint))
        
        layer.startEditing()
        layer.addFeature(feature)
        layer.commitChanges()
        layer.endEditCommand()

    def createFeatureFromGpsInfos(gpsInfos, fields):
        
        feature =  QgsFeature()

        feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(gpsInfos['longitude'], gpsInfos['latitude'])))
        feature.setFields(fields)

        for field in Utils.point_fields:
            if field[0] in gpsInfos:
                if field[0] == 'measurementEndTime' or field[0] == 'measurementStartTime':
                    feature.setAttribute(field[0], QDateTime.fromMSecsSinceEpoch(gpsInfos[field[0]]))
                else:
                    feature.setAttribute(field[0], gpsInfos[field[0]])
        
        return feature

    def addPointToLayer(layerName, aggregatedValues, gpsInfos):


        fields = Utils.getGPSInfoFields()
        layer = Utils.getPrivateLayers(layerName, 'point', False, False, fields)

        if layer is None:
            return

        feature = Utils.createFeatureFromGpsInfos(aggregatedValues, fields)

        feature.setAttribute('raw', json.dumps(gpsInfos))

        layer.startEditing()
        layer.addFeature(feature)
        layer.commitChanges()
        layer.endEditCommand()
    
    def getGPSInfoFields():
        fields = QgsFields()

        for field in Utils.point_fields:
            fields.append(QgsField(field[0], field[1]))

        return fields