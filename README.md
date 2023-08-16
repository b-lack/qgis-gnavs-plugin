# GNAVS - GNSS Navigate and Save

## Description

Dieses QGIS-Plugin ermöglicht das Anzeigen deiner aktuellen Position (mithilfe eines internen oder externen GPS-Gerätes) auf der Karte.

Bei ausgewählten Zielpunkten wird die Entfernung in Kilometer, Meter und Zentimeter sowie Winkel in wahlweise Grad, Gon oder Radiant angezeigt. Die Luftlinie zwischen deiner aktuellen Position und dem Zielpunkt wird auf der Karte visualisiert.

Ist die Zielposition erreicht, können Punkte "eingemessen" werden. Hierfür werden solange DAten erhoben, bis die gewünsche Qualität erreicht wird. In den Einstellungen des Plugins können Anforderungen an die Genauigkeit der Positionsbestimmung festgelegt werden.

BEi erreichter Qualität können die Daten in einem GeoPackage gespeichert werden. Hierfür wird ein Layer angelegt. Die Daten können anschließend in QGIS oder anderen Anwendungen weiterverarbeitet werden.

## Installation from Repository

QGIS: ``Plugins`` -> ``Manage and Install Plugins...`` -> ``Settings``

In the **Plugin Repositories** section click `+Add`.

- Name: `Find and Search Plugin`
- URL: `https://raw.githubusercontent.com/b-lack/qgis-gnavs-plugin/main/plugins.xml`

Check: "Allow experimental plugins"

Confirm by clicking `OK`

Restart QGIS

QGIS: ``Plugins`` -> ``Manage and Install Plugins...`` -> ``ALL``

Search for `LFB` and select `LFB Verjüngungszustands- und Wildeinfluss Monitoring`

Confirm by clicking `Install Plugin`

Done: The plugin is now installed and can be used.
