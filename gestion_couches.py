from qgis.PyQt.QtWidgets import QTreeWidgetItem, QDockWidget
from qgis.core import QgsProject
import qgis
from sip import delete
from .resources import *

class gestion_couches(QDockWidget):
    
    def __init__(self, main, iface, parent):
        super(gestion_couches, self).__init__(parent)
        self.iface = iface
        self.main = main
    
    # récumpère le nombre de couches choisies pour les contrôles
    def get_active_layers(self):
        self.main.couches_actives = 0
        for items in self.main.couche_list:
            if items[2] == QtCore.Qt.Checked:
                self.main.couches_actives += 1

    # prépare les boites et remets à létat initial les choix si ils n'ont pas étés validés en appuyant sur ok et affiches la boite de dialogue choix_couches
    def choix_couches(self):
        for items in self.main.couche_list:
            root = self.main.dlg_couches.treeWidget.invisibleRootItem()
            for i in range(root.childCount()):
                signal = root.child(i)
                num_children = signal.childCount()
                if (signal.text(0) == items[0]):
                    signal.setCheckState(0, items[2])
                if (num_children != 0):
                    self.global_couche_prep(num_children, signal)
        self.main.dlg_couches.show()
        self.main.dlg_couches.treeWidget.expandAll()
    def global_couche_prep(self, num_children, parent):
        for items in self.main.couche_list:
            for i in range(parent.childCount()):
                child = parent.child(i)
                num_children = child.childCount()
                if (child.text(0) == items[0]):
                    child.setCheckState(0, items[2])
                if num_children != 0:
                    self.global_couche_prep(num_children, child)

    # coche ou décoche toutes les couches présentes dans le treeView
    def global_checkbox_edit(self, check):
        root = self.main.dlg_couches.treeWidget.invisibleRootItem()
        for i in range(root.childCount()):
            signal = root.child(i)
            num_children = signal.childCount()
            signal.setCheckState(0, check)
            if (num_children != 0):
                self.global_checkbox_edit2(num_children, signal, check)
    def global_checkbox_edit2(self, num_children, parent, check):
        for i in range(parent.childCount()):
            child = parent.child(i)
            num_children = child.childCount()
            child.setCheckState(0, check)
            if num_children != 0:
                self.global_checkbox_edit2(num_children, child, check)
    def check_layer_boxes(self):
        self.global_checkbox_edit(QtCore.Qt.Checked)
    def uncheck_layer_boxes(self):
        self.global_checkbox_edit(QtCore.Qt.Unchecked)

    # mets a jour les checkbox pour les couches
    def update_layer_boxes(self):
        temp = self.main.dlg_couches.lineEdit.text()
        if (temp != ""):
            self.main.dlg_couches.lineEdit.setText("")
            self.main.recherche.search_couche()
        root = self.main.dlg_couches.treeWidget.invisibleRootItem()
        for items in self.main.couche_list:
            for i in range(root.childCount()):
                signal = root.child(i)
                num_children = signal.childCount()
                if (signal.text(0) == items[0] and signal.checkState(0) != items[2]):
                    items[2] = signal.checkState(0)
                if (num_children != 0):
                    self.update_layer_boxes2(num_children, signal)
        self.main.dlg_couches.lineEdit.setText(temp)
        self.main.recherche.search_couche()
    def update_layer_boxes2(self, num_children, parent):
        for items in self.main.couche_list:
            for i in range(parent.childCount()):
                child = parent.child(i)
                num_children = child.childCount()
                if (child.text(0) == items[0] and child.checkState(0) != items[2]):
                    items[2] = child.checkState(0)
                if num_children != 0:
                    self.update_layer_boxes2(num_children, child)


    # coche tous les layers actifs dans la gestion de couches de QGIS
    def check_active_layers(self):
        root = self.main.dlg_couches.treeWidget.invisibleRootItem()
        allLayers = qgis.core.QgsProject.instance().layerTreeRoot().children()
        for layer in allLayers:
            if (layer.isVisible()):
                if(type(layer) == qgis._core.QgsLayerTreeLayer):
                    for i in range(root.childCount()):
                        signal = root.child(i)
                        if (signal.text(0) == layer.name()):
                            signal.setCheckState(0, 2)
                if(type(layer) == qgis._core.QgsLayerTreeGroup):
                    for i in range(root.childCount()):
                        signal = root.child(i)
                        num_children = signal.childCount()
                        if(layer.name() == signal.text(0)):
                            self.activate_in_groups(num_children, signal, layer)
    def activate_in_groups(self, nb, signal, layer):
        i = 0
        if (nb == 0):
            if (layer.isVisible()):
                signal.setCheckState(0, 2)
            return
        node = layer
        for childs in node.children():
            child = signal.child(i)
            num_children = child.childCount()
            self.activate_in_groups(num_children, child, childs)
            if layer.name() == child.text(0) and layer.isVisible():
                child.setCheckState(0, 2)
            i += 1
    
    # ajoute les groupes dans la liste couche_list
    def append_for_groups(self, num_children, parent, total):
        for i in range(parent.childCount()):
            child = parent.child(i)
            num_children = child.childCount()
            self.main.couche_list.append([child.text(0), total, child.checkState(0)])
            if num_children != 0:
                self.append_for_groups(num_children, child, total)
            total += 1

    # coche les boites précédemment checkés dans les groupes
    def check_groups(self, num_children, parent):
        for items in self.main.couche_list:
            for i in range(parent.childCount()):
                child = parent.child(i)
                num_children = child.childCount()
                if (child.text(0) == items[0] and child.checkState(0) != items[2]):
                        child.setCheckState(0, items[2])
                if num_children != 0:
                    self.check_groups(num_children, child)

    # créé les groupes et ajoutes les enfants dans les groupes
    def set_group_items(self, item, nb):
        if (item.children() == []):
            return 1
        if (nb == None):
            parent = QTreeWidgetItem(self.main.dlg_couches.treeWidget)
        else:
            parent = QTreeWidgetItem(nb)
        parent.setText(0, '%s' % item.name())
        parent.setFlags(parent.flags() | QtCore.Qt.ItemIsTristate | QtCore.Qt.ItemIsUserCheckable)
        node = item
        for childs in node.children():
            if(type(childs) == qgis._core.QgsLayerTreeGroup):
                if (self.set_group_items(childs, parent) == 0):
                    continue
            child = QTreeWidgetItem(parent)
            child.setFlags(child.flags() | QtCore.Qt.ItemIsUserCheckable)
            child.setText(0, '%s' % childs.name())
            child.setCheckState(0, QtCore.Qt.Unchecked)
        return 0

    # récupère la taille de l'abrorésence des couches
    def get_tree_size(self):
        allLayers = qgis.core.QgsProject.instance().layerTreeRoot().children()
        if allLayers:
            for i in allLayers:
                if(type(i) == qgis._core.QgsLayerTreeGroup):
                    self.check_if_subgroup(i)
    def check_if_subgroup(self, item):
        if (item.children() == []):
            return 1
        for childs in item.children():
            if(type(childs) == qgis._core.QgsLayerTreeGroup):
                if (self.check_if_subgroup(childs) == 0):
                    self.main.total_sub_groups += 1
                    continue
        return 0
        

    # ajoute les layers présents dans la séléction de couche de QGIS dans un treeView
    def add_layers(self):
        self.main.total_sub_groups = 0
        self.get_tree_size()
        if (self.main.total_sub_groups > 1):
            return
        self.main.dlg_couches.treeWidget.setHeaderHidden(True)
        allLayers = QgsProject.instance().layerTreeRoot().children()
        # copie le tableau self.main.couche_list si il existe
        temp = []
        if self.main.couche_list != []:
            temp = self.main.couche_list.copy()
        # nettoye le treeView
        for i in self.main.dlg_couches.treeWidget.findItems("", QtCore.Qt.MatchContains , 0): delete(i)
        # ajoute les couches dans le treeView
        for i in allLayers:
            if(type(i) == qgis._core.QgsLayerTreeLayer):
                if i.name() == self.main.controlpoint_layer_name:
                    self.main.control_layer_found = True
                    layer = QgsProject.instance().mapLayersByName(self.main.controlpoint_layer_name)[0]
                    self.controlpoint_layer = layer
                    continue
                layer = QTreeWidgetItem(self.main.dlg_couches.treeWidget)
                layer.setText(0, '%s' % i.name())
                layer.setCheckState(0, 0)
            if(type(i) == qgis._core.QgsLayerTreeGroup):
                self.set_group_items(i, None)

        # ajoute les variables dans le treeView dans couche_list
        total = 0
        self.main.couche_list = []
        self.check_active_layers()
        root = self.main.dlg_couches.treeWidget.invisibleRootItem()
        for i in range(root.childCount()):
            signal = root.child(i)
            self.main.couche_list.append([signal.text(0), total, signal.checkState(0)])
            num_children = signal.childCount()
            if (num_children != 0):
                self.append_for_groups(num_children, signal, total)
            total += 1
        # mets les anciennes variables décochées de nouveau cochées
            for old_item in temp:
                for new_item in self.main.couche_list:
                    if old_item[0] == new_item[0]:
                        new_item[2] = old_item[2]
        # coche toutes les boites à cocher
        for items in self.main.couche_list:
            for i in range(root.childCount()):
                signal = root.child(i)
                num_children = signal.childCount()
                if (signal.text(0) == items[0] and signal.checkState(0) != items[2]):
                    signal.setCheckState(0, items[2])
                if (num_children != 0):
                    self.check_groups(num_children, signal)
        if self.main.dlg_couches.lineEdit.text() != "":
            self.main.recherche.search_couche()