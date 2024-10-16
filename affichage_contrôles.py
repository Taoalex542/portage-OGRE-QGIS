from qgis.PyQt.QtCore import QVariant, QDateTime
from qgis.PyQt.QtGui import  QColor
from qgis.PyQt.QtWidgets import QTableWidgetItem, QHeaderView, QDockWidget
from qgis.core import QgsField, QgsVectorLayer, QgsProject, QgsGeometry, QgsRectangle, edit
import ast
import re
from .resources import *
# Import the code for the dialog

class affichage_controles(QDockWidget):

    def __init__(self, main, iface, parent):
        super(affichage_controles, self).__init__(parent)
        self.iface = iface
        self.main = main
    
    # créé la couche pour les contrôles
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
        QgsProject.instance().addMapLayer(self.main.controlpoint_layer)
        layer = QgsProject.instance().mapLayersByName("controles_IGN")[0]
        root = QgsProject.instance().layerTreeRoot()
        mylayer = root.findLayer(layer.id())
        myClone = mylayer.clone()
        parent = mylayer.parent()
        root.insertChildNode(0, myClone)
        parent.removeChildNode(mylayer)
        self.main.controlpoint_layer = myClone.layer()
        self.main.control_layer_found = True
    
    # renvoie le nombre total d'objets contrôles présents dans la couche temporaire
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
    
    # formate les valeurs de la cinquème colone pour avoir le nom devant les valeurs, et avoir le bon format des dates
    def add_names_to_values(self, data):
        list = ""
        for i in range (len(data[0])):
            string = str(data[1][i])
            string += ": "
            if(type(data[0][i]) == QDateTime):
                string += data[0][i].toString()
            else:
                string += str(data[0][i])
            if i < len(data[0]) - 1:
                string += " | "
            list += string
        return list
    
    # popule le tableau avec tous les contrôles et leurs informations
    # si il n'y a pas de controles, montre la fenêtres "pas_controles", sinon montre la fenêtre "voir_contrôles"
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
            header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
            for f in self.main.controlpoint_layer.getFeatures():
                geom = f.geometry()
                attributes = f.attributes()
                # mets les coordonées du contrôle dans la première colone
                nums = re.findall(r'\-?[0-9]+(?:\.[0-9]*)?', str(QgsGeometry.asPoint(geom)))
                coords = tuple(zip(*[map(float, nums)] * 2))[0]
                self.main.dlg_voir.tableWidget.setItem(i , 0, QTableWidgetItem(str(coords)))
                j = 1
                # ajoute les attibuts du controle dans le tableau*
                for info in attributes:
                    temp = info
                    if (j == 4):
                        temp = self.add_names_to_values(info)
                    self.main.dlg_voir.tableWidget.setItem(i , j, QTableWidgetItem(str(temp)))
                    j += 1
                i += 1
            self.main.dlg_voir.show()
            result = self.main.dlg_voir.exec_()
            if result:
                return
        else:
            self.main.dlg_pas.show()
    
    # fait clignoter tous les objets contrôles
    def clignoter(self):
        list = []
        i = 0
        if self.get_total_controles != 0:
            for f in self.main.controlpoint_layer.getFeatures():
                if i == self.main.row:
                    list.append(f.geometry())
                i += 1
            self.main.iface.mapCanvas().flashGeometries(list)
    
    # déplace la caméra et zoome sur l'objet à une échelle de 1:8
    def zoomto(self):
        self.main.row = self.main.dlg_voir.tableWidget.currentRow()
        item = self.main.dlg_voir.tableWidget.item(self.main.row, 0)
        canvas = self.main.iface.mapCanvas()
        canvas.zoomScale(768)
        test = ast.literal_eval(item.text())
        rect = QgsRectangle(test[0], test[1], test[0], test[1])
        canvas.zoomScale(8)
        canvas.setExtent(rect)
    
    # déplace la "caméra" et gardes le zoom actuel de l'utilisateur, le changement d'échelle est nécéssaire pour mieux centrer le controle
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
    
    # récupère le contrôle choisi et le supprime de la couche ainsi que du tableau
    def suppr_controle(self):
        i = 0
        self.main.dlg_voir.tableWidget.removeRow(self.main.row)
        with edit(self.main.controlpoint_layer):
            for f in self.main.controlpoint_layer.getFeatures():
                if i == self.main.row:
                    self.main.controlpoint_layer.deleteFeature(f.id())
                    return
                i += 1