#0
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
    angle = 0
    distance = 0
    if os.path.isfile(filename):
        f = open(filename)
        for line in f:
            parametres.append(line)
            line_number += 1
        f.close()

        if line_number >= 1:
            return[]
        return [0]

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
                        if ("LineString" in QgsWkbTypes.displayString(part.wkbType())):
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

# execution du controle
def controle_vide(self, func):
    nom_controle = "contrôle vide"
    for item in self.dlg_controles.treeWidget.findItems("controle vide", QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive):
        # vérifie si le contrôle "contrôle vide" est coché et si il existe des objets de type Ligne
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
                bar = QProgressDialog("Contrôle {0} en cours\nContrôle {1}/{2}".format(str(nom_controle), int(self.controles_restants + 1), int(self.controles_actifs)), "Cancel", 0, 100)
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
                            # récupère les informations des couches
                            # print(layers.fields().names())
                            for f in layers.getFeatures():
                                # récupère la géométrie dans ces infos
                                geom = f.geometry()

                                # récupère les informations nécéssaires dans la géométrie tel que le nom, le type, et les points
                                for part in geom.parts():
                                    # mets a jour le progrès de la bar de progrès
                                    if ("LineString" not in QgsWkbTypes.displayString(part.wkbType())):
                                        break
                                    bar.setValue(int(items_done / quantity * 100))
                                    # parse le WKT de la géométrie pour avoir accès a chaque chiffre en tant que floats
                                    nums = re.findall(r'\-?[0-9]+(?:\.[0-9]*)?', part.asWkt()) # regex cherche entre chaque virgule: au moins un chiffre, puis un point, puis une chiffre si il y en a un, avec des parenthèses optionellement
                                    coords = tuple(zip(*[map(float, nums)] * nb_for_tuple(self, part.asWkt()))) # récupère les coordonnées en float et les ajoutes dans un tableau de floats pour une utilisation facile des données antérieurement
                                    # lance le controle rebroussement
                                    for otherLayers in allLayers:
                                        for otherf in otherLayers.getFeatures():
                                            otherGeom = otherf.geometry()
                                            for otherPart in otherGeom.parts():
                                                if ("LineString" not in QgsWkbTypes.displayString(otherPart.wkbType())):
                                                    break
                                                othernums = re.findall(r'\-?[0-9]+(?:\.[0-9]*)?', otherPart.asWkt())
                                                othercoords = tuple(zip(*[map(float, othernums)] * nb_for_tuple(self, otherPart.asWkt())))
                                                temp = func(parametres[0], coords, othercoords)
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
                                                            ctrl.setAttributes(["Géométrie", "contrôle vide", layers.name(), test])
                                                            self.controlpoint_layer.dataProvider().addFeature(ctrl)
                                                            self.controlpoint_layer.updateExtents()
                                                temp = []
                                    items_done += 1
                                    if (bar.wasCanceled()):
                                        self.iface.messageBar().clearWidgets()
                                        self.iface.messageBar().pushMessage("Info", "Contrôle {} annulé".format(str(nom_controle)), level=Qgis.Info, duration=5)
                                        return 1
                self.iface.messageBar().clearWidgets()
                self.iface.messageBar().pushMessage("Info", "Contrôle {} terminé".format(str(nom_controle)), level=Qgis.Success, duration=5)
                self.controles_restants += 1
                return 0
            else:
                self.iface.messageBar().clearWidgets()
                self.iface.messageBar().pushMessage("Info", "Contrôle {} impossible: il n'y a pas d'objets de type \"Ligne\". Passage au suivant".format(str(nom_controle)), level=Qgis.Warning, duration=10)
                self.controles_restants += 1
                return 2