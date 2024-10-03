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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon, QPixmap, QStandardItemModel, QStandardItem
from qgis.PyQt.QtWidgets import QAction, QProgressDialog
from qgis.utils import iface
from qgis.core import *
from qgis import *
from numpy import copy
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
        self.dlg2 = choix_couche()
        self.dlg2.setFixedSize(self.dlg2.size())
        self.dlg3 = choix_controles()
        self.dlg3.setFixedSize(self.dlg3.size())
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
        self.controle_actif = False
        self.value = 0
        self.control_list = []
        self.couche_list = []
        self.add_controls()

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


    def reset(self):
        self.check_all_ctrl()
        self.check_layer_boxes()
        self.iface.messageBar().pushMessage("Info", "paramètres réinitialisés", level=Qgis.Info)


    def choix_controles(self):
        for i in range (self.dlg3.listView.model().rowCount()):
            for items in self.control_list:
                if self.dlg3.listView.model().item(i).text() == items[0] and self.dlg3.listView.model().item(i).checkState() != items[2]:
                    self.dlg3.listView.model().item(i).setCheckState(items[2])
        self.dlg3.show()

    def add_controls(self):
        model = QStandardItemModel()
        item = QStandardItem('%s' % "rebroussement")
        item.setCheckable(True)
        item.setCheckState(QtCore.Qt.Checked)
        model.appendRow(item)
        item = QStandardItem('%s' % "contôle")
        item.setCheckable(True)
        item.setCheckState(QtCore.Qt.Checked)
        model.appendRow(item)
        self.dlg3.listView.setModel(model)
        self.dlg3.listView.show()
        for i in range (self.dlg3.listView.model().rowCount()):
            self.control_list.append([self.dlg3.listView.model().item(i).text(), i, self.dlg3.listView.model().item(i).checkState()])

    def update_control_checkboxes(self):
        for i in range (self.dlg3.listView.model().rowCount()):
            for items in self.control_list:
                if self.dlg3.listView.model().item(i).text() == items[0] and self.dlg3.listView.model().item(i).checkState() != items[2]:
                    items[2] = self.dlg3.listView.model().item(i).checkState()

    def uncheck_all_ctrl(self):
        for i in range (self.dlg3.listView.model().rowCount()):
            self.dlg3.listView.model().item(i).setCheckState(0)

    def check_all_ctrl(self):
        for i in range (self.dlg3.listView.model().rowCount()):
            self.dlg3.listView.model().item(i).setCheckState(2)



    def choix_couches(self):
        for i in range (self.dlg2.listView.model().rowCount()):
            for items in self.couche_list:
                if self.dlg2.listView.model().item(i).text() == items[0] and self.dlg2.listView.model().item(i).checkState() != items[2]:
                    self.dlg2.listView.model().item(i).setCheckState(items[2])
        self.dlg2.show()

    def check_layer_boxes(self):
        for i in range (self.dlg2.listView.model().rowCount()):
            self.dlg2.listView.model().item(i).setCheckState(2)

    def uncheck_layer_boxes(self):
        for i in range (self.dlg2.listView.model().rowCount()):
            self.dlg2.listView.model().item(i).setCheckState(0)

    def update_layer_checkboxes(self):
        for i in range (self.dlg2.listView.model().rowCount()):
            for items in self.couche_list:
                if self.dlg2.listView.model().item(i).text() == items[0] and self.dlg2.listView.model().item(i).checkState() != items[2]:
                    items[2] = self.dlg2.listView.model().item(i).checkState()

    def add_layers(self):
        """ Adds Checkboxes inside the listview dynamically based on the number of layers loaded in QGIS. """

        canvas = qgis.utils.iface.mapCanvas()
        allLayers = canvas.layers()
        temp = []
        if self.couche_list != []:
            temp = self.couche_list.copy()
        if canvas.layerCount != 0:
            model = QStandardItemModel()
            for i in allLayers:
                item = QStandardItem('%s' % i.name())
                item.setCheckable(True)
                item.setCheckState(QtCore.Qt.Checked)
                model.appendRow(item)

            self.dlg2.listView.setModel(model)
            self.dlg2.listView.show()
        
        model = self.dlg2.listView.model()
        self.couche_list = []
        for i in range (self.dlg2.listView.model().rowCount()):
            self.couche_list.append([self.dlg2.listView.model().item(i).text(), i, self.dlg2.listView.model().item(i).checkState()])
        if temp != []:
            for old_item in temp:
                for new_item in self.couche_list:
                    if old_item[0] == new_item[0]:
                        new_item[2] = old_item[2]
        for i in range (self.dlg2.listView.model().rowCount()):
            for items in self.couche_list:
                if self.dlg2.listView.model().item(i).text() == items[0] and self.dlg2.listView.model().item(i).checkState() != items[2]:
                    self.dlg2.listView.model().item(i).setCheckState(items[2])


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False

        # ajoute les couches dans self.couche_list et dans la boite de selection de self.dlg2
        self.add_layers()

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        # self.addLayers()
        self.dlg.resetButton.clicked.connect(self.reset)  
        self.dlg.coucheButton.clicked.connect(self.choix_couches)
        self.dlg.controleButton.clicked.connect(self.choix_controles)
        self.dlg3.buttonBox.clicked.connect(self.update_control_checkboxes)
        self.dlg3.uncheck_all.clicked.connect(self.uncheck_all_ctrl)
        self.dlg3.check_all.clicked.connect(self.check_all_ctrl)
        self.dlg2.buttonBox.clicked.connect(self.update_layer_checkboxes)
        self.dlg2.uncheck_all.clicked.connect(self.uncheck_layer_boxes)
        self.dlg2.check_all.clicked.connect(self.check_layer_boxes)
        # for i in range(len(self.control_list)):
        #     print(self.control_list[i][2])
        #     self.control_list[i][0].clicked.connect(self.update_check_status)
        # See if OK was pressed
        result = self.dlg.exec_()
        if result:
            if (rebroussement(self) == 1):
                print("contrôles annulés")

