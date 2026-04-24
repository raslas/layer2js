# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Layer2js
                                 A QGIS plugin
 Description of the plugin
                             -------------------
        begin                : 2026-04-15
        copyright            : (C) 2026 by Author
        email                : rlraslas@gmail.com
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


def classFactory(iface):
    from .layer2js import Layer2js
    return Layer2js(iface)
