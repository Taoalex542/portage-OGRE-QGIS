from qgis.PyQt.QtWidgets import QTreeWidgetItem, QDockWidget
from qgis.core import *
from .resources import *

# Import the code for the dialog

class gestion_controles(QDockWidget):

    def __init__(self, main, iface):
        super(gestion_controles, self).__init__()
        self.iface = iface
        self.main = main
        self.control_list = []
    
    # prépare les boites et remets à létat initial les choix si ils n'ont pas étés validés en appuyant sur ok et affiches la boite de dialogue choix_controles
    def choix_controles(self):
        for items in self.control_list:
            root = self.main.dlg_controles.treeWidget.invisibleRootItem()
            for i in range(root.childCount()):
                signal = root.child(i)
                num_children = signal.childCount()
                if (signal.text(0) == items[0]):
                    signal.setCheckState(0, items[2])
                if (num_children != 0):
                    self.global_contrôle_prep(num_children, signal)
        self.main.dlg_controles.show()
        self.main.dlg_controles.treeWidget.expandAll()
    def global_contrôle_prep(self, num_children, parent):
        for items in self.control_list:
            for i in range(parent.childCount()):
                child = parent.child(i)
                num_children = child.childCount()
                if (child.text(0) == items[0]):
                    child.setCheckState(0, items[2])
                if num_children != 0:
                    self.global_contrôle_prep(num_children, child)

    # mets a jour les checkbox pour les couches
    def update_control_boxes(self):
        root = self.main.dlg_controles.treeWidget.invisibleRootItem()
        temp = self.main.dlg_controles.lineEdit.text()
        if (temp != ""):
            self.main.dlg_controles.lineEdit.setText("")
            self.main.recherche.search_controles()
        for items in self.control_list:
            for i in range(root.childCount()):
                signal = root.child(i)
                num_children = signal.childCount()
                if (signal.text(0) == items[0] and signal.checkState(0) != items[2]):
                    items[2] = signal.checkState(0)
                if (num_children != 0):
                    self.update_control_boxes2(num_children, signal)
        self.main.dlg_controles.lineEdit.setText(temp)
        self.main.recherche.search_control()
    def update_control_boxes2(self, num_children, parent):
        for items in self.control_list:
            for i in range(parent.childCount()):
                child = parent.child(i)
                num_children = child.childCount()
                if (child.text(0) == items[0] and child.checkState(0) != items[2]):
                    items[2] = child.checkState(0)
                if num_children != 0:
                    self.update_control_boxes2(num_children, child)

    # coche ou décoche toutes les couches présentes dans le treeView
    def global_control_edit(self, check):
        root = self.main.dlg_controles.treeWidget.invisibleRootItem()
        for i in range(root.childCount()):
            signal = root.child(i)
            num_children = signal.childCount()
            signal.setCheckState(0, check)
            if (num_children != 0):
                self.global_control_edit2(num_children, signal, check)
    def global_control_edit2(self, num_children, parent, check):
        for i in range(parent.childCount()):
            child = parent.child(i)
            num_children = child.childCount()
            child.setCheckState(0, check)
            if num_children != 0:
                self.global_control_edit2(num_children, child, check)
    def check_control_boxes(self):
        self.global_control_edit(QtCore.Qt.Checked)
    def uncheck_control_boxes(self):
        self.main.dialog += 1
        if (self.main.dialog == 10):
            self.main.dlg_dialog.show()
        self.global_control_edit(QtCore.Qt.Unchecked)

    # ajoute les groupes dans la liste control_list
    def append_ctrl_to_list(self):
        total = 0
        root = self.main.dlg_controles.treeWidget.invisibleRootItem()
        for i in range(root.childCount()):
            signal = root.child(i)
            num_children = signal.childCount()
            if (num_children != 0):
                self.append_ctrl_2(num_children, signal, total)
            else:
                self.control_list.append([signal.text(0), total, signal.checkState(0)])
                total += 1
    def append_ctrl_2(self, num_children, parent, total):
        for i in range(parent.childCount()):
            child = parent.child(i)
            num_children = child.childCount()
            if num_children != 0:
                self.append_ctrl_2(num_children, child, total)
            else:
                self.control_list.append([child.text(0), total, child.checkState(0)])
                total += 1

    # changes les '_' en ' ' pour l'affichage
    # ex: controle_test => controle test
    def joli_noms(self, controle):
        test = controle.copy()
        for i in range(len(test) - 4):
            test[i + 4] = test[i + 4].replace("_", " ")
        return test

    # ajoute les contrôles voulus dans le treeView de self.main.dlg_controles
    def add_controls(self, search):
        self.main.dlg_controles.treeWidget.setHeaderHidden(True)
        for controle in self.main.organisation:
            path_len = len(controle)
            if (controle[4] + ".py" in self.main.loaded_controles and "ctrl_" + controle[4] + ".py" in self.main.loaded_controles and controle[3] == 1): #si le controle est éxécutable
                temp = self.joli_noms(controle)
                if (path_len == 5): #si le controle est à la racine
                    item = QTreeWidgetItem(self.main.dlg_controles.treeWidget)
                    item.setText(0, '%s' % temp[4])
                    item.setCheckState(0, 2)
                else :
                    category = self.main.dlg_controles.treeWidget.findItems(controle[path_len - 1], QtCore.Qt.MatchRecursive)
                    if category != []:
                        type = category[0]
                    else:
                        type = QTreeWidgetItem(self.main.dlg_controles.treeWidget)
                        type.setText(0, '%s' % temp[path_len - 1])
                        type.setFlags(type.flags() | QtCore.Qt.ItemIsTristate | QtCore.Qt.ItemIsUserCheckable)
                    for i in range(path_len - 6): #si il y a plus de 1 dossier parent, passes dans la boucle
                        soustype = self.main.dlg_controles.treeWidget.findItems(controle[path_len - 5 - i], QtCore.Qt.MatchRecursive)
                        if soustype != []:
                            sous = soustype[0]
                        else:
                            sous = QTreeWidgetItem(type)
                            sous.setText(0, '%s' % controle[path_len - 5 - i])
                            sous.setFlags(sous.flags() | QtCore.Qt.ItemIsTristate | QtCore.Qt.ItemIsUserCheckable)
                        type = sous
                    if (path_len - 6 != 0):
                        item = QTreeWidgetItem(sous)
                    else:
                        item = QTreeWidgetItem(type)
                    item.setText(0, '%s' % temp[4])
                    item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                item.setCheckState(0, 2)
        if search == False:
            self.append_ctrl_to_list()
        if self.main.dlg_controles.lineEdit.text() != "":
            self.main.recherche.search_controles()
    
    #renvoie le nombre de controles actifs dans la liste
    def nb_controles_actifs(self):
        self.main.controles_actifs = 0
        for items in self.control_list:
            if items[2] == QtCore.Qt.Checked:
                self.main.controles_actifs += 1
        self.main.controles_restants = 1
