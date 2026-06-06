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
import yaml
import shutil
import csv
from pathlib import Path
from typing import Dict, List, Any
import re
from collections import defaultdict, Counter
from dotenv import load_dotenv

# Import utility functions
from utils import (
    sanitize_filename,
    convert_latex_to_markdown,
    extract_first_sentence,
    load_yaml_file,
    get_tutors_weburl_path,
    format_module_status
)

# Import icon utilities
from icons import (
    load_icon_mappings,
    load_icon_mappings_from_paths,
    get_icon_for_item,
    create_icon_frontmatter
)

# Import markdown utilities
from markdown import generate_module_markdown

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


    def generate_department_unit(self, unit_num: int, dept_name: str, dept_filter: str, icon_type: str, icon_color: str):
        """Generate a complete department unit with programmes, clusters, and all-modules"""
        print(f"\nGenerating Unit {unit_num}: {dept_name}...")

        # Create unit directory
        unit_dir = self.output_dir / f"unit-{unit_num}"
        unit_dir.mkdir(exist_ok=True)

        # Create unit topic.md
        with open(unit_dir / "topic.md", 'w') as f:
            f.write(create_icon_frontmatter(icon_type, icon_color))
            f.write(f"# {dept_name}\n\n")
            f.write("Browse programmes, clusters, and modules.\n")

        # Filter descriptors by department
        dept_descriptors = {
            code: desc for code, desc in self.descriptors.items()
            if desc.get('department') == dept_filter
        }

        # Filter programmes by department
        # Special case: Science unit includes both Science and Land Sciences departments
        if dept_filter == "Science":
            dept_programmes = {
                code: prog for code, prog in self.programmes.items()
                if prog['department'] in ['Science', 'Land Sciences']
            }
        else:
            dept_programmes = {
                code: prog for code, prog in self.programmes.items()
                if prog['department'] == dept_filter
            }

        # Filter clusters (only clusters with modules from this department)
        dept_clusters = {}
        for cluster_name, module_codes in self.clusters.items():
            dept_modules = [code for code in module_codes if code in dept_descriptors]
            if dept_modules:
                dept_clusters[cluster_name] = dept_modules

        print(f"  Department has {len(dept_descriptors)} modules, {len(dept_programmes)} programmes, {len(dept_clusters)} clusters")

        # Generate the three topics (clusters first to build path mapping)
        module_to_cluster_path = self._generate_clusters_topic(unit_dir, dept_clusters, dept_descriptors)
        self._generate_programmes_topic(unit_dir, dept_programmes, dept_descriptors, module_to_cluster_path)
        self._generate_all_modules_topic(unit_dir, dept_descriptors, module_to_cluster_path)

    def _generate_programmes_topic(self, unit_dir: Path, programmes: dict, descriptors: dict, module_to_cluster_path: dict):
        """Generate programmes topic for a department"""
        programmes_dir = unit_dir / "topic-01-programmes"
        programmes_dir.mkdir(exist_ok=True)

        # Create programmes topic.md
        with open(programmes_dir / "topic.md", 'w') as f:
            f.write(create_icon_frontmatter("mdi:school", "2E7D32"))
            f.write("# Programmes\n\n")
            f.write(f"{len(programmes)} programmes\n")

        # Sort programmes alphabetically
        sorted_programmes = sorted(programmes.items(), key=lambda x: x[1]['name'])

        for idx, (prog_code, prog_data) in enumerate(sorted_programmes):
            prog_name = prog_data['name']
            semesters = prog_data['semesters']

            # Create programme directory
            prog_dir = programmes_dir / f"topic-{idx:02d}-{prog_code}"
            prog_dir.mkdir(exist_ok=True)

            # Get icon for programme
            icon_type, icon_color = get_icon_for_item(
                prog_code,
                self.programme_icons,
                default_icon='mdi:book-education',
                default_color='455A64'
            )

            # Create programme topic.md
            with open(prog_dir / "topic.md", 'w') as f:
                f.write(create_icon_frontmatter(icon_type, icon_color))
                f.write(f"# {prog_name}\n\n")
                f.write("TODO: Programme leader information\n")

            # Create semester units
            for semester_num in sorted(semesters.keys()):
                semester_modules = semesters[semester_num]

                # Create semester unit directory
                semester_unit_dir = prog_dir / f"unit-{semester_num}"
                semester_unit_dir.mkdir(exist_ok=True)

                # Create semester topic.md
                with open(semester_unit_dir / "topic.md", 'w') as f:
                    f.write(f"# Semester {semester_num}\n\n")
                    f.write(f"{len(semester_modules)} modules\n")

                # Create web objects for each module
                for mod_idx, module_info in enumerate(semester_modules, 1):
                    module_code = module_info['code']
                    descriptor = module_info['descriptor']

                    # Skip if not in this department's descriptors
                    if module_code not in descriptors:
                        continue

                    short_title = descriptor.get('short_title', descriptor.get('full_title', module_code))
                    full_title = descriptor.get('full_title', module_code)
                    module_name = sanitize_filename(full_title)

                    # Create web object directory
                    web_dir = semester_unit_dir / f"web-{mod_idx:02d}-web-{mod_idx:02d}-{module_name}"
                    web_dir.mkdir(exist_ok=True)

                    # Get cluster for icon
                    cluster_name = descriptor.get('cluster', 'Uncategorized')

                    # Get icon
                    icon_type, icon_color = get_icon_for_item(
                        module_code,
                        self.module_icons,
                        cluster_name=cluster_name,
                        cluster_icons=self.cluster_icons
                    )

                    # Extract first sentence of aim
                    aim_text = descriptor.get('aim', '')
                    if aim_text:
                        first_sentence = convert_latex_to_markdown(extract_first_sentence(aim_text))
                    else:
                        first_sentence = ''

                    # Create link.md
                    with open(web_dir / "link.md", 'w') as f:
                        f.write(create_icon_frontmatter(icon_type, icon_color))
                        f.write(short_title)
                        if first_sentence:
                            f.write("\n\n")
                            f.write(first_sentence)

                    # Create weburl pointing to cluster note
                    cluster_path = module_to_cluster_path.get(module_code, "#")
                    with open(web_dir / "weburl", 'w') as f:
                        f.write(cluster_path)

        print(f"    Generated {len(programmes)} programmes")

    def _generate_clusters_topic(self, unit_dir: Path, clusters: dict, descriptors: dict) -> dict:
        """Generate clusters topic for a department and return module-to-path mapping"""
        clusters_dir = unit_dir / "topic-02-clusters"
        clusters_dir.mkdir(exist_ok=True)

        # Create clusters topic.md
        with open(clusters_dir / "topic.md", 'w') as f:
            f.write(create_icon_frontmatter("mdi:view-grid", "5E35B1"))
            f.write("# Clusters\n\n")
            f.write(f"{len(clusters)} subject clusters\n")

        module_to_cluster_path = {}

        # Sort clusters alphabetically
        sorted_clusters = sorted(clusters.items(), key=lambda x: x[0])

        for idx, (cluster_name, module_codes) in enumerate(sorted_clusters, 1):
            cluster_dir_name = sanitize_filename(cluster_name)
            cluster_dir = clusters_dir / f"topic-{idx:02d}-{cluster_dir_name}"
            cluster_dir.mkdir(exist_ok=True)

            # Create cluster topic.md with icon
            with open(cluster_dir / "topic.md", 'w') as f:
                if cluster_name in self.cluster_icons:
                    # Use get_icon_for_item for consistent icon selection
                    icon_type, icon_color = get_icon_for_item(
                        cluster_name,
                        self.cluster_icons
                    )
                    f.write(create_icon_frontmatter(icon_type, icon_color))
                f.write(f"# {cluster_name}\n\n\n")

            # Sort modules alphabetically
            module_with_names = []
            for module_code in module_codes:
                descriptor = descriptors.get(module_code)
                if descriptor:
                    name = descriptor.get('full_title', module_code)
                    module_with_names.append((module_code, name))

            sorted_modules = [code for code, name in sorted(module_with_names, key=lambda x: x[1])]

            for mod_idx, module_code in enumerate(sorted_modules, 1):
                descriptor = descriptors.get(module_code)
                if not descriptor:
                    continue

                module_name = sanitize_filename(descriptor.get('full_title', module_code))
                note_dir_name = f"note-{mod_idx:02d}-note-{mod_idx:02d}-{module_name}"
                note_dir = cluster_dir / note_dir_name
                note_dir.mkdir(exist_ok=True)

                # Store the path for this module
                cluster_path = get_tutors_weburl_path(
                    self.tutors_course_id,
                    unit_dir.name,
                    "topic-02-clusters",
                    f"topic-{idx:02d}-{cluster_dir_name}",
                    note_dir_name
                )
                module_to_cluster_path[module_code] = cluster_path

                # Create archives directory
                archives_dir = note_dir / "archives"
                archives_dir.mkdir(exist_ok=True)

                # Copy PDF if exists from Descriptors/pdf
                pdf_dir = self.source_dir / "Descriptors" / "pdf"
                # PDF files use full filename format: A00841_-_Module_Title.pdf
                module_ref = descriptor.get('reference', module_code)
                # Try exact match first (with full title in filename)
                pdf_source = None
                for pdf_file in pdf_dir.glob(f"{module_ref}_*.pdf"):
                    pdf_source = pdf_file
                    break

                if not pdf_source:
                    # Fallback to simple module code
                    pdf_source = pdf_dir / f"{module_ref}.pdf"

                # Try alternate naming pattern if not found
                if not pdf_source.exists() and pdf_dir.exists():
                    # Try to find PDF with module code in filename
                    for pdf_file in pdf_dir.glob(f"{module_code}*.pdf"):
                        pdf_source = pdf_file
                        break

                if pdf_source.exists():
                    shutil.copy(pdf_source, archives_dir / f"{module_code}.pdf")
                else:
                    print(f"      Warning: PDF not found for {module_code}")

                # Generate module markdown
                descriptor = self.descriptors.get(module_code)
                markdown_content = generate_module_markdown(
                    module_code,
                    descriptor,
                    self.module_icons,
                    self.cluster_icons,
                    cluster_name=cluster_name
                )

                # Write note.md
                with open(note_dir / "note.md", 'w') as f:
                    f.write(markdown_content)

        print(f"    Generated {len(clusters)} clusters with {len(module_to_cluster_path)} modules")
        return module_to_cluster_path

    def _generate_all_modules_topic(self, unit_dir: Path, descriptors: dict, module_to_cluster_path: dict):
        """Generate all-modules topic for a department"""
        all_modules_dir = unit_dir / "topic-03-all-modules"
        all_modules_dir.mkdir(exist_ok=True)

        # Create all-modules topic.md
        with open(all_modules_dir / "topic.md", 'w') as f:
            f.write(create_icon_frontmatter("mdi:sort-alphabetical-ascending", "1976D2"))
            f.write("# All Modules\n\n")
            f.write(f"{len(descriptors)} modules listed alphabetically\n")

        # Sort modules alphabetically by full title
        sorted_modules = sorted(
            descriptors.items(),
            key=lambda x: x[1].get('full_title', x[0])
        )

        for idx, (module_code, descriptor) in enumerate(sorted_modules, 1):
            short_title = descriptor.get('short_title', descriptor.get('full_title', module_code))
            full_title = descriptor.get('full_title', module_code)
            module_name = sanitize_filename(full_title)

            # Create web object directory
            web_dir = all_modules_dir / f"web-{idx:03d}-web-{idx:03d}-{module_name}"
            web_dir.mkdir(exist_ok=True)

            # Get cluster for icon
            cluster_name = descriptor.get('cluster', 'Uncategorized')

            # Get icon
            icon_type, icon_color = get_icon_for_item(
                module_code,
                self.module_icons,
                cluster_name=cluster_name,
                cluster_icons=self.cluster_icons
            )

            # Extract first sentence of aim
            aim_text = descriptor.get('aim', '')
            if aim_text:
                first_sentence = convert_latex_to_markdown(extract_first_sentence(aim_text))
            else:
                first_sentence = ''

            # Create link.md
            with open(web_dir / "link.md", 'w') as f:
                f.write(create_icon_frontmatter(icon_type, icon_color))
                f.write(short_title)
                if first_sentence:
                    f.write("\n\n")
                    f.write(first_sentence)

            # Create weburl pointing to cluster note
            cluster_path = module_to_cluster_path.get(module_code, "#")
            with open(web_dir / "weburl", 'w') as f:
                f.write(cluster_path)

        print(f"    Generated {len(descriptors)} module web links")

    def update_programme_weburls(self, unit_dir: Path, module_to_cluster_path: dict):
        """Update programme web object URLs to point to cluster notes"""
        programmes_dir = unit_dir / "topic-01-programmes"

        if not programmes_dir.exists():
            return

        for prog_dir in programmes_dir.iterdir():
            if not prog_dir.is_dir() or not prog_dir.name.startswith('topic-'):
                continue

            for semester_dir in prog_dir.iterdir():
                if not semester_dir.is_dir() or not semester_dir.name.startswith('unit-'):
                    continue

                for web_dir in semester_dir.iterdir():
                    if not web_dir.is_dir() or not web_dir.name.startswith('web-'):
                        continue

                    # Extract module code from web directory name or link.md
                    link_file = web_dir / "link.md"
                    weburl_file = web_dir / "weburl"

                    if link_file.exists() and weburl_file.exists():
                        # Try to find module code by matching against descriptors
                        web_name = web_dir.name.split('-', 4)[-1] if len(web_dir.name.split('-')) > 4 else ""

                        # Find matching module
                        for module_code in module_to_cluster_path.keys():
                            module_title = self.descriptors.get(module_code, {}).get('full_title', '')
                            if sanitize_filename(module_title) == web_name:
                                cluster_path = module_to_cluster_path[module_code]
                                with open(weburl_file, 'w') as f:
                                    f.write(cluster_path)
                                break

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
            dept_name="Computing and Mathematics Department",
            dept_filter="Computing and Mathematics",
            icon_type="mdi:laptop",
            icon_color="1976D2"
        )

        # Generate Unit 2: Science Department
        self.generate_department_unit(
            unit_num=2,
            dept_name="Science Department",
            dept_filter="Science",
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
