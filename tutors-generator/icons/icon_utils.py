"""
Icon utilities for SETU catalogue generators.

This module contains functions for loading, selecting, and formatting icons
for Tutors content (modules, programmes, clusters, etc.).
"""

import sys
from pathlib import Path
from typing import Optional
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import load_yaml_file from utils (needed for load_icon_mappings)
from utils import load_yaml_file


# ============================================================================
# Icon Loading Utilities
# ============================================================================

def load_icon_mappings(icons_dir: Path, icon_type: str) -> dict:
    """
    Load icon mappings from the icons directory.

    Args:
        icons_dir: Path to the icons directory
        icon_type: Type of icons to load ('cluster', 'programme', 'module')

    Returns:
        Dictionary of icon mappings
    """
    icon_file = icons_dir / f"{icon_type}-icons.yaml"
    icons = load_yaml_file(icon_file)

    if icons:
        print(f"Loaded {len(icons)} {icon_type} icon mappings")
    else:
        print(f"Warning: {icon_type}-icons.yaml not found or empty")

    return icons


def load_icon_mappings_from_paths(possible_paths: list[Path], description: str = "icons") -> dict:
    """
    Load icon mappings from multiple possible paths (tries each until successful).

    Args:
        possible_paths: List of paths to try in order
        description: Description of icons for logging (e.g., "computing icons")

    Returns:
        Dictionary of icon mappings, or empty dict if none found
    """
    for icon_path in possible_paths:
        if icon_path.exists():
            icons = load_yaml_file(icon_path, default={})
            print(f"Loaded {len(icons)} {description} from {icon_path.name}")
            return icons

    print(f"{description} not found, will use defaults")
    return {}


# ============================================================================
# Icon Selection Utilities
# ============================================================================

def get_icon_for_item(item_code: str,
                       item_icons: dict,
                       cluster_name: Optional[str] = None,
                       cluster_icons: Optional[dict] = None,
                       default_icon: str = "carbon:sys-provision",
                       default_color: str = "014771") -> tuple[str, str]:
    """
    Get icon type and color for an item (module, programme, etc.).

    Priority:
    1. Item-specific icon
    2. Cluster icon (if cluster_name and cluster_icons provided)
    3. Default icon

    Args:
        item_code: Code of the item (e.g., module code, programme code)
        item_icons: Dictionary of item-specific icon mappings
        cluster_name: Optional cluster name for fallback
        cluster_icons: Optional cluster icon mappings
        default_icon: Default icon type
        default_color: Default icon color

    Returns:
        Tuple of (icon_type, icon_color)
    """
    # Try item-specific icon first
    if item_code in item_icons:
        icon_info = item_icons[item_code]
        return (
            icon_info.get('type', default_icon),
            icon_info.get('color', default_color)
        )

    # Try cluster icon as fallback
    if cluster_name and cluster_icons and cluster_name in cluster_icons:
        cluster_icon = cluster_icons[cluster_name]
        return (
            cluster_icon.get('type', default_icon),
            cluster_icon.get('color', default_color)
        )

    # Use default
    return (default_icon, default_color)


# ============================================================================
# Icon Formatting Utilities
# ============================================================================

def create_icon_frontmatter(icon_type: str, icon_color: str) -> str:
    """
    Create YAML frontmatter for Tutors icons.

    Args:
        icon_type: Icon type (e.g., 'mdi:laptop')
        icon_color: Icon color (hex without #, e.g., '1976D2')

    Returns:
        Formatted YAML frontmatter as string
    """
    return f"""---
icon:
  type: {icon_type}
  color: {icon_color}
---

"""
