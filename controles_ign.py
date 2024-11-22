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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QPushButton, QDialogButtonBox, QToolButton
from qgis.core import QgsProject, Qgis, QgsMapLayer
from datetime import datetime
import os
import importlib
from .gestion_couches import gestion_couches
from .gestion_contrôles import gestion_controles
from .recherche import recherche
from .affichage_contrôles import affichage_controles
from .multi_selection_point import multi_selection_point
from .multi_selection_rectangle import multi_selection_rectangle
import re

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .controles_ign_dialog import Controles_IGNDialog, choix_couche, choix_controles, voir_controles, pas_controles, trop_de_couches, choix_precis
import os.path


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
        self.dlg_precis = choix_precis()
        self.dlg_precis.setFixedSize(self.dlg_precis.size())
        self.couche_list = []
        self.controles_actifs = 0
        self.controles_restants = 0
        self.couches_actives = 0
        self.controlpoint_layer = None
        self.control_layer_found = False
        self.voir_clicked = False
        self.controlpoint_layer_name = "controles_IGN_" + datetime.today().strftime('%d_%m_%Y')
        self.total_sub_groups = 0
        self.gestion_couches = gestion_couches(self, self.iface)
        self.gestion_controles = gestion_controles(self, self.iface)
        self.recherche = recherche(self, self.iface)
        self.affichage_controles = affichage_controles(self, self.iface)
        self.loaded_controles = []
        self.organisation = []
        self.dynamic_import_from_src(os.path.dirname(os.path.realpath(__file__)) + "\\controles", False)
        self.gestion_controles.add_controls(False)
        self.actionList = []
        self.selected = 0
        self.shift = 0
        # Créer sa propre toolbar sur QGIS
        self.toolbar = self.iface.addToolBar(u'Controles_IGN')
        self.toolbar.setObjectName(u'Controles_IGN')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        # initialisation de toutes les données utilisées
        self.first_start = None

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

    def creerBouton(self, parent, text):
        button = QToolButton(parent)
        button.setObjectName(text)
        button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        button.setPopupMode(QToolButton.MenuButtonPopup)
        parent.addWidget(button)
        return button

    def creerAction(self, icon_path, text, callback, checkable=True):
        action = QAction(
            QIcon(icon_path),
            text,
            self.iface.mainWindow())
        # connect the action to the run method
        action.setCheckable(checkable)
        if checkable:
            action.toggled.connect(callback)
        else:
            action.triggered.connect(callback)
        self.iface.registerMainWindowAction(action, '')
        self.actionList.append(action)
        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = os.path.dirname(os.path.realpath(__file__)) + "\\resources_img\\ign.jpg"
        self.add_action(
            icon_path,
            text=self.tr(u'Lancer fenêtre des contrôles'),
            callback=self.run,
            parent=self.iface.mainWindow())

        self.selecPoint = self.creerAction(os.path.dirname(os.path.realpath(__file__)) + "\\resources_img\\point.jpg",
                                            u"Multi Sélection par Point",
                                            self.run_select)
        self.selecRectangle = self.creerAction(os.path.dirname(os.path.realpath(__file__)) + "\\resources_img\\rectangle.png",
                                                      u"Sélection Multiple avec Rectangle",
                                                      self.runRectangle)
        self.actionClear = self.creerAction(os.path.dirname(os.path.realpath(__file__)) + "\\resources_img\\annuler.png",
                                                      u"Tout Déséléctionner",
                                                      self.clear,
                                                      checkable=False)
        self.tool = multi_selection_point(self.iface.mapCanvas(), self.selecPoint, self)
        self.toolRectangle = multi_selection_rectangle(self.iface.mapCanvas(), self.selecRectangle, self)
        self.selectionButton = self.creerBouton(self.toolbar, u'MultipleSelectionButton')
        self.selectionButton.addAction(self.selecRectangle)
        self.selectionButton.addAction(self.selecPoint)
        self.selectionButton.addAction(self.actionClear)
        self.selectionButton.setDefaultAction(self.selecRectangle)

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


# PARTIE PLUGIN

    # récupère les objets cochés dans la fenètre de précisions et les renvoies dans un tableau
    def deuxieme_demande(self, nom, func):
        temp = []
        text = self.dlg_precis.lineEdit.text()
        self.dlg_precis.lineEdit.setText("")
        otext = self.dlg_controles.lineEdit.text()
        self.dlg_couches.lineEdit.setText("")
        for item in self.dlg_controles.treeWidget.findItems(nom, QtCore.Qt.MatchRecursive):
            if item.checkState(0) == 2:
                self.dlg_precis.setWindowTitle("deuxième choix: " + nom)
                self.gestion_couches.precis_add_layers()
                tuples = func(self)
                self.dlg_precis.lineEdit.setText(text)
                if(self.dlg_precis.exec()):
                    temp = tuples
                    for layers in self.dlg_precis.treeWidget.findItems("", QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive):
                        if layers.checkState(0):
                            temp.append(layers.text(0))
                else:
                    return ["b*#ZfD=ku%P-QGUd~s;e5MzEmKvaSC"]
            else :
                self.dlg_couches.lineEdit.setText(otext)
                return [None]
        self.dlg_couches.lineEdit.setText(otext)
        return temp
    
    def has_selected(self):
        allLayers = QgsProject.instance().mapLayers().values()
        for layers in allLayers:
            layer = layers.selectedFeatures()
            if layer != []:
                return 1
        return 0
    
    # vérifie si tout est ok et que il y a des contrôles a lancer, puis lances les contrôles
    def run_controls(self):
        self.gestion_controles.nb_controles_actifs()
        if (self.controles_actifs <= 0):
            self.iface.messageBar().clearWidgets()
            self.iface.messageBar().pushMessage("Erreur", "Aucun contrôle séléctionné", level=Qgis.Warning, duration=10)
            return
        self.gestion_couches.get_active_layers()
        if (self.couches_actives <= 0):
            self.iface.messageBar().clearWidgets()
            self.iface.messageBar().pushMessage("Erreur", "Aucune couche séléctionnée", level=Qgis.Warning, duration=10)
            return
        #supprime la couche des contrôles si ell existe
        self.precis_intersection = self.deuxieme_demande("intersection", intersection.get_params) #type: ignore
        if self.precis_intersection[0] == "b*#ZfD=ku%P-QGUd~s;e5MzEmKvaSC":
            self.iface.messageBar().clearWidgets()
            self.iface.messageBar().pushMessage("Info", "Contrôles annulés", level=Qgis.Info, duration=10)
            return
        if self.affichage_controles.get_total_controles() != 0:
            qinst = QgsProject.instance()
            qinst.removeMapLayer(self.controlpoint_layer)
            self.control_layer_found = False
        self.controles_restants = 0
        self.selected = self.has_selected()
        # lance le controle si les deux fichiers sont chargés (ceci est la seule partie non automatique pour lancer les controles, il suffit de remplacer le mot "intersection" avec le controle voulu pour ajouter le controle dans les lancements)
        if ("intersection.py" in self.loaded_controles and "ctrl_intersection.py" in self.loaded_controles):
            intersection.intersection(self, ctrl_intersection.ctrl_intersection) #type: ignore
        if ("rebroussement.py" in self.loaded_controles and "ctrl_rebroussement.py" in self.loaded_controles):
            rebroussement.rebroussement(self, ctrl_rebroussement.ctrl_rebroussement) #type: ignore
        if ("auto_intersection.py" in self.loaded_controles and "ctrl_auto_intersection.py" in self.loaded_controles):
            auto_intersection.auto_intersection(self, ctrl_auto_intersection.ctrl_auto_intersection) #type: ignore
        if ("attributs.py" in self.loaded_controles and "ctrl_attributs.py" in self.loaded_controles):
            attributs.attributs(self, ctrl_attributs.ctrl_attributs) #type: ignore


        # informe l'utilisateur que les contrôles sont terminés
        widget = self.iface.messageBar().createMessage("Contrôles_IGN", "Contrôles terminés, {} erreurs trouvées".format(int(self.affichage_controles.get_total_controles())))
        button = QPushButton(widget)
        button.setText("Montre Moi")
        button.pressed.connect(self.affichage_controles.show_controles)
        widget.layout().addWidget(button)
        self.iface.messageBar().clearWidgets()
        self.iface.messageBar().pushWidget(widget, Qgis.Warning, duration=10)



    # récupère tous les fichiers pythons présents dans la source donnée
    def get_py_files(self, src):
        cwd = os.getcwd() # Current Working directory
        py_files = [] 
        for root, dirs, files in os.walk(src):
            for file in files:
                if file.endswith(".py"):
                    self.loaded_controles.append(file)
                    py_files.append(os.path.join(cwd, root, file))
        return py_files

    # importe les fichiers python présents dans une liste
    def dynamic_import(self, module_name, py_path):
        module_spec = importlib.util.spec_from_file_location(module_name, py_path)
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        return module

    # gestion d'erreur de la lecture des paramètres
    def get_info(self, file, name, path, controle):
        if file == []:
            self.iface.messageBar().clearWidgets()
            self.iface.messageBar().pushMessage("Erreur Critique", "La variable {} du fichier {} est illisible, la valeur par défaut va être utilisée".format(name, path), level=Qgis.Critical)
            if name == "actif":
                controle.append(1)
            elif name == "importance":
                controle.append(10000)
            else:
                controle.append(0)
        else:
            if file[0] != 0 and file[0] != 1 and name != "importance":
                self.iface.messageBar().clearWidgets()
                self.iface.messageBar().pushMessage("Erreur Critique", "La variable {} du fichier {} est inutilisable, la valeur par défaut va être utilisée".format(name, path), level=Qgis.Critical)
                if name == "actif":
                    controle.append(1)
                else:
                    controle.append(0)
            else:
                controle.append(file[0])

    # importes tous les fichiers python présents dans le dossier controle 
    def dynamic_import_from_src(self, src, star_import = False):
        sources = self.get_py_files(src)
        for py_file in sources:
            module_name = os.path.split(py_file)[-1].strip(".py")
            imported_module = self.dynamic_import(module_name, py_file)
            if star_import:
                for obj in dir(imported_module):
                    globals()[obj] = imported_module.__dict__[obj]
            else:
                globals()[module_name] = imported_module
        # ajoute les controles ainsi que leurs dossier parents jusqu'à "controles" dans une liste ajoutée à self.organisation
        for item in sources:
            controle = []
            if ("ctrl" not in item):
                temp = item.split('\\')
                split_len = len(temp)
                with open(item.replace(temp[split_len - 1], "param.txt")) as f:
                    count = sum(1 for _ in f)
                if count < 4:
                    self.iface.messageBar().clearWidgets()
                    self.iface.messageBar().pushMessage("Erreur Critique", "Le fichier {} est illisible, les valeurs par défaut vont être utilisées".format(item.replace(temp[split_len - 1], "param.txt")), level=Qgis.Critical)
                    controle.append(0)
                    controle.append(0)
                    controle.append(10000)
                    controle.append(1)
                else:
                    path = item.replace(temp[split_len - 1], "param.txt")
                    f = open(path)
                    self.get_info([int(d) for d in re.findall(r'-?\d+', f.readline().replace("\n", ""))], "bloquant", path, controle)
                    self.get_info([int(d) for d in re.findall(r'-?\d+', f.readline().replace("\n", ""))], "obligatoire", path, controle)
                    self.get_info([int(d) for d in re.findall(r'-?\d+', f.readline().replace("\n", ""))], "importance", path, controle)
                    self.get_info([int(d) for d in re.findall(r'-?\d+', f.readline().replace("\n", ""))], "actif", path, controle)
                    f.close()
                for i in range(split_len):
                    if (temp[i] == "Contrôles_IGN"):
                        for j in range(split_len - i):
                            if (".py" in temp[j + i]):
                                k = 1
                                while temp[j + i - k] != "controles":
                                    controle.append(temp[j + i - k])
                                    k = k + 1
                                if controle not in self.organisation:
                                    self.organisation.append(controle)
        return
    
    def clear(self):
        # ferme le bouton de séléction
        try:
            self.selectionButton.setDefaultAction(self.actionClear)
        except:
            pass
        layers = self.iface.mapCanvas().layers()
        # déséléctionne tous les objets
        for layer in layers:
            if layer.type() == QgsMapLayer.RasterLayer:
                continue
            layer.removeSelection()

    def run_select(self, b):
        # si sélectionné ajoute curseur
        if b:
            try:
                self.selectionButton.setDefaultAction(self.selecPoint)
            except:
                pass
            self.iface.mapCanvas().setMapTool(self.tool)
        # si désélectionné: enlève curseur
        else:
            self.iface.mapCanvas().unsetMapTool(self.tool)

    def runRectangle(self, b):
        # si sélectionné ajoute curseur
        if b:
            try:
                self.selectionButton.setDefaultAction(self.selecRectangle)
            except:
                pass
            self.iface.mapCanvas().setMapTool(self.toolRectangle)
        # si désélectionné: enlève curseur
        else:
            self.iface.mapCanvas().unsetMapTool(self.toolRectangle)
            


# PARTIE DE LANCEMENT DU CODE

    def run(self):
        """Run method that performs all the real work"""

        # ajoute les couches dans self.couche_list et dans la boite de selection de self.dlg_couches
        self.gestion_couches.add_layers()

        # show the dialog
        if (self.total_sub_groups > 1):
            self.dlg_trop.show()
            self.iface.messageBar().clearWidgets()
            self.iface.messageBar().pushMessage("ATTENTION", "Le nombre de sous groupe dépasse la puissance de calcul de QGIS pour faire les contrôles, veulliez diminuer le nombre de sous groupes pour une utilisation fluide du plugin", level=Qgis.Critical)
            return
        self.dlg.show()
        # Run the dialog event loop
        if self.first_start == True:
            self.first_start = False
            self.dlg_controles.check_all.button(QDialogButtonBox.YesToAll).setText("Tout cocher")
            self.dlg_controles.uncheck_all.button(QDialogButtonBox.NoToAll).setText("Tout déocher")
            self.dlg_couches.check_all.button(QDialogButtonBox.YesToAll).setText("Tout cocher")
            self.dlg_couches.uncheck_all.button(QDialogButtonBox.NoToAll).setText("Tout déocher")
            self.dlg_precis.check_all.button(QDialogButtonBox.YesToAll).setText("Tout cocher")
            self.dlg_precis.uncheck_all.button(QDialogButtonBox.NoToAll).setText("Tout déocher")
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
            self.dlg_precis.lineEdit.textChanged.connect(self.recherche.search_precis)
            self.dlg_precis.check_all.clicked.connect(self.gestion_couches.precis_check_layer_boxes)
            self.dlg_precis.uncheck_all.clicked.connect(self.gestion_couches.precis_uncheck_layer_boxes)
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
