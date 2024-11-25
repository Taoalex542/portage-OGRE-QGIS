# coding=utf-8
import os
from qgis.core import QgsGeometry, QgsProject, Qgis, QgsFeature, QgsPointXY, edit, QgsMapLayer
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
    todo = []
    line_number = 0
    # lis le fichier
    if os.path.isfile(filename):
        f = open(filename)
        for line in f:
            temp.append(line)
            line_number += 1
        f.close()
        # pour chaque lignes
        for i in range (len(temp) - 4):
            values = []
            params = temp[i + 4].split(" : ")
            # regardes si il y a bien deux parties, et seulment 2
            if (len(params) != 2):
                self.iface.messageBar().pushMessage("Attention", "Erreur dans la lecture de la ligne {} du paramétrage: cette ligne sera ignorée".format(i + 3), level=Qgis.Warning, duration=10)
                continue
            # partie du parent
            # coupe la string en deux
            parent = params[0].split(" -- ")
            lparent = len(parent)
            if lparent == 1 and '-' in parent[0]:
                self.iface.messageBar().pushMessage("Attention", "Erreur dans le parsage de la ligne {} du paramétrage: cette ligne sera ignorée".format(i + 3), level=Qgis.Warning, duration=10)
                continue
            # récupère les attributs du parent
            for layers in QgsProject.instance().mapLayers().values():
                if layers.name() == parent[0]:
                    attributs = layers.fields().names()
                    break
            # si l'attribut voulu n'a pas été trouvé 
            if lparent == 2 and parent[1] not in attributs:
                self.iface.messageBar().pushMessage("Attention", "Attribut {} pour la variable {} non trouvé dans la ligne {} du paramétrage: cette ligne sera ignorée".format(parent[1], parent[0], i + 3), level=Qgis.Warning, duration=10)
                continue
            # partie des enfants 
            enfant = []
            # récupère chaque enfant
            for objects in params[1].split(" ; "):
                # coupe la string en deux
                enfant.append(objects.split(" -- "))
            lenfant = len(enfant)
            # si il n'y a pas d'enfants
            if lenfant < 1:
                self.iface.messageBar().pushMessage("Attention", "Valeurs à comparer non trouvées dans la ligne {} du paramétrage: cette ligne sera ignorée".format(i + 3), level=Qgis.Warning, duration=10)
                continue
            # enlève le retour à la ligne de la dernière variable
            if len(enfant[lenfant - 1]) == 1:
                place = 0
            else:
                place = 1
            enfant[lenfant - 1][place] = enfant[lenfant - 1][place].replace("\n", "")
            # active les enfants si toutes les variables sont ok
            for item in self.dlg_couches.treeWidget.findItems(parent[0], QtCore.Qt.MatchRecursive):
                if item.checkState(0) == 2 and see_if_ok(self, enfant, i) == 0:
                    for j in range (lenfant):
                        if (len(enfant[j]) == 1):
                            for objects in self.dlg_precis.treeWidget.findItems(enfant[j][0], QtCore.Qt.MatchRecursive):
                                objects.setCheckState(0, 2)
                            continue
                        for objects in self.dlg_precis.treeWidget.findItems(enfant[j][0], QtCore.Qt.MatchRecursive):
                            objects.setCheckState(0, 2)
                        if (lparent == 2):
                            # ajoute les valeurs dans la liste des choses à checker
                            if (values == [] and len (parent) == 2):
                                values.append(tuple((parent[0], parent[1])))
                            values.append(tuple((enfant[j][0], enfant[j][1])))
            if values != []:
                todo.append(values)
    return todo

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
                if self.selected == 1:
                    layer = layers.selectedFeatures()
                else:
                    layer = layers.getFeatures()
                for f in layer:
                    geom = f.geometry()
                    for part in geom.parts():
                        quantity += 1
    return quantity

# récupère le nombre de tuples nécéssaire
def nb_for_tuple(self, str):
    nb = 0
    i = 0
    while str[i] != ',' and str[i] != ')':
        if str[i] == ' ':
            nb += 1
        i += 1
    return nb

# vérifie si la couche est présente dans les choses à comparer
def has_settings(param, name):
    for item in param:
        if isinstance(item, list):
            for things in item:
                if name == things[0]:
                    return things[1]
    return None

# récupère la position de l'attribut désiré dans la liste des attributs
def get_value_pos(param, names):
    nb = 0
    if param == None:
        return None
    for name in names:
        if param == name:
            return nb
        nb += 1
    if nb == len(names) - 1:
        nb = None
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
                                attributs = f.attributes()
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
                                        if otherLayers.type() == QgsMapLayer.RasterLayer:
                                            continue
                                        if otherLayers.name() not in self.precis_intersection:
                                            continue
                                        if self.selected == 1:
                                            olayer = otherLayers.selectedFeatures()
                                        else:
                                            olayer = otherLayers.getFeatures()
                                        for otherf in olayer:
                                            otherAttributs = otherf.attributes()
                                            otherGeom = otherf.geometry()
                                            for otherPart in otherGeom.parts():
                                                if (layers.name() == otherLayers.name() and otherf.id() < f.id()):
                                                    continue
                                                othernums = re.findall(r'\-?[0-9]+(?:\.[0-9]*)?', otherPart.asWkt())
                                                othercoords = tuple(zip(*[map(float, othernums)] * nb_for_tuple(self, otherPart.asWkt())))
                                                parametres = []
                                                # ajoute les paramètres dans la variable paramètres
                                                settings = has_settings(self.precis_intersection, layers.name())
                                                if settings != None:
                                                    parametres.append(attributs[get_value_pos(settings, layers.fields().names())])
                                                else:
                                                    parametres.append(None)
                                                othersettings = has_settings(self.precis_intersection, otherLayers.name())
                                                if othersettings != None:
                                                    parametres.append(otherAttributs[get_value_pos(othersettings, otherLayers.fields().names())])
                                                else:
                                                    parametres.append(None)
                                                # controle
                                                temp = func(parametres, coords, othercoords)
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
                                                            if f.id() == otherf.id():
                                                                ctrl.setAttributes(["Géométrie", "{} identifiant {} s'auto-intersecte".format(layers.name(), f.id()), layers.name(), test])
                                                            else:
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