# -*- coding: utf-8 -*-
# ============================================================
# Spidergraph Connector
# QGIS Plugin - Main  Plugin
#
# Author   : Achmad Amrulloh (Dinzo)
# Email    : achmad.amrulloh@gmail.com
# LinkedIn : https://www.linkedin.com/in/achmad-amrulloh/
#
# © 2026 Dinzo. All rights reserved.
#
# This software is provided as freeware.
# Redistribution, modification, or reuse without
# proper attribution is not permitted.
# ============================================================

"""
SpiderGraph Connector - Main Plugin Class
"""

import os
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon


class SpiderGraphPlugin:
    """Main plugin class for SpiderGraph Connector"""

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.action = None
        self.toolbar = None

    def initGui(self):
        """Create menu entries and toolbar buttons"""
        # Load icon
        icon_path = os.path.join(self.plugin_dir, 'resources', 'icon.png')
        if not os.path.exists(icon_path):
            # Use default icon if custom icon not found
            icon_path = None

        # Create action
        self.action = QAction(
            QIcon(icon_path) if icon_path else QIcon(),
            "SpiderGraph Connector",
            self.iface.mainWindow()
        )
        self.action.setWhatsThis("Create connector lines between two layers based on field matching")
        self.action.triggered.connect(self.run)

        # Add to menu
        self.iface.addPluginToMenu("&SpiderGraph Connector", self.action)

        # Add to toolbar
        self.toolbar = self.iface.addToolBar("SpiderGraph Connector")
        self.toolbar.setObjectName("SpiderGraphConnectorToolbar")
        self.toolbar.addAction(self.action)

    def unload(self):
        """Remove menu entries and toolbar buttons"""
        # Remove from menu
        self.iface.removePluginMenu("&SpiderGraph Connector", self.action)
        
        # Remove toolbar - use parent's removeToolBar method
        if self.toolbar is not None:
            # Get the parent widget (main window)
            main_window = self.iface.mainWindow()
            if main_window:
                main_window.removeToolBar(self.toolbar)
            self.toolbar = None
            
        # Delete the action
        del self.action

    def run(self):
        """Run the plugin dialog (single instance, safe reopen)"""
        from .spidergraph_dialog import SpiderGraphDialog

        # Check if dialog exists
        if hasattr(self, 'dlg') and self.dlg is not None:
            try:
                # If still visible → bring to front
                if self.dlg.isVisible():
                    self.dlg.raise_()
                    self.dlg.activateWindow()
                    return
                else:
                    # Dialog exists but hidden/closed → reset
                    self.dlg = None
            except RuntimeError:
                # Qt object already deleted
                self.dlg = None

        # Create new dialog
        self.dlg = SpiderGraphDialog(self.iface)

        # Reset reference when dialog destroyed
        self.dlg.destroyed.connect(lambda: setattr(self, 'dlg', None))

        self.dlg.show()
        self.dlg.raise_()
        self.dlg.activateWindow()