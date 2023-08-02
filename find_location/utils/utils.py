from qgis import qgis
from qgis.core import QgsSettings, QgsProject, QgsMessageLog, QgsGpsDetector, QgsDistanceArea, QgsCoordinateTransform, QgsExpressionContextUtils, QgsFeature, QgsMapLayer, QgsFields, QgsStyle, QgsGeometry, QgsField, QgsVectorLayer, QgsCoordinateReferenceSystem
from qgis.utils import iface
from qgis.PyQt.QtCore import QVariant
from PyQt5.QtGui import QColor

PLUGIN_NAME = "find_location"

class Utils(object):

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
    
    def getPrivateLayers(layerName, type):

        names = [layer for layer in QgsProject.instance().mapLayers().values()]

        for i in names:
            if QgsExpressionContextUtils.layerScope(i).variable('LFB-NAME') == layerName :
                #Utils.setStyle(i)
                return i

        vl = QgsVectorLayer(type, layerName, "memory")
        QgsExpressionContextUtils.setLayerVariable(vl, 'LFB-NAME', layerName)
        vl.setFlags(QgsMapLayer.Private)

        QgsProject.instance().addMapLayer(vl)

        Utils.setStyle(vl, type)

        return vl
    
    def clearLayer(layerName, type='point'):
        layer = Utils.getPrivateLayers(layerName, type)

        if layer is None:
            return
        
        layer.startEditing()
        layer.selectAll()
        layer.deleteSelectedFeatures()
        layer.commitChanges()
        layer.endEditCommand()

    def removeLayer(layerNames):
        layers = QgsProject.instance().mapLayers().values()

        for layer in layers:
            if QgsExpressionContextUtils.layerScope(layer).variable('LFB-NAME') in layerNames :
                QgsProject.instance().removeMapLayer(layer.id())

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