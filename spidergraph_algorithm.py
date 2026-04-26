# -*- coding: utf-8 -*-
# ============================================================
# Spidergraph Connector
# QGIS Plugin - Algorithm
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
SpiderGraph Connector - Core Algorithm
"""

from collections import defaultdict
from qgis.core import (
    QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY,
    QgsField, QgsWkbTypes, QgsMessageLog
)
from PyQt5.QtCore import QVariant


class SpiderGraphAlgorithm:
    """Core algorithm for creating spider connector lines"""

    def __init__(self):
        self.canceled = False
        self.source_extra_fields = []
        self.target_extra_fields = []
        self.source_field_types = {}
        self.target_field_types = {}

    def log(self, message):
        """Log message to QGIS log"""
        QgsMessageLog.logMessage(f"SpiderGraph: {message}", "SpiderGraph", level=0)

    def get_geometry_point(self, feature, layer):
        """
        Extract point from any geometry type
        - Point: return as-is
        - Line/Polygon: return centroid
        """
        geom = feature.geometry()
        if not geom or geom.isEmpty():
            return None

        geom_type = layer.geometryType()

        if geom_type == QgsWkbTypes.PointGeometry:
            return geom.asPoint()
        else:
            # For Line and Polygon, use centroid
            centroid = geom.centroid()
            if centroid and not centroid.isEmpty():
                return centroid.asPoint()
        return None

    def normalize_id(self, value, case_sensitive=False):
        """Normalize ID for matching"""
        if value is None:
            return ""
        s = str(value).strip()
        if not case_sensitive:
            s = s.lower()
        return s

    def build_target_index(self, target_layer, target_field, delimiters, case_sensitive, progress_callback=None):
        """Build index for target layer supporting multiple IDs per feature"""
        target_index = defaultdict(list)
        total_features = target_layer.featureCount()
        
        self.log(f"Building index for {total_features} target features...")

        if progress_callback:
            progress_callback(0, total_features)

        for idx, feature in enumerate(target_layer.getFeatures()):
            if self.canceled:
                break

            raw_value = feature[target_field]
            if raw_value:
                value_str = str(raw_value).strip()

                # Check for delimiters
                found_delimiter = False
                for delim in delimiters:
                    if delim and delim in value_str:
                        parts = [p.strip() for p in value_str.split(delim) if p.strip()]
                        for part in parts:
                            norm_id = self.normalize_id(part, case_sensitive)
                            if norm_id:
                                target_index[norm_id].append(feature)
                        found_delimiter = True
                        break

                if not found_delimiter:
                    norm_id = self.normalize_id(value_str, case_sensitive)
                    if norm_id:
                        target_index[norm_id].append(feature)

            if progress_callback and idx % 100 == 0:
                progress_callback(idx, total_features)

        self.log(f"Index built: {len(target_index)} unique IDs, total relations: {sum(len(v) for v in target_index.values())}")
        return target_index

    def run(self, params, progress_callback=None, status_callback=None):
        """Main algorithm execution"""
        try:
            source_layer = params['source_layer']
            target_layer = params['target_layer']
            source_field = params['source_field']
            target_field = params['target_field']
            output_name = params['output_name']
            partial_match = params['partial_match']
            case_sensitive = params['case_sensitive']
            delimiters = params['delimiters']
            
            # Get extra fields from params (default to empty list if not provided)
            source_extra_fields = params.get('source_extra_fields', [])
            target_extra_fields = params.get('target_extra_fields', [])

            self.log("Starting SpiderGraph algorithm...")
            self.log(f"Source: {source_layer.name()} [{source_field}]")
            self.log(f"Target: {target_layer.name()} [{target_field}]")
            self.log(f"Options: partial_match={partial_match}, case_sensitive={case_sensitive}, delimiters={delimiters}")
            self.log(f"Source extra fields: {source_extra_fields}")
            self.log(f"Target extra fields: {target_extra_fields}")

            if status_callback:
                status_callback("Membangun indeks target layer...")

            # Build target index
            target_index = self.build_target_index(
                target_layer, target_field, delimiters,
                case_sensitive, progress_callback
            )

            if status_callback:
                status_callback(f"Indeks selesai: {len(target_index)} unique IDs")

            # Prepare output layer
            crs = source_layer.crs()
            connector_layer = QgsVectorLayer(
                f"LineString?crs={crs.authid()}",
                output_name,
                "memory"
            )

            if not connector_layer.isValid():
                return False, "Gagal membuat memory layer", None

            provider = connector_layer.dataProvider()
            
            # ========== START: BUILD OUTPUT FIELDS ==========
            # Base fields (always included)
            output_fields = [
                QgsField("source_id", QVariant.String),
                QgsField("target_id", QVariant.String),
                QgsField("connection_type", QVariant.String),
                QgsField("target_count", QVariant.Int)
            ]
            
            # Add source extra fields (with src_ prefix)
            for field_name in source_extra_fields:
                src_field = source_layer.fields().field(field_name)
                src_field_type = src_field.type()
                prefixed_name = f"src_{field_name}"
                output_fields.append(QgsField(prefixed_name, src_field_type))
                self.log(f"Adding source field: {prefixed_name} (type: {src_field_type})")
            
            # Add target extra fields (with tgt_ prefix)
            for field_name in target_extra_fields:
                tgt_field = target_layer.fields().field(field_name)
                tgt_field_type = tgt_field.type()
                prefixed_name = f"tgt_{field_name}"
                output_fields.append(QgsField(prefixed_name, tgt_field_type))
                self.log(f"Adding target field: {prefixed_name} (type: {tgt_field_type})")
            
            # Add all fields to provider
            provider.addAttributes(output_fields)
            connector_layer.updateFields()
            # ========== END: BUILD OUTPUT FIELDS ==========

            # Process source features
            source_count = source_layer.featureCount()
            features_to_add = []
            matched_connections = 0
            unmatched_sources = 0
            multi_match_sources = 0
            processed = 0

            self.log(f"Processing {source_count} source features...")

            if status_callback:
                status_callback(f"Processing {source_count} fitur source...")

            for source_feat in source_layer.getFeatures():
                if self.canceled:
                    break

                processed += 1
                source_raw = source_feat[source_field]
                if not source_raw:
                    unmatched_sources += 1
                    continue

                source_id = self.normalize_id(source_raw, case_sensitive)
                source_point = self.get_geometry_point(source_feat, source_layer)

                if not source_point:
                    self.log(f"Warning: Could not get point from source feature {source_raw}")
                    continue

                # Find matching targets
                matching_targets = []

                # Exact match
                if source_id in target_index:
                    matching_targets.extend(target_index[source_id])

                # Partial match (if enabled)
                if partial_match and not matching_targets:
                    for target_key, target_features in target_index.items():
                        if source_id in target_key:
                            matching_targets.extend(target_features)

                # Create lines for each match
                if matching_targets:
                    conn_type = "one-to-many" if len(matching_targets) > 1 else "one-to-one"

                    for i, target_feat in enumerate(matching_targets):
                        target_point = self.get_geometry_point(target_feat, target_layer)
                        if target_point:
                            line_geom = QgsGeometry.fromPolylineXY([source_point, target_point])

                            if line_geom and not line_geom.isEmpty():
                                # ========== START: BUILD ATTRIBUTES ==========
                                # Base attributes
                                attributes = [
                                    str(source_raw),
                                    str(target_feat[target_field]),
                                    f"{conn_type}_{i+1}",
                                    len(matching_targets)
                                ]
                                
                                # Add source extra field values
                                for extra_field in source_extra_fields:
                                    val = source_feat[extra_field]
                                    attributes.append(val)
                                
                                # Add target extra field values
                                for extra_field in target_extra_fields:
                                    val = target_feat[extra_field]
                                    attributes.append(val)
                                # ========== END: BUILD ATTRIBUTES ==========
                                
                                feat = QgsFeature()
                                feat.setGeometry(line_geom)
                                feat.setAttributes(attributes)
                                features_to_add.append(feat)

                    matched_connections += len(matching_targets)
                    if len(matching_targets) > 1:
                        multi_match_sources += 1
                else:
                    unmatched_sources += 1

                # Update progress
                if progress_callback and processed % 10 == 0:
                    progress_callback(processed, source_count)

            # Add features to layer
            if features_to_add:
                provider.addFeatures(features_to_add)
                connector_layer.updateExtents()

                self.log(f"Added {len(features_to_add)} line features")

                # Generate summary
                summary = f"""
========================================
         SPIDERGRAPH COMPLETE
========================================
Lines created:      {matched_connections}
Source features:    {source_count}
Matched sources:    {source_count - unmatched_sources}
Unmatched sources:  {unmatched_sources}
Multi-connections:  {multi_match_sources}
Unique target IDs:  {len(target_index)}
Extra src fields:   {len(source_extra_fields)}
Extra tgt fields:   {len(target_extra_fields)}
========================================
"""
                return True, summary, connector_layer
            else:
                self.log("No lines created - no matches found")
                return False, "Tidak ada garis penghubung yang dibuat. Periksa data dan field matching!", None

        except Exception as e:
            import traceback
            error_msg = traceback.format_exc()
            self.log(f"Error: {str(e)}")
            self.log(f"Traceback: {error_msg}")
            return False, f"Terjadi error: {str(e)}", None