# coding=utf-8
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
    valeur = 0

    if os.path.isfile(filename):
        f = open(filename)
        for line in f:
            parametres.append(line)
            line_number += 1
        f.close()

        if line_number >= 1:
            # lis la première ligne pour le paramètre de la valeur contenu dans paramètre[0]
            # si le paramètre est autre chose qu'un chiffre pu un retour à la ligne (\n) il redevient à son état de base et arrète de lire
            for characters in parametres[0]:
                if ((characters < '0' or characters > '9') and characters != '\n'):
                    self.iface.messageBar().clearWidgets()
                    self.iface.messageBar().pushMessage("Attention", "paramètre de valeur invalide".format(str(filename)), level=Qgis.Critical, duration=10)
                    valeur = 10
                    break
            if (valeur == 0):
                valeur = int(parametres[0])
            # gestion d'erreur pour une valeur invalide (dans ce cas si valeur est plus grand de 50)
            if (valeur > 50):
                valeur = 10
                self.iface.messageBar().clearWidgets()
                self.iface.messageBar().pushMessage("Attention", "paramètre de valeur invalide".format(str(filename)), level=Qgis.Critical, duration=10)
        else:
            valeur = 10
        parametres = [valeur]
        return parametres
    else:
        self.iface.messageBar().clearWidgets()
        self.iface.messageBar().pushMessage("Attention", "{} n'a pas pu être ouvert".format(str(filename)), level=Qgis.Critical, duration=10)
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
                        if ("LineString" in QgsWkbTypes.displayString(part.wkbType()) and "Polygon" not in QgsWkbTypes.displayString(part.wkbType())):
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
def auto_intersection(self, func):
    nom_controle = "auto intersection"
    # objets_controle = ["limite_administrative", "ligne_frontalière", "tronçon_hydrographique", "limite_terre_mer"
    #            , "histolitt", "ligne_électrique", "canalisation", "construction_linéaire", "ligne_orographique"
    #            , "troncon_de_route", "densification_des_chemins", "tronçon_de_voie_ferrée", "transport_par_câble", "voie_de_triage"
    #            , "itinéraire_ski_de_randonnée", "haie", "ligne_caractéristique", "limites_diverses", "modification_d_attribut"]
    for item in self.dlg_controles.treeWidget.findItems("auto intersection", QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive):
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
                parametres = read(self)
                # créé une barre de progrès avec pour total le nombre d'objets à faire, et en information supplémentaire le nombre de contrôle total à faire et le numéro de contrôle actif
                bar = QProgressDialog("Contrôle {0} en cours\nContrôle {1}/{2}".format(str(nom_controle), int(self.controles_restants), int(self.controles_actifs)), "Cancel", 0, 100)
                bar.setWindowModality(QtCore.Qt.WindowModal)
                bar.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
                # récupère les couches chargées et cochées sur qgis
                allLayers = QgsProject.instance().mapLayers().values()
                prev = []
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
                                # print('Area :', geom.area())
                                # print('Perimeter :', geom.length())
                                # print('Type :', QgsWkbTypes.displayString(geom.wkbType()))
                                # récupère les informations nécéssaires dans la géométrie tel que le nom, le type, et les points
                                for part in geom.parts():
                                    # mets a jour le progrès de la bar de progrès
                                    if ("LineString" not in QgsWkbTypes.displayString(part.wkbType()) and "Polygon" not in QgsWkbTypes.displayString(part.wkbType())):
                                        break
                                    bar.setValue(int(items_done / quantity * 100))
                                    # mets comme type de données l'ESPG 2154
                                    # part.transform(QgsCoordinateTransform(
                                    #     QgsCoordinateReferenceSystem("IGNF:LAMB93"),
                                    #     QgsCoordinateReferenceSystem("EPSG:2154"),
                                    #     QgsProject.instance()))
                                    # parse le WKT de la géométrie pour avoir accès a chaque chiffre en tant que floats
                                    print(part.asWkt())
                                    return
                                    nums = re.findall(r'\-?[0-9]+(?:\.[0-9]*)?', part.asWkt()) # regex cherche entre chaque virgule: au moins un chiffre, puis un point, puis une chiffre si il y en a un, avec des parenthèses optionellement
                                    coords = tuple(zip(*[map(float, nums)] * nb_for_tuple(self, part.asWkt()))) # récupère les coordonnées en float et les ajoutes dans un tableau de floats pour une utilisation facile des données antérieurement
                                    # lance le controle rebroussement
                                    temp = func(parametres, coords)
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