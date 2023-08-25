import json
import os
import re

from qgis import qgis
from qgis.core import QgsSettings, QgsLayerTreeLayer, QgsPoint, QgsVectorFileWriter, QgsCoordinateTransformContext, QgsPointXY, QgsProject, QgsMessageLog, QgsGpsDetector, QgsDistanceArea, QgsCoordinateTransform, QgsExpressionContextUtils, QgsFeature, QgsMapLayer, QgsFields, QgsStyle, QgsGeometry, QgsField, QgsVectorLayer, QgsCoordinateReferenceSystem
from qgis.utils import iface
from qgis.PyQt.QtCore import QVariant, QDateTime, QFileInfo
from PyQt5.QtGui import QColor

PLUGIN_NAME = "find_location"

class Utils(object):
    """
    Utils class.
    Contains all the helper functions.
    """

    # Fields for the resulting point layer
    point_fields = [
        
        ("fid", QVariant.Int),
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

        ("satellitesUsed", QVariant.Double),
        
        ("sorting", QVariant.String),
        ("raw", QVariant.String),
    ]

    def getPluginByName(plugin_name):
        """Get the plugin object by name."""

        return qgis.utils.plugins[plugin_name]

    def checkPluginExists(plugin_name):
        """Check if the plugin exists."""
        return plugin_name in qgis.utils.plugins
    
    # _deprecated
    #def getPosition(self, name):
    #    return 'position: ' + name
    
    #Settings
    def getSerialPortSettings(self):
        """Get the serial port settings."""

        s=QgsSettings()
        return s.value(Utils.getPluginName()+"/serialPort")
    
    def setSerialPortSettings(self, serialPort):
        """Set the serial port settings."""
        s=QgsSettings()
        return s.setValue(Utils.getPluginName()+"/serialPort", serialPort)
    
    def getSetting(name, default=None):
        """ return the setting value
        Get the plugin setting by name.
        If the setting does not exist, create it with the default value
        """

        setting = QgsSettings().value(Utils.getPluginName()+"/" + name)
        if setting == None:
            if default is not None:
                Utils.setSetting(name, default)
            return default
        return setting
    
    def setSetting(name, value):
        """Set the setting by name and value."""

        QgsSettings().setValue(Utils.getPluginName()+"/" + name, value)
        return
    
    def getPluginName():
        """Get the plugin name."""

        return PLUGIN_NAME
    
    def getSerialPorts():
        """Get the serial ports available."""

        ports = QgsGpsDetector.availablePorts()
        return ports
    
    def distanceFromPoints(point1, point2):
        """Calculate the distance between two points."""

        distance = QgsDistanceArea()
        units = distance.lengthUnits()
        distance.setEllipsoid('WGS84')
        return distance.measureLine(point1, point2)
    
    def bearingFromPoints(point1, point2):
        """Calculate the bearing between two points."""

        distance = QgsDistanceArea()
        units = distance.lengthUnits()
        distance.setEllipsoid('WGS84')
        return distance.bearing(point1, point2)
        
    def deselectFeature(layer, feature):
        """Deselect a feature from a layer by ID."""

        layer.deselect(feature.id())

    def fokusToFeature(feature):
        """Zoom to a feature."""

        iface.mapCanvas().zoomToFeatureExtent(feature.geometry().boundingBox())
    
    def focusToXY(x, y, zoom = 150000):
        """Center map to a coordinate."""

        iface.mapCanvas().setCenter(QgsPointXY(x, y))

    def transformCoordinates(geom):
        """Transform coordinates from WGS84 to the current project CRS."""

        crs = QgsProject.instance().crs().authid()
    
        sourceCrs = QgsCoordinateReferenceSystem.fromEpsgId(4326)
        destCrs = QgsCoordinateReferenceSystem(crs)

        tr = QgsCoordinateTransform(sourceCrs, destCrs, QgsProject.instance())
        geom.transform(tr)
        return geom

    def centerFeature(feature, zoom = 150000):
        """Center (zoom) map to a feature."""
        geom = feature.geometry()
        coordinates = geom.asPoint()

        geom = Utils.transformCoordinates(geom)

        coordinates = geom.asPoint()
        iface.mapCanvas().setCenter(coordinates)
        
        current_scale =  iface.mapCanvas().scale()
        iface.mapCanvas().zoomScale(min(zoom, current_scale))

    def getSelectedFeaturesFromAllLayers(geometryType):
        """Get all selected features from all layers."""

        features = []

        layers = Utils.selectLayerByType(geometryType)
        
        for layer in layers:
            if layer.selectedFeatureCount() > 0:
                for feature in layer.selectedFeatures():
                    features.append({
                        'layer': layer,
                        'feature': feature
                    })

        return features
    
    def selectLayerByType(geometryType):
        """List all layers with geometry type."""

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
        """Set the fields for the point layer."""
        fields = QgsFields()
        fields.append(QgsField("id", QVariant.String))
        return fields
    
    def setStyle(layer, type):
        """Set the style for a point/linestring layer."""

        renderer = layer.renderer()
        symbol = renderer.symbol()

        get_styles = QgsStyle.defaultStyle()

        if type == 'point':

            style = get_styles.symbol('topo pop capital')
            renderer.setSymbol(style)
        
        elif type == 'linestring':
            symbol.setColor(QColor(255,255,1, 155))
            symbol.setWidth(1)

        layer.triggerRepaint()
    
    def getPrivateLayers(layerName, type, private=True, addStyle=True, fields=None):
        """
        Get the private layer by name.
        If the layer does not exist, create it.
        """

        names = [layer for layer in QgsProject.instance().mapLayers().values()]

        for i in names:
            layer = Utils.getLayerById(layerName)
            if layer is not None:
                return layer
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
    
    def getLayerDirectory(layerName):
        """Get the layer directory by name."""

        layer = Utils.getLayerById(layerName)

        if layer is None:
            return None
        path = layer.dataProvider().dataSourceUri().split("|")[0]
        if path.startswith('memory'):
            return None
        if path.endswith('.gpkg'):
            return path
        else:
            return path + '.gpkg'
    
    def saveLayerAsFile(layerName):
        """Save the vector layer by Name."""

        pathToBeSet = Utils.getSetting('directory')
        layer = Utils.getLayerById(layerName)

        if layer is None or pathToBeSet is None:
            return None
        
        writer = QgsVectorFileWriter.writeAsVectorFormatV3(layer, pathToBeSet, QgsCoordinateTransformContext(), QgsVectorFileWriter.SaveVectorOptions())
        if writer[0] == QgsVectorFileWriter.NoError:
            layer.setDataSource(pathToBeSet, layer.name(), 'ogr')
            layer.triggerRepaint() 
        else:
            print("error")

    def saveDraftPath(directory, layerName):
        """Save the vector layer in the given directory."""

        layers = QgsProject.instance().mapLayers().values()

        for layer in layers:
            if QgsExpressionContextUtils.layerScope(layer).variable('LFB-NAME') == layerName :
                pathToBeSet = os.path.join(directory, layerName + '.gpkg')
                writer = QgsVectorFileWriter.writeAsVectorFormatV3(layer, pathToBeSet, QgsCoordinateTransformContext(), QgsVectorFileWriter.SaveVectorOptions())

                if writer[0] == QgsVectorFileWriter.NoError:
                    layer.setDataSource(pathToBeSet, layer.name(), 'ogr')
                    layer.triggerRepaint() 
                else:
                    print("error")

    def clearLayer(layerName, type='point'):
        """Clear a layer by name and type."""

        layer = Utils.getPrivateLayers(layerName, type)

        if layer is None:
            return
        
        layer.startEditing()
        
        listOfIds = [feat.id() for feat in layer.getFeatures()]
        layer.deleteFeatures( listOfIds )

        layer.commitChanges()
        layer.endEditCommand()

    def removeLayer(layerNames):
        """Remove layers by name."""
        layers = QgsProject.instance().mapLayers().values()

        for layer in layers:
            if QgsExpressionContextUtils.layerScope(layer).variable('LFB-NAME') in layerNames :
                QgsProject.instance().removeMapLayer(layer.id())


    def layersToTop(layerNames):
        """Move layers to the top of the layer list"""
        # TODO: Put Layer to top of the layer list

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
        """Draw a line between two points."""

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
        """Draw a point at given position."""

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
        """Create a feature from GPS infos."""
        
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
    
    
    def getLayerById(layerName):
        """Get the layer by name."""

        layers = QgsProject.instance().mapLayers().values()

        layerId1 = re.sub('[^a-zA-Z0-9 \n\.]', '', layerName)
        layerId2 = layerName.replace('-', '_')

        for layer in layers:
            if layer.id().startswith(layerId1) or layer.id().startswith(layerId2) :
                return layer
        
        return None

    def addPointToLayer(layerName, aggregatedValues, gpsInfos):
        """Add a point to the layer."""

        layer = Utils.getLayerById(layerName)

        fields = Utils.getGPSInfoFields()

        if layer is None:
            layer = Utils.getPrivateLayers(layerName, 'point', False, False, fields)

        if layer is None:
            return

        feature = Utils.createFeatureFromGpsInfos(aggregatedValues, fields)

        sorting = Utils.getSetting('sortingValues')
        feature.setAttribute('sorting', sorting)
        feature.setAttribute('raw', json.dumps(gpsInfos))

        layer.startEditing()
        layer.addFeature(feature)
        layer.commitChanges()
        layer.endEditCommand()
    
    def getGPSInfoFields():
        """Append the GPS info fields."""

        fields = QgsFields()

        for field in Utils.point_fields:
            fields.append(QgsField(field[0], field[1]))

        return fields