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

        # Load all data
        self._load_programme_registry()
        self._load_module_descriptors()
        self._extract_clusters()
        self._load_all_icons()

    def _load_programme_registry(self):
        """Load programme registry from programmes.csv"""
        programmes_csv = self.source_dir / "data" / "programmes.csv"

        if not programmes_csv.exists():
            print(f"Warning: programmes.csv not found at {programmes_csv}")
            return

        with open(programmes_csv, 'r', encoding='utf-8-sig') as f:  # utf-8-sig handles BOM
            reader = csv.DictReader(f)
            for row in reader:
                if 'code' in row and row['code']:  # Skip empty rows
                    code = row['code']
                    self.programme_registry[code] = {
                        'title': row.get('title', ''),
                        'department': row.get('department', ''),
                        'faculty': row.get('faculty', ''),
                        'category': row.get('category', '')
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
        # Load module icons from computing catalogue (for overlapping modules)
        possible_computing_paths = [
            Path("../computing/module-catalogue/module-icons.yaml"),
            self.source_dir / "computing" / "module-catalogue" / "module-icons.yaml"
        ]
        self.module_icons = load_icon_mappings_from_paths(
            possible_computing_paths,
            description="icon mappings from computing catalogue"
        )

        # Load cluster and programme icons from this script's directory
        script_dir = Path(__file__).parent
        icons_dir = script_dir / "icons"
        self.cluster_icons = load_icon_mappings(icons_dir, 'cluster')
        self.programme_icons = load_icon_mappings(icons_dir, 'programme')

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
