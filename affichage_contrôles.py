from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import  QColor
from qgis.PyQt.QtWidgets import QTableWidgetItem, QHeaderView, QDockWidget
from qgis.core import *
import ast
import re
from .resources import *
# Import the code for the dialog

class affichage_controles(QDockWidget):

    def __init__(self, main, iface, parent):
        super(affichage_controles, self).__init__(parent)
        self.iface = iface
        self.main = main
        
    def create_controlpoint_layer(self):
        self.main.controlpoint_layer = QgsVectorLayer("Point?crs=IGNF:LAMB93", "controles_IGN", "memory")
        self.main.provider = self.main.controlpoint_layer.dataProvider()
        self.main.provider.addAttributes([QgsField("type", QVariant.String),
                                    QgsField("libellé",  QVariant.String),
                                    QgsField("couche", QVariant.String),
                                    QgsField("attributs objet", QVariant.List)])
        self.main.controlpoint_layer.updateFields()
        single_symbol_renderer = self.main.controlpoint_layer.renderer()
        symbol = single_symbol_renderer.symbol()
        symbol.setColor(QColor.fromRgb(0, 225, 0))
        self.main.control_layer_found = True

    def get_controlpoint_layer(self):
        layer = QgsProject.instance().mapLayersByName('controles_IGN')[0]
        self.main.controlpoint_layer = layer
        self.main.provider = self.main.controlpoint_layer.dataProvider()
        self.main.provider.addAttributes([QgsField("type", QVariant.String),
                                    QgsField("libellé",  QVariant.String),
                                    QgsField("couche", QVariant.String),
                                    QgsField("attributs objet", QVariant.List)])
        self.main.controlpoint_layer.updateFields()
        
    def get_total_controles(self):
        total = 0
        layer = QgsProject.instance().mapLayersByName('controles_IGN')
        test = len(layer)
        if test == 0:
            self.main.control_layer_found = False
            return total
        self.main.controlpoint_layer = layer[0]
        if (self.main.controlpoint_layer):
            for f in self.main.controlpoint_layer.getFeatures():
                geom = f.geometry()
                for parts in geom.parts():
                    total += 1
            return total
        else:
            return total
    
    def show_controles(self):
        total = self.get_total_controles()
        i = 0
        if total != 0:
            if self.main.voir_clicked == False:
                self.main.dlg_voir.showme.clicked.connect(self.moveto)
                self.main.dlg_voir.zoom.clicked.connect(self.zoomto)
                self.main.dlg_voir.blink.clicked.connect(self.clignoter)
                self.main.dlg_voir.suppr.clicked.connect(self.suppr_controle)
                self.main.voir_clicked = True
            self.main.dlg_voir.tableWidget.setRowCount(total)
            header = self.main.dlg_voir.tableWidget.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(4, QHeaderView.Stretch)
            for f in self.main.controlpoint_layer.getFeatures():
                geom = f.geometry()
                attributes = f.attributes()
                # mets les coordonées du contrôle dans la première colone
                nums = re.findall(r'\-?[0-9]+(?:\.[0-9]*)?', str(QgsGeometry.asPoint(geom)))
                coords = tuple(zip(*[map(float, nums)] * 2))[0]
                self.main.dlg_voir.tableWidget.setItem(i , 0, QTableWidgetItem(str(coords)))
                self.main.dlg_voir.tableWidget
                j = 1
                # ajoute les attibuts du controle dans le tableau*
                for info in attributes:
                    self.main.dlg_voir.tableWidget.setItem(i , j, QTableWidgetItem(str(info)))
                    j += 1
                i += 1
            self.main.dlg_voir.show()
            result = self.main.dlg_voir.exec_()
            if result:
                return
        else:
            self.main.dlg_pas.show()
    
    def clignoter(self):
        list = []
        if self.get_total_controles != 0:
            for f in self.main.controlpoint_layer.getFeatures():
                list.append(f.geometry())
            self.main.iface.mapCanvas().flashGeometries(list)
    
    def zoomto(self):
        self.main.row = self.main.dlg_voir.tableWidget.currentRow()
        item = self.main.dlg_voir.tableWidget.item(self.main.row, 0)
        canvas = self.main.iface.mapCanvas()
        canvas.zoomScale(768)
        test = ast.literal_eval(item.text())
        rect = QgsRectangle(test[0], test[1], test[0], test[1])
        canvas.zoomScale(8)
        canvas.setExtent(rect)
    
    def moveto(self):
        self.main.row = self.main.dlg_voir.tableWidget.currentRow()
        item = self.main.dlg_voir.tableWidget.item(self.main.row, 0)
        canvas = self.main.iface.mapCanvas()
        scale = canvas.scale()
        canvas.zoomScale(768)
        test = ast.literal_eval(item.text())
        rect = QgsRectangle(test[0], test[1], test[0], test[1])
        canvas.setExtent(rect)
        canvas.zoomScale(scale)
                
    def suppr_controle(self):
        i = 0
        self.main.dlg_voir.tableWidget.removeRow(self.main.row)
        with edit(self.main.controlpoint_layer):
            for f in self.main.controlpoint_layer.getFeatures():
                if i == self.main.row:
                    self.main.controlpoint_layer.deleteFeature(f.id())
                    return
                i += 1