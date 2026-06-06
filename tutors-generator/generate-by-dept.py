#!/usr/bin/env python3
"""
SETU Science Module Catalogue Generator - By Department
This script generates the tutors-modules-by-dept course from Descriptors/yaml data.
It creates two units: Unit 1 for Computing & Mathematics, Unit 2 for Science.
Each unit contains Programmes, Clusters, and All Modules filtered by department.

Data sources:
- Module descriptors: Descriptors/yaml/*.yaml
- PDFs: Descriptors/pdf/*.pdf
- Programmes: data/programmes.csv
"""

import os
import shutil
import csv
from pathlib import Path
from collections import defaultdict
from dotenv import load_dotenv

# Import utility functions
from utils import load_yaml_file

# Import icon utilities
from icons import (
    load_icon_mappings,
    load_icon_mappings_from_paths
)

# Import department catalogue
from department_catalogue import DepartmentCatalogue

# Load environment variables from .env file
load_dotenv()


class ByDeptCatalogueGenerator:
    def __init__(self, source_dir: str = "..", output_dir: str = "../tutors-modules-by-dept"):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)

        # Load Tutors course ID from environment
        self.tutors_course_id = os.getenv('TUTORS_COURSE_ID', 'setu-science-modules')

        # Data stores
        self.descriptors = {}
        self.clusters = {}
        self.programmes = {}
        self.programme_registry = {}  # From programmes.csv

        # Department catalogues (populated after load_data())
        self.departments = {}

        # Load icon mappings
        self.module_icons = {}
        self.cluster_icons = {}
        self.programme_icons = {}
        self.load_computing_icons()
        self.load_cluster_icons()
        self.load_programme_icons()

    def load_computing_icons(self):
        """Load icon mappings from computing catalogue for overlapping modules"""
        possible_paths = [
            Path("../computing/module-catalogue/module-icons.yaml"),
            self.source_dir / "computing" / "module-catalogue" / "module-icons.yaml"
        ]
        self.module_icons = load_icon_mappings_from_paths(
            possible_paths,
            description="icon mappings from computing catalogue"
        )

    def load_cluster_icons(self):
        """Load cluster icon mappings"""
        script_dir = Path(__file__).parent
        icons_dir = script_dir / "icons"
        self.cluster_icons = load_icon_mappings(icons_dir, 'cluster')

    def load_programme_icons(self):
        """Load programme icon mappings"""
        script_dir = Path(__file__).parent
        icons_dir = script_dir / "icons"
        self.programme_icons = load_icon_mappings(icons_dir, 'programme')

    def load_programme_registry(self):
        """Load programme registry from programmes.csv"""
        programmes_csv = self.source_dir / "data" / "programmes.csv"
        if not programmes_csv.exists():
            print("Warning: programmes.csv not found")
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

    def load_data(self):
        """Load all YAML descriptors from source directory"""
        print("Loading catalogue data...")

        # Load programme registry first
        self.load_programme_registry()

        # Load descriptors from Descriptors/yaml
        descriptors_dir = self.source_dir / "Descriptors" / "yaml"
        if not descriptors_dir.exists():
            print(f"Warning: Descriptors directory not found at {descriptors_dir}")
            return

        for desc_file in descriptors_dir.glob("*.yaml"):
            data = load_yaml_file(desc_file, default={})
            module_code = data.get('reference', desc_file.stem.split('_')[0])
            self.descriptors[module_code] = data

        print(f"Loaded {len(self.descriptors)} modules")

        # Extract clusters
        self.extract_clusters()

        # Extract programmes
        self.extract_programmes()

        print(f"Found {len(self.clusters)} clusters")
        print(f"Found {len(self.programmes)} programmes")

        # Create department catalogues
        self.create_department_catalogues()

    def extract_clusters(self):
        """Extract cluster information from descriptors"""
        for module_code, descriptor in self.descriptors.items():
            cluster_name = descriptor.get('cluster', 'Uncategorized')
            if cluster_name not in self.clusters:
                self.clusters[cluster_name] = []
            self.clusters[cluster_name].append(module_code)

    def extract_programmes(self):
        """Extract programme information from module descriptors using programmes.csv registry"""
        # Target departments we want to include
        TARGET_DEPARTMENTS = {'Computing and Mathematics', 'Science', 'Land Sciences'}

        # Count modules per programme
        prog_module_counts = defaultdict(int)

        for module_code, descriptor in self.descriptors.items():
            if 'programmes' in descriptor and descriptor['programmes']:
                for prog in descriptor['programmes']:
                    if prog and 'code' in prog and prog.get('semester'):
                        prog_module_counts[prog['code']] += 1

        # Identify valid programmes using registry department + minimum module count
        valid_programmes = {}  # prog_code -> department from registry
        for prog_code in prog_module_counts:
            if prog_code in self.programme_registry:
                registry_dept = self.programme_registry[prog_code]['department']
                module_count = prog_module_counts[prog_code]
                # Include if from target department and has >= 3 modules
                if registry_dept in TARGET_DEPARTMENTS and module_count >= 3:
                    valid_programmes[prog_code] = registry_dept

        # Extract programmes and their modules
        programmes_data = {}

        for module_code, descriptor in self.descriptors.items():
            if 'programmes' in descriptor and descriptor['programmes']:
                for prog in descriptor['programmes']:
                    if prog and 'code' in prog:
                        prog_code = prog['code']

                        # Skip programmes not in our target departments
                        if prog_code not in valid_programmes:
                            continue

                        prog_name = prog['name']
                        semester = prog.get('semester', 0)
                        status = prog.get('status', '')

                        # Initialize programme if not seen
                        if prog_code not in programmes_data:
                            programmes_data[prog_code] = {
                                'name': prog_name,
                                'department': valid_programmes[prog_code],
                                'semesters': defaultdict(list)
                            }

                        # Add module to semester (only if semester is specified)
                        if semester:
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

    def create_department_catalogues(self):
        """Create DepartmentCatalogue instances for each department"""
        # Computing and Mathematics Department
        self.departments['computing'] = DepartmentCatalogue(
            name="Computing and Mathematics Department",
            filter_criteria=["Computing and Mathematics"],
            all_descriptors=self.descriptors,
            all_programmes=self.programmes,
            all_clusters=self.clusters,
            module_icons=self.module_icons,
            cluster_icons=self.cluster_icons,
            programme_icons=self.programme_icons,
            source_dir=self.source_dir,
            tutors_course_id=self.tutors_course_id
        )

        # Science Department (includes Land Sciences)
        self.departments['science'] = DepartmentCatalogue(
            name="Science Department",
            filter_criteria=["Science", "Land Sciences"],
            all_descriptors=self.descriptors,
            all_programmes=self.programmes,
            all_clusters=self.clusters,
            module_icons=self.module_icons,
            cluster_icons=self.cluster_icons,
            programme_icons=self.programme_icons,
            source_dir=self.source_dir,
            tutors_course_id=self.tutors_course_id
        )

        # Print summaries
        print(f"\nDepartment catalogues created:")
        for key, dept in self.departments.items():
            print(f"  {dept.name}: {dept.get_summary()}")

    def clean_output(self):
        """Clean the output directory (preserving course files that will be regenerated)"""
        if self.output_dir.exists():
            # These files will be regenerated, so we clean everything except them during generation
            # Note: properties.yaml and course.png are copied from source, so we preserve them
            keep_files = ['properties.yaml', 'course.md', 'course.png', 'topic.md']

            for item in self.output_dir.iterdir():
                if item.name not in keep_files:
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()

    def create_course_files(self):
        """Create required course files"""
        print("\nSetting up course files...")

        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Get script directory for source files
        script_dir = Path(__file__).parent

        # Tutors files directory
        tutors_files_dir = script_dir / "tutors-files"

        # Copy course.md from tutors-files directory
        source_course_md = tutors_files_dir / "course.md"
        dest_course_md = self.output_dir / "course.md"
        if source_course_md.exists():
            shutil.copy(source_course_md, dest_course_md)
            print("  Copied course.md")
        else:
            # Fallback: create basic course.md
            with open(dest_course_md, 'w') as f:
                f.write("# SETU Science Modules by Department\n\n")
                f.write("This site contains a complete catalogue of approved modules organized by department.\n\n")
                f.write("**Unit 1:** Computing and Mathematics Department\n\n")
                f.write("**Unit 2:** Science Department\n")
            print("  Created course.md (source not found)")

        # Create root topic.md
        root_topic = self.output_dir / "topic.md"
        with open(root_topic, 'w') as f:
            f.write("# SETU Science Modules by Department\n\n")
            f.write("Browse modules organized by department.\n")
        print("  Created topic.md")

        # Copy properties.yaml from tutors-files directory
        source_props = tutors_files_dir / "properties.yaml"
        dest_props = self.output_dir / "properties.yaml"
        if source_props.exists():
            shutil.copy(source_props, dest_props)
            print("  Copied properties.yaml")
        else:
            # Fallback: create basic properties.yaml
            with open(dest_props, 'w') as f:
                f.write("credits: SETU Faculty\n")
                f.write("parent: #\n")
            print("  Created properties.yaml (source not found)")

        # Copy course.png from tutors-files directory
        source_png = tutors_files_dir / "course.png"
        dest_png = self.output_dir / "course.png"
        if source_png.exists():
            shutil.copy(source_png, dest_png)
            print("  Copied course.png")
        else:
            print("  Warning: course.png not found in tutors-files directory")


    def generate_department_unit(self, unit_num: int, dept_catalogue: DepartmentCatalogue, icon_type: str, icon_color: str):
        """
        Generate a complete department unit with programmes, clusters, and all-modules.

        Args:
            unit_num: Unit number (1, 2, etc.)
            dept_catalogue: DepartmentCatalogue instance containing department data
            icon_type: Icon type for the unit (e.g., "mdi:laptop")
            icon_color: Icon color for the unit (e.g., "1976D2")
        """
        print(f"\nGenerating Unit {unit_num}: {dept_catalogue.name}...")

        # Create unit directory
        unit_dir = self.output_dir / f"unit-{unit_num}"

        # Delegate to the department catalogue to generate its content
        dept_catalogue.generate_unit(unit_dir, icon_type, icon_color)

    def generate(self):
        """Main generation process"""
        print("=" * 60)
        print("SETU Science Module Catalogue Generator - By Department")
        print("=" * 60)

        # Load all data
        self.load_data()

        # Create course files first
        self.create_course_files()

        # Clean output directory (except course files)
        self.clean_output()

        # Generate Unit 1: Computing and Mathematics
        self.generate_department_unit(
            unit_num=1,
            dept_catalogue=self.departments['computing'],
            icon_type="mdi:laptop",
            icon_color="1976D2"
        )

        # Generate Unit 2: Science Department
        self.generate_department_unit(
            unit_num=2,
            dept_catalogue=self.departments['science'],
            icon_type="mdi:flask",
            icon_color="00897B"
        )

        print("\n" + "=" * 60)
        print("Generation complete!")
        print("=" * 60)
        print(f"\nOutput directory: {self.output_dir}")
        print(f"- Unit 1: Computing and Mathematics Department")
        print(f"- Unit 2: Science Department")


def main():
    generator = ByDeptCatalogueGenerator()
    generator.generate()


if __name__ == "__main__":
    main()
