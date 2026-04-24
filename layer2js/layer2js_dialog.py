# -*- coding: utf-8 -*-
import os
import json
import re

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox
from qgis.core import QgsProject, QgsWkbTypes, QgsCoordinateReferenceSystem, QgsCoordinateTransform

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'layer2js_dialog_base.ui'))


def _safe_js_name(name):
    """Convert a layer name to a valid JavaScript identifier."""
    sanitized = re.sub(r'[^A-Za-z0-9_$]', '_', name)
    if sanitized and sanitized[0].isdigit():
        sanitized = '_' + sanitized
    return sanitized or '_layer'


class Layer2jsDialog(QtWidgets.QDialog, FORM_CLASS):

    def __init__(self, parent=None):
        super(Layer2jsDialog, self).__init__(parent)
        self.setupUi(self)
        self._populate_layers()
        self.layerComboBox.currentIndexChanged.connect(self._on_layer_changed)
        self.exportButton.clicked.connect(self._export_js)

    def _populate_layers(self):
        self.layerComboBox.clear()
        self._layers = []
        for layer in QgsProject.instance().mapLayers().values():
            if hasattr(layer, 'wkbType'):  # vector layers have wkbType
                self.layerComboBox.addItem(layer.name())
                self._layers.append(layer)
        self._on_layer_changed(self.layerComboBox.currentIndex())

    def _on_layer_changed(self, index):
        self.fieldListWidget.clear()
        if index < 0 or index >= len(self._layers):
            return
        layer = self._layers[index]
        for field in layer.fields():
            self.fieldListWidget.addItem(field.name())

    def _export_js(self):
        index = self.layerComboBox.currentIndex()
        if index < 0 or index >= len(self._layers):
            QMessageBox.warning(self, 'No layer', 'Please select a vector layer.')
            return

        layer = self._layers[index]
        dest_crs = QgsCoordinateReferenceSystem('EPSG:4326')
        transform = QgsCoordinateTransform(layer.crs(), dest_crs, QgsProject.instance())

        selected_fields = [
            item.text()
            for item in self.fieldListWidget.selectedItems()
        ]

        obj = {}
        for feature in layer.getFeatures():
            fid = feature.id()
            geom = feature.geometry()
            if geom and not geom.isNull():
                geom.transform(transform)
                wkt = geom.asWkt()
            else:
                wkt = ''
            values = [wkt] + [
                feature[f] if feature[f] is not None else None
                for f in selected_fields
            ]
            obj[fid] = values

        js_name = _safe_js_name(layer.name())
        js_lines = [f'const {js_name} = {{']
        for fid, values in obj.items():
            js_lines.append(f'  {fid}: {json.dumps(values, ensure_ascii=False)},')
        js_lines.append('};')
        js_content = '\n'.join(js_lines) + '\n'

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            'Save JavaScript file',
            f'{js_name}.js',
            'JavaScript files (*.js)'
        )
        if not save_path:
            return

        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(js_content)
            QMessageBox.information(
                self, 'Exported', f'File saved to:\n{save_path}'
            )
        except Exception as e:
            QMessageBox.critical(self, 'Export failed', str(e))
