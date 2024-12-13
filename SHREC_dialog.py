# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SHRECDialog
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

import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/SHREC_dialog_base.ui'))


class SHREC_Dialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(SHRECDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

FORM_CLASS1, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),'ui/choix_couches.ui'))
class choix_couche(QtWidgets.QDialog, FORM_CLASS1):

    def __init__(self, parent=None):
        """Constructor."""
        super(choix_couche, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

FORM_CLASS1, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),'ui/choix_controles.ui'))
class choix_controles(QtWidgets.QDialog, FORM_CLASS1):

    def __init__(self, parent=None):
        """Constructor."""
        super(choix_controles, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        
FORM_CLASS1, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),'ui/voir_controles.ui'))
class voir_controles(QtWidgets.QDialog, FORM_CLASS1):

    def __init__(self, parent=None):
        """Constructor."""
        super(voir_controles, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        
FORM_CLASS1, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),'ui/pas_controles.ui'))
class pas_controles(QtWidgets.QDialog, FORM_CLASS1):

    def __init__(self, parent=None):
        """Constructor."""
        super(pas_controles, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

FORM_CLASS1, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),'ui/trop_de_couches.ui'))
class trop_de_couches(QtWidgets.QDialog, FORM_CLASS1):

    def __init__(self, parent=None):
        """Constructor."""
        super(trop_de_couches, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

FORM_CLASS1, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),'ui/choix_precis.ui'))
class choix_precis(QtWidgets.QDialog, FORM_CLASS1):

    def __init__(self, parent=None):
        """Constructor."""
        super(choix_precis, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

FORM_CLASS1, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),'ui/lancer.ui'))
class lancer(QtWidgets.QDialog, FORM_CLASS1):

    def __init__(self, parent=None):
        """Constructor."""
        super(lancer, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)