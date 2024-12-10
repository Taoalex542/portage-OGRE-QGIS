# coding=utf-8
import os
from qgis.core import QgsGeometry, QgsProject, Qgis, QgsWkbTypes, QgsFeature, QgsPointXY, edit, QgsMapLayer
from qgis import QtCore
from qgis.PyQt.QtWidgets import QProgressDialog
import re

# récupère le nombre total d'objets sur le quel le contrôle va travailler (actuellement seul les lignes)
def get_quantity(self):
    quantity = 0
    allLayers = QgsProject.instance().mapLayers().values()
    for layers in allLayers:
        for items in self.couche_list:
            # si la couche est cochée
            if layers.name() == items[0] and items[2] == QtCore.Qt.Checked: #(QtCore.Qt.Checked == 2)
                # récupère les informations des couches
                if self.selected == 1:
                    layer = layers.selectedFeatures()
                else:
                    layer = layers.getFeatures()
                for f in layer:
                    geom = f.geometry()
                    if reconciliation(self, geom) == 2:
                        continue
                    for part in geom.parts():
                        if ("LineString" in QgsWkbTypes.displayString(part.wkbType()) or "Polygon" in QgsWkbTypes.displayString(part.wkbType())):
                            quantity += 1
    return quantity

def nb_for_tuple(self, str):
    nb = 0
    i = 0
    while str[i] != ',' and str[i] != ')':
        if str[i] == ' ':
            nb += 1
        i += 1
    return nb

def reconciliation(self, geom):
    if (self.rec == []):
        return 1
    for zones in self.rec:
        if geom.intersects(zones):
            return 0
    return 2

# execution du controle
def auto_intersection(self, func):
    nom_controle = "auto intersection"
    for item in self.dlg_controles.treeWidget.findItems("auto intersection", QtCore.Qt.MatchRecursive):
        # vérifie si le contrôle "auto_intersection" est coché et si il existe des objets de type Ligne
        if item.checkState(0) == 2:
            items_done = 0
            quantity = get_quantity(self)
            print("nombre d'objets", quantity)
            if quantity > 0:
                # informe l'utilisateur le lancement du contrôle
                self.iface.messageBar().clearWidgets()
                self.iface.messageBar().pushMessage("Info", "Contrôle {} lancé".format(str(nom_controle)), level=Qgis.Info)
                # récupère les paramètres si possible
                # créé une barre de progrès avec pour total le nombre d'objets à faire, et en information supplémentaire le nombre de contrôle total à faire et le numéro de contrôle actif
                bar = QProgressDialog("Contrôle {0} en cours\nContrôle {1}/{2}".format(str(nom_controle), int(self.controles_restants + 1), int(self.controles_actifs)), "Annuler", 0, quantity)
                bar.setWindowModality(QtCore.Qt.WindowModal)
                bar.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
                # récupère les couches chargées et cochées sur qgis
                allLayers = QgsProject.instance().mapLayers().values()
                prev = []
                # parcours des couches
                for layers in allLayers:
                    if layers.type() == QgsMapLayer.RasterLayer:
                        continue
                    # parcours la liste actuelle des couches
                    for items in self.couche_list:
                        # si la couche est présente dans la liste et qu'elle est cochée 
                        if layers.name() == items[0] and items[2] == QtCore.Qt.Checked: #(QtCore.Qt.Checked == 2)
                            # récupère les informations des couches
                            if self.selected == 1:
                                layer = layers.selectedFeatures()
                            else:
                                layer = layers.getFeatures()
                            for f in layer:
                                # récupère la géométrie dans ces infos
                                geom = f.geometry()
                                if reconciliation(self, geom) == 2:
                                    continue
                                # récupère les informations nécéssaires dans la géométrie tel que le nom, le type, et les points
                                for part in geom.parts():
                                    # mets a jour le progrès de la bar de progrès
                                    if ("LineString" not in QgsWkbTypes.displayString(part.wkbType()) or "Polygon" in QgsWkbTypes.displayString(part.wkbType())):
                                        break
                                    bar.setValue(items_done)
                                    # parse le WKT de la géométrie pour avoir accès a chaque chiffre en tant que floats
                                    nums = re.findall(r'\-?[0-9]+(?:\.[0-9]*)?', part.asWkt()) # regex cherche entre chaque virgule: au moins un chiffre, puis un point, puis une chiffre si il y en a un, avec des parenthèses optionellement
                                    coords = tuple(zip(*[map(float, nums)] * nb_for_tuple(self, part.asWkt()))) # récupère les coordonnées en float et les ajoutes dans un tableau de floats pour une utilisation facile des données antérieurement
                                    # lance le controle rebroussement
                                    temp = func(coords)
                                    if temp != []:
                                        if self.control_layer_found == False:
                                            self.affichage_controles.create_controlpoint_layer()
                                        for controles in temp:
                                            with edit(self.controlpoint_layer):
                                                test = []
                                                test.append(f.attributes())
                                                test.append(layers.fields().names())
                                                ctrl = QgsFeature()
                                                ctrl.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(controles[0], controles[1])))
                                                ctrl.setAttributes(["Géométrie", "auto_intersection", layers.name(), test])
                                                self.controlpoint_layer.dataProvider().addFeature(ctrl)
                                                self.controlpoint_layer.updateExtents()
                                    temp = []
                                    items_done += 1
                                    if (bar.wasCanceled()):
                                        self.iface.messageBar().clearWidgets()
                                        self.controles_restants += 1
                                        self.iface.messageBar().pushMessage("Info", "Contrôle {} annulé".format(str(nom_controle)), level=Qgis.Info, duration=5)
                                        return 1
                self.iface.messageBar().clearWidgets()
                self.iface.messageBar().pushMessage("Info", "Contrôle {} terminé".format(str(nom_controle)), level=Qgis.Success, duration=5)
                self.controles_restants += 1
                for things in self.organisation:
                    if nom_controle in things:
                        things[1] = 0
                return 0
            else:
                self.iface.messageBar().clearWidgets()
                self.iface.messageBar().pushMessage("Info", "Contrôle {} impossible: il n'y a pas d'objets de type \"Ligne\". Passage au suivant".format(str(nom_controle)), level=Qgis.Warning, duration=10)
                self.controles_restants += 1
                for things in self.organisation:
                    if nom_controle in things:
                        things[1] = 0
                return 2