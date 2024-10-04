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
def get_quantity(self, objets_controle):
    quantity = 0
    canvas = qgis.utils.iface.mapCanvas() 
    allLayers = canvas.layers()
    for layers in allLayers:
        for items in self.couche_list:
            # si la couche est présente dans la liste et qu'elle est cochée et qu'elle est présente dans les objets voulu
            if layers.name() == items[0] and items[2] == QtCore.Qt.Checked and layers.name() in objets_controle: #(QtCore.Qt.Checked == 2)
                # récupère les informations des couches
                for f in layers.getFeatures():
                    geom = f.geometry()
                    for part in geom.parts():
                        quantity += 1
    return quantity



def set_checked_layers_active(self):
    active_layers = []
    in_list = []
    temp = []
    canvas = qgis.utils.iface.mapCanvas() 
    allLayers = canvas.layers()
    for layers in allLayers:
        active_layers.append(layers.name())
    for items in self.couche_list:
        if items[2] == 2:
            in_list.append(items[0])
    for items in in_list:
        if items not in active_layers:
            temp.append(items)
    for i in temp:
        test = qgis.core.QgsProject.instance().mapLayersByName(i)
        qgis.core.QgsProject.instance().layerTreeRoot().findLayer(test[0]).setItemVisibilityChecked(True)
    return temp



# execution du controle
def rebroussement(self):
    nom_controle = "rebroussement"
    objets_controle = ["limite_administrative", "ligne_frontalière", "tronçon_hydrographique", "limite_terre_mer"
               , "histolitt", "ligne_électrique", "canalisation", "construction_linéaire", "ligne_orographique"
               , "troncon_de_route", "densification_des_chemins", "tronçon_de_voie_ferrée", "transport_par_câble", "voie_de_triage"
               , "itinéraire_ski_de_randonnée", "haie", "ligne_caractéristique", "limites_diverses", "modification_d_attribut"]
    for i in range (self.dlg3.listView.model().rowCount()):
        # vérifie si le contrôle "rebroussement" est coché et si il existe des objets de type Ligne
        if self.dlg3.listView.model().item(i).text() == nom_controle and self.dlg3.listView.model().item(i).checkState() == 2:
            temp = set_checked_layers_active(self)
            items_done = 0
            quantity = get_quantity(self, objets_controle)
            if quantity <= 0:
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
                for i in temp:
                    test = qgis.core.QgsProject.instance().mapLayersByName(i)
                    qgis.core.QgsProject.instance().layerTreeRoot().findLayer(test[0]).setItemVisibilityChecked(False)
                # parcours des couches
                for layers in allLayers:
                    # parcours la liste actuelle des couches
                    for items in self.couche_list:
                        # si la couche est présente dans la liste et qu'elle est cochée 
                        if layers.name() == items[0] and items[2] == QtCore.Qt.Checked and layers.name() in objets_controle: #(QtCore.Qt.Checked == 2)
                            # récupère les informations des couches
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
                return 0
            else:
                self.iface.messageBar().pushMessage("Info", "Contrôle {} impossible: il n'y a pas d'objets de type \"Ligne\". Passage au suivant".format(str(nom_controle)), level=Qgis.Warning, duration=10)
                return 2
            
# ['COMMUNE_0000000009738132', 'Guerlesquin', 'GUERLESQUIN', '29067', 'Commune simple', 1273, '20', '3', '29', '53', '242900835']
# BEFORE : <QgsPolygon: Polygon ((213580.29999999998835847 6849033.20000000018626451, 213591.60000000000582077 6848979.09999999962747097, 213612.79999999998835847 6848879, 213617.79999999998835847 6848878.29999999981373549, 213622.70000000001164153 6848876.40000000037252903, 213626.89999999999417923 6848873.20000000018626451, 213637.70000000001164153 6848862.40000000037252903, 213655.5 6848842.40000000037252903, 213669.29999999998835847 6848823.79999999981373549, 213677.79999999998835847 6848810.90000000037252903, 213686.79999999998835847 6848794.90000000037252903, 213691.10000000000582077 6848785.90000000037252903, 213695.89999999999417923 6848776, 213699.60000000000582077 6848769.40000000037252903, 213704.10000000000582077 6848763.79999999981373549, 213709.29999999998835847 6848758.5, 213751.89999999999417923 6848724.59999999962747097, 213759.20000000001164153 6848718.20000000018626451, 213779 6848703.90000000037252903, 213788.20000000001164153 6848696.90000000037252903, 213790.89999999999417923 6848693.599...>
# AFTER (IGNF:LAMB93) : ((213580.3, 6849033.2), (213591.6, 6848979.1), (213612.8, 6848879.0), (213617.8, 6848878.3), (213622.7, 6848876.4), (213626.9, 6848873.2), (213637.7, 6848862.4), (213655.5, 6848842.4), (213669.3, 6848823.8), (213677.8, 6848810.9), (213686.8, 6848794.9), (213691.1, 6848785.9), (213695.9, 6848776.0), (213699.6, 6848769.4), (213704.1, 6848763.8), (213709.3, 6848758.5), (213751.9, 6848724.6), (213759.2, 6848718.2), (213779.0, 6848703.9), (213788.2, 6848696.9), (213790.9, 6848693.6)
# AFTER (ESPG: 2154) : ((213580.29999999987, 6849033.199999998), (213591.59999999998, 6848979.099999999), (213612.79999999993, 6848878.999999999), (213617.79999999987, 6848878.299999999), (213622.7, 6848876.4), (213626.89999999985, 6848873.199999997), (213637.69999999995, 6848862.399999999), (213655.5, 6848842.399999999), (213669.3, 6848823.799999999), (213677.8, 6848810.899999999), (213686.8, 6848794.899999999), (213691.09999999986, 6848785.8999999985), (213695.90000000008, 6848775.999999999), (213699.6000000001, 6848769.399999999), (213704.1000000001, 6848763.800000001), (213709.29999999993, 6848758.499999999), (213751.90000000008, 6848724.599999998), (213759.20000000007, 6848718.199999999), (213779.00000000012, 6848703.899999999), (213788.20000000007, 6848696.9), (213790.9000000002, 6848693.599999999)

# ['CONSPONC0000002276339187', 'Croix', NULL, NULL, NULL, NULL, NULL, NULL, 'Sans intérêt touristique', 'En service', 0, PyQt5.QtCore.QDateTime(2022, 2, 22, 14, 14, 17, 804), NULL, NULL, NULL, NULL, 1, NULL, NULL, NULL, 'Orthophotographie', 3, 'Pas de Z', 9999, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 41373676, 'FXX', '56d9997690a66ffdb7eacb2245caba26', NULL, NULL, 'LINESTRING(932402 6848245.5, 932402 6848245.5)']
# ['BATIMENT0000000334775750', 'Indifférenciée', 'Résidentiel', NULL, 0, 'En service', 0, PyQt5.QtCore.QDateTime(2014, 6, 3, 21, 6, 38, 489), PyQt5.QtCore.QDateTime(2019, 3, 21, 18, 14, 59, 409), NULL, PyQt5.QtCore.QDate(1912, 1, 1), NULL, 1, NULL, NULL, '', 'BDParcellaire recalée', 3, 'Interpolation bâti BDTopo', 2.5, NULL, 3, 2, '20', '10', 6.5, 210.1, 216.6, NULL, NULL, NULL, '', NULL, '', 'Cadastre', '', 'TA=1BDU-1BDP;TX=-1;TY=-1;Id Parcelle=054395000BK010200;Type BDP=Bâtiment en dur;Anc. SG2D=BDTopo;Anc. CLEABS=BATIMENT0000000053818382;', '{"classe_q": "A", "fusion": "false", "id_bati_ff": "54395000BK0200-3690-0025-T-A", "id_par_ou_tup": "54395000BK0200", "indice_app": "1.0", "nb_bati_bdt": "1", "nb_bati_ff": "1", "nb_bdt_non_app": "0", "nb_ff_non_app": "0", "type_parcelle": "SIMPLE"}', 'A 1.0', '54395000BK0200', '', '', 35406727, 'FXX', 'b83543a9126f10662865b958dafa5aad', NULL, '', 'LINESTRING(935152.9 6846126.9, 935163.8 6846137.8)']
# ['CANALISA0000000224178924', 'Autres matières premières', '0', 'En service', 1, PyQt5.QtCore.QDateTime(2009, 9, 10, 12, 17, 22, 463), NULL, PyQt5.QtCore.QDateTime(2016, 9, 9, 13, 5, 3, 508), NULL, NULL, 1, NULL, NULL, '', 'Géoroute', 20, 'Pas de Z', 9999, NULL, '', NULL, NULL, NULL, '', 14947438, 'FXX', '0', NULL, '', 'LINESTRING(934352.1 6849364, 934352.3 6849376.6)']
# ['LIM_ADMI0000000054046148', 'Limite de commune', 0, PyQt5.QtCore.QDateTime(2007, 1, 26, 9, 24, 52, 838), NULL, NULL, NULL, NULL, 1, NULL, NULL, NULL, 'Non validé', 'Topologique', '', NULL, NULL, NULL, '54274', '54526', NULL, NULL, NULL, NULL, NULL, NULL, 205881, 'FXX', '0', NULL, '', 'LINESTRING(936487.7 6846221.2, 937026.1 6846362)']
# ['CIMETIER0000000053717077', 'Civil', NULL, 'Cimetière de Préville', 'Validé', '[{"date": "1998-03-05", "graphie": "cimeti\\u00e8re de pr\\u00e9ville", "source1": "IGN", "statut": "Valid\\u00e9"}]', '8', '4', NULL, 'En service', 0, PyQt5.QtCore.QDateTime(2007, 1, 25, 11, 28, 20, 932), PyQt5.QtCore.QDateTime(2014, 6, 3, 21, 9, 17, 324), NULL, NULL, PyQt5.QtCore.QDate(2009, 7, 1), 1, NULL, NULL, '', 'Photogrammétrie', 2.5, 'Photogrammétrie', 1.5, NULL, '', NULL, '', ' Restit PVA 2009', '', 'PAIRELIG0000000053673320', '', 11211374, 'FXX', '0', '54 Meurthe-et-Moselle', '', 'LINESTRING(932558.3 6847803.1, 933048.5 6848212.6)']
# ['COM_VTRI0000000229266061', 'En service', 1, PyQt5.QtCore.QDateTime(2010, 2, 10, 9, 19, 56, 241), PyQt5.QtCore.QDateTime(2018, 3, 26, 16, 33, 0, 270), PyQt5.QtCore.QDateTime(2018, 12, 20, 15, 9, 48, 293), NULL, NULL, NULL, NULL, NULL, 'Scan25', NULL, '', NULL, NULL, NULL, 35048412, 'FXX', 'cb041744e7b0ed7e96e7928ee147f2f6', 'dep54_BDCOMP', NULL, 'LINESTRING(935013.6 6848674.4, 935148.5 6848995.6)']
# [NULL, NULL, 1, NULL, '54395_2273', 'Allée George Sand', '54395', 'Nancy', NULL, 6.158889, 48.702493, '', '', '', 'commune', 0, NULL, NULL, NULL, NULL, '54395_2273_00001', PyQt5.QtCore.QDate(2018, 11, 28), 'LINESTRING(932403 6849354.8, 932403 6849354.8)', PyQt5.QtCore.QDateTime(2022, 9, 27, 9, 20, 25, 292), PyQt5.QtCore.QDateTime(2022, 12, 11, 9, 50, 1, 708), PyQt5.QtCore.QDateTime(2024, 2, 3, 1, 4, 4, 791), NULL, 'ADR_BAN_0000002308650732', 46254017, 1, 'c48344a25ffb8f2cd232d6c4dca4ae1f', 'FXX', 'Sémantique', 'Gauche', 'TRONROUT0000000236208380', 'LINESTRING(932403 6849354.8, 932393.443866 6849350.204596)', 1]
# ['PT_ACCES0000002206725371', 0, PyQt5.QtCore.QDateTime(2020, 5, 12, 16, 0, 37, 962), NULL, NULL, NULL, NULL, 1, NULL, 'Orthophotographie', 3, NULL, 'Sortie', 'Véhicule', NULL, NULL, NULL, NULL, 'EQ_RESEA0000000356722718', 37274637, 'FXX', '70906fce1a2ca4a55031f681c060f746', NULL, NULL, 'LINESTRING(932750.5 6847292.4, 932750.5 6847292.4)']
# ['SURFACTI0000002222582184', 'Industriel et commercial', 'Zone industrielle', "Zone d'activités", 'Rives de Meurthe-Oberlin', 'Collecté', '[{"date": "2021-01-28", "graphie": "rives de meurthe-oberlin", "source1": "Terrain", "statut": "Collect\\u00e9"}]', NULL, '5', 0, 'Sans intérêt touristique', 'En service', 0, PyQt5.QtCore.QDateTime(2021, 1, 28, 9, 38, 42, 90), PyQt5.QtCore.QDateTime(2023, 4, 14, 11, 43, 39, 11), NULL, NULL, NULL, 1, NULL, NULL, NULL, 'Orthophotographie', 3, NULL, 'Prévalidé', 'Prévalidé', NULL, NULL, '54395', 'NANCY', NULL, NULL, NULL, 44310338, 'FXX', '79511c4cad89bef75f4f17c75b006615', NULL, NULL, 'LINESTRING(934094.5 6849313.2, 934647.5 6849695.4)', PyQt5.QtCore.QByteArray(), NULL, NULL]
# ['PAIHABIT0000000053721226', 'Lieu-dit habité', NULL, 'les Muguets', 'Collecté', '[{"date": "2013-09-13", "graphie": "les muguets", "source1": "IGN", "statut": "Collect\\u00e9"}]', NULL, '6', 1, 'Sans intérêt touristique', 'En service', 0, PyQt5.QtCore.QDateTime(2007, 1, 25, 11, 28, 20, 932), PyQt5.QtCore.QDateTime(2020, 5, 12, 16, 0, 37, 962), NULL, NULL, NULL, 1, NULL, NULL, NULL, 'Calculé', 20, NULL, NULL, NULL, NULL, NULL, NULL, '', '54395', 'NANCY', '54395#06G', NULL, 37274637, 'FXX', '6117b5c72d69c2a7eb4ec905d8be907d', '54 Meurthe-et-Moselle', NULL, 'LINESTRING(932734.7 6845740.7, 932744.8 6845779.7)', 'POINT(932737.2 6845777.2)', NULL, NULL]
# ['PAIHYDRO0000002203064783', 'Fontaine', NULL, NULL, NULL, NULL, NULL, '6', NULL, 'En service', 0, PyQt5.QtCore.QDateTime(2019, 6, 17, 13, 13, 40, 834), PyQt5.QtCore.QDateTime(2019, 9, 20, 18, 10, 23, 317), NULL, NULL, NULL, 1, NULL, NULL, NULL, 'Orthophotographie', 3, NULL, NULL, NULL, NULL, NULL, NULL, 36168624, 'FXX', 'fccafdd48507bd23105ff669251b9c72', NULL, NULL, 'LINESTRING(933399.7 6846092, 933399.7 6846092)', '54395', NULL, NULL]
# ['TRON_EAU0000002287825664', '02T0000002287825664', 'FR', 'Ecoulement naturel', 1, '0', 'En service', 0, PyQt5.QtCore.QDateTime(2022, 6, 8, 12, 11, 50, 789), PyQt5.QtCore.QDateTime(2022, 6, 10, 20, 19, 20, 1), NULL, NULL, NULL, 1, NULL, NULL, '', 'Calculé', 20, 'Pas de Z', 9999, 'Autres modes', 'Inconnu', NULL, 'Validé', 'Permanent', 0, 0, 0, '7', NULL, 'Naturelle non aménagée', 'FR', 'Sens direct', 1, 1, 'Plus de 50 m', 'Principal', '', NULL, '', NULL, 'A6--0100', '', 'TA : 1GE-1ME/CleabsGE : TRON_EAU0000000053686645/CleabsME : BDCTROHY0000000068655186', 200016441, 'A', 'A693', 'rivière la meurthe', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '', 'COURDEAU0000002000793627', 'COURNOMM0000000053698132', 'SURF_EAU0000000053695457', NULL, 42161875, 'FXX', 'd4a43e6ba334f7f97e6fde908e42a424', NULL, '', 'la Meurthe', 'la Meurthe', NULL, 'LINESTRING(936239.9 6846359.4, 936426.3 6846831.6)', NULL, NULL, NULL, NULL, NULL, NULL]
# ['DENSIFCH0000000318670379', 'Sentier', '0', NULL, 'En service', 1, PyQt5.QtCore.QDateTime(2013, 2, 12, 10, 14, 55, 327), NULL, PyQt5.QtCore.QDateTime(2013, 7, 26, 14, 52, 19, 139), NULL, NULL, NULL, NULL, NULL, 'Scan25', 'Pas de Z', NULL, '', NULL, '', NULL, '', NULL, NULL, NULL, 9673415, 'FXX', '0', NULL, '', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'LINESTRING(933685.9 6849962.2, 933797.7 6850033.7)']
# ['LIGNOROG0000000053704245', 'Talus', 'En service', 0, PyQt5.QtCore.QDateTime(2007, 1, 25, 11, 28, 20, 932), NULL, NULL, NULL, NULL, 1, NULL, NULL, NULL, 'BDTopo', 2.5, 'BDTopo', 1.5, NULL, NULL, NULL, NULL, NULL, '', 203281, 'FXX', '0', '54 Meurthe-et-Moselle', '', 'LINESTRING(936374.8 6846159.5, 936405.5 6846296.7)', NULL, NULL, NULL]
# ['CONSLINE0000002206391088', 'Mur de soutènement', NULL, NULL, NULL, NULL, NULL, NULL, 'Sans intérêt touristique', 'En service', 0, PyQt5.QtCore.QDateTime(2020, 3, 10, 8, 55, 20, 424), NULL, NULL, NULL, NULL, 1, NULL, NULL, NULL, 'Orthophotographie', 3, 'Pas de Z', 9999, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 37033053, 'FXX', '0cfa36edf61578d33b6c8d4f9f1ef057', NULL, NULL, 'LINESTRING(932200.4 6849685.2, 932213.7 6849715.1)']
# ['EQ_RESEA0000000129651108', 'Carrefour', 'Rond-point', 'Rond-Point de Buthégnemont', 'Collecté', '[{"date": "2008-05-16", "graphie": "rond-point de buth\\u00e9gnemont", "source1": "SGA", "statut": "Collect\\u00e9"}]', NULL, '5', 0, NULL, 'En service', 0, PyQt5.QtCore.QDateTime(2008, 5, 16, 17, 1, 16, 407), PyQt5.QtCore.QDateTime(2022, 2, 22, 15, 13, 49, 989), NULL, NULL, NULL, 1, NULL, NULL, NULL, 'Calculé', 20, 'Pas de Z', 9999, NULL, NULL, NULL, NULL, NULL, '', '54395', 'NANCY', '54395#057', NULL, NULL, 41374743, 'FXX', 'cd2252bb67a813e8ebe4a79018c004a4', NULL, NULL, 'LINESTRING(931734.6 6848499.3, 931759 6848523.7)', 'POINT(931746.7 6848512.2)', NULL, NULL]
# ['SURF_EAU0000000053695455', '02S0000000053695455', 'FR', 'Ecoulement naturel', '0', 'En service', 0, PyQt5.QtCore.QDateTime(2007, 1, 25, 11, 28, 20, 932), PyQt5.QtCore.QDateTime(2023, 6, 22, 12, 59, 21, 737), NULL, NULL, NULL, 1, NULL, NULL, NULL, 'BDTopo', 2.5, 'BDTopo', 1.5, 'Imagerie satellite ou aérienne', 'Autres modes', NULL, 'Validé', 'Permanent', 0, 'Naturelle non aménagée', NULL, NULL, NULL, NULL, NULL, 'TA : 1GE-0ME/CleabsGE : SURF_EAU0000000053695455', NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL, 44848315, 'FXX', '1cd65160af602ca6f3111fa5d69f4b8c', '54 Meurthe-et-Moselle', NULL, NULL, NULL, NULL, 'LINESTRING(935937.5 6846825.3, 936322 6847815.1)', NULL]
# ['CONSSURF0000002206562492', 'Pont', NULL, NULL, NULL, NULL, NULL, '5', NULL, 'En service', 0, PyQt5.QtCore.QDateTime(2020, 4, 10, 10, 15, 31, 230), NULL, NULL, NULL, NULL, 1, NULL, NULL, NULL, 'BDTopo', 2.5, 'BDTopo', 1.5, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 37147359, 'FXX', '33e38286a2ce41b56307e212ca02345b', NULL, NULL, 'LINESTRING(935596 6846762, 935682.9 6846806.6)']
# ['PT_RESEA0000000322230992', 'Barrière', NULL, NULL, NULL, NULL, 'En service', 0, PyQt5.QtCore.QDateTime(2013, 5, 21, 14, 44, 35, 128), PyQt5.QtCore.QDateTime(2019, 9, 23, 22, 0, 29, 374), NULL, NULL, NULL, 1, NULL, NULL, '', 'Scan25', 10, 'Pas de Z', 999, NULL, '', NULL, '', NULL, NULL, 36171885, 'FXX', '1cface1d254b916e08052a4854d3baf8', NULL, NULL, 'LINESTRING(933313.3 6849004.4, 933313.3 6849004.4)', '54395', NULL]
# ['COM_ACLO0000002201470716', 'Curiosité', 'Hôpital des Frères de la Charité', 'Collecté', '[{"date": "2019-02-08", "graphie": "h\\u00f4pital des fr\\u00e8res de la charit\\u00e9", "source1": "IGN", "statut": "Collect\\u00e9"}]', NULL, '6', 'Sans intérêt touristique', 'En service', 0, PyQt5.QtCore.QDateTime(2019, 2, 8, 12, 1, 24, 386), PyQt5.QtCore.QDateTime(2023, 8, 31, 22, 38, 36, 446), NULL, NULL, PyQt5.QtCore.QDate(2023, 8, 31), NULL, NULL, NULL, 'Calculé', NULL, NULL, 'prévalidé', NULL, NULL, NULL, '54395', NULL, 45243990, 'FXX', '4b4bd327a980d138931939e56001f0ca', NULL, NULL, 'LINESTRING(934378.7 6848518.9, 934378.7 6848518.9)']
# ['POIN_REP0000002001501458', '54-59', 1, PyQt5.QtCore.QDateTime(2017, 2, 2, 10, 35, 29, 725), NULL, PyQt5.QtCore.QDateTime(2017, 7, 10, 19, 34, 46, 340), NULL, PyQt5.QtCore.QDate(2016, 1, 1), 1, NULL, 'DSCR_2016', NULL, NULL, 'D400', '35', 36897, 'U', PyQt5.QtCore.QDate(2015, 12, 31), 'PR valide', 35.0, '54-D400-U', '', NULL, '', '54', NULL, NULL, 31200481, 'FXX', '0', 'BDPR', '', 'LINESTRING(934300.3 6847917.4, 934300.3 6847917.4)', NULL, NULL, NULL]
# ['RESERVOI0000002204079187', "Réservoir d'eau ou château d'eau au sol", 'En service', 0, PyQt5.QtCore.QDateTime(2019, 9, 11, 13, 0, 9, 763), PyQt5.QtCore.QDateTime(2023, 2, 3, 19, 38, 44, 12), NULL, NULL, PyQt5.QtCore.QDate(2018, 9, 30), 1, NULL, NULL, NULL, 'Photogrammétrie', 2.5, 'Photogrammétrie', 1.5, NULL, 199.1, NULL, 5.9, 205, NULL, 199.8, NULL, NULL, NULL, 'Restit PVA 2018 DEP 54', NULL, NULL, 43816936, 'FXX', '867be0b6ba6f333d9e7fd54b93e684eb', NULL, NULL, 'LINESTRING(936074.9 6846924.7, 936087.6 6846942.7)', 'Imagerie aérienne', NULL]
# ['AERODROM0000000129506376', 'Autre', 'Héliport', 'Civil', 'Héliport Nancy Hôpital Central', 'Collecté', '[{"date": "1900-01-01", "graphie": "h\\u00e9liport nancy h\\u00f4pital central", "source1": "IGN", "statut": "Collect\\u00e9"}]', 0, 'En service', 0, PyQt5.QtCore.QDateTime(2008, 5, 6, 10, 24, 3, 53), PyQt5.QtCore.QDateTime(2023, 3, 28, 16, 14, 55, 575), NULL, NULL, PyQt5.QtCore.QDate(2023, 3, 2), 1, NULL, 'SIA 2023', 'SIA:231', 'Orthophotographie', 3, NULL, NULL, NULL, NULL, NULL, '', NULL, NULL, NULL, 44181880, 'FXX', '60963620a8376958e1429d2315af00b5', NULL, NULL, 'LINESTRING(934934.9 6847533.9, 934967.8 6847565.9)', 'POINT(934949.3 6847555.6)']
# ['TRONFERR0000000330421570', 'Sans objet', '0', 'Non exploité', 0, PyQt5.QtCore.QDateTime(2013, 12, 9, 17, 12, 43, 372), PyQt5.QtCore.QDateTime(2023, 7, 11, 16, 32, 17, 631), NULL, NULL, NULL, 1, NULL, NULL, NULL, 'BDTopo', 2.5, 'BDTopo', 1.5, NULL, 0, 'Normale', '1', 'Sans objet', NULL, NULL, NULL, NULL, NULL, NULL, 'VOIEFERR0000002206228885', 45006101, 'FXX', 'bc3ccbd9e7acebcdb2fd72802a5e1673', NULL, NULL, NULL, 'LINESTRING(933406.5 6849358.2, 934713.8 6850290.6)', NULL]
# ['TERRSPOR0000000053717785', 'Terrain de tennis', NULL, 'En service', 0, PyQt5.QtCore.QDateTime(2007, 1, 25, 11, 28, 20, 932), NULL, NULL, NULL, NULL, 1, NULL, NULL, NULL, 'BDTopo', 2.5, 'BDTopo', 1.5, NULL, NULL, NULL, NULL, NULL, '', '', 203281, 'FXX', '0', '54 Meurthe-et-Moselle', '', 'LINESTRING(932794.5 6848773.6, 932816.6 6848788.2)']
# ['PAIE_NAT0000002012326483', 'Lieu-dit non habité', 'Tour des Énergies', 'Collecté', '[{"date": "1900-01-01", "graphie": "tour des \\u00e9nergies", "source1": "Terrain", "statut": "Collect\\u00e9"}]', NULL, '6', 'Sans intérêt touristique', 0, PyQt5.QtCore.QDateTime(2018, 7, 31, 15, 8, 3, 109), PyQt5.QtCore.QDateTime(2018, 9, 14, 7, 51, 42, 872), NULL, NULL, NULL, 1, NULL, NULL, NULL, 'Levé non GPS', 5, NULL, '', '', NULL, '54395', '', '', 33580041, 'FXX', '3b7858e88e45058c3e08b06e400d5a26', NULL, '', 'LINESTRING(931987.7 6849275.6, 931987.7 6849275.6)', NULL]
# ['EVOLPONC0000000054035952', 'Bâtiment', 1, PyQt5.QtCore.QDateTime(2007, 1, 25, 11, 28, 20, 932), NULL, PyQt5.QtCore.QDateTime(2009, 9, 10, 14, 1, 27, 434), NULL, 'En construction', PyQt5.QtCore.QDate(2006, 4, 1), PyQt5.QtCore.QDate(2007, 1, 1), NULL, NULL, '', PyQt5.QtCore.QDate(2006, 8, 25), 'A collecter', 0, 'BATIMENT 40 LOGEMENTS LOBAU/MOLITOR ET VOIRIE', NULL, NULL, '', '', '540050180', 'CORRESPT0000000054035979', 3542272, 'FXX', '0', '54 Meurthe-et-Moselle', '', 'LINESTRING(935424.1 6847224.8, 935424.1 6847224.8)']
# ['COMMUNE_0000000009736880', 'Nancy', 'NANCY', '54395', 'Préfecture', 104260, '99', '3', '54', '44', '245400676']

# ['TRONROUT0000000053972590', 'Route à 1 chaussée', 'R MARECHAL OUDINOT', 'R MARECHAL OUDINOT', NULL, NULL, '4', 0, '0', 'En service', 0, PyQt5.QtCore.QDateTime(2007, 1, 25, 11, 28, 20, 932), PyQt5.QtCore.QDateTime(2024, 2, 3, 18, 24, 40, 188), NULL, NULL, NULL, 1, NULL, NULL, NULL, 'BDTopo', 2.5, 'BDTopo', 1.5, NULL, '2', 5.5, 0, 0, 'Double sens', NULL, NULL, 1, 25, 'Libre', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, '126', NULL, '126', NULL, '54395', '54395', 'Classique', NULL, NULL, '54000', '54000', NULL, NULL, NULL, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '543953440', '543953440', NULL, NULL, NULL, NULL, NULL, 46254077, 'FXX', '9c0237a0f3a22523afd62a9b467d37f7', '54 Meurthe-et-Moselle', NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'LINESTRING(933834 6846095, 933851 6846108.9)', NULL, NULL, NULL, 'commune', 'commune', 'Rue Maréchal Oudinot', 'Rue Maréchal Oudinot', '', '', '54395_3440', '54395_3440', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL]



#{'COMMUNE_f137bd72_0f23_48c7_85be_e1ea764c0099': <QgsVectorLayer: 'COMMUNE' (ogr)>, 'DEPARTEMENT_b32ea3fd_66f3_447b_91c6_347298b2dfdb': <QgsVectorLayer: 'DEPARTEMENT' (ogr)>, 'adresse_ban_38f48cdb_6c0f_4009_89e3_e891b0625dee': <QgsVectorLayer: 'adresse_ban' (spatialite)>, 'aerodrome_37a4899c_e1b1_495f_bb6a_87e8d11f322e': <QgsVectorLayer: 'aerodrome' (spatialite)>, 'batiment_b60353bc_e90e_4e4d_bade_3905a98b6664': <QgsVectorLayer: 'batiment' (spatialite)>, 'canalisation_a6001cd8_3cd5_4ef0_8705_21402fb3e553': <QgsVectorLayer: 'canalisation' (spatialite)>, 'cimetiere_ef5b0d53_4ddc_4a49_81ce_05ce53a3caad': <QgsVectorLayer: 'cimetiere' (spatialite)>, 'construction_lineaire_2431e34c_2182_493f_865f_0ab1a91863d8': <QgsVectorLayer: 'construction_lineaire' (spatialite)>, 'construction_ponctuelle_2685c08c_5c25_4159_8052_bd2fa8867fc0': <QgsVectorLayer: 'construction_ponctuelle' (spatialite)>, 'construction_surfacique_e40000c1_b579_4fd1_ad66_e8d6c7fa0cdb': <QgsVectorLayer: 'construction_surfacique' (spatialite)>, 'densification_des_chemins_ab4e9476_984b_4a1b_a27b_44f138da7635': <QgsVectorLayer: 'densification_des_chemins' (spatialite)>, 'detail_hydrographique_b11f4c55_6662_46d6_9182_65ea4da839bd': <QgsVectorLayer: 'detail_hydrographique' (spatialite)>, 'detail_orographique_dd46ce60_2ee3_45e8_bfd3_225ec4e59879': <QgsVectorLayer: 'detail_orographique' (spatialite)>, 'edifice_ou_curiosite_2d458f13_9447_47ed_ba6a_2038eea8e344': <QgsVectorLayer: 'edifice_ou_curiosite' (spatialite)>, 'equipement_de_transport_f90583aa_720a_459d_ad0f_666d1bd1d58e': <QgsVectorLayer: 'equipement_de_transport' (spatialite)>, 'evolution_ponctuelle_af21f061_000f_4f80_9319_6fdc8b7ec3da': <QgsVectorLayer: 'evolution_ponctuelle' (spatialite)>, 'itineraire_ski_de_randonnee_a3e61b56_2ab5_4bdf_b21d_8e30d0c81925': <QgsVectorLayer: 'itineraire_ski_de_randonnee' (spatialite)>, 'lieu_dit_non_habite_440cf5eb_adf6_49a2_a718_a9829ebab221': <QgsVectorLayer: 'lieu_dit_non_habite' (spatialite)>, 'ligne_caracteristique_995e7979_1bca_4af6_b335_f84664f6c7b4': <QgsVectorLayer: 'ligne_caracteristique' (spatialite)>, 'ligne_electrique_295fa963_4d36_4b80_b6c1_7f77870bb1cd': <QgsVectorLayer: 'ligne_electrique' (spatialite)>, 'ligne_orographique_4f981341_1014_49dd_a86a_1af5f54a8f6c': <QgsVectorLayer: 'ligne_orographique' (spatialite)>, 'limite_administrative_aeca4358_9e2f_4864_ad08_9975db0ade83': <QgsVectorLayer: 'limite_administrative' (spatialite)>, 'limite_terre_mer_d278bfbf_f4dd_479f_a84c_287d5681eeda': <QgsVectorLayer: 'limite_terre_mer' (spatialite)>, 'limites_diverses_b3161648_b94b_411f_9a9c_faaa6981c8e4': <QgsVectorLayer: 'limites_diverses' (spatialite)>, 'nature_du_sol_993f572a_535b_4d8f_843b_6852622924a8': <QgsVectorLayer: 'nature_du_sol' (spatialite)>, 'parcellaire_forestier_4a7efc17_912f_4223_b020_673359f85c42': <QgsVectorLayer: 'parcellaire_forestier' (spatialite)>, 'piste_d_aerodrome_05c8b9a4_e17d_44bf_8a1f_54ee330d8045': <QgsVectorLayer: 'piste_d_aerodrome' (spatialite)>, 'point_cote_afc0bf85_c43a_4277_9ab0_5ece42c68fba': <QgsVectorLayer: 'point_cote' (spatialite)>, 'point_d_acces_ee5ef5b4_a0b4_4a94_aa0b_57cea674b369': <QgsVectorLayer: 'point_d_acces' (spatialite)>, 'point_de_repere_6177e052_f8a7_488d_889b_156bb64c488a': <QgsVectorLayer: 'point_de_repere' (spatialite)>, 'point_du_reseau_cbb365f2_2c95_46a1_b35e_31651f17c673': <QgsVectorLayer: 'point_du_reseau' (spatialite)>, 'poste_de_transformation_6bebe6e6_2059_4ccd_b58c_86ecc19097f9': <QgsVectorLayer: 'poste_de_transformation' (spatialite)>, 'pylone_19b685e6_20af_4a0b_a076_992b3c4906c3': <QgsVectorLayer: 'pylone' (spatialite)>, 'reservoir_c12a0a9c_4ca2_4dd8_a24e_ef882eb48c54': <QgsVectorLayer: 'reservoir' (spatialite)>, 'surface_hydrographique_ee4c1dcd_4b2b_4a7d_a2af_cd969a7d4f20': <QgsVectorLayer: 'surface_hydrographique' (spatialite)>, 'terrain_de_sport_b076488f_c2e3_4f01_8d30_e6d54d84a963': <QgsVectorLayer: 'terrain_de_sport' (spatialite)>, 'transport_par_cable_26a837e6_0ea7_4454_8705_9dfcff74a3ad': <QgsVectorLayer: 'transport_par_cable' (spatialite)>, 'troncon_de_route_2360a132_fdaf_449c_b619_6d6498e43dd3': <QgsVectorLayer: 'troncon_de_route' (spatialite)>, 'troncon_de_voie_ferree_936721d7_ea83_427f_ba2e_2e4e45d75314': <QgsVectorLayer: 'troncon_de_voie_ferree' (spatialite)>, 'troncon_hydrographique_563897dd_27a8_4e71_b14a_17b27346054c': <QgsVectorLayer: 'troncon_hydrographique' (spatialite)>, 'voie_de_triage_6fb2886d_9000_4586_bc8d_e22ad04668b4': <QgsVectorLayer: 'voie_de_triage' (spatialite)>, 'zone_d_activite_ou_d_interet_6dc24279_d18d_4904_8e57_1804ae58db09': <QgsVectorLayer: 'zone_d_activite_ou_d_interet' (spatialite)>, 'zone_d_estran_c1a49091_36c2_4909_a7a0_589ab28f50e4': <QgsVectorLayer: 'zone_d_estran' (spatialite)>, 'zone_d_habitation_0a12b464_10e4_419e_9926_000931b7babb': <QgsVectorLayer: 'zone_d_habitation' (spatialite)>}