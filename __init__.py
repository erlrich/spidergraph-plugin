# -*- coding: utf-8 -*-

"""
SpiderGraph Connector Plugin for QGIS
"""


def classFactory(iface):
    """Return the plugin class"""
    from .spidergraph_plugin import SpiderGraphPlugin
    return SpiderGraphPlugin(iface)