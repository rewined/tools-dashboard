#!/usr/bin/env python3
"""Test script to verify label formats are properly loaded"""

import sys
sys.path.insert(0, 'src')

from label_formats import LABEL_FORMATS

print("=== Label Formats Test ===")
print(f"Total formats: {len(LABEL_FORMATS)}")
print("\nAvailable formats:")
for key, format in LABEL_FORMATS.items():
    print(f"  - {key}: {format.name}")

print(f"\nOL1000WX exists: {'ol1000wx' in LABEL_FORMATS}")
if 'ol1000wx' in LABEL_FORMATS:
    ol = LABEL_FORMATS['ol1000wx']
    print(f"  Name: {ol.name}")
    print(f"  Size: {ol.width}\" x {ol.height}\"")
    print(f"  Grid: {ol.columns} cols x {ol.rows} rows")