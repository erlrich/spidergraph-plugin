# -*- coding: utf-8 -*-
# ============================================================
# Spidergraph Connector
# QGIS Plugin - UI Dialog
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
SpiderGraph Connector - Modern UI Dialog
"""

from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QComboBox,
    QLabel, QCheckBox, QLineEdit, QPushButton, QProgressBar,
    QTextEdit, QFrame, QApplication, QListWidget, QTabWidget,
    QWidget, QMessageBox
)
from qgis.PyQt.QtCore import Qt, QThread, pyqtSignal
from qgis.core import QgsProject, QgsMapLayer, QgsMessageLog
from .about_dialog import AboutDialog

class AlgorithmThread(QThread):
    """Thread for running algorithm with progress reporting"""
    progressChanged = pyqtSignal(int, int)
    statusChanged = pyqtSignal(str)
    finishedChanged = pyqtSignal(bool, str, object)

    def __init__(self, params):
        super().__init__()
        self.params = params

    def run(self):
        from .spidergraph_algorithm import SpiderGraphAlgorithm
        algorithm = SpiderGraphAlgorithm()
        success, message, layer = algorithm.run(
            self.params, 
            self.progressChanged.emit, 
            self.statusChanged.emit
        )
        self.finishedChanged.emit(success, message, layer)


class SpiderGraphDialog(QDialog):
    """Main dialog for SpiderGraph Connector - Modern UI"""

    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.iface = iface

        self.setWindowTitle("SpiderGraph Connector")

        # Set initial size (better UX)
        self.resize(600, 750)

        # Set minimum size (prevent too small)
        self.setMinimumWidth(500)
        self.setMinimumHeight(700)

        # Allow minimize
        from qgis.PyQt.QtCore import Qt
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint)

        self.thread = None
        self.pending_layer = None

        self.setup_ui()
        self.apply_style()
        self.populate_layers()

    def apply_style(self):
        """Apply modern styling to the dialog"""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 3px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton#cancelButton {
                background-color: #f44336;
            }
            QPushButton#cancelButton:hover {
                background-color: #da190b;
            }
            QPushButton#closeButton {
                background-color: #555555;
            }
            QPushButton#closeButton:hover {
                background-color: #333333;
            }
            QPushButton#actionButton {
                background-color: #2196F3;
            }
            QPushButton#actionButton:hover {
                background-color: #0b7dda;
            }
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
            QListWidget {
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 3px;
            }
            QListWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #4CAF50;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #e0e0e0;
            }
            QToolTip {
                background-color: #333333;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
            }
        """)

    def setup_ui(self):
        """Setup the UI components"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        
        # ===== TAB WIDGET =====
        self.tab_widget = QTabWidget()
        
        # ===== TAB 1: PARAMETERS =====
        tab1 = QWidget()
        tab1_layout = QVBoxLayout(tab1)
        tab1_layout.setSpacing(8)
        
        # ----- SOURCE GROUP -----
        source_group = QGroupBox("📍 Source Layer")
        source_layout = QVBoxLayout(source_group)
        source_layout.setSpacing(8)

        # Source layer row
        layer_row1 = QHBoxLayout()
        layer_row1.addWidget(QLabel("Layer:"))
        self.source_layer_combo = QComboBox()
        self.source_layer_combo.setToolTip("Select the source vector layer")
        self.source_layer_combo.currentIndexChanged.connect(self.on_source_layer_changed)
        layer_row1.addWidget(self.source_layer_combo, 1)
        source_layout.addLayout(layer_row1)

        # Source field row
        field_row1 = QHBoxLayout()
        field_row1.addWidget(QLabel("Match Field:"))
        self.source_field_combo = QComboBox()
        self.source_field_combo.setToolTip("Field used for matching with target layer")
        field_row1.addWidget(self.source_field_combo, 1)
        source_layout.addLayout(field_row1)

        tab1_layout.addWidget(source_group)

        # ----- TARGET GROUP -----
        target_group = QGroupBox("🎯 Target Layer")
        target_layout = QVBoxLayout(target_group)
        target_layout.setSpacing(8)

        # Target layer row
        layer_row2 = QHBoxLayout()
        layer_row2.addWidget(QLabel("Layer:"))
        self.target_layer_combo = QComboBox()
        self.target_layer_combo.setToolTip("Select the target vector layer")
        self.target_layer_combo.currentIndexChanged.connect(self.on_target_layer_changed)
        layer_row2.addWidget(self.target_layer_combo, 1)
        target_layout.addLayout(layer_row2)

        # Target field row
        field_row2 = QHBoxLayout()
        field_row2.addWidget(QLabel("Match Field:"))
        self.target_field_combo = QComboBox()
        self.target_field_combo.setToolTip("Field used for matching with source layer")
        field_row2.addWidget(self.target_field_combo, 1)
        target_layout.addLayout(field_row2)

        tab1_layout.addWidget(target_group)

        # ----- OPTIONS GROUP -----
        options_group = QGroupBox("⚙️ Matching Options")
        options_layout = QVBoxLayout(options_group)
        options_layout.setSpacing(5)

        self.partial_match_cb = QCheckBox("Partial Match (contains)")
        self.partial_match_cb.setToolTip("Match if source ID is contained within target ID")
        options_layout.addWidget(self.partial_match_cb)

        self.case_sensitive_cb = QCheckBox("Case Sensitive")
        self.case_sensitive_cb.setToolTip("Match with case sensitivity (default: case-insensitive)")
        options_layout.addWidget(self.case_sensitive_cb)

        delim_row = QHBoxLayout()
        delim_row.addWidget(QLabel("Multi-ID Delimiters:"))
        self.delimiters_edit = QLineEdit(", ;")
        self.delimiters_edit.setToolTip("Separators for multiple IDs in one cell (e.g., comma, semicolon)")
        delim_row.addWidget(self.delimiters_edit, 1)
        options_layout.addLayout(delim_row)

        geom_info = QLabel("✓ Supports Point, Line, Polygon geometries (centroid used for Line/Polygon)")
        geom_info.setStyleSheet("color: #666666; font-size: 9px; padding: 5px 0;")
        options_layout.addWidget(geom_info)

        tab1_layout.addWidget(options_group)

        # ----- OUTPUT GROUP -----
        output_group = QGroupBox("💾 Output")
        output_layout = QVBoxLayout(output_group)

        output_row = QHBoxLayout()
        output_row.addWidget(QLabel("Layer Name:"))
        self.output_name_edit = QLineEdit("SpiderLine_Connector")
        self.output_name_edit.setToolTip("Name of the output connector layer")
        output_row.addWidget(self.output_name_edit, 1)
        output_layout.addLayout(output_row)

        tab1_layout.addWidget(output_group)

        # ----- PROGRESS GROUP -----
        progress_group = QGroupBox("📊 Progress")
        progress_layout = QVBoxLayout(progress_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFormat("%p%")
        progress_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #666666; font-size: 10px;")
        progress_layout.addWidget(self.status_label)

        tab1_layout.addWidget(progress_group)

        # ----- RESULT GROUP -----
        result_group = QGroupBox("📋 Results")
        result_layout = QVBoxLayout(result_group)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)

        # Increase height for better readability
        self.result_text.setMinimumHeight(100)
        self.result_text.setMaximumHeight(180)

        self.result_text.setStyleSheet("background-color: #f9f9f9; font-family: monospace;")
        result_layout.addWidget(self.result_text)

        tab1_layout.addWidget(result_group)
        
        tab1_layout.addStretch()
        
        # ===== TAB 2: ATTRIBUTES =====
        tab2 = QWidget()
        tab2_layout = QVBoxLayout(tab2)
        tab2_layout.setSpacing(15)
        
        # ----- SOURCE EXTRA FIELDS -----
        src_extra_group = QGroupBox("📥 Source - Additional Attributes")
        src_extra_layout = QVBoxLayout(src_extra_group)
        
        src_extra_row = QHBoxLayout()
        
        # Available fields panel
        src_available_box = QVBoxLayout()
        src_available_box.addWidget(QLabel("Available Fields:"))
        self.src_available_list = QListWidget()
        self.src_available_list.setSelectionMode(QListWidget.MultiSelection)
        self.src_available_list.setToolTip("Select fields to add (Ctrl+click for multiple)")
        self.src_available_list.setMinimumWidth(200)
        src_available_box.addWidget(self.src_available_list)
        src_extra_row.addLayout(src_available_box)
        
        # Button panel - centered vertically
        src_btn_box = QVBoxLayout()
        src_btn_box.setAlignment(Qt.AlignVCenter)  # Add this line for vertical centering
        self.src_add_btn = QPushButton(">>")
        self.src_add_btn.setObjectName("actionButton")
        self.src_add_btn.setToolTip("Add selected fields to output")
        self.src_add_btn.setFixedWidth(40)
        self.src_add_btn.clicked.connect(self.add_source_fields)
        
        self.src_remove_btn = QPushButton("<<")
        self.src_remove_btn.setObjectName("actionButton")
        self.src_remove_btn.setToolTip("Remove selected fields from output")
        self.src_remove_btn.setFixedWidth(40)
        self.src_remove_btn.clicked.connect(self.remove_source_fields)
        
        src_btn_box.addWidget(self.src_add_btn)
        src_btn_box.addWidget(self.src_remove_btn)

        # Move Select/Clear HERE (below << button)
        src_select_all = QPushButton("Select All")
        src_select_all.setToolTip("Select all available fields")
        src_select_all.clicked.connect(lambda: self.select_all_fields(self.src_available_list))

        src_clear_all = QPushButton("Clear All")
        src_clear_all.setToolTip("Clear all selections")
        src_clear_all.clicked.connect(lambda: self.clear_all_fields(self.src_available_list))

        src_btn_box.addSpacing(10)
        src_btn_box.addWidget(src_select_all)
        src_btn_box.addWidget(src_clear_all)

        src_extra_row.addLayout(src_btn_box)
        
        # Selected fields panel
        src_selected_box = QVBoxLayout()
        src_selected_box.addWidget(QLabel("Selected Fields:"))
        self.src_selected_list = QListWidget()
        self.src_selected_list.setSelectionMode(QListWidget.MultiSelection)
        self.src_selected_list.setToolTip("Fields that will be added to output (prefix: src_)")
        self.src_selected_list.setMinimumWidth(200)
        src_selected_box.addWidget(self.src_selected_list)
        src_extra_row.addLayout(src_selected_box)
        
        src_extra_layout.addLayout(src_extra_row)
        
        
        tab2_layout.addWidget(src_extra_group)
        
        # ----- TARGET EXTRA FIELDS -----
        tgt_extra_group = QGroupBox("📤 Target - Additional Attributes")
        tgt_extra_layout = QVBoxLayout(tgt_extra_group)
        
        tgt_extra_row = QHBoxLayout()
        
        # Available fields panel
        tgt_available_box = QVBoxLayout()
        tgt_available_box.addWidget(QLabel("Available Fields:"))
        self.tgt_available_list = QListWidget()
        self.tgt_available_list.setSelectionMode(QListWidget.MultiSelection)
        self.tgt_available_list.setToolTip("Select fields to add (Ctrl+click for multiple)")
        self.tgt_available_list.setMinimumWidth(200)
        tgt_available_box.addWidget(self.tgt_available_list)
        tgt_extra_row.addLayout(tgt_available_box)
        
        # Button panel - centered vertically
        tgt_btn_box = QVBoxLayout()
        tgt_btn_box.setAlignment(Qt.AlignVCenter)  # Add this line for vertical centering
        self.tgt_add_btn = QPushButton(">>")
        self.tgt_add_btn.setObjectName("actionButton")
        self.tgt_add_btn.setToolTip("Add selected fields to output")
        self.tgt_add_btn.setFixedWidth(40)
        self.tgt_add_btn.clicked.connect(self.add_target_fields)
        
        self.tgt_remove_btn = QPushButton("<<")
        self.tgt_remove_btn.setObjectName("actionButton")
        self.tgt_remove_btn.setToolTip("Remove selected fields from output")
        self.tgt_remove_btn.setFixedWidth(40)
        self.tgt_remove_btn.clicked.connect(self.remove_target_fields)
        
        tgt_btn_box.addWidget(self.tgt_add_btn)
        tgt_btn_box.addWidget(self.tgt_remove_btn)

        tgt_select_all = QPushButton("Select All")
        tgt_select_all.clicked.connect(lambda: self.select_all_fields(self.tgt_available_list))

        tgt_clear_all = QPushButton("Clear All")
        tgt_clear_all.clicked.connect(lambda: self.clear_all_fields(self.tgt_available_list))

        tgt_btn_box.addSpacing(10)
        tgt_btn_box.addWidget(tgt_select_all)
        tgt_btn_box.addWidget(tgt_clear_all)
        tgt_extra_row.addLayout(tgt_btn_box)
        
        # Selected fields panel
        tgt_selected_box = QVBoxLayout()
        tgt_selected_box.addWidget(QLabel("Selected Fields:"))
        self.tgt_selected_list = QListWidget()
        self.tgt_selected_list.setSelectionMode(QListWidget.MultiSelection)
        self.tgt_selected_list.setToolTip("Fields that will be added to output (prefix: tgt_)")
        self.tgt_selected_list.setMinimumWidth(200)
        tgt_selected_box.addWidget(self.tgt_selected_list)
        tgt_extra_row.addLayout(tgt_selected_box)
        
        tgt_extra_layout.addLayout(tgt_extra_row)
        
        tab2_layout.addWidget(tgt_extra_group)
        
        # Info note
        info_note = QLabel(
            "ℹ️ Note: Source attributes will be prefixed with 'src_', target attributes with 'tgt_' "
            "to avoid name conflicts in the output layer."
        )
        info_note.setStyleSheet("color: #666666; font-size: 10px; background-color: #f0f0f0; padding: 8px; border-radius: 3px;")
        info_note.setWordWrap(True)
        tab2_layout.addWidget(info_note)
        
        tab2_layout.addStretch()
        
        # ===== ADD TABS =====
        self.tab_widget.addTab(tab1, "Parameters")
        self.tab_widget.addTab(tab2, "Attributes")
        
        main_layout.addWidget(self.tab_widget)
        
        # ===== BUTTON PANEL =====
        button_panel = QWidget()
        button_layout = QHBoxLayout(button_panel)
        button_layout.setContentsMargins(0, 5, 0, 5)
        button_layout.setSpacing(10)

        self.run_button = QPushButton("▶ Run")
        self.run_button.setToolTip("Execute the spider graph connection")
        self.run_button.clicked.connect(self.run_algorithm)
        button_layout.addWidget(self.run_button)

        self.cancel_button = QPushButton("✖ Cancel")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.cancel_algorithm)
        self.cancel_button.setToolTip("Cancel the running process")
        self.cancel_button.setEnabled(False)
        button_layout.addWidget(self.cancel_button)

        button_layout.addStretch()

        self.help_button = QPushButton("❓ Help")
        self.help_button.setToolTip("Show help information")
        self.help_button.clicked.connect(self.show_help)
        button_layout.addWidget(self.help_button)

        self.about_button = QPushButton("ℹ About")
        self.about_button.setObjectName("actionButton")
        self.about_button.setToolTip("About this plugin")
        self.about_button.clicked.connect(self.show_about)
        button_layout.addWidget(self.about_button)
        
        main_layout.addWidget(button_panel)

        # Footer tip
        footer_label = QLabel(
            "💡 Tip: Use 'Save As...' on the output layer to export to Shapefile, GeoJSON, or other formats"
        )
        footer_label.setStyleSheet("color: #888888; font-size: 9px;")
        main_layout.addWidget(footer_label)

    def show_help(self):
        """Show help message box"""
        QMessageBox.information(
            self,
            "SpiderGraph Connector Help",
            "How to use SpiderGraph Connector:\n\n"
            "1. Select Source Layer (origin points)\n"
            "2. Select Target Layer (destination points)\n"
            "3. Choose matching fields from both layers\n"
            "4. (Optional) Select additional attributes to include\n"
            "5. Configure matching options:\n"
            "   • Partial Match: match if source ID is inside target ID\n"
            "   • Case Sensitive: match with exact case\n"
            "   • Delimiters: handle multiple IDs in one cell\n"
            "6. Click 'Run' to create connector lines\n\n"
            "Output layer will contain:\n"
            "• Line geometries connecting matched features\n"
            "• Source and target IDs\n"
            "• Additional attributes (if selected) with prefix src_/tgt_\n\n"
            "The result is a memory layer that you can save to disk."
        )

    def show_about(self):
        """Open About dialog"""
        dlg = AboutDialog(self)
        dlg.exec_()

    def populate_layers(self):
        """Populate layer comboboxes with vector layers"""
        project = QgsProject.instance()
        layers = project.mapLayers().values()
        vector_layers = [l for l in layers if l.type() == QgsMapLayer.VectorLayer]

        self.source_layer_combo.clear()
        self.target_layer_combo.clear()

        for layer in vector_layers:
            self.source_layer_combo.addItem(layer.name(), layer.id())
            self.target_layer_combo.addItem(layer.name(), layer.id())

    def on_source_layer_changed(self):
        """Update source field combobox when layer changes"""
        layer = self.get_source_layer()
        if layer:
            self.populate_fields(self.source_field_combo, layer)
            self.populate_source_extra_fields()

    def on_target_layer_changed(self):
        """Update target field combobox when layer changes"""
        layer = self.get_target_layer()
        if layer:
            self.populate_fields(self.target_field_combo, layer)
            self.populate_target_extra_fields()

    def populate_fields(self, combo, layer):
        """Populate field combobox"""
        combo.clear()
        fields = layer.fields()
        for field in fields:
            combo.addItem(field.name())
    
    def populate_source_extra_fields(self):
        """Populate source available fields list for attributes tab"""
        src_layer = self.get_source_layer()
        if src_layer:
            self.src_available_list.clear()
            fields = src_layer.fields()
            current_connector_field = self.source_field_combo.currentText()
            for field in fields:
                if field.name() != current_connector_field:
                    self.src_available_list.addItem(field.name())
            self.src_available_list.sortItems()
    
    def populate_target_extra_fields(self):
        """Populate target available fields list for attributes tab"""
        tgt_layer = self.get_target_layer()
        if tgt_layer:
            self.tgt_available_list.clear()
            fields = tgt_layer.fields()
            current_connector_field = self.target_field_combo.currentText()
            for field in fields:
                if field.name() != current_connector_field:
                    self.tgt_available_list.addItem(field.name())
            self.tgt_available_list.sortItems()
    
    def select_all_fields(self, list_widget):
        """Select all items in a list widget"""
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            item.setSelected(True)
    
    def clear_all_fields(self, list_widget):
        """Clear all selections in a list widget"""
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            item.setSelected(False)
    
    def add_source_fields(self):
        """Move selected fields from available to selected list"""
        selected_items = self.src_available_list.selectedItems()
        for item in selected_items:
            field_name = item.text()
            # Check if already in selected list
            exists = False
            for i in range(self.src_selected_list.count()):
                if self.src_selected_list.item(i).text() == field_name:
                    exists = True
                    break
            if not exists:
                self.src_selected_list.addItem(field_name)
            self.src_available_list.takeItem(self.src_available_list.row(item))
        self.src_selected_list.sortItems()
    
    def remove_source_fields(self):
        """Move selected fields from selected back to available list"""
        selected_items = self.src_selected_list.selectedItems()
        for item in selected_items:
            field_name = item.text()
            self.src_available_list.addItem(field_name)
            self.src_selected_list.takeItem(self.src_selected_list.row(item))
        self.src_available_list.sortItems()
    
    def add_target_fields(self):
        """Move selected fields from available to selected list"""
        selected_items = self.tgt_available_list.selectedItems()
        for item in selected_items:
            field_name = item.text()
            # Check if already in selected list
            exists = False
            for i in range(self.tgt_selected_list.count()):
                if self.tgt_selected_list.item(i).text() == field_name:
                    exists = True
                    break
            if not exists:
                self.tgt_selected_list.addItem(field_name)
            self.tgt_available_list.takeItem(self.tgt_available_list.row(item))
        self.tgt_selected_list.sortItems()
    
    def remove_target_fields(self):
        """Move selected fields from selected back to available list"""
        selected_items = self.tgt_selected_list.selectedItems()
        for item in selected_items:
            field_name = item.text()
            self.tgt_available_list.addItem(field_name)
            self.tgt_selected_list.takeItem(self.tgt_selected_list.row(item))
        self.tgt_available_list.sortItems()
    
    def get_selected_source_fields(self):
        """Get list of selected source extra fields"""
        fields = []
        for i in range(self.src_selected_list.count()):
            fields.append(self.src_selected_list.item(i).text())
        return fields
    
    def get_selected_target_fields(self):
        """Get list of selected target extra fields"""
        fields = []
        for i in range(self.tgt_selected_list.count()):
            fields.append(self.tgt_selected_list.item(i).text())
        return fields

    def get_source_layer(self):
        """Get selected source layer"""
        idx = self.source_layer_combo.currentIndex()
        if idx >= 0:
            layer_id = self.source_layer_combo.currentData()
            if layer_id:
                return QgsProject.instance().mapLayer(layer_id)
        return None

    def get_target_layer(self):
        """Get selected target layer"""
        idx = self.target_layer_combo.currentIndex()
        if idx >= 0:
            layer_id = self.target_layer_combo.currentData()
            if layer_id:
                return QgsProject.instance().mapLayer(layer_id)
        return None

    def run_algorithm(self):
        """Run the spider graph algorithm"""
        # Validate inputs
        source_layer = self.get_source_layer()
        target_layer = self.get_target_layer()

        if not source_layer or not target_layer:
            self.result_text.append("❌ Error: Please select source and target layers")
            return

        source_field = self.source_field_combo.currentText()
        target_field = self.target_field_combo.currentText()

        if not source_field or not target_field:
            self.result_text.append("❌ Error: Please select fields for matching")
            return

        if self.output_name_edit.text().strip() == "":
            self.result_text.append("❌ Error: Output layer name cannot be empty")
            return

        # Parse delimiters
        delimiters = [d.strip() for d in self.delimiters_edit.text().split() if d.strip()]

        # Prepare parameters
        params = {
            'source_layer': source_layer,
            'target_layer': target_layer,
            'source_field': source_field,
            'target_field': target_field,
            'output_name': self.output_name_edit.text().strip(),
            'partial_match': self.partial_match_cb.isChecked(),
            'case_sensitive': self.case_sensitive_cb.isChecked(),
            'delimiters': delimiters,
            'source_extra_fields': self.get_selected_source_fields(),
            'target_extra_fields': self.get_selected_target_fields()
        }

        # Disable UI during processing
        self.set_ui_enabled(False)

        # Clear previous results
        self.result_text.clear()
        self.result_text.setStyleSheet("background-color: #f9f9f9; font-family: monospace;")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Processing...")
        self.status_label.setStyleSheet("color: #ff9800; font-size: 10px;")

        # Run algorithm in thread
        if self.thread and self.thread.isRunning():
            self.result_text.append("⚠ Process already running")
            return
        self.thread = AlgorithmThread(params)
        self.thread.progressChanged.connect(self.update_progress)
        self.thread.statusChanged.connect(self.update_status)
        self.thread.finishedChanged.connect(self.on_algorithm_finished)
        self.thread.start()

    def update_progress(self, current, total):
        """Update progress bar"""
        if total > 0:
            percent = int((current / total) * 100)
            self.progress_bar.setValue(percent)
        QApplication.processEvents()

    def update_status(self, message):
        """Update status label and log"""
        self.status_label.setText(message)
        QApplication.processEvents()
        QgsMessageLog.logMessage(f"SpiderGraph: {message}", "SpiderGraph", level=0)
        
        
    def on_algorithm_finished(self, success, message, layer):
        """Handle algorithm completion - thread safe version"""
        # First, always clean up thread reference
        old_thread = self.thread
        self.thread = None
        
        try:
            self.progress_bar.setVisible(False)
            QApplication.processEvents()

            if success:
                self.status_label.setText("✓ Completed")
                self.status_label.setStyleSheet("color: #4CAF50; font-size: 10px;")
                self.result_text.setStyleSheet("background-color: #e8f5e9; font-family: monospace;")
                self.result_text.append(message)
                QApplication.processEvents()

                if layer:
                    # Store for main thread addition
                    self.pending_layer = layer
                    # Schedule addition in main thread
                    from PyQt5.QtCore import QTimer
                    QTimer.singleShot(100, self._add_layer_to_project)
                else:
                    self.set_ui_enabled(True)
            else:
                self.status_label.setText("✗ Failed")
                self.status_label.setStyleSheet("color: #f44336; font-size: 10px;")
                self.result_text.setStyleSheet("background-color: #ffebee; font-family: monospace;")
                self.result_text.append(f"❌ Error: {message}")
                self.set_ui_enabled(True)

        except Exception as e:
            self.result_text.append(f"⚠ Error: {str(e)}")
            self.set_ui_enabled(True)
        
        # Clean up old thread
        if old_thread:
            old_thread.deleteLater()

    def _add_layer_to_project(self):
        """Safely add layer to project in main thread"""
        try:
            if hasattr(self, 'pending_layer') and self.pending_layer:
                layer = self.pending_layer
                
                if layer and layer.isValid():
                    # Add to project
                    QgsProject.instance().addMapLayer(layer)
                    QApplication.processEvents()
                    self.result_text.append(f"\n✓ Layer '{layer.name()}' added to project")
                    
                    # Try to zoom
                    try:
                        extent = layer.extent()
                        if extent and not extent.isEmpty():
                            self.iface.mapCanvas().setExtent(extent)
                            self.iface.mapCanvas().refresh()
                            self.result_text.append("✓ Zoomed to layer extent")
                    except Exception as e:
                        self.result_text.append(f"⚠ Could not zoom: {str(e)}")
                else:
                    self.result_text.append("⚠ Cannot add layer: Layer is not valid")
                    
        except Exception as e:
            self.result_text.append(f"⚠ Failed to add layer: {str(e)}")
        finally:
            self.pending_layer = None
            self.set_ui_enabled(True)

    def cancel_algorithm(self):
        """Cancel running algorithm"""
        if self.thread and self.thread.isRunning():
            self.thread.terminate()
            self.thread.wait()
            self.status_label.setText("⚠ Cancelled")
            self.status_label.setStyleSheet("color: #ff9800; font-size: 10px;")
            self.result_text.append("⚠ Process cancelled by user")
            self.set_ui_enabled(True)
            self.thread = None
    
    def closeEvent(self, event):
        """Ensure thread is properly stopped when dialog is closed"""
        try:
            if self.thread and self.thread.isRunning():
                self.thread.terminate()
                self.thread.wait()
        except:
            pass
        event.accept()
    
    def set_ui_enabled(self, enabled):
        """Enable/disable UI controls"""
        self.run_button.setEnabled(enabled)
        self.cancel_button.setEnabled(not enabled)
        self.source_layer_combo.setEnabled(enabled)
        self.target_layer_combo.setEnabled(enabled)
        self.source_field_combo.setEnabled(enabled)
        self.target_field_combo.setEnabled(enabled)
        self.partial_match_cb.setEnabled(enabled)
        self.case_sensitive_cb.setEnabled(enabled)
        self.delimiters_edit.setEnabled(enabled)
        self.output_name_edit.setEnabled(enabled)
        self.tab_widget.setEnabled(enabled)
        self.help_button.setEnabled(enabled)
        self.about_button.setEnabled(enabled)

        if enabled:
            self.cancel_button.setEnabled(False)