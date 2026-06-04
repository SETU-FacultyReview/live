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

# Load environment variables from .env file
load_dotenv()


class ByDeptCatalogueGenerator:
    def __init__(self, source_dir: str = "..", output_dir: str = "./tutors-modules-by-dept"):
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
        # Try multiple possible locations for computing icons
        possible_paths = [
            Path("../computing/module-catalogue/module-icons.yaml"),
            self.source_dir / "computing" / "module-catalogue" / "module-icons.yaml"
        ]

        for computing_icons in possible_paths:
            if computing_icons.exists():
                with open(computing_icons) as f:
                    self.module_icons = yaml.safe_load(f) or {}
                print(f"Loaded {len(self.module_icons)} icon mappings from computing catalogue")
                return

        print("Computing icon mappings not found, will use defaults")

    def load_cluster_icons(self):
        """Load cluster icon mappings"""
        script_dir = Path(__file__).parent
        cluster_icon_file = script_dir / "cluster-icons.yaml"
        if cluster_icon_file.exists():
            with open(cluster_icon_file) as f:
                self.cluster_icons = yaml.safe_load(f) or {}
            print(f"Loaded {len(self.cluster_icons)} cluster icon mappings")
        else:
            print("Warning: cluster-icons.yaml not found, clusters will use default icons")

    def load_programme_icons(self):
        """Load programme icon mappings"""
        script_dir = Path(__file__).parent
        programme_icon_file = script_dir / "programme-icons.yaml"
        if programme_icon_file.exists():
            with open(programme_icon_file) as f:
                self.programme_icons = yaml.safe_load(f) or {}
            print(f"Loaded {len(self.programme_icons)} programme icon mappings")
        else:
            self.programme_icons = {}
            print("Warning: programme-icons.yaml not found, programmes will use default icons")

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
            with open(desc_file) as f:
                data = yaml.safe_load(f)
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

        # Create course.md
        course_md = self.output_dir / "course.md"
        with open(course_md, 'w') as f:
            f.write("# SETU Science Modules by Department\n\n")
            f.write("This site contains a complete catalogue of approved modules organized by department.\n\n")
            f.write("**Unit 1:** Computing and Mathematics Department\n\n")
            f.write("**Unit 2:** Science Department\n")
        print("  Created course.md")

        # Create root topic.md
        root_topic = self.output_dir / "topic.md"
        with open(root_topic, 'w') as f:
            f.write("# SETU Science Modules by Department\n\n")
            f.write("Browse modules organized by department.\n")
        print("  Created topic.md")

        # Copy properties.yaml from script directory
        source_props = script_dir / "properties.yaml"
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

        # Copy course.png from script directory
        source_png = script_dir / "course.png"
        dest_png = self.output_dir / "course.png"
        if source_png.exists():
            shutil.copy(source_png, dest_png)
            print("  Copied course.png")
        else:
            print("  Warning: course.png not found in script directory")

    def sanitize_filename(self, text: str) -> str:
        """Convert text to safe filename"""
        text = text.replace(' ', '_')
        text = re.sub(r'[^\w\-]', '', text)
        return text

    def convert_latex_to_markdown(self, text: str) -> str:
        """Convert LaTeX formatting to markdown"""
        if not text:
            return text
        text = re.sub(r'\\emph\{([^}]+)\}', r'*\1*', text)
        return text

    def generate_module_markdown(self, module_code: str, cluster_name: str = None) -> str:
        """Generate markdown content for a module from science schema"""
        descriptor = self.descriptors.get(module_code)

        if not descriptor:
            return f"# {module_code}\n\nModule data not available."

        md = []

        # Icon selection priority:
        # 1. Module-specific icon from computing catalogue
        # 2. Cluster icon (if cluster_name provided)
        # 3. Default icon
        icon_info = self.module_icons.get(module_code)
        if icon_info:
            icon_type = icon_info.get('type', 'carbon:sys-provision')
            icon_color = icon_info.get('color', '014771')
        elif cluster_name and cluster_name in self.cluster_icons:
            cluster_icon = self.cluster_icons[cluster_name]
            icon_type = cluster_icon.get('type', 'carbon:sys-provision')
            icon_color = cluster_icon.get('color', '014771')
        else:
            # Default icon
            icon_type = 'carbon:sys-provision'
            icon_color = '014771'

        md.append("---")
        md.append("icon:")
        md.append(f"  type: {icon_type}")
        md.append(f"  color: {icon_color}")
        md.append("---")
        md.append("")
        md.append(f"# {descriptor.get('short_title', descriptor.get('full_title', module_code))}")
        md.append("")

        # Aim - extract first sentence only for the summary
        if 'aim' in descriptor:
            aim_text = descriptor['aim']
            # Extract first sentence
            match = re.search(r'(?<![A-Z]\d)\.(?:\s+[A-Z]|[A-Z](?=[a-z]))', aim_text)
            if match:
                first_sentence = aim_text[:match.start() + 1].strip()
            else:
                first_sentence = aim_text.strip()
                if not first_sentence.endswith('.'):
                    first_sentence += '.'
            md.append(first_sentence)
        md.append("")
        md.append(f'<p><a href="./archives/{module_code}.pdf" target="_blank" rel="noopener noreferrer" style="display: inline-flex; align-items: center; text-decoration: none;"><img src="https://upload.wikimedia.org/wikipedia/commons/6/60/Adobe_Acrobat_Reader_icon_%282020%29.svg" width="20" height="20" style="margin-right: 4px;" alt="Adobe Acrobat Icon"><span>Module Descriptor (PDF)</span></a></p>')
        md.append("")

        # Module information table
        md.append("## Module Information")
        md.append("")
        md.append("| **Field** | **Details** |")
        md.append("|-----------|-------------|")
        md.append(f"| **Module Code** | {module_code} |")
        md.append(f"| **Module Title** | {descriptor.get('full_title', 'N/A')} |")
        md.append(f"| **Short Title** | {descriptor.get('short_title', 'N/A')} |")
        md.append(f"| **Credits** | {descriptor.get('credits', 'N/A')} ECTS |")
        md.append(f"| **Level** | {descriptor.get('level', 'N/A')} |")
        md.append(f"| **School** | {descriptor.get('school', 'N/A')} |")
        md.append(f"| **Department** | {descriptor.get('department', 'N/A')} |")
        md.append(f"| **Module Author** | {descriptor.get('author', 'N/A')} |")
        md.append(f"| **Cluster** | {descriptor.get('cluster', 'N/A')} |")
        md.append("")
        md.append("---")
        md.append("")

        # Module aim
        if 'aim' in descriptor:
            md.append("## Module Aim")
            md.append("")
            md.append(self.convert_latex_to_markdown(descriptor['aim']))
            md.append("")
            md.append("---")
            md.append("")

        # Learning outcomes
        if 'learning_outcomes' in descriptor:
            md.append("## Learning Outcomes")
            md.append("")
            md.append("On successful completion of this module, learners will be able to:")
            md.append("")
            for i, outcome in enumerate(descriptor['learning_outcomes'], 1):
                md.append(f"{i}. {self.convert_latex_to_markdown(outcome)}")
            md.append("")
            md.append("---")
            md.append("")

        # Indicative content
        if 'indicative_content' in descriptor:
            md.append("## Indicative Content")
            md.append("")
            md.append("The module covers the following topics:")
            md.append("")
            for topic in descriptor['indicative_content']:
                md.append(f"- {self.convert_latex_to_markdown(topic)}")
            md.append("")
            md.append("---")
            md.append("")

        # Learning and teaching methods
        if 'learning_and_teaching_methods' in descriptor:
            md.append("## Learning and Teaching Methods")
            md.append("")
            for method in descriptor['learning_and_teaching_methods']:
                md.append(self.convert_latex_to_markdown(method))
                md.append("")

            # Contact hours table
            if 'learning_modes' in descriptor:
                md.append("### Contact Hours")
                md.append("")
                md.append("| **Activity** | **Full Time Hours** | **Part Time Hours** |")
                md.append("|--------------|---------------------|---------------------|")

                total_ft = 0
                total_pt = 0
                for mode in descriptor['learning_modes']:
                    ft = mode.get('full_time', 0)
                    pt = mode.get('part_time', 0)
                    # Handle cases where values might be strings or missing
                    try:
                        ft_val = int(ft) if ft else 0
                    except (ValueError, TypeError):
                        ft_val = 0
                    try:
                        pt_val = int(pt) if pt else 0
                    except (ValueError, TypeError):
                        pt_val = 0
                    total_ft += ft_val
                    total_pt += pt_val
                    md.append(f"| {mode['name']} | {ft_val} | {pt_val} |")

                md.append(f"| **Total** | **{total_ft}** | **{total_pt}** |")
                md.append("")

            md.append("---")
            md.append("")

        # Assessment methods
        if 'assessment_methods' in descriptor:
            md.append("## Assessment Methods")
            md.append("")
            md.append("| **Assessment Type** | **Learning Outcomes** | **Weighting** |")
            md.append("|---------------------|----------------------|---------------|")

            main_assessments = [a for a in descriptor['assessment_methods'] if a.get('main', False)]
            sub_assessments = [a for a in descriptor['assessment_methods'] if not a.get('main', False)]

            for assessment in main_assessments:
                los = assessment.get('learning_outcomes', 'All')
                weight = assessment.get('weighting', 0)
                md.append(f"| **{assessment['name']}** | {los} | **{weight}%** |")

            for assessment in sub_assessments:
                los = assessment.get('learning_outcomes', '')
                weight = assessment.get('weighting', 0)
                md.append(f"| - {assessment['name']} | {los} | {weight}% |")

            md.append("")
            md.append("---")
            md.append("")

        # Assessment criteria
        if 'assessment_criteria' in descriptor:
            md.append("## Assessment Criteria")
            md.append("")

            for criterion in descriptor['assessment_criteria']:
                criterion_text = self.convert_latex_to_markdown(criterion)
                md.append(criterion_text)
                md.append("")

            md.append("---")
            md.append("")

        # Pre-requisites and co-requisites
        prereqs = descriptor.get('prerequisites', [])
        coreqs = descriptor.get('corequisites', [])

        md.append("## Pre-requisites and Co-requisites")
        md.append("")
        md.append(f"- **Pre-requisites:** {', '.join(prereqs) if prereqs else 'None'}")
        md.append(f"- **Co-requisites:** {', '.join(coreqs) if coreqs else 'None'}")
        md.append("")
        md.append("---")
        md.append("")

        # Recommended reading
        if 'supplementary_material' in descriptor:
            md.append("## Recommended Reading")
            md.append("")
            md.append("### Supplementary Material")
            md.append("")
            for material in descriptor['supplementary_material']:
                md.append(f"- {self.convert_latex_to_markdown(material)}")
            md.append("")
            md.append("---")
            md.append("")

        if 'essential_material' in descriptor:
            if 'supplementary_material' not in descriptor:
                md.append("## Recommended Reading")
                md.append("")
            md.append("### Essential Material")
            md.append("")
            for material in descriptor['essential_material']:
                md.append(f"- {self.convert_latex_to_markdown(material)}")
            md.append("")
            md.append("---")
            md.append("")

        # Programme information
        if 'programmes' in descriptor and descriptor['programmes']:
            md.append("## Programme Information")
            md.append("")
            md.append("This module is available on the following programmes:")
            md.append("")
            md.append("| **Programme Code** | **Programme Title** | **Stage** | **Semester** | **Status** |")
            md.append("|-------------------|---------------------|-----------|--------------|------------|")

            for prog_info in descriptor['programmes']:
                if prog_info:  # Skip None entries
                    prog_code = prog_info.get('code', '')
                    prog_title = prog_info.get('name', '')
                    stage = prog_info.get('stage', '')
                    semester = prog_info.get('semester', '')
                    status = 'Mandatory' if prog_info.get('status') == 'M' else 'Elective'
                    md.append(f"| {prog_code} | {prog_title} | {stage} | {semester} | {status} |")

            md.append("")
            md.append("---")
            md.append("")

        # Resources required
        if 'requested_resources' in descriptor:
            md.append("## Resources Required")
            md.append("")
            for resource in descriptor['requested_resources']:
                md.append(f"- {self.convert_latex_to_markdown(resource)}")
            md.append("")
            md.append("---")
            md.append("")

        # Footer
        timetable_code = 'N/A'
        if 'programmes' in descriptor and descriptor['programmes']:
            for prog in descriptor['programmes']:
                if prog and prog.get('timetable'):
                    timetable_code = prog['timetable']
                    break

        md.append(f"*Module Code: {module_code} | Timetable Code: {timetable_code}*")

        return '\n'.join(md)

    def generate_department_unit(self, unit_num: int, dept_name: str, dept_filter: str, icon_type: str, icon_color: str):
        """Generate a complete department unit with programmes, clusters, and all-modules"""
        print(f"\nGenerating Unit {unit_num}: {dept_name}...")

        # Create unit directory
        unit_dir = self.output_dir / f"unit-{unit_num}"
        unit_dir.mkdir(exist_ok=True)

        # Create unit topic.md
        with open(unit_dir / "topic.md", 'w') as f:
            f.write("---\n")
            f.write("icon:\n")
            f.write(f"  type: {icon_type}\n")
            f.write(f"  color: {icon_color}\n")
            f.write("---\n\n")
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
            f.write("---\n")
            f.write("icon:\n")
            f.write("  type: mdi:school\n")
            f.write("  color: 2E7D32\n")
            f.write("---\n\n")
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

            # Get icon from programme-icons.yaml
            icon_info = self.programme_icons.get(prog_code)
            if icon_info:
                icon_type = icon_info.get('type', 'mdi:book-education')
                icon_color = icon_info.get('color', '455A64')
            else:
                icon_type = 'mdi:book-education'
                icon_color = '455A64'

            # Create programme topic.md
            with open(prog_dir / "topic.md", 'w') as f:
                f.write("---\n")
                f.write("icon:\n")
                f.write(f"  type: {icon_type}\n")
                f.write(f"  color: {icon_color}\n")
                f.write("---\n\n")
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
                    module_name = self.sanitize_filename(full_title)

                    # Create web object directory
                    web_dir = semester_unit_dir / f"web-{mod_idx:02d}-web-{mod_idx:02d}-{module_name}"
                    web_dir.mkdir(exist_ok=True)

                    # Get cluster for icon
                    cluster_name = descriptor.get('cluster', 'Uncategorized')

                    # Get icon
                    icon_info = self.module_icons.get(module_code)
                    if icon_info:
                        icon_type = icon_info.get('type', 'carbon:sys-provision')
                        icon_color = icon_info.get('color', '014771')
                    elif cluster_name in self.cluster_icons:
                        cluster_icon = self.cluster_icons[cluster_name]
                        icon_type = cluster_icon.get('type', 'carbon:sys-provision')
                        icon_color = cluster_icon.get('color', '014771')
                    else:
                        icon_type = 'carbon:sys-provision'
                        icon_color = '014771'

                    # Extract first sentence of aim
                    aim_text = descriptor.get('aim', '')
                    if aim_text:
                        match = re.search(r'(?<![A-Z]\d)\.(?:\s+[A-Z]|[A-Z](?=[a-z]))', aim_text)
                        if match:
                            first_sentence = aim_text[:match.start() + 1].strip()
                        else:
                            first_sentence = aim_text.strip()
                            if not first_sentence.endswith('.'):
                                first_sentence += '.'
                        first_sentence = self.convert_latex_to_markdown(first_sentence)
                    else:
                        first_sentence = ''

                    # Create link.md
                    with open(web_dir / "link.md", 'w') as f:
                        f.write("---\n")
                        f.write("icon:\n")
                        f.write(f"  type: {icon_type}\n")
                        f.write(f"  color: {icon_color}\n")
                        f.write("---\n\n")
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
            f.write("---\n")
            f.write("icon:\n")
            f.write("  type: mdi:view-grid\n")
            f.write("  color: 5E35B1\n")
            f.write("---\n\n")
            f.write("# Clusters\n\n")
            f.write(f"{len(clusters)} subject clusters\n")

        module_to_cluster_path = {}

        # Sort clusters alphabetically
        sorted_clusters = sorted(clusters.items(), key=lambda x: x[0])

        for idx, (cluster_name, module_codes) in enumerate(sorted_clusters, 1):
            cluster_dir_name = self.sanitize_filename(cluster_name)
            cluster_dir = clusters_dir / f"topic-{idx:02d}-{cluster_dir_name}"
            cluster_dir.mkdir(exist_ok=True)

            # Create cluster topic.md with icon
            with open(cluster_dir / "topic.md", 'w') as f:
                if cluster_name in self.cluster_icons:
                    cluster_icon = self.cluster_icons[cluster_name]
                    f.write("---\n")
                    f.write("icon:\n")
                    f.write(f"  type: {cluster_icon.get('type', 'carbon:sys-provision')}\n")
                    f.write(f"  color: {cluster_icon.get('color', '014771')}\n")
                    f.write("---\n\n")
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

                module_name = self.sanitize_filename(descriptor.get('full_title', module_code))
                note_dir_name = f"note-{mod_idx:02d}-note-{mod_idx:02d}-{module_name}"
                note_dir = cluster_dir / note_dir_name
                note_dir.mkdir(exist_ok=True)

                # Store the path for this module
                cluster_path = f"/note/{self.tutors_course_id}/{unit_dir.name}/topic-02-clusters/topic-{idx:02d}-{cluster_dir_name}/{note_dir_name}"
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
                markdown_content = self.generate_module_markdown(module_code, cluster_name)

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
            f.write("---\n")
            f.write("icon:\n")
            f.write("  type: mdi:sort-alphabetical-ascending\n")
            f.write("  color: 1976D2\n")
            f.write("---\n\n")
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
            module_name = self.sanitize_filename(full_title)

            # Create web object directory
            web_dir = all_modules_dir / f"web-{idx:03d}-web-{idx:03d}-{module_name}"
            web_dir.mkdir(exist_ok=True)

            # Get cluster for icon
            cluster_name = descriptor.get('cluster', 'Uncategorized')

            # Get icon
            icon_info = self.module_icons.get(module_code)
            if icon_info:
                icon_type = icon_info.get('type', 'carbon:sys-provision')
                icon_color = icon_info.get('color', '014771')
            elif cluster_name in self.cluster_icons:
                cluster_icon = self.cluster_icons[cluster_name]
                icon_type = cluster_icon.get('type', 'carbon:sys-provision')
                icon_color = cluster_icon.get('color', '014771')
            else:
                icon_type = 'carbon:sys-provision'
                icon_color = '014771'

            # Extract first sentence of aim
            aim_text = descriptor.get('aim', '')
            if aim_text:
                match = re.search(r'(?<![A-Z]\d)\.(?:\s+[A-Z]|[A-Z](?=[a-z]))', aim_text)
                if match:
                    first_sentence = aim_text[:match.start() + 1].strip()
                else:
                    first_sentence = aim_text.strip()
                    if not first_sentence.endswith('.'):
                        first_sentence += '.'
                first_sentence = self.convert_latex_to_markdown(first_sentence)
            else:
                first_sentence = ''

            # Create link.md
            with open(web_dir / "link.md", 'w') as f:
                f.write("---\n")
                f.write("icon:\n")
                f.write(f"  type: {icon_type}\n")
                f.write(f"  color: {icon_color}\n")
                f.write("---\n\n")
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
                            if self.sanitize_filename(module_title) == web_name:
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
