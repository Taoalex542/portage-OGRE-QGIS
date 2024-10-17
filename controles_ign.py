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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QPushButton
from qgis.core import QgsProject, Qgis
from datetime import datetime
from .gestion_couches import gestion_couches
from .gestion_contrôles import gestion_controles
from .recherche import recherche
from .affichage_contrôles import affichage_controles

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
        self.value = 0
        self.control_list = []
        self.couche_list = []
        self.controles_actifs = 0
        self.controles_restants = 0
        self.couches_actives = 0
        self.controlpoint_layer = None
        self.provider = None
        self.control_layer_found = False
        self.voir_clicked = False
        self.clicked_ctrl = None
        self.row = 0
        self.date = datetime.today().strftime('%d_%m_%Y')
        self.controlpoint_layer_name = "controles_IGN_" + self.date
        self.total_sub_groups = 0
        self.temp_ctrl_list = []
        self.temp_couche_list = []
        self.gestion_couches = gestion_couches(self, self.iface, self.iface.mainWindow())
        self.gestion_controles = gestion_controles(self, self.iface, self.iface.mainWindow())
        self.recherche = recherche(self, self.iface, self.iface.mainWindow())
        self.affichage_controles = affichage_controles(self, self.iface, self.iface.mainWindow())
        self.gestion_controles.add_controls(False)

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
            callback=self.affichage_controles.show_controles,
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


# PARTIE GLOBALE
    def run_controls(self):
        self.gestion_controles.nb_controles_actifs()
        if (self.controles_actifs <= 0):
            self.iface.messageBar().pushMessage("Erreur", "Aucun contrôle séléctionné", level=Qgis.Warning, duration=10)
            return
        self.gestion_couches.get_active_layers()
        if (self.couches_actives <= 0):
            self.iface.messageBar().pushMessage("Erreur", "Aucune couche séléctionnée", level=Qgis.Warning, duration=10)
            return
        if self.affichage_controles.get_total_controles() != 0:
            qinst = QgsProject.instance()
            qinst.removeMapLayer(self.controlpoint_layer)
            self.control_layer_found = False
        rebroussement(self)
    
        widget = self.iface.messageBar().createMessage("Contrôles_IGN", "Contrôles terminés, {} erreurs trouvées".format(int(self.affichage_controles.get_total_controles())))
        button = QPushButton(widget)
        button.setText("Montres Moi")
        button.pressed.connect(self.affichage_controles.show_controles)
        widget.layout().addWidget(button)
        self.iface.messageBar().pushWidget(widget, Qgis.Warning, duration=10)

    # coche toutes les cases
    def reset(self):
        self.gestion_controles.check_control_boxes()
        self.gestion_couches.check_layer_boxes()
        self.iface.messageBar().pushMessage("Info", "paramètres réinitialisés", level=Qgis.Info)

    

# PARTIE DE LANCEMENT DU CODE

    def run(self):
        """Run method that performs all the real work"""

        # ajoute les couches dans self.couche_list et dans la boite de selection de self.dlg_couches
        self.gestion_couches.add_layers()

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
            self.dlg.coucheButton.clicked.connect(self.gestion_couches.choix_couches)
            self.dlg.controleButton.clicked.connect(self.gestion_controles.choix_controles)
            self.dlg_controles.buttonBox.clicked.connect(self.gestion_controles.update_control_boxes)
            self.dlg_controles.uncheck_all.clicked.connect(self.gestion_controles.uncheck_control_boxes)
            self.dlg_controles.check_all.clicked.connect(self.gestion_controles.check_control_boxes)
            self.dlg_couches.buttonBox.clicked.connect(self.gestion_couches.update_layer_boxes)
            self.dlg_couches.uncheck_all.clicked.connect(self.gestion_couches.uncheck_layer_boxes)
            self.dlg_couches.check_all.clicked.connect(self.gestion_couches.check_layer_boxes)
            self.dlg_controles.lineEdit.textChanged.connect(self.recherche.search_control)
            self.dlg_couches.lineEdit.textChanged.connect(self.recherche.search_couche)
        if self.voir_clicked == False:
            self.dlg_voir.showme.clicked.connect(self.affichage_controles.moveto)
            self.dlg_voir.zoom.clicked.connect(self.affichage_controles.zoomto)
            self.dlg_voir.suppr.clicked.connect(self.affichage_controles.suppr_controle)
            self.dlg_voir.blink.clicked.connect(self.affichage_controles.clignoter)
            self.voir_clicked = True


        # See if OK was pressed
        result = self.dlg.exec_()
        if result:
            self.run_controls()
