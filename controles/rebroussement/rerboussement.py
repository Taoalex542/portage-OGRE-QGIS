# coding=utf-8
import os
from qgis.core import *
from qgis import *
from qgis.PyQt.QtWidgets import QProgressDialog
from .ctrl import rebroussement_ctrl
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
            # lis la première ligne pour le paramètre de l'angle contenu dans paramètre[0]
            # si le paramètre est autre chose qu'un chiffre pu un retour à la ligne (\n) il redevient à son état de base et arrète de lire
            for characters in parametres[0]:
                if ((characters < '0' or characters > '9') and characters != '\n'):
                    self.iface.messageBar().pushMessage("Attention", "paramètre d'angle invalide".format(str(filename)), level=Qgis.Critical, duration=10)
                    angle = 10
                    break
            if (angle == 0):
                angle = int(parametres[0])
            # gestion d'erreur pour un angle invalide (dans ce cas si angle est plus grand de 50° ou plus petit que 1°)
            if (angle > 50 or angle < 1):
                angle = 10
                self.iface.messageBar().pushMessage("Attention", "paramètre d'angle invalide".format(str(filename)), level=Qgis.Critical, duration=10)

            # lis la deuxième ligne (si elle existe) de la même manière que la première
            if line_number >= 2:
                for characters in parametres[1]:
                    if ((characters < '0' or characters > '9') and characters != '\n' and characters !='.'):
                        self.iface.messageBar().pushMessage("Attention", "paramètre de distance minimale invalide".format(str(filename)), level=Qgis.Critical, duration=10)
                        distance = 0.01
                        break
                if (distance == 0):
                    distance = float(parametres[1])
            else:
                distance = 0.01
        else:
            angle = 10
            distance = 0.01
        
        parametres = [angle, distance]
        return parametres
    else:
        self.iface.messageBar().pushMessage("Attention", "{} n'a pas pu être ouvert".format(str(filename)), level=Qgis.Critical, duration=10)
        return [10, 0.01]

def get_info_in_groups(self, parent, objets_controle, quantity):
    for items in self.couche_list:
        for childs in parent.children():
            if childs.name() == items[0] and items[2] == QtCore.Qt.Checked and childs.name() in objets_controle:
                for f in childs.getFeatures():
                    geom = f.geometry()
                    for part in geom.parts():
                        quantity += 1

# récupère le nombre total d'objets sur le quel le contrôle va travailler (actuellement seul les lignes)
def get_quantity(self, objets_controle):
    quantity = 0
    allLayers = QgsProject.instance().mapLayers().values()
    for layers in allLayers:
        for items in self.couche_list:
            if(type(layers) == qgis._core.QgsLayerTreeGroup):
                get_info_in_groups(self, layers, objets_controle, quantity)
                continue
            # si la couche est présente dans la liste et qu'elle est cochée et qu'elle est présente dans les objets voulu
            if layers.name() == items[0] and items[2] == QtCore.Qt.Checked and layers.name() in objets_controle: #(QtCore.Qt.Checked == 2)
                # récupère les informations des couches
                for f in layers.getFeatures():
                    geom = f.geometry()
                    for part in geom.parts():
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

# execution du controle
def rebroussement(self):
    nom_controle = "rebroussement"
    objets_controle = ["limite_administrative", "ligne_frontalière", "tronçon_hydrographique", "limite_terre_mer"
               , "histolitt", "ligne_électrique", "canalisation", "construction_linéaire", "ligne_orographique"
               , "troncon_de_route", "densification_des_chemins", "tronçon_de_voie_ferrée", "transport_par_câble", "voie_de_triage"
               , "itinéraire_ski_de_randonnée", "haie", "ligne_caractéristique", "limites_diverses", "modification_d_attribut"]
    for item in self.dlg_controles.treeWidget.findItems("rebroussement", QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive):
        # vérifie si le contrôle "rebroussement" est coché et si il existe des objets de type Ligne
        if item.checkState(0) == 2:
            items_done = 0
            quantity = get_quantity(self, objets_controle)
            print("nombre d'objets", quantity)
            if quantity > 0:
                # informe l'utilisateur le lancement du contrôle
                self.iface.messageBar().pushMessage("Info", "Contrôle {} lancé".format(str(nom_controle)), level=Qgis.Info)
                # récupère les paramètres si possible
                parametres = read(self)
                # créé une barre de progrès avec pour total le nombre d'objets à faire, et en information supplémentaire le nombre de contrôle total à faire et le numéro de contrôle actif
                bar = QProgressDialog("Contrôle {0} en cours\nContrôle {1}/{2}".format(str(nom_controle), int(self.controles_restants), int(self.controles_actifs)), "Cancel", 0, 100)
                bar.setWindowModality(QtCore.Qt.WindowModal)
                bar.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
                # récupère les couches chargées et cochées sur qgis
                allLayers = QgsProject.instance().mapLayers().values()
                # parcours des couches
                for layers in allLayers:
                    # parcours la liste actuelle des couches
                    for items in self.couche_list:
                        # si la couche est présente dans la liste et qu'elle est cochée 
                        if layers.name() == items[0] and items[2] == QtCore.Qt.Checked and layers.name() in objets_controle: #(QtCore.Qt.Checked == 2)
                            # récupère les informations des couches
                            print(layers.name())
                            for f in layers.getFeatures():
                                # récupère la géométrie dans ces infos
                                geom = f.geometry()
                                attributes = f.attributes()
                                # print('Area :', geom.area())
                                # print('Perimeter :', geom.length())
                                # print('Type :', QgsWkbTypes.displayString(geom.wkbType()))
                                # récupère les informations nécéssaires dans la géométrie tel que le nom, le type, et les points
                                for part in geom.parts():
                                    # mets a jour le progrès de la bar de progrès
                                    bar.setValue(int(items_done / quantity * 100))
                                    # mets comme type de données l'ESPG 2154
                                    # part.transform(QgsCoordinateTransform(
                                    #     QgsCoordinateReferenceSystem("IGNF:LAMB93"),
                                    #     QgsCoordinateReferenceSystem("EPSG:2154"),
                                    #     QgsProject.instance()))
                                    # parse le WKT de la géométrie pour avoir accès a chaque chiffre en tant que floats
                                    nums = re.findall(r'\-?[0-9]+(?:\.[0-9]*)?', part.asWkt()) # regex cherche entre chaque virgule: au moins un chiffre, puis un point, puis une chiffre si il y en a un, avec des parenthèses optionellement
                                    coords = tuple(zip(*[map(float, nums)] * nb_for_tuple(self, part.asWkt()))) # récupère les coordonnées en float et les ajoutes dans un tableau de floats pour une utilisation facile des données antérieurement
                                    # lance le controle rebroussement
                                    temp = rebroussement_ctrl(parametres[0], parametres[1], coords)
                                    if temp != None:
                                        if self.control_layer_found == False:
                                            self.create_controlpoint_layer()
                                        for controles in temp:
                                            ctrl = QgsFeature()
                                            ctrl.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(controles[0], controles[1])))
                                            ctrl.setAttributes(["Géométrie", "Rebroussement", attributes])
                                            self.provider.addFeature(ctrl)
                                            self.controlpoint_layer.updateExtents() 
                                            QgsProject.instance().addMapLayer(self.controlpoint_layer)
                                    temp = []
                                    items_done += 1
                                    if (bar.wasCanceled()):
                                        self.iface.messageBar().pushMessage("Info", "Contrôles annulés", level=Qgis.Info, duration=5)
                                        return 1
                self.iface.messageBar().pushMessage("Info", "Contrôle {} terminé".format(str(nom_controle)), level=Qgis.Success, duration=5)
                self.controles_restants += 1
                return 0
            else:
                self.iface.messageBar().pushMessage("Info", "Contrôle {} impossible: il n'y a pas d'objets de type \"Ligne\". Passage au suivant".format(str(nom_controle)), level=Qgis.Warning, duration=10)
                self.controles_restants += 1
                return 2

# canalisation
# ['934352.30000000004656613', '6849376.59999999962747097', '-1000']
# ((934352.3, 6849376.6, -1000.0),)
# LineStringZ (934352.30000000004656613 6849376.59999999962747097 -1000, 934352.09999999997671694 6849364 -1000)

# troncon_de_route
# ['933836', '6846096.79999999981373549', '226.80000000000001137', '933843.80000000004656613', '6846103', '226.59999999999999432']
# ((933836.0, 6846096.8, 226.8), (933843.8, 6846103.0, 226.6))
# LineStringZ (933836 6846096.79999999981373549 226.80000000000001137, 933843.80000000004656613 6846103 226.59999999999999432, 933851 6846108.90000000037252903 226.40000000000000568)

# troncon_de_route
# ['933836', '6846096.79999999981373549', '226.80000000000001137', '933843.80000000004656613', '6846103', '226.59999999999999432']
# ((933836.0, 6846096.8, 226.8), (933843.8, 6846103.0, 226.6))
# LineStringZ (933836 6846096.79999999981373549 226.80000000000001137, 933843.80000000004656613 6846103 226.59999999999999432
# LineStringZ (933836 6846096.79999999981373549 226.80000000000001137, 933843.80000000004656613 6846103 226.59999999999999432, 933851 6846108.90000000037252903 226.40000000000000568)

# troncon_de_route
# ['933836', '6846096.79999999981373549', '226.80000000000001137', '933843.80000000004656613', '6846103', '226.59999999999999432', '933851', '6846108.90000000037252903', '226.40000000000000568']
# ((933836.0, 6846096.8, 226.8), (933843.8, 6846103.0, 226.6), (933851.0, 6846108.9, 226.4))
# LineStringZ (933836 6846096.79999999981373549 226.80000000000001137, 933843.80000000004656613 6846103 226.59999999999999432
# LineStringZ (933836 6846096.79999999981373549 226.80000000000001137, 933843.80000000004656613 6846103 226.59999999999999432, 933851 6846108.90000000037252903 226.40000000000000568)

# exemple avec canalisation[0]
# part.asWkt().rpartition(',')[0]                                                         =>  LineStringZ (934352.30000000004656613 6849376.59999999962747097 -1000
# part.asWkt()                                                                            =>  LineStringZ (934352.30000000004656613 6849376.59999999962747097 -1000, 934352.09999999997671694 6849364 -1000)
# re.findall(r'\-?[0-9]+(?:\.[0-9]*)?', part.asWkt())                                     =>  ['934352.30000000004656613', '6849376.59999999962747097', '-1000', '934352.09999999997671694', '6849364', '-1000']
# tuple(zip(*[map(float, REGEX^)] * nb_for_tuple(self, part.asWkt())))                    =>  ((934352.3, 6849376.6, -1000.0), (934352.1, 6849364.0, -1000.0))
# valeurs au mètre, avec une précision de 10cm au total (échelle de précision l'ign)