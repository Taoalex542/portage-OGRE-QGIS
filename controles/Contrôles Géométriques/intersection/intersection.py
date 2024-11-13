#1
import os
from qgis.core import QgsGeometry, QgsProject, Qgis, QgsWkbTypes, QgsFeature, QgsPointXY, edit
from qgis import QtCore
from qgis.PyQt.QtWidgets import QProgressDialog
import re

def see_if_ok(self, enfant, i):
    for j in range (len(enfant)):
        for layers in QgsProject.instance().mapLayers().values():
            if layers.name() == enfant[j][0]:
                attributs = layers.fields().names()
                break
        if len(enfant[j]) > 1 and enfant[j][1] not in attributs :
            self.iface.messageBar().pushMessage("Attention", "Attribut {} pour la variable {} non trouvé dans la ligne {} du paramétrage: cette ligne sera ignorée".format(enfant[j][1], enfant[j][0], i + 3), level=Qgis.Warning, duration=10)
            return 1
    return 0

# lecture du fichier param.txt pour les paramètres du controles
# récupère les lignes à partir de la quatrième, et parses les paramètres
# la partie à gauche du : est le "parent", si il est trouvé et valide, coches les valeurs à droite si elles sont valides
def get_params(self):
    filename = (os.path.dirname(os.path.realpath(__file__)) + "\\param.txt")
    temp = []
    line_number = 0
    if os.path.isfile(filename):
        f = open(filename)
        for line in f:
            temp.append(line)
            line_number += 1
        f.close()
        for i in range (len(temp) - 3):
            params = temp[i + 3].split(" : ")
            # regardes si il y à bien deux parties, et seuelemnt 2
            if (len(params) != 2):
                self.iface.messageBar().pushMessage("Attention", "Erreur dans la lecture de la ligne {} du paramétrage: cette ligne sera ignorée".format(i + 3), level=Qgis.Warning, duration=10)
                continue
            # partie du parent
            parent = params[0].split(" -- ")
            for layers in QgsProject.instance().mapLayers().values():
                if layers.name() == parent[0]:
                    attributs = layers.fields().names()
                    break
            if parent[1] not in attributs:
                self.iface.messageBar().pushMessage("Attention", "Attribut {} pour la variable {} non trouvé dans la ligne {} du paramétrage: cette ligne sera ignorée".format(parent[1], parent[0], i + 3), level=Qgis.Warning, duration=10)
                continue
            # partie des enfants 
            enfant = []
            for objects in params[1].split(" ; "):
                enfant.append(objects.split(" -- "))
            if len(enfant) < 1:
                self.iface.messageBar().pushMessage("Attention", "Valeurs à comparer non trouvéés dans la ligne {} du paramétrage: cette ligne sera ignorée".format(i + 3), level=Qgis.Warning, duration=10)
                continue
            # enlève le retour à la ligne de la dernière variable
            if len(enfant[len(enfant) - 1]) == 1:
                place = 0
            else:
                place = 1
            for j in range(len(enfant[len(enfant) - 1][place])):
                if (enfant[len(enfant) - 1][place][j] == '\n'):
                    enfant[len(enfant) - 1][place] = enfant[len(enfant) - 1][place][:j] + '' + enfant[len(enfant) - 1][place][j + 1:]
            # active les enfants si toutes les variables sont ok
            for item in self.dlg_couches.treeWidget.findItems(parent[0], QtCore.Qt.MatchRecursive):
                if item.checkState(0) == 2 and see_if_ok(self, enfant, i) == 0:
                    for j in range (len(enfant)):
                        if (len(enfant[j]) == 1):
                            for objects in self.dlg_precis.treeWidget.findItems(enfant[j][0], QtCore.Qt.MatchRecursive):
                                objects.setCheckState(0, 2)
                            continue
                        for objects in self.dlg_precis.treeWidget.findItems(enfant[j][0], QtCore.Qt.MatchRecursive):
                            objects.setCheckState(0, 2)   
    return

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

        if line_number >= 1:
            return parametres
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
def intersection(self, func):
    nom_controle = "intersection"
    for item in self.dlg_controles.treeWidget.findItems("intersection", QtCore.Qt.MatchRecursive):
        # vérifie si le contrôle "intersection" est coché et si il existe des objets de type Ligne
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
                            # récupère les informations des couches
                            for f in layers.getFeatures():
                                # récupère la géométrie dans ces infos
                                geom = f.geometry()
                                # récupère les informations nécéssaires dans la géométrie tel que le nom, le type, et les points
                                for part in geom.parts():
                                    # mets a jour le progrès de la bar de progrès
                                    bar.setValue(items_done)
                                    # parse le WKT de la géométrie pour avoir accès a chaque chiffre en tant que floats
                                    nums = re.findall(r'\-?[0-9]+(?:\.[0-9]*)?', part.asWkt()) # regex cherche entre chaque virgule: au moins un chiffre, puis un point, puis une chiffre si il y en a un, avec des parenthèses optionellement
                                    coords = tuple(zip(*[map(float, nums)] * nb_for_tuple(self, part.asWkt()))) # récupère les coordonnées en float et les ajoutes dans un tableau de floats pour une utilisation facile des données antérieurement
                                    # lance le controle rebroussement
                                    for otherLayers in allLayers:
                                        if otherLayers.name() not in self.precis_intersection:
                                            continue
                                        for otherf in otherLayers.getFeatures():
                                            otherGeom = otherf.geometry()
                                            for otherPart in otherGeom.parts():
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
                                                            ctrl.setAttributes(["Géométrie", "{} identifiant {} inersecte avec {} identifiant {}".format(layers.name(), f.id(), otherLayers.name(), otherf.id()), layers.name(), test])
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
                return 0
            else:
                self.iface.messageBar().clearWidgets()
                self.iface.messageBar().pushMessage("Info", "Contrôle {} impossible: il n'y a pas d'objets de type \"Ligne\". Passage au suivant".format(str(nom_controle)), level=Qgis.Warning, duration=10)
                self.controles_restants += 1
                return 2