"""
Department - Filtered view of catalogue data for a single department.

This class receives a Catalogue object and filters it based on department criteria,
providing access to:
- Department programmes
- Department modules
- Department clusters
"""

from pathlib import Path
from typing import List
from collections import defaultdict


class Department:
    """
    A filtered view of catalogue data for a single department.

    This class takes a Catalogue object and filter criteria, then provides
    access to the programmes, modules, and clusters that belong to this department.
    """

    def __init__(self, name: str, filter_criteria: List[str], catalogue):
        """
        Initialize a department with filtered catalogue data.

        Args:
            name: Display name of the department (e.g., "Computing and Mathematics Department")
            filter_criteria: List of department names to include from the catalogue
                           (e.g., ["Computing and Mathematics"] or ["Science", "Land Sciences"])
            catalogue: Catalogue object containing all catalogue data
        """
        self.name = name
        self.filter_criteria = filter_criteria if isinstance(filter_criteria, list) else [filter_criteria]
        self.catalogue = catalogue

        # Filtered data (retrieved from catalogue)
        self.programmes = {}
        self.modules = {}
        self.clusters = {}

        # Filter data from catalogue
        self._retrieve_modules()
        self._retrieve_programmes()
        self._retrieve_clusters()

    def _retrieve_modules(self):
        """
        Retrieve modules for this department from the catalogue.

        Filters by the department field in module descriptors.
        """
        # Use the first filter criterion as the primary department
        # (In most cases there's only one, except Science which includes Land Sciences)
        primary_dept = self.filter_criteria[0]

        self.modules = {
            code: desc for code, desc in self.catalogue.descriptors.items()
            if desc.get('department') == primary_dept
        }

    def _retrieve_programmes(self):
        """
        Retrieve programmes for this department from the catalogue.

        Handles multi-department inclusion (e.g., Science unit includes both
        Science and Land Sciences programmes).
        """
        # First, identify valid programmes from the registry
        valid_programme_codes = {
            code for code, prog_info in self.catalogue.programme_registry.items()
            if prog_info['department'] in self.filter_criteria
        }

        # Count modules per programme to filter out programmes with too few modules
        # Note: semester 0 means "any semester" and should be counted
        prog_module_counts = defaultdict(int)
        for module_code, descriptor in self.catalogue.descriptors.items():
            if 'programmes' in descriptor and descriptor['programmes']:
                for prog in descriptor['programmes']:
                    if prog and 'code' in prog and 'semester' in prog:
                        prog_module_counts[prog['code']] += 1

        # Build programmes data with semester structure
        programmes_data = {}

        for module_code, descriptor in self.catalogue.descriptors.items():
            if 'programmes' in descriptor and descriptor['programmes']:
                for prog in descriptor['programmes']:
                    if prog and 'code' in prog:
                        prog_code = prog['code']

                        # Skip if not in valid programmes or has too few modules
                        if prog_code not in valid_programme_codes:
                            continue
                        if prog_module_counts[prog_code] < 3:
                            continue

                        prog_name = prog['name']
                        semester = prog.get('semester', 0)
                        status = prog.get('status', '')

                        # Initialize programme if not seen
                        if prog_code not in programmes_data:
                            # Get department from registry
                            dept_from_registry = self.catalogue.programme_registry.get(prog_code, {}).get('department', '')
                            programmes_data[prog_code] = {
                                'name': prog_name,
                                'department': dept_from_registry,
                                'semesters': defaultdict(list)
                            }

                        # Add module to semester (semester 0 = "any semester")
                        # Only skip if semester key doesn't exist in the data
                        if 'semester' in prog:
                            programmes_data[prog_code]['semesters'][semester].append({
                                'code': module_code,
                                'status': status,
                                'descriptor': descriptor
                            })

        # Filter out programmes with no semester data
        self.programmes = {
            code: data for code, data in programmes_data.items()
            if data['semesters']
        }

    def _retrieve_clusters(self):
        """
        Retrieve clusters for this department from the catalogue.

        Only includes clusters that have at least one module from this department.
        """
        dept_clusters = {}

        for cluster_name, module_codes in self.catalogue.clusters.items():
            # Filter modules to only those in this department
            dept_modules = [code for code in module_codes if code in self.modules]

            # Only include cluster if it has modules from this department
            if dept_modules:
                dept_clusters[cluster_name] = dept_modules

        self.clusters = dept_clusters

    def get_module_count(self) -> int:
        """Get the number of modules in this department."""
        return len(self.modules)

    def get_programme_count(self) -> int:
        """Get the number of programmes in this department."""
        return len(self.programmes)

    def get_cluster_count(self) -> int:
        """Get the number of clusters in this department."""
        return len(self.clusters)

    def get_summary(self) -> str:
        """
        Get a summary string for this department.

        Returns:
            Summary string (e.g., "Department has 238 modules, 15 programmes, 14 clusters")
        """
        return (f"Department has {self.get_module_count()} modules, "
                f"{self.get_programme_count()} programmes, "
                f"{self.get_cluster_count()} clusters")

    def __repr__(self) -> str:
        """String representation of the department."""
        return (f"Department(name='{self.name}', "
                f"modules={self.get_module_count()}, "
                f"programmes={self.get_programme_count()}, "
                f"clusters={self.get_cluster_count()})")
