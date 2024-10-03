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



# récupère le nombre total d'objets sur le quel le contrôle va travailler (actuellement seul les lignes)
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
                    if (QgsWkbTypes.displayString(geom.wkbType()) == "Line"):
                        for part in geom.parts():
                            quantity += 1
    return quantity
                        


# execution du controle
def rebroussement(self):
    for i in range (self.dlg3.listView.model().rowCount()):
        # vérifie si le contrôle "rebroussement" est coché et si il existe des objets de type Ligne
        nom_controle = "rebroussement"
        items_done = 0
        quantity = get_quantity(self)
        if self.dlg3.listView.model().item(i).text() == nom_controle and self.dlg3.listView.model().item(i).checkState() == 2 and quantity != 0:
            # informe l'utilisateur le lancement du contrôle
            self.iface.messageBar().pushMessage("Info", "Contrôle {} lancé".format(str(nom_controle)), level=Qgis.Info)
            # récupère les paramètres si possible
            parametres = read(self)
            # créé une barre de progrès avec pour total le nombre d'objets à faire, et en information supplémentaire le nombre de contrôle total à faire et le numéro de contrôle actif
            bar = QProgressDialog("Contrôle {0} en cours\nContrôle {1}/{2}".format(str(nom_controle), int(self.dlg3.listView.model().item(i).row() + 1), int(self.dlg3.listView.model().rowCount())), "Cancel", 0, 100)
            bar.setWindowModality(QtCore.Qt.WindowModal)
            bar.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
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
                            attributes = f.attributes()
                            print(attributes)
                            # print('Area :', geom.area())
                            # print('Perimeter :', geom.length())
                            # print('Type :', QgsWkbTypes.displayString(geom.wkbType()))
                            # récupère les informations nécéssaires dans la géométrie tel que le nom, le type, et les points 
                            for part in geom.parts():
                                # mets a jour le progrès de la bar de progrès
                                bar.setValue(int(items_done / quantity * 100))
                                #mets comme type de données l'ESPG 2154
                                # part.transform(QgsCoordinateTransform(
                                #     QgsCoordinateReferenceSystem("IGNF:LAMB93"),
                                #     QgsCoordinateReferenceSystem("EPSG:2154"),
                                #     QgsProject.instance()))
                                # parse le WKT de la géométrie pour avoir accès a chaque chiffre en tant que floats
                                nums = re.findall(r'[0-9]+(?:\.[0-9]*)?', part.asWkt().rpartition(',')[0]) # regex cherche entre chaque virgule: au moins un chiffre, puis un point, puis une chiffre si il y en a un, avec des parenthèses optionellement
                                coords = tuple(zip(*[map(float, nums)] * 2)) #récupère les coordonnées en float et les ajoutes dans un tableau de floats pour une utilisation facile des données antérieurement
                                # lance le controle rebroussement
                                rebroussement_ctrl(parametres[0], parametres[1], coords)
                                items_done += 1
                                if (bar.wasCanceled()):
                                    self.iface.messageBar().pushMessage("Info", "Contrôles annulés", level=Qgis.Info, duration=5)
                                    return 1
            self.iface.messageBar().pushMessage("Info", "Contrôle {} terminé".format(str(nom_controle)), level=Qgis.Info, duration=5)
        else:
            self.iface.messageBar().pushMessage("Info", "Contrôle {} impossible: il n'y a pas d'objets de type \"Ligne\". Passage au suivant".format(str(nom_controle)), level=Qgis.Warning, duration=10)
            
# ['COMMUNE_0000000009738132', 'Guerlesquin', 'GUERLESQUIN', '29067', 'Commune simple', 1273, '20', '3', '29', '53', '242900835']
# BEFORE : <QgsPolygon: Polygon ((213580.29999999998835847 6849033.20000000018626451, 213591.60000000000582077 6848979.09999999962747097, 213612.79999999998835847 6848879, 213617.79999999998835847 6848878.29999999981373549, 213622.70000000001164153 6848876.40000000037252903, 213626.89999999999417923 6848873.20000000018626451, 213637.70000000001164153 6848862.40000000037252903, 213655.5 6848842.40000000037252903, 213669.29999999998835847 6848823.79999999981373549, 213677.79999999998835847 6848810.90000000037252903, 213686.79999999998835847 6848794.90000000037252903, 213691.10000000000582077 6848785.90000000037252903, 213695.89999999999417923 6848776, 213699.60000000000582077 6848769.40000000037252903, 213704.10000000000582077 6848763.79999999981373549, 213709.29999999998835847 6848758.5, 213751.89999999999417923 6848724.59999999962747097, 213759.20000000001164153 6848718.20000000018626451, 213779 6848703.90000000037252903, 213788.20000000001164153 6848696.90000000037252903, 213790.89999999999417923 6848693.599...>
# AFTER (IGNF:LAMB93) : ((213580.3, 6849033.2), (213591.6, 6848979.1), (213612.8, 6848879.0), (213617.8, 6848878.3), (213622.7, 6848876.4), (213626.9, 6848873.2), (213637.7, 6848862.4), (213655.5, 6848842.4), (213669.3, 6848823.8), (213677.8, 6848810.9), (213686.8, 6848794.9), (213691.1, 6848785.9), (213695.9, 6848776.0), (213699.6, 6848769.4), (213704.1, 6848763.8), (213709.3, 6848758.5), (213751.9, 6848724.6), (213759.2, 6848718.2), (213779.0, 6848703.9), (213788.2, 6848696.9), (213790.9, 6848693.6)
# AFTER (ESPG: 2154) : ((213580.29999999987, 6849033.199999998), (213591.59999999998, 6848979.099999999), (213612.79999999993, 6848878.999999999), (213617.79999999987, 6848878.299999999), (213622.7, 6848876.4), (213626.89999999985, 6848873.199999997), (213637.69999999995, 6848862.399999999), (213655.5, 6848842.399999999), (213669.3, 6848823.799999999), (213677.8, 6848810.899999999), (213686.8, 6848794.899999999), (213691.09999999986, 6848785.8999999985), (213695.90000000008, 6848775.999999999), (213699.6000000001, 6848769.399999999), (213704.1000000001, 6848763.800000001), (213709.29999999993, 6848758.499999999), (213751.90000000008, 6848724.599999998), (213759.20000000007, 6848718.199999999), (213779.00000000012, 6848703.899999999), (213788.20000000007, 6848696.9), (213790.9000000002, 6848693.599999999)
