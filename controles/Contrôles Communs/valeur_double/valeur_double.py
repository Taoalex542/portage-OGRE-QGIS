# coding=utf-8
import os
from qgis.core import QgsGeometry, QgsProject, Qgis, QgsFeature, QgsPointXY, edit, QgsMapLayer
from qgis import QtCore
from qgis.PyQt.QtWidgets import QProgressDialog
import re

# lecture du fichier param.txt pour les paramètres du controles
# un seul paramètre est pris en comote actuellement, et ne prends que les chiffres
def read(self):
    filename = (os.path.dirname(os.path.realpath(__file__)) + "\\param.txt")
    parametres = []
    line_number = 0

    if os.path.isfile(filename):
        f = open(filename)
        for line in f:
            parametres.append(line)
            line_number += 1
        f.close()

        if line_number > 4:
            return parametres[4]
        else:
            return None
        

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
                            quantity += 1
    return quantity

def get_value_pos(param, names):
    nb = 0
    if param == None:
        return nb
    for name in names:
        if param == name:
            return nb
        nb += 1
    if nb == len(names) - 1:
        nb = 0
    return nb

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

def get_att(self, name):
    for items in self.organisation:
        if (name in items):
            return items[2]

# execution du controle
def valeur_double(self, func):
    nom_controle = "valeur double"
    importance = get_att(self, "valeur_double")
    done = []
    for item in self.dlg_controles.treeWidget.findItems("valeur double", QtCore.Qt.MatchRecursive):
        # vérifie si le contrôle "valeur_double" est coché
        if item.checkState(0) == 2:
            items_done = 0
            quantity = get_quantity(self)
            print("nombre d'objets", quantity)
            if quantity > 0:
                # informe l'utilisateur le lancement du contrôle
                self.iface.messageBar().clearWidgets()
                self.iface.messageBar().pushMessage("Info", "Contrôle {} lancé".format(str(nom_controle)), level=Qgis.Info)
                # récupère les paramètres si possible
                parametres = read(self)
                # créé une barre de progrès avec pour total le nombre d'objets à faire, et en information supplémentaire le nombre de contrôle total à faire et le numéro de contrôle actif
                bar = QProgressDialog("Contrôle {0} en cours\nContrôle {1}/{2}".format(str(nom_controle), int(self.controles_restants + 1), int(self.controles_actifs)), "Annuler", 0, quantity)
                bar.setWindowModality(QtCore.Qt.WindowModal)
                bar.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
                # récupère les couches chargées et cochées sur qgis
                allLayers = QgsProject.instance().mapLayers().values()
                # parcours des couches
                for layers in allLayers:
                    if layers.type() == QgsMapLayer.RasterLayer:
                        continue
                    # parcours la liste actuelle des couches
                    for items in self.couche_list:
                        # si la couche est présente dans la liste et qu'elle est cochée 
                        if layers.name() == items[0] and items[2] == QtCore.Qt.Checked: #(QtCore.Qt.Checked == 2)
                            pos = get_value_pos(parametres, layers.fields().names())
                            # récupère les informations des couches
                            if self.selected == 1:
                                layer = layers.selectedFeatures()
                            else:
                                layer = layers.getFeatures()
                            for f in layer:
                                # mets a jour le progrès de la bar de progrès
                                geom = f.geometry()
                                if reconciliation(self, geom) == 2:
                                    continue
                                for part in geom.parts():
                                    attributs = f.attributes()
                                    bar.setValue(int(items_done))
                                    for otherf in layers.getFeatures():
                                        if otherf.id() < f.id():
                                            continue
                                        other_attributs = otherf.attributes()
                                        if (len(attributs) == 1 or len(other_attributs) == 1):
                                            continue
                                        othergeom = otherf.geometry()
                                        for otherpart in othergeom.parts():
                                            temp = func(attributs[pos], other_attributs[pos], f.id(), otherf.id())
                                            if temp == True:
                                                if self.control_layer_found == False:
                                                    self.affichage_controles.create_controlpoint_layer()
                                                coords = tuple(zip(*[map(float, re.findall(r'\-?[0-9]+(?:\.[0-9]*)?', part.centroid().asWkt()))] * nb_for_tuple(self, part.centroid().asWkt())))
                                                othercoords = tuple(zip(*[map(float, re.findall(r'\-?[0-9]+(?:\.[0-9]*)?', otherpart.centroid().asWkt()))] * nb_for_tuple(self, otherpart.centroid().asWkt())))
                                                locations = [coords[0], othercoords[0]]
                                                for controles in locations:
                                                    if (controles in done):
                                                        break
                                                    done.append(controles)
                                                    with edit(self.controlpoint_layer):
                                                        test = []
                                                        test.append(attributs)
                                                        test.append(layers.fields().names())
                                                        ctrl = QgsFeature()
                                                        ctrl.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(controles[0], controles[1])))
                                                        ctrl.setAttributes([importance, "Géométrie", "objet d'identifient {} sur la couche {} possède le même attribut que l'objet avec l'identifiant {}".format(f.id(), layers.name(), otherf.id()), layers.name(), test])
                                                        self.controlpoint_layer.dataProvider().addFeature(ctrl)
                                                        self.controlpoint_layer.updateExtents()
                                            temp = False
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
                self.iface.messageBar().pushMessage("Info", "Contrôle {} impossible: il n'y a pas d'objets. Passage au suivant".format(str(nom_controle)), level=Qgis.Warning, duration=10)
                self.controles_restants += 1
                for things in self.organisation:
                    if nom_controle in things:
                        things[1] = 0
                return 2