<h1>
  <img src="./gnavs/icon.png" alt="Logo Plugin"/>
  GNAVS - GNSS Navigate and Save
</h1>

## Description

Dieses QGIS-Plugin ermöglicht das Anzeigen deiner aktuellen Position (mithilfe eines internen oder externen GPS-Gerätes) auf der Karte.

Bei ausgewählten Zielpunkten wird die Entfernung in Kilometer, Meter und Zentimeter sowie Winkel in wahlweise Grad, Gon oder Radiant angezeigt. Die Luftlinie zwischen deiner aktuellen Position und dem Zielpunkt wird auf der Karte visualisiert.

Ist die Zielposition erreicht, können Punkte "eingemessen" werden. Hierfür werden solange DAten erhoben, bis die gewünsche Qualität erreicht wird. In den Einstellungen des Plugins können Anforderungen an die Genauigkeit der Positionsbestimmung festgelegt werden.

Bei erreichter Qualität können die Daten in einem GeoPackage gespeichert werden. Hierfür wird ein Layer angelegt. Die Daten können anschließend in QGIS oder anderen Anwendungen weiterverarbeitet werden.

## Features

### Navigation
- Selection of the external/internal GPS device
- Display of the current position
- Display of the distance to the target point
- Display of the angle to the target point

### Point recording
- Recording of the current position
- Save the recorded points in a GeoPackage layer with relevant GNSS attributes

## Installation from Repository

1. QGIS: ``Plugins`` -> ``Manage and Install Plugins...`` -> ``Settings``

2. In the **Plugin Repositories** section click `+Add`.

  - Name: `GNAVS`
  - URL: `https://raw.githubusercontent.com/b-lack/qgis-gnavs-plugin/main/plugins.xml`

3. Check: "Allow experimental plugins"

4. QGIS: ``Plugins`` -> ``Manage and Install Plugins...`` -> ``ALL``

5. Search for `GNAVS` and select `GNAVS - GNSS Navigate and Save`

6. Confirm by clicking `Install Plugin`

Done: The plugin is now installed and can be used.

# Reporting Issues

Please report any issue regarding the GNAVS plugin [here](https://github.com/b-lack/qgis-gnavs-plugin/issues).

# License

This plugin is licensed under the [GNU GENERAL PUBLIC LICENSE](./LICENSE).

# About

Commissioned through the [Brandenburg State Forestry Office](https://forst.brandenburg.de/).

- Concept by: [Torsten Wiebke](https://www.gruenecho.de/)
- Develpment by: [Gerrit Balindt](https://gruenecho.de/)


💚 Free to use by everyone 💚