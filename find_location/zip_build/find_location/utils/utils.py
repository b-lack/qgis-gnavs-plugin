from qgis import qgis

class Utils(object):

    def getPluginByName(plugin_name):
        return qgis.utils.plugins[plugin_name]

    def checkPluginExists(plugin_name):
        return plugin_name in qgis.utils.plugins