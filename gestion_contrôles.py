from qgis.PyQt.QtWidgets import QTreeWidgetItem, QDockWidget
from qgis.core import *
from .resources import *

# Import the code for the dialog

class gestion_controles(QDockWidget):

    def __init__(self, main, iface, parent):
        super(gestion_controles, self).__init__(parent)
        self.iface = iface
        self.main = main
    
    # prépare les boites et remets à létat initial les choix si ils n'ont pas étés validés en appuyant sur ok et affiches la boite de dialogue choix_controles
    def choix_controles(self):
        for items in self.main.control_list:
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
        for items in self.main.control_list:
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
        for items in self.main.control_list:
            for i in range(root.childCount()):
                signal = root.child(i)
                num_children = signal.childCount()
                if (signal.text(0) == items[0] and signal.checkState(0) != items[2]):
                    items[2] = signal.checkState(0)
                if (num_children != 0):
                    self.update_control_boxes2(num_children, signal)
    def update_control_boxes2(self, num_children, parent):
        for items in self.main.control_list:
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
                self.main.control_list.append([signal.text(0), total, signal.checkState(0)])
                total += 1
    def append_ctrl_2(self, num_children, parent, total):
        for i in range(parent.childCount()):
            child = parent.child(i)
            num_children = child.childCount()
            if num_children != 0:
                self.append_ctrl_2(num_children, child, total)
            else:
                self.main.control_list.append([child.text(0), total, child.checkState(0)])
                total += 1

    # ajoute les contrôles voulus dans le treeView de self.main.dlg_controles
    def add_controls(self, search):
        self.main.dlg_controles.treeWidget.setHeaderHidden(True)
        echelle = QTreeWidgetItem(self.main.dlg_controles.treeWidget)
        echelle.setText(0, '%s' % "Grande Échelle")
        echelle.setFlags(echelle.flags() | QtCore.Qt.ItemIsTristate | QtCore.Qt.ItemIsUserCheckable)
        type = QTreeWidgetItem(echelle)
        type.setText(0, '%s' % "Contrôles Géométrie")
        type.setFlags(type.flags() | QtCore.Qt.ItemIsTristate | QtCore.Qt.ItemIsUserCheckable)
        item = QTreeWidgetItem(type)
        item.setText(0, '%s' % "rebroussement")
        item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
        item.setCheckState(0, 2)
        item = QTreeWidgetItem(self.main.dlg_controles.treeWidget)
        item.setText(0, '%s' % "test")
        item.setCheckState(0, 2)
        if search == False:
            self.append_ctrl_to_list()
    
    #renvoie le nombre de controles actifs dans la liste
    def nb_controles_actifs(self):
        self.main.controles_actifs = 0
        for items in self.main.control_list:
            if items[2] == QtCore.Qt.Checked:
                self.main.controles_actifs += 1
        self.main.controles_restants = 1
