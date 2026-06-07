"""
Catalogue - Complete module catalogue data loader.

This class is responsible for loading the complete catalogue data including:
- Programme registry
- All module descriptors
- All clusters
- All icon mappings

It should be loaded once at generator startup.
"""

import csv
from pathlib import Path
from collections import defaultdict

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import load_yaml_file
from icons import (
    load_icon_mappings,
    load_icon_mappings_from_paths
)


class Catalogue:
    """
    Loads and stores the complete module catalogue data.

    This class is responsible for loading all catalogue data once at startup,
    making it available to other components of the generator.
    """

    def __init__(self, source_dir: Path = None):
        """
        Initialize the catalogue and load all data.

        Args:
            source_dir: Path to the source directory containing catalogue data.
                       Defaults to parent directory of script if not provided.
        """
        # Set source directory
        if source_dir is None:
            source_dir = Path(__file__).parent.parent
        self.source_dir = Path(source_dir)

        # Data stores
        self.programme_registry = {}  # From programmes.csv
        self.descriptors = {}         # All module descriptors
        self.clusters = {}            # All clusters

        # Icon mappings
        self.module_icons = {}
        self.cluster_icons = {}
        self.programme_icons = {}
        self.catalogue_icons = {}

        # Load all data
        self._load_programme_registry()
        self._load_module_descriptors()
        self._extract_clusters()
        self._load_all_icons()

    def _load_programme_registry(self):
        """Load programme registry from programmes.yaml"""
        programmes_yaml = self.source_dir / "data" / "programmes.yaml"

        if not programmes_yaml.exists():
            print(f"Warning: programmes.yaml not found at {programmes_yaml}")
            return

        # Load YAML file
        programmes_data = load_yaml_file(programmes_yaml, default={})

        # Extract programmes from hierarchical structure
        # Structure: departments -> department_name -> level_X -> [programmes]
        if 'departments' in programmes_data:
            for dept_name, levels in programmes_data['departments'].items():
                for level_name, programmes in levels.items():
                    for prog in programmes:
                        code = prog.get('code')
                        if code:
                            self.programme_registry[code] = {
                                'title': prog.get('title', ''),
                                'department': dept_name,
                                'faculty': prog.get('faculty', ''),
                                'category': prog.get('category', ''),
                                'level': level_name  # Add level information
                            }

        print(f"Loaded {len(self.programme_registry)} programmes from registry")

    def _load_module_descriptors(self):
        """Load all YAML module descriptors"""
        descriptors_dir = self.source_dir / "Descriptors" / "yaml"

        if not descriptors_dir.exists():
            print(f"Warning: Descriptors directory not found at {descriptors_dir}")
            return

        for desc_file in descriptors_dir.glob("*.yaml"):
            data = load_yaml_file(desc_file, default={})
            module_code = data.get('reference', desc_file.stem.split('_')[0])
            self.descriptors[module_code] = data

        print(f"Loaded {len(self.descriptors)} module descriptors")

    def _extract_clusters(self):
        """Extract cluster information from module descriptors"""
        for module_code, descriptor in self.descriptors.items():
            cluster_name = descriptor.get('cluster', 'Uncategorized')
            if cluster_name not in self.clusters:
                self.clusters[cluster_name] = []
            self.clusters[cluster_name].append(module_code)

        print(f"Found {len(self.clusters)} clusters")

    def _load_all_icons(self):
        """Load all icon mappings (module, cluster, programme)"""
        # Get icons directory (one level up from models/ directory)
        script_dir = Path(__file__).parent.parent  # tutors-generator/
        icons_dir = script_dir / "icons"

        # Load module icons - try local icons dir first, then computing catalogue
        possible_module_icon_paths = [
            icons_dir / "module-icons.yaml",
            Path("../computing/module-catalogue/module-icons.yaml"),
            self.source_dir / "computing" / "module-catalogue" / "module-icons.yaml"
        ]
        self.module_icons = load_icon_mappings_from_paths(
            possible_module_icon_paths,
            description="module icon mappings"
        )

        # Load cluster, programme, and catalogue icons
        self.cluster_icons = load_icon_mappings(icons_dir, 'cluster')
        self.programme_icons = load_icon_mappings(icons_dir, 'programme')
        self.catalogue_icons = load_icon_mappings(icons_dir, 'catalogue')

    def get_summary(self) -> str:
        """
        Get a summary of the loaded catalogue.

        Returns:
            Summary string describing catalogue contents
        """
        return (f"Catalogue: {len(self.programme_registry)} programmes, "
                f"{len(self.descriptors)} modules, "
                f"{len(self.clusters)} clusters")

    def __repr__(self) -> str:
        """String representation of the catalogue."""
        return f"Catalogue({len(self.descriptors)} modules, {len(self.programme_registry)} programmes)"
