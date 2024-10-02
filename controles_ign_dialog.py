# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Controles_IGNDialog
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

import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'controles_ign_dialog_base.ui'))


class Controles_IGNDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(Controles_IGNDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

FORM_CLASS1, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),'choix_couches.ui'))
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

FORM_CLASS1, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),'choix_controles.ui'))
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