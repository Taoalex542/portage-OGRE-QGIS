#1
import os
from qgis.core import QgsGeometry, QgsProject, Qgis, QgsWkbTypes, QgsFeature, QgsPointXY, edit
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

        if line_number != 0:
            return parametres[0]
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
                for f in layers.getFeatures():
                    geom = f.geometry()
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

# execution du controle
def attributs(self, func):
    nom_controle = "attributs"
    done = []
    for item in self.dlg_controles.treeWidget.findItems("attributs", QtCore.Qt.MatchRecursive):
        # vérifie si le contrôle "attributs" est coché et si il existe des objets de type Ligne
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
                bar = QProgressDialog("Contrôle {0} en cours\nContrôle {1}/{2}".format(str(nom_controle), int(self.controles_restants + 1), int(self.controles_actifs)), "Cancel", 0, quantity)
                bar.setWindowModality(QtCore.Qt.WindowModal)
                bar.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
                # récupère les couches chargées et cochées sur qgis
                allLayers = QgsProject.instance().mapLayers().values()
                # parcours des couches
                for layers in allLayers:
                    # parcours la liste actuelle des couches
                    for items in self.couche_list:
                        # si la couche est présente dans la liste et qu'elle est cochée 
                        if layers.name() == items[0] and items[2] == QtCore.Qt.Checked: #(QtCore.Qt.Checked == 2)
                            pos = get_value_pos(parametres, layers.fields().names())
                            # récupère les informations des couches
                            for f in layers.getFeatures():
                                # mets a jour le progrès de la bar de progrès
                                geom = f.geometry()
                                for part in geom.parts():
                                    attributs = f.attributes()
                                    bar.setValue(int(items_done))
                                    for otherf in layers.getFeatures():
                                        if otherf.id() < items_done:
                                            continue
                                        other_attributs = otherf.attributes()
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
                                                        ctrl.setAttributes(["Géométrie", "objet d'identifient {} sur la couche {} possède le même attribut que l'objet avec l'identifiant {}".format(f.id(), layers.name(), otherf.id()), layers.name(), test])
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
                return 0
            else:
                self.iface.messageBar().clearWidgets()
                self.iface.messageBar().pushMessage("Info", "Contrôle {} impossible: il n'y a pas d'objets. Passage au suivant".format(str(nom_controle)), level=Qgis.Warning, duration=10)
                self.controles_restants += 1
                return 2