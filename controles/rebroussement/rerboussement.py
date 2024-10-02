# coding=utf-8
import os
from qgis.core import *
from qgis.utils import iface
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
            #gestion d'erreur pour un angle invalide (dans ce cas si angle est plus grand de 50° ou plus petit que 1°)
            if (angle > 50 or angle < 1):
                angle = 10
                self.iface.messageBar().pushMessage("Attention", "paramètre d'angle invalide".format(str(filename)), level=Qgis.Critical, duration=10)

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


# récupère le nombre total d'objets sur le quel le contrôle va travailler (actuellement tout)
def get_quantity(self):
    quantity = 0
    canvas = qgis.utils.iface.mapCanvas() 
    allLayers = canvas.layers()
    for layers in allLayers:
        for items in self.couche_list:
            # si la couche est présente dans la liste et qu'elle est cochée 
            if layers.name() == items[0] and items[2] == QtCore.Qt.Checked: #(QtCore.Qt.Checked == 2)
                # récupère les informations des couches
                for f in layers.getFeatures():
                    geom = f.geometry()
                    for part in geom.parts():
                        quantity += 1
    return quantity
                        


# execution du controle
def rebroussement(self):
    nom_controle = "rebroussement"
    items_done = 0
    for i in range (self.dlg3.listView.model().rowCount()):
        # vérifie si le contrôle "rebroussement" est coché
        if self.dlg3.listView.model().item(i).text() == nom_controle and self.dlg3.listView.model().item(i).checkState() == 2:
            # informe l'utilisateur le lancement du contrôle
            self.iface.messageBar().pushMessage("Info", "Contrôle {} lancé".format(str(nom_controle)), level=Qgis.Info)
            # récupère les paramètres si possible
            parametres = read(self)
            # créé une bar de progrès avec pour total le nombre d'objets à faire
            bar = QProgressDialog("Contrôle {} en cours".format(str(nom_controle)), "Cancel", 0, 100)
            bar.setWindowModality(QtCore.Qt.WindowModal)
            quantity = get_quantity(self)
            # récupère les couches chargées et cochées sur qgis
            canvas = qgis.utils.iface.mapCanvas() 
            allLayers = canvas.layers()
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
                            # attributes = f.attributes()
                            # print(attributes)
                            # print('Area :', geom.area())
                            # print('Perimeter :', geom.length())
                            # print('Type :', QgsWkbTypes.displayString(geom.wkbType()))
                            # récupère les informations nécéssaires dans la géométrie tel que le nom, le type, et les points 
                            for part in geom.parts():
                                # mets a jour le progrès de la bar de progrès
                                bar.setValue(int(items_done / quantity * 100))
                                # mets comme type de données l'ESPG 2154
                                part.transform(QgsCoordinateTransform(
                                    QgsCoordinateReferenceSystem("EPSG:4326"),
                                    QgsCoordinateReferenceSystem("EPSG:2154"),
                                    QgsProject.instance()))
                                # parse le WKT de la géométrie pour avoir accès a chaque chiffre en tant que floats
                                nums = re.findall(r'[0-9]+(?:\.[0-9]*)?', part.asWkt().rpartition(',')[0]) # regex cherche entre chaque virgule: au moins un chiffre, puis un point, puis une chiffre si il y en a un, avec des parenthèses optionellement
                                coords = tuple(zip(*[map(float, nums)] * 2)) #récupère les coordonnées en float et les ajoutes dans un tableau de floats pour une utilisation facile des données antérieurement
                                # lance le controle rebroussement
                                rebroussement_ctrl(parametres[0], parametres[1], coords)
                                items_done += 1
                                if (bar.wasCanceled()):
                                    self.iface.messageBar().pushMessage("Info", "Contrôles annulés", level=Qgis.Info)
                                    return 1
            self.iface.messageBar().pushMessage("Info", "Contrôle {} terminé".format(str(nom_controle)), level=Qgis.Info)
            
