# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Controles_IGN
                                 A QGIS plugin
 Saves attributes of the selected vector
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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, QVariant
from qgis.PyQt.QtGui import QIcon, QPixmap, QColor
from qgis.PyQt.QtWidgets import QAction, QTreeWidgetItem
from qgis.core import *
import qgis
from sip import delete
import base64
import time

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .controles_ign_dialog import Controles_IGNDialog, choix_couche, choix_controles
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
        self.add_controls()
        self.controles_actifs = 0
        self.controles_restants = 0
        self.couches_actives = 0
        self.controlpoint_layer = None
        self.provider = None
        self.control_layer_found = False

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
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        # image en base64 utilisée pour l'icone, permettant de ne pas avoir l'image en local
        base64_data = "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"
        pm1 = QPixmap()
        pm1.loadFromData(base64.b64decode(base64_data))
        self.add_action(
            QIcon(pm1),
            text=self.tr(u'Lancer fenêtre des contrôles'),
            callback=self.run,
            parent=self.iface.mainWindow())
        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
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
    def add_controls(self):
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
        if self.controlpoint_layer:
            qinst = QgsProject.instance()
            qinst.removeMapLayer(self.controlpoint_layer)
            self.control_layer_found = False
        rebroussement(self)
        self.iface.messageBar().pushMessage("Info", "Contrôles terminés", level=Qgis.Success, duration=5)
  
  
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

    # ajoute les layers présents dans la séléction de couche de QGIS dans un treeView
    def add_layers(self):
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
        self.check_all_ctrl()
        self.check_layer_boxes()
        self.iface.messageBar().pushMessage("Info", "paramètres réinitialisés", level=Qgis.Info)

    def create_controlpoint_layer(self):
        self.controlpoint_layer = QgsVectorLayer("Point?crs=IGNF:LAMB93", "controles_IGN", "memory")
        self.provider = self.controlpoint_layer.dataProvider()
        self.provider.addAttributes([QgsField("type", QVariant.String),
                        QgsField("libllé",  QVariant.String),
                        QgsField("attrubuts objet", QVariant.List)])
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
                                    QgsField("libllé",  QVariant.String),
                                    QgsField("attrubuts objet", QVariant.List)])
        self.controlpoint_layer.updateFields()
        

# PARTIE DE LANCEMENT DU CODE

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False

        # ajoute les couches dans self.couche_list et dans la boite de selection de self.dlg_couches
        self.add_layers()

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        self.dlg.resetButton.clicked.connect(self.reset)
        self.dlg.coucheButton.clicked.connect(self.choix_couches)
        self.dlg.controleButton.clicked.connect(self.choix_controles)
        self.dlg_controles.buttonBox.clicked.connect(self.update_control_boxes)
        self.dlg_controles.uncheck_all.clicked.connect(self.uncheck_control_boxes)
        self.dlg_controles.check_all.clicked.connect(self.check_control_boxes)
        self.dlg_couches.buttonBox.clicked.connect(self.update_layer_boxes)
        self.dlg_couches.uncheck_all.clicked.connect(self.uncheck_layer_boxes)
        self.dlg_couches.check_all.clicked.connect(self.check_layer_boxes)

        # See if OK was pressed
        result = self.dlg.exec_()
        if result:
            self.run_controls()
