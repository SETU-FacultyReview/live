"""
Icons package - Icon utilities and mappings for the catalogue system.

This package contains icon mapping files (YAML) and utilities for loading
and working with icons for Tutors content.
"""

from .icon_utils import (
    load_icon_mappings,
    load_icon_mappings_from_paths,
    get_icon_for_item,
    create_icon_frontmatter
)

__all__ = [
    'load_icon_mappings',
    'load_icon_mappings_from_paths',
    'get_icon_for_item',
    'create_icon_frontmatter'
]
