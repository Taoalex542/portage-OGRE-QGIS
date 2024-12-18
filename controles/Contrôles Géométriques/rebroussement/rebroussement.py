# coding=utf-8
import os
from qgis.core import QgsGeometry, QgsProject, Qgis, QgsWkbTypes, QgsFeature, QgsPointXY, edit, QgsMapLayer
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

        if line_number >= 5:
            # lis la première ligne pour le paramètre de l'angle contenu dans paramètre[0]
            # si le paramètre est autre chose qu'un chiffre pu un retour à la ligne (\n) il redevient à son état de base et arrète de lire
            angle = [int(d) for d in re.findall(r'-?\d+',parametres[4])]
            if angle == []:
                angle = 10
                self.iface.messageBar().clearWidgets()
                self.iface.messageBar().pushMessage("Attention", "paramètre d'angle invalide, utilisation de la valeur par défaut".format(str(filename)), level=Qgis.Critical, duration=10)
            else:
                angle = angle[0]
            # gestion d'erreur pour un angle invalide (dans ce cas si angle est plus grand de 50°)
            if (angle > 50):
                angle = 10
                self.iface.messageBar().clearWidgets()
                self.iface.messageBar().pushMessage("Attention", "paramètre d'angle invalide, utilisation de la valeur par défaut".format(str(filename)), level=Qgis.Critical, duration=10)

            # lis la deuxième ligne (si elle existe) de la même manière que la première
            if line_number >= 6:
                distance = [int(d) for d in re.findall(r'-?\d+(?:\.|\,)?\d+',parametres[4])]
                if distance == []:
                    self.iface.messageBar().clearWidgets()
                    self.iface.messageBar().pushMessage("Attention", "paramètre de distance minimale invalide, utilisation de la valeur par défaut".format(str(filename)), level=Qgis.Critical, duration=10)
                    distance = 0.01
                else:
                    distance = distance[0]
            else:
                distance = 0.01
        else:
            angle = 10
            distance = 0.01
        
        parametres = [angle, distance]
        return parametres
    else:
        self.iface.messageBar().clearWidgets()
        self.iface.messageBar().pushMessage("Attention", "{} n'a pas pu être ouvert, utilisation des valeurs par défaut".format(str(filename)), level=Qgis.Critical, duration=10)
        return [10, 0.01]

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
                        if ("LineString" in QgsWkbTypes.displayString(part.wkbType())):
                            quantity += 1
    return quantity

def nb_for_tuple(self, str):
    nb = 0
    i = 0
    while str[i] != ',':
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
def rebroussement(self, func):
    nom_controle = "rebroussement"
    importance = get_att(self, "rebroussement")
    for item in self.dlg_controles.treeWidget.findItems("rebroussement", QtCore.Qt.MatchRecursive):
        # vérifie si le contrôle "rebroussement" est coché et si il existe des objets de type Ligne
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
                                    if ("LineString" not in QgsWkbTypes.displayString(part.wkbType())):
                                        break
                                    bar.setValue(items_done)
                                    # parse le WKT de la géométrie pour avoir accès a chaque chiffre en tant que floats
                                    nums = re.findall(r'\-?[0-9]+(?:\.[0-9]*)?', part.asWkt()) # regex cherche entre chaque virgule: au moins un chiffre, puis un point, puis une chiffre si il y en a un, avec des parenthèses optionellement
                                    coords = tuple(zip(*[map(float, nums)] * nb_for_tuple(self, part.asWkt()))) # récupère les coordonnées en float et les ajoutes dans un tableau de floats pour une utilisation facile des données antérieurement
                                    # lance le controle rebroussement
                                    temp = func(parametres[0], parametres[1], coords)
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
                                                ctrl.setAttributes([importance, "Géométrie", "Rebroussement", layers.name(), test])
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
