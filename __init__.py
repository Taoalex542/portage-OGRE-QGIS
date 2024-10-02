# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Controles_IGN
                                 A QGIS plugin
 Saves attributes of the selected vector
                             -------------------
        begin                : 2024-09-26
        copyright            : (C) 2024 by Ta'o D
        email                : ta-o.darbellay@ign.fr
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Controles_IGN class from file Controles_IGN.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .controles_ign import Controles_IGN
    return Controles_IGN(iface)
