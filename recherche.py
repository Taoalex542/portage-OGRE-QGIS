from qgis.PyQt.QtWidgets import QTreeWidgetItem, QDockWidget
from qgis.core import *
from sip import delete

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog

class recherche(QDockWidget):

    def __init__(self, main, iface):
        super(recherche, self).__init__()
        self.iface = iface
        self.main = main
        self.temp_ctrl_list = []
        self.temp_couche_list = []
        self.temp_precis_list = []
    
    
    # recherche pour les couches
    
    def search_update_couche_status(self, name, status):
        for items in self.temp_couche_list:
            if items[0] == name:
                items[1] = status

    def search_couche2(self, num_children, parent):
        for i in range(parent.childCount()):
            child = parent.child(i)
            num_children = child.childCount()
            if num_children != 0:
                self.main.search_control2(num_children, child)
            else:
                if [child.text(0), 0] not in self.temp_couche_list and [child.text(0), 2] not in self.temp_couche_list:
                    self.temp_couche_list.append([child.text(0), child.checkState(0)])
                else:
                    self.search_update_couche_status(child.text(0), child.checkState(0))
                    
    def search_update_couche_groups(self, num_children, parent):
        for items in self.temp_couche_list:
            for i in range(parent.childCount()):
                child = parent.child(i)
                num_children = child.childCount()
                if (child.text(0) == items[0]):
                    child.setCheckState(0, items[1])
                if num_children != 0:
                    self.search_update_couche_groups(num_children, child)
    
    # fonction principale de la recherche 
    def search_couche(self):
        root = self.main.dlg_couches.treeWidget.invisibleRootItem()
        # récupère le statut de tous les objets cochables
        for i in range(root.childCount()):
            signal = root.child(i)
            num_children = signal.childCount()
            if (num_children != 0):
                self.search_couche2(num_children, signal)
            else:
                if [signal.text(0), 0] not in self.temp_couche_list and [signal.text(0), 2] not in self.temp_couche_list:
                    self.temp_couche_list.append([signal.text(0), signal.checkState(0)])
                else:
                    self.search_update_couche_status(signal.text(0), signal.checkState(0))
        for i in self.main.dlg_couches.treeWidget.findItems("", QtCore.Qt.MatchContains , 0): delete(i)
        
        # si le texte est vide, affiche l'arbre de choix normalement
        if self.main.dlg_couches.lineEdit.text() == "":
            self.main.gestion_couches.add_layers()
            for items in self.temp_couche_list:
                root = self.main.dlg_couches.treeWidget.invisibleRootItem()
                for i in range(root.childCount()):
                    signal = root.child(i)
                    num_children = signal.childCount()
                    if (signal.text(0) == items[0]):
                        signal.setCheckState(0, items[1])
                    if (num_children != 0):
                        self.search_update_couche_groups(num_children, signal)

        # sinon affiche seulement les objets commencant par la recherche
        else:
            self.main.dlg_couches.treeWidget.setHeaderHidden(True)
            for items in self.temp_couche_list:
                if items[0].startswith(self.main.dlg_couches.lineEdit.text()):
                    item = QTreeWidgetItem(self.main.dlg_couches.treeWidget)
                    item.setText(0, '%s' % items[0])
                    item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                    item.setCheckState(0, items[1])
        self.main.dlg_couches.treeWidget.expandAll()
        self.main.dlg_precis.lineEdit.setText(self.main.dlg_couches.lineEdit.text())


    # recherche dans les contrôles

    def search_update_status(self, name, status):
        for items in self.temp_ctrl_list:
            if items[0] == name:
                items[1] = status

    def search_control2(self, num_children, parent):
        for i in range(parent.childCount()):
            child = parent.child(i)
            num_children = child.childCount()
            if num_children != 0:
                self.search_control2(num_children, child)
            else:
                if [child.text(0), 0] not in self.temp_ctrl_list and [child.text(0), 2] not in self.temp_ctrl_list:
                    self.temp_ctrl_list.append([child.text(0), child.checkState(0)])
                else:
                    self.search_update_status(child.text(0), child.checkState(0))
                    
    def search_update_groups(self, num_children, parent):
        for items in self.temp_ctrl_list:
            for i in range(parent.childCount()):
                child = parent.child(i)
                num_children = child.childCount()
                if (child.text(0) == items[0]):
                    child.setCheckState(0, items[1])
                if num_children != 0:
                    self.search_update_groups(num_children, child)
    
    # fonction principale de la recherche 
    def search_control(self):
        root = self.main.dlg_controles.treeWidget.invisibleRootItem()
        # récupère le statut de tous les objets cochables
        for i in range(root.childCount()):
            signal = root.child(i)
            num_children = signal.childCount()
            if (num_children != 0):
                self.search_control2(num_children, signal)
            else:
                if [signal.text(0), 0] not in self.temp_ctrl_list and [signal.text(0), 2] not in self.temp_ctrl_list:
                    self.temp_ctrl_list.append([signal.text(0), signal.checkState(0)])
                else:
                    self.search_update_status(signal.text(0), signal.checkState(0))
        for i in self.main.dlg_controles.treeWidget.findItems("", QtCore.Qt.MatchContains , 0): delete(i)
        
        # si le texte est vide, affiche l'arbre de choix normalement
        if self.main.dlg_controles.lineEdit.text() == "":
            self.main.gestion_controles.add_controls(True)
            for items in self.temp_ctrl_list:
                root = self.main.dlg_controles.treeWidget.invisibleRootItem()
                for i in range(root.childCount()):
                    signal = root.child(i)
                    num_children = signal.childCount()
                    if (signal.text(0) == items[0]):
                        signal.setCheckState(0, items[1])
                    if (num_children != 0):
                        self.search_update_groups(num_children, signal)
                        
        # sinon affiche seulement les objets commencant par la recherche
        else:
            self.main.dlg_controles.treeWidget.setHeaderHidden(True)
            for items in self.temp_ctrl_list:
                if items[0].startswith(self.main.dlg_controles.lineEdit.text()):
                    item = QTreeWidgetItem(self.main.dlg_controles.treeWidget)
                    item.setText(0, '%s' % items[0])
                    item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                    item.setCheckState(0, items[1])
        self.main.dlg_controles.treeWidget.expandAll()
        
        
    
    # Recherche pour precis

    def search_update_precis_status(self, name, status):
        for items in self.temp_precis_list:
            if items[0] == name:
                items[1] = status

    def search_precis2(self, num_children, parent):
        for i in range(parent.childCount()):
            child = parent.child(i)
            num_children = child.childCount()
            if num_children != 0:
                self.main.search_control2(num_children, child)
            else:
                if [child.text(0), 0] not in self.temp_precis_list and [child.text(0), 2] not in self.temp_precis_list:
                    self.temp_precis_list.append([child.text(0), child.checkState(0)])
                else:
                    self.search_update_precis_status(child.text(0), child.checkState(0))
                    
    def search_update_precis_groups(self, num_children, parent):
        for items in self.temp_precis_list:
            for i in range(parent.childCount()):
                child = parent.child(i)
                num_children = child.childCount()
                if (child.text(0) == items[0]):
                    child.setCheckState(0, items[1])
                if num_children != 0:
                    self.search_update_precis_groups(num_children, child)
    
    # fonction principale de la recherche 
    def search_precis(self):
        root = self.main.dlg_precis.treeWidget.invisibleRootItem()
        # récupère le statut de tous les objets cochables
        for i in range(root.childCount()):
            signal = root.child(i)
            num_children = signal.childCount()
            if (num_children != 0):
                self.search_precis2(num_children, signal)
            else:
                if [signal.text(0), 0] not in self.temp_precis_list and [signal.text(0), 2] not in self.temp_precis_list:
                    self.temp_precis_list.append([signal.text(0), signal.checkState(0)])
                else:
                    self.search_update_precis_status(signal.text(0), signal.checkState(0))
        for i in self.main.dlg_precis.treeWidget.findItems("", QtCore.Qt.MatchContains , 0): delete(i)
        
        # si le texte est vide, affiche l'arbre de choix normalement
        if self.main.dlg_precis.lineEdit.text() == "":
            self.main.gestion_couches.precis_add_layers()
            for items in self.temp_precis_list:
                root = self.main.dlg_precis.treeWidget.invisibleRootItem()
                for i in range(root.childCount()):
                    signal = root.child(i)
                    num_children = signal.childCount()
                    if (signal.text(0) == items[0]):
                        signal.setCheckState(0, items[1])
                    if (num_children != 0):
                        self.search_update_precis_groups(num_children, signal)

        # sinon affiche seulement les objets commencant par la recherche
        else:
            self.main.dlg_precis.treeWidget.setHeaderHidden(True)
            for items in self.temp_precis_list:
                if items[0].startswith(self.main.dlg_precis.lineEdit.text()):
                    item = QTreeWidgetItem(self.main.dlg_precis.treeWidget)
                    item.setText(0, '%s' % items[0])
                    item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                    item.setCheckState(0, items[1])
        self.main.dlg_precis.treeWidget.expandAll()
