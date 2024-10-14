# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Controles_IGN
                                 A QGIS plugin
 Plugin pour controller les géométries
                              -------------------
        begin                : 2024-09-26
        git sha              : $Format:%H$
        copyright            : (C) 2024 by Ta'o D
        email                : ta-o.darbellay@ign.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, QVariant, QResource
from qgis.PyQt.QtGui import QIcon, QPixmap, QColor
from qgis.PyQt.QtWidgets import QAction, QTreeWidgetItem, QPushButton, QTableWidgetItem, QHeaderView
from qgis.core import *
import qgis
from sip import delete
import ast
import re

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .controles_ign_dialog import Controles_IGNDialog, choix_couche, choix_controles, voir_controles, pas_controles, trop_de_couches
import os.path
from .controles.rebroussement.rerboussement import rebroussement


class Controles_IGN:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        self.dlg = Controles_IGNDialog()
        self.dlg.setFixedSize(self.dlg.size())
        self.dlg_couches = choix_couche()
        self.dlg_couches.setFixedSize(self.dlg_couches.size())
        self.dlg_controles = choix_controles()
        self.dlg_controles.setFixedSize(self.dlg_controles.size())
        self.dlg_voir = voir_controles()
        self.dlg_pas = pas_controles()
        self.dlg_trop = trop_de_couches()
        self.dlg_trop.setFixedSize(self.dlg_trop.size())
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Controles_IGN_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Controles_IGN')
        # Créer sa propre toolbar sur QGIS
        self.toolbar = self.iface.addToolBar(u'Controles_IGN')
        self.toolbar.setObjectName(u'Controles_IGN')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None
        self.controles_actifs = False
        self.value = 0
        self.control_list = []
        self.couche_list = []
        self.add_controls(False)
        self.controles_actifs = 0
        self.controles_restants = 0
        self.couches_actives = 0
        self.controlpoint_layer = None
        self.provider = None
        self.control_layer_found = False
        self.voir_clicked = False
        self.clicked_ctrl = None
        self.row = 0
        self.total_sub_groups = 0
        self.temp_ctrl_list = []
        self.temp_couche_list = []

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Controles_IGN', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins own toolbar
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        # image en base64 utilisée pour l'icone, permettant de ne pas avoir l'image en local
        icon_path = os.path.dirname(os.path.realpath(__file__)) + "\\resources_img\\ign.jpg"
        self.add_action(
            icon_path,
            text=self.tr(u'Lancer fenêtre des contrôles'),
            callback=self.run,
            parent=self.iface.mainWindow())
        icon_path = os.path.dirname(os.path.realpath(__file__)) + "\\resources_img\\see.jpg"
        self.add_action(
            icon_path,
            text=self.tr(u'Voir les contrôles'),
            callback=self.show_controles,
            parent=self.iface.mainWindow())
        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Controles_IGN'),
                action)
            self.iface.removeToolBarIcon(action)



#  PARTIE CONTRÔLES

    # prépare les boites et remets à létat initial les choix si ils n'ont pas étés validés en appuyant sur ok et affiches la boite de dialogue choix_controles
    def choix_controles(self):
        for items in self.control_list:
            root = self.dlg_controles.treeWidget.invisibleRootItem()
            for i in range(root.childCount()):
                signal = root.child(i)
                num_children = signal.childCount()
                if (signal.text(0) == items[0]):
                    signal.setCheckState(0, items[2])
                if (num_children != 0):
                    self.global_contrôle_prep(num_children, signal)
        self.dlg_controles.show()
        self.dlg_controles.treeWidget.expandAll()
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
        root = self.dlg_controles.treeWidget.invisibleRootItem()
        for items in self.control_list:
            for i in range(root.childCount()):
                signal = root.child(i)
                num_children = signal.childCount()
                if (signal.text(0) == items[0] and signal.checkState(0) != items[2]):
                    items[2] = signal.checkState(0)
                if (num_children != 0):
                    self.update_control_boxes2(num_children, signal)
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
        root = self.dlg_controles.treeWidget.invisibleRootItem()
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
        root = self.dlg_controles.treeWidget.invisibleRootItem()
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

    # ajoute les contrôles voulus dans le treeView de self.dlg_controles
    def add_controls(self, search):
        self.dlg_controles.treeWidget.setHeaderHidden(True)
        echelle = QTreeWidgetItem(self.dlg_controles.treeWidget)
        echelle.setText(0, '%s' % "Grande Échelle")
        echelle.setFlags(echelle.flags() | QtCore.Qt.ItemIsTristate | QtCore.Qt.ItemIsUserCheckable)
        type = QTreeWidgetItem(echelle)
        type.setText(0, '%s' % "Contrôles Géométrie")
        type.setFlags(type.flags() | QtCore.Qt.ItemIsTristate | QtCore.Qt.ItemIsUserCheckable)
        item = QTreeWidgetItem(type)
        item.setText(0, '%s' % "rebroussement")
        item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
        item.setCheckState(0, 2)
        item = QTreeWidgetItem(self.dlg_controles.treeWidget)
        item.setText(0, '%s' % "test")
        item.setCheckState(0, 2)
        if search == False:
            self.append_ctrl_to_list()
    
    #renvoie le nombre de controles actifs dans la liste
    def nb_controles_actifs(self):
        self.controles_actifs = 0
        for items in self.control_list:
            if items[2] == QtCore.Qt.Checked:
                self.controles_actifs += 1
        self.controles_restants = 1

    # fonctin de lancement de contrôles, récupère le nombre de contrôles cochés ainsi que le nombre de couches cochées et agis accordément
    def run_controls(self):
        self.nb_controles_actifs()
        if (self.controles_actifs <= 0):
            self.iface.messageBar().pushMessage("Erreur", "Aucun contrôle séléctionné", level=Qgis.Warning, duration=10)
            return
        self.get_active_layers()
        if (self.couches_actives <= 0):
            self.iface.messageBar().pushMessage("Erreur", "Aucune couche séléctionnes", level=Qgis.Warning, duration=10)
            return
        if self.get_total_controles() != 0:
            qinst = QgsProject.instance()
            qinst.removeMapLayer(self.controlpoint_layer)
            self.control_layer_found = False
        rebroussement(self)
    
        widget = self.iface.messageBar().createMessage("Contrôles_IGN", "Contrôles terminés, {} erreurs trouvées".format(int(self.get_total_controles())))
        button = QPushButton(widget)
        button.setText("Montres Moi")
        button.pressed.connect(self.show_controles)
        widget.layout().addWidget(button)
        self.iface.messageBar().pushWidget(widget, Qgis.Warning, duration=10)


  
  # PARTIE COUCHES :

    # récumpère le nombre de couches choisies pour les contrôles
    def get_active_layers(self):
        self.couches_actives = 0
        for items in self.couche_list:
            if items[2] == QtCore.Qt.Checked:
                self.couches_actives += 1

    # prépare les boites et remets à létat initial les choix si ils n'ont pas étés validés en appuyant sur ok et affiches la boite de dialogue choix_couches
    def choix_couches(self):
        for items in self.couche_list:
            root = self.dlg_couches.treeWidget.invisibleRootItem()
            for i in range(root.childCount()):
                signal = root.child(i)
                num_children = signal.childCount()
                if (signal.text(0) == items[0]):
                    signal.setCheckState(0, items[2])
                if (num_children != 0):
                    self.global_couche_prep(num_children, signal)
        self.dlg_couches.show()
        self.dlg_couches.treeWidget.expandAll()
    def global_couche_prep(self, num_children, parent):
        for items in self.couche_list:
            for i in range(parent.childCount()):
                child = parent.child(i)
                num_children = child.childCount()
                if (child.text(0) == items[0]):
                    child.setCheckState(0, items[2])
                if num_children != 0:
                    self.global_couche_prep(num_children, child)

    # coche ou décoche toutes les couches présentes dans le treeView
    def global_checkbox_edit(self, check):
        root = self.dlg_couches.treeWidget.invisibleRootItem()
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
        root = self.dlg_couches.treeWidget.invisibleRootItem()
        for items in self.couche_list:
            for i in range(root.childCount()):
                signal = root.child(i)
                num_children = signal.childCount()
                if (signal.text(0) == items[0] and signal.checkState(0) != items[2]):
                    items[2] = signal.checkState(0)
                if (num_children != 0):
                    self.update_layer_boxes2(num_children, signal)
    def update_layer_boxes2(self, num_children, parent):
        for items in self.couche_list:
            for i in range(parent.childCount()):
                child = parent.child(i)
                num_children = child.childCount()
                if (child.text(0) == items[0] and child.checkState(0) != items[2]):
                    items[2] = child.checkState(0)
                if num_children != 0:
                    self.update_layer_boxes2(num_children, child)


    # coche tous les layers actifs dans la gestion de couches de QGIS
    def check_active_layers(self):
        root = self.dlg_couches.treeWidget.invisibleRootItem()
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
            self.couche_list.append([child.text(0), total, child.checkState(0)])
            if num_children != 0:
                self.append_for_groups(num_children, child, total)
            total += 1

    # coche les boites précédemment checkés dans les groupes
    def check_groups(self, num_children, parent):
        for items in self.couche_list:
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
            parent = QTreeWidgetItem(self.dlg_couches.treeWidget)
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
                    self.total_sub_groups += 1
                    continue
        return 0
        

    # ajoute les layers présents dans la séléction de couche de QGIS dans un treeView
    def add_layers(self):
        self.total_sub_groups = 0
        self.get_tree_size()
        if (self.total_sub_groups > 1):
            return
        self.dlg_couches.treeWidget.setHeaderHidden(True)
        allLayers = qgis.core.QgsProject.instance().layerTreeRoot().children()
        # copie le tableau self.couche_list si il existe
        temp = []
        if self.couche_list != []:
            temp = self.couche_list.copy()
        # nettoye le treeView
        for i in self.dlg_couches.treeWidget.findItems("", QtCore.Qt.MatchContains , 0): delete(i)
        # ajoute les couches dans le treeView
        if allLayers:
            for i in allLayers:
                if(type(i) == qgis._core.QgsLayerTreeLayer):
                    if i.name() == "controles_IGN":
                        self.control_layer_found = True
                        self.get_controlpoint_layer()
                        continue
                    azerty = QTreeWidgetItem(self.dlg_couches.treeWidget)
                    azerty.setText(0, '%s' % i.name())
                    azerty.setCheckState(0, 0)
                if(type(i) == qgis._core.QgsLayerTreeGroup):
                    self.set_group_items(i, None)

        # ajoute les variables dans le treeView dans couche_list
        total = 0
        self.couche_list = []
        self.check_active_layers()
        root = self.dlg_couches.treeWidget.invisibleRootItem()
        for i in range(root.childCount()):
            signal = root.child(i)
            self.couche_list.append([signal.text(0), total, signal.checkState(0)])
            num_children = signal.childCount()
            if (num_children != 0):
                self.append_for_groups(num_children, signal, total)
            total += 1
        # mets les anciennes variables décochées de nouveau cochées
        if temp != []:
            for old_item in temp:
                for new_item in self.couche_list:
                    if old_item[0] == new_item[0]:
                        new_item[2] = old_item[2]
        # coche toutes les boites à checker
        for items in self.couche_list:
            for i in range(root.childCount()):
                signal = root.child(i)
                num_children = signal.childCount()
                if (signal.text(0) == items[0] and signal.checkState(0) != items[2]):
                    signal.setCheckState(0, items[2])
                if (num_children != 0):
                    self.check_groups(num_children, signal)



# PARTIE GLOBALE

    # coche toutes les cases
    def reset(self):
        print("a")
        self.check_control_boxes()
        self.check_layer_boxes()
        self.iface.messageBar().pushMessage("Info", "paramètres réinitialisés", level=Qgis.Info)

    def create_controlpoint_layer(self):
        self.controlpoint_layer = QgsVectorLayer("Point?crs=IGNF:LAMB93", "controles_IGN", "memory")
        self.provider = self.controlpoint_layer.dataProvider()
        self.provider.addAttributes([QgsField("type", QVariant.String),
                                    QgsField("libellé",  QVariant.String),
                                    QgsField("couche", QVariant.String),
                                    QgsField("attributs objet", QVariant.List)])
        self.controlpoint_layer.updateFields()
        single_symbol_renderer = self.controlpoint_layer.renderer()
        symbol = single_symbol_renderer.symbol()
        symbol.setColor(QColor.fromRgb(0, 225, 0))
        self.control_layer_found = True

    def get_controlpoint_layer(self):
        layer = QgsProject.instance().mapLayersByName('controles_IGN')[0]
        self.controlpoint_layer = layer
        self.provider = self.controlpoint_layer.dataProvider()
        self.provider.addAttributes([QgsField("type", QVariant.String),
                                    QgsField("libellé",  QVariant.String),
                                    QgsField("couche", QVariant.String),
                                    QgsField("attributs objet", QVariant.List)])
        self.controlpoint_layer.updateFields()
        
    def get_total_controles(self):
        total = 0
        layer = QgsProject.instance().mapLayersByName('controles_IGN')
        test = len(layer)
        if test == 0:
            self.control_layer_found = False
            return total
        self.controlpoint_layer = layer[0]
        if (self.controlpoint_layer):
            for f in self.controlpoint_layer.getFeatures():
                geom = f.geometry()
                for parts in geom.parts():
                    total += 1
            return total
        else:
            return total
    
    def show_controles(self):
        total = self.get_total_controles()
        i = 0
        if total != 0:
            if self.voir_clicked == False:
                self.dlg_voir.showme.clicked.connect(self.moveto)
                self.dlg_voir.zoom.clicked.connect(self.zoomto)
                self.dlg_voir.blink.clicked.connect(self.clignoter)
                self.dlg_voir.suppr.clicked.connect(self.suppr_controle)
                self.voir_clicked = True
            self.dlg_voir.tableWidget.setRowCount(total)
            header = self.dlg_voir.tableWidget.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(4, QHeaderView.Stretch)
            for f in self.controlpoint_layer.getFeatures():
                geom = f.geometry()
                attributes = f.attributes()
                # mets les coordonées du contrôle dans la première colone
                nums = re.findall(r'\-?[0-9]+(?:\.[0-9]*)?', str(QgsGeometry.asPoint(geom)))
                coords = tuple(zip(*[map(float, nums)] * 2))[0]
                self.dlg_voir.tableWidget.setItem(i , 0, QTableWidgetItem(str(coords)))
                self.dlg_voir.tableWidget
                j = 1
                # ajoute les attibuts du controle dans le tableau*
                for info in attributes:
                    self.dlg_voir.tableWidget.setItem(i , j, QTableWidgetItem(str(info)))
                    j += 1
                i += 1
            self.dlg_voir.show()
            result = self.dlg_voir.exec_()
            if result:
                return
        else:
            self.dlg_pas.show()
    
    def clignoter(self):
        list = []
        if self.get_total_controles != 0:
            for f in self.controlpoint_layer.getFeatures():
                list.append(f.geometry())
            self.iface.mapCanvas().flashGeometries(list)
    
    def zoomto(self):
        self.row = self.dlg_voir.tableWidget.currentRow()
        item = self.dlg_voir.tableWidget.item(self.row, 0)
        canvas = self.iface.mapCanvas()
        canvas.zoomScale(768)
        test = ast.literal_eval(item.text())
        rect = QgsRectangle(test[0], test[1], test[0], test[1])
        canvas.zoomScale(8)
        canvas.setExtent(rect)
    
    def moveto(self):
        self.row = self.dlg_voir.tableWidget.currentRow()
        item = self.dlg_voir.tableWidget.item(self.row, 0)
        canvas = self.iface.mapCanvas()
        scale = canvas.scale()
        canvas.zoomScale(768)
        test = ast.literal_eval(item.text())
        rect = QgsRectangle(test[0], test[1], test[0], test[1])
        canvas.setExtent(rect)
        canvas.zoomScale(scale)
                
    def suppr_controle(self):
        i = 0
        self.dlg_voir.tableWidget.removeRow(self.row)
        with edit(self.controlpoint_layer):
            for f in self.controlpoint_layer.getFeatures():
                if i == self.row:
                    self.controlpoint_layer.deleteFeature(f.id())
                    return
                i += 1

# PARTIE DE LANCEMENT DU CODE


    def search_update_couche_status(self, name, status):
        for items in self.temp_couche_list:
            if items[0] == name:
                items[1] = status

    def search_couche2(self, num_children, parent):
        for i in range(parent.childCount()):
            child = parent.child(i)
            num_children = child.childCount()
            if num_children != 0:
                self.search_control2(num_children, child)
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
                    
    def search_couche(self):
        root = self.dlg_couches.treeWidget.invisibleRootItem()
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
        for i in self.dlg_couches.treeWidget.findItems("", QtCore.Qt.MatchContains , 0): delete(i)
        if self.dlg_couches.lineEdit.text() == "":
            self.add_layers()
            for items in self.temp_couche_list:
                root = self.dlg_couches.treeWidget.invisibleRootItem()
                for i in range(root.childCount()):
                    signal = root.child(i)
                    num_children = signal.childCount()
                    if (signal.text(0) == items[0]):
                        signal.setCheckState(0, items[1])
                    if (num_children != 0):
                        self.search_update_couche_groups(num_children, signal)
        else:
            self.dlg_couches.treeWidget.setHeaderHidden(True)
            for items in self.temp_couche_list:
                if items[0].startswith(self.dlg_couches.lineEdit.text()):
                    item = QTreeWidgetItem(self.dlg_couches.treeWidget)
                    item.setText(0, '%s' % items[0])
                    item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                    item.setCheckState(0, items[1])
        self.dlg_couches.treeWidget.expandAll()


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
                    
    def search_control(self):
        root = self.dlg_controles.treeWidget.invisibleRootItem()
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
        for i in self.dlg_controles.treeWidget.findItems("", QtCore.Qt.MatchContains , 0): delete(i)
        if self.dlg_controles.lineEdit.text() == "":
            self.add_controls(True)
            for items in self.temp_ctrl_list:
                root = self.dlg_controles.treeWidget.invisibleRootItem()
                for i in range(root.childCount()):
                    signal = root.child(i)
                    num_children = signal.childCount()
                    if (signal.text(0) == items[0]):
                        signal.setCheckState(0, items[1])
                    if (num_children != 0):
                        self.search_update_groups(num_children, signal)
        else:
            self.dlg_controles.treeWidget.setHeaderHidden(True)
            for items in self.temp_ctrl_list:
                if items[0].startswith(self.dlg_controles.lineEdit.text()):
                    item = QTreeWidgetItem(self.dlg_controles.treeWidget)
                    item.setText(0, '%s' % items[0])
                    item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                    item.setCheckState(0, items[1])
        self.dlg_controles.treeWidget.expandAll()

    def run(self):
        """Run method that performs all the real work"""

        # ajoute les couches dans self.couche_list et dans la boite de selection de self.dlg_couches
        self.add_layers()

        # show the dialog
        if (self.total_sub_groups > 1):
            self.dlg_trop.show()
            self.iface.messageBar().pushMessage("ATTENTION", "Le nombre de sous groupe dépasse la puissance de calcul de QGIS pour faire les contrôles, veulliez diminuer le nombre de sous groupes pour une utilisation fluide du plugin", level=Qgis.Critical)
            return
        self.dlg.show()
        # Run the dialog event loop
        if self.first_start == True:
            self.first_start = False
            self.dlg.resetButton.clicked.connect(self.reset)
            self.dlg.coucheButton.clicked.connect(self.choix_couches)
            self.dlg.controleButton.clicked.connect(self.choix_controles)
            self.dlg_controles.buttonBox.clicked.connect(self.update_control_boxes)
            self.dlg_controles.uncheck_all.clicked.connect(self.uncheck_control_boxes)
            self.dlg_controles.check_all.clicked.connect(self.check_control_boxes)
            self.dlg_couches.buttonBox.clicked.connect(self.update_layer_boxes)
            self.dlg_couches.uncheck_all.clicked.connect(self.uncheck_layer_boxes)
            self.dlg_couches.check_all.clicked.connect(self.check_layer_boxes)
            self.dlg_controles.lineEdit.textChanged.connect(self.search_control)
            self.dlg_couches.lineEdit.textChanged.connect(self.search_couche)
        if self.voir_clicked == False:
            self.dlg_voir.showme.clicked.connect(self.moveto)
            self.dlg_voir.zoom.clicked.connect(self.zoomto)
            self.dlg_voir.suppr.clicked.connect(self.suppr_controle)
            self.dlg_voir.blink.clicked.connect(self.clignoter)
            self.voir_clicked = True


        # See if OK was pressed
        result = self.dlg.exec_()
        if result:
            self.run_controls()
