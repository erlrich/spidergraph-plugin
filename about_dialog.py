# -*- coding: utf-8 -*-
# ============================================================
# Spidergraph Connector
# QGIS Plugin - About Dialog
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

import os
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QSizePolicy
)
from qgis.PyQt.QtCore import Qt, QUrl
from qgis.PyQt.QtGui import QFont, QPixmap, QDesktopServices


ABOUT_STYLE = """
QDialog {
    background-color: #f5f5f5;
}

QLabel {
    color: #333333;
    background: transparent;
}

QPushButton#closeBtn {
    background-color: #1976d2;
    color: #ffffff;
    border: none;
    border-radius: 5px;
    padding: 6px 20px;
    font-size: 12px;
    font-weight: 500;
}
QPushButton#closeBtn:hover {
    background-color: #1565c0;
}

QPushButton#linkBtn {
    background-color: transparent;
    color: #1976d2;
    border: 1px solid #1976d2;
    border-radius: 4px;
    padding: 4px 12px;
    font-size: 11px;
}
QPushButton#linkBtn:hover {
    background-color: #1976d2;
    color: white;
}

QFrame#divider {
    background-color: #d0d0d0;
}

QFrame#card {
    background-color: #ffffff;
    border: 1px solid #dddddd;
    border-radius: 6px;
}
"""


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About SpiderGraph Connector")
        self.setFixedWidth(480)
        self.setStyleSheet(ABOUT_STYLE)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 22)
        layout.setSpacing(0)

        # --- Header: icon + title ---
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)

        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'icon.png')
        if os.path.exists(icon_path):
            icon_lbl = QLabel()
            pix = QPixmap(icon_path).scaled(56, 56, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_lbl.setPixmap(pix)
            icon_lbl.setFixedSize(56, 56)
            header_layout.addWidget(icon_lbl)

        title_vbox = QVBoxLayout()
        title_vbox.setSpacing(2)

        title_lbl = QLabel("SpiderGraph Connector")
        title_font = QFont("Segoe UI", 22, QFont.Bold)
        title_lbl.setFont(title_font)
        title_lbl.setStyleSheet("color: #1976d2; background: transparent;")

        sub_lbl = QLabel("Spatial Connection & Matching Analysis Tool")
        sub_font = QFont("Segoe UI", 10)
        sub_lbl.setFont(sub_font)
        sub_lbl.setStyleSheet("color: #666666; background: transparent;")

        ver_lbl = QLabel("Version 1.0.0  ·  QGIS 3.40+")
        ver_font = QFont("Segoe UI", 9)
        ver_lbl.setFont(ver_font)
        ver_lbl.setStyleSheet("color: #888888; background: transparent;")

        title_vbox.addWidget(title_lbl)
        title_vbox.addWidget(sub_lbl)
        title_vbox.addWidget(ver_lbl)
        header_layout.addLayout(title_vbox)
        header_layout.addStretch()

        layout.addLayout(header_layout)
        layout.addSpacing(18)

        # --- Divider ---
        div1 = QFrame()
        div1.setObjectName("divider")
        div1.setFrameShape(QFrame.HLine)
        div1.setFixedHeight(1)
        layout.addWidget(div1)
        layout.addSpacing(16)

        # --- Description card ---
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 14, 16, 14)
        card_layout.setSpacing(6)

        desc_lbl = QLabel(
            "SpiderGraph Connector is a QGIS plugin for creating connection lines between spatial layers based on field matching. It supports one-to-many relationships, multi-ID parsing, and flexible attribute enrichment for telecom and spatial analysis workflows."
        )
        desc_lbl.setWordWrap(True)
        desc_lbl.setFont(QFont("Segoe UI", 10))
        desc_lbl.setStyleSheet("color: #444444; line-height: 1.5;")
        card_layout.addWidget(desc_lbl)

        layout.addWidget(card)
        layout.addSpacing(16)

        # --- Feature tags ---
        features_lbl = QLabel("Key Features")
        features_lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        features_lbl.setStyleSheet("color: #1976d2;")
        layout.addWidget(features_lbl)
        layout.addSpacing(6)

        features = [
            "🔗 One-to-many connection mapping",
            "🧩 Multi-ID field parsing support",
            "📊 Attribute enrichment (src_/tgt_)",
            "📍 Supports Point, Line, Polygon (centroid)",
            "⚙ Flexible matching (exact / partial / case-sensitive)"
        ]
        for f in features:
            fl = QLabel(f)
            fl.setFont(QFont("Segoe UI", 9))
            fl.setStyleSheet("color: #555555; padding-left: 4px;")
            layout.addWidget(fl)

        layout.addSpacing(16)

        # --- Divider ---
        div2 = QFrame()
        div2.setObjectName("divider")
        div2.setFrameShape(QFrame.HLine)
        div2.setFixedHeight(1)
        layout.addWidget(div2)
        layout.addSpacing(14)

        # --- Author row ---
        author_layout = QHBoxLayout()
        author_layout.setSpacing(10)

        author_lbl = QLabel(
            "<b>Author:</b>  Achmad Amrulloh (Dinzo)<br>"
            "<b>Email:</b>  achmad.amrulloh@gmail.com<br>"
            "<b>© 2026 Dinzo. All rights reserved.</b>"
        )
        author_lbl.setFont(QFont("Segoe UI", 9))
        author_lbl.setStyleSheet("color: #666666; line-height: 1.6;")
        author_layout.addWidget(author_lbl)
        author_layout.addStretch()

        btn_linkedin = QPushButton("LinkedIn")
        btn_linkedin.setObjectName("linkBtn")
        btn_linkedin.setCursor(Qt.PointingHandCursor)
        btn_linkedin.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://www.linkedin.com/in/achmad-amrulloh/"))
        )

        btn_github = QPushButton("GitHub")
        btn_github.setObjectName("linkBtn")
        btn_github.setCursor(Qt.PointingHandCursor)
        btn_github.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://github.com/erlrich/spidergraph-plugin"))
        )

        btn_col = QVBoxLayout()
        btn_col.setSpacing(6)
        btn_col.addWidget(btn_linkedin)
        btn_col.addWidget(btn_github)
        author_layout.addLayout(btn_col)

        layout.addLayout(author_layout)
        layout.addSpacing(18)

        # --- Close button ---
        close_row = QHBoxLayout()
        close_row.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setObjectName("closeBtn")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        close_row.addWidget(close_btn)
        layout.addLayout(close_row)
