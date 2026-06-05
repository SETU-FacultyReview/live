#!/usr/bin/env python3
"""
SETU Science Module Catalogue Generator - Master
This script generates the tutors-modules-master course from science/module-catalogue data.
It creates a cluster-based view similar to computing's unit-2-clusters.
"""

import os
import yaml
import shutil
from pathlib import Path
from typing import Dict, List, Any
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class MasterCatalogueGenerator:
    def __init__(self, source_dir: str = "module-catalogue", output_dir: str = "tutors-modules-master"):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)

        # Load Tutors course ID from environment
        self.tutors_course_id = os.getenv('TUTORS_COURSE_ID', 'setu-science-modules')

        # Data stores
        self.descriptors = {}
        self.clusters = {}
        self.module_to_cluster_path = {}  # Maps module code to cluster note path
        self.programmes = {}  # Maps programme code to programme info and modules

        # Load icon mappings from computing if available
        self.module_icons = {}
        self.load_computing_icons()

        # Load cluster icons
        self.cluster_icons = {}
        self.load_cluster_icons()
        self.load_programme_icons()

    def load_computing_icons(self):
        """Load icon mappings from computing catalogue for overlapping modules"""
        computing_icons = Path("../computing/module-catalogue/module-icons.yaml")
        if computing_icons.exists():
            with open(computing_icons) as f:
                self.module_icons = yaml.safe_load(f) or {}
            print(f"Loaded {len(self.module_icons)} icon mappings from computing catalogue")
        else:
            print("Computing icon mappings not found, will use defaults")

    def load_cluster_icons(self):
        """Load cluster icon mappings"""
        # Look in tutors-generator directory (same as this script)
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

    def load_data(self):
        """Load all YAML descriptors from source directory"""
        print("Loading catalogue data...")

        # Load descriptors
        for desc_file in (self.source_dir / "descriptors" / "yaml").glob("*.yaml"):
            with open(desc_file) as f:
                data = yaml.safe_load(f)
                # Extract module code from reference field
                module_code = data.get('reference', desc_file.stem.split('_')[0])
                self.descriptors[module_code] = data

        # Build cluster index from descriptors
        for code, descriptor in self.descriptors.items():
            cluster = descriptor.get('cluster', 'Uncategorized')
            if cluster not in self.clusters:
                self.clusters[cluster] = []
            self.clusters[cluster].append(code)

        # Build programmes index from descriptors
        self.extract_programmes()

        print(f"Loaded {len(self.descriptors)} modules")
        print(f"Found {len(self.clusters)} clusters")
        print(f"Found {len(self.programmes)} programmes")

    def extract_programmes(self):
        """Extract programme information from module descriptors (Science & Computing only)"""
        from collections import defaultdict, Counter

        # First pass: determine primary school and department for each programme
        prog_school_counts = defaultdict(Counter)  # prog_code -> {school: count}
        prog_dept_counts = defaultdict(Counter)  # prog_code -> {department: count}
        prog_module_counts = defaultdict(int)  # prog_code -> total module count

        for module_code, descriptor in self.descriptors.items():
            school = descriptor.get('school', 'Unknown')
            department = descriptor.get('department', 'Unknown')
            if 'programmes' in descriptor and descriptor['programmes']:
                for prog in descriptor['programmes']:
                    if prog and 'code' in prog and prog.get('semester'):
                        prog_school_counts[prog['code']][school] += 1
                        prog_dept_counts[prog['code']][department] += 1
                        prog_module_counts[prog['code']] += 1

        # Identify Science & Computing programmes (where it's the primary school AND has >= 3 modules)
        science_computing_programmes = {}  # prog_code -> primary_department
        for prog_code, school_counts in prog_school_counts.items():
            primary_school = school_counts.most_common(1)[0][0]
            module_count = prog_module_counts[prog_code]
            if primary_school == 'Science and Computing' and module_count >= 3:
                primary_dept = prog_dept_counts[prog_code].most_common(1)[0][0]
                science_computing_programmes[prog_code] = primary_dept

        # Second pass: extract only Science & Computing programmes
        programmes_data = {}  # prog_code -> {name, semesters, department}

        for module_code, descriptor in self.descriptors.items():
            if 'programmes' in descriptor and descriptor['programmes']:
                for prog in descriptor['programmes']:
                    if prog and 'code' in prog:
                        prog_code = prog['code']

                        # Skip programmes not in Science & Computing
                        if prog_code not in science_computing_programmes:
                            continue

                        prog_name = prog['name']
                        semester = prog.get('semester', 0)
                        status = prog.get('status', '')

                        # Initialize programme if not seen
                        if prog_code not in programmes_data:
                            programmes_data[prog_code] = {
                                'name': prog_name,
                                'department': science_computing_programmes[prog_code],
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
        """Clean the output directory"""
        if self.output_dir.exists():
            # Keep these files
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

        # Create course.md
        course_md = self.output_dir / "course.md"
        if not course_md.exists():
            with open(course_md, 'w') as f:
                f.write("# SETU Science Module Catalogue\n\n")
                f.write("This site contains a complete catalogue of approved modules across all of SETU's science programmes.\n\n")
                f.write(f"**{len(self.descriptors)} modules** organized into **{len(self.clusters)} subject clusters**.\n")
            print("  Created course.md")
        else:
            print("  course.md already exists")

        # Create root topic.md
        root_topic = self.output_dir / "topic.md"
        with open(root_topic, 'w') as f:
            f.write("# SETU Science Modules\n\n")
            f.write("Browse all modules alphabetically or by subject cluster.\n")
        print("  Created topic.md")

        # Create properties.yaml
        props = self.output_dir / "properties.yaml"
        if not props.exists():
            with open(props, 'w') as f:
                f.write("credits: SETU Faculty\n")
                f.write("parent: #\n")
                f.write("pdfOrientation: portrait\n")
                f.write("llm: 2\n")
            print("  Created properties.yaml")
        else:
            print("  properties.yaml already exists")

    def sanitize_filename(self, text: str) -> str:
        """Convert text to safe filename"""
        # Replace spaces with underscores
        text = text.replace(' ', '_')
        # Remove special characters except dash and underscore
        text = re.sub(r'[^\w\-]', '', text)
        return text

    def convert_latex_to_markdown(self, text: str) -> str:
        """Convert LaTeX formatting to markdown"""
        if not text:
            return text

        # Replace \emph{...} with *...*
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

    def generate_clusters(self):
        """Generate cluster-based folder structure inside topic-02-clusters"""
        print("\nGenerating cluster view...")

        # Create clusters container directory
        clusters_container = self.output_dir / "topic-02-clusters"
        clusters_container.mkdir(exist_ok=True)

        # Create clusters topic.md with icon
        with open(clusters_container / "topic.md", 'w') as f:
            f.write("---\n")
            f.write("icon:\n")
            f.write("  type: mdi:view-grid\n")
            f.write("  color: 5E35B1\n")
            f.write("---\n\n")
            f.write("# All Modules by Cluster\n\n")
            f.write("Browse modules organized by subject cluster.\n")

        # Sort clusters alphabetically
        sorted_clusters = sorted(self.clusters.items(), key=lambda x: x[0])

        for idx, (cluster_name, module_codes) in enumerate(sorted_clusters, 1):
            cluster_dir_name = self.sanitize_filename(cluster_name)
            cluster_dir = clusters_container / f"topic-{idx:02d}-{cluster_dir_name}"
            cluster_dir.mkdir(exist_ok=True)

            # Create cluster topic.md with icon
            with open(cluster_dir / "topic.md", 'w') as f:
                # Add icon frontmatter if cluster icon exists
                if cluster_name in self.cluster_icons:
                    cluster_icon = self.cluster_icons[cluster_name]
                    f.write("---\n")
                    f.write("icon:\n")
                    f.write(f"  type: {cluster_icon.get('type', 'carbon:sys-provision')}\n")
                    f.write(f"  color: {cluster_icon.get('color', '014771')}\n")
                    f.write("---\n\n")
                f.write(f"# {cluster_name}\n\n\n")

            # Sort modules in cluster alphabetically by module name
            module_with_names = []
            for module_code in module_codes:
                descriptor = self.descriptors.get(module_code)
                if descriptor:
                    name = descriptor.get('full_title', module_code)
                    module_with_names.append((module_code, name))

            # Sort by name
            sorted_modules = [code for code, name in sorted(module_with_names, key=lambda x: x[1])]

            for mod_idx, module_code in enumerate(sorted_modules, 1):
                descriptor = self.descriptors.get(module_code)

                if not descriptor:
                    continue

                module_name = self.sanitize_filename(descriptor.get('full_title', module_code))
                note_dir_name = f"note-{mod_idx:02d}-note-{mod_idx:02d}-{module_name}"
                note_dir = cluster_dir / note_dir_name
                note_dir.mkdir(exist_ok=True)

                # Store the path mapping for weburl generation
                relative_path = f"/note/{self.tutors_course_id}/topic-02-clusters/topic-{idx:02d}-{cluster_dir_name}/{note_dir_name}"
                self.module_to_cluster_path[module_code] = relative_path

                # Create archives directory
                archives_dir = note_dir / "archives"
                archives_dir.mkdir(exist_ok=True)

                # Copy PDF if exists
                pdf_source = self.source_dir / "descriptors" / "pdf" / f"{descriptor.get('reference', module_code)}.pdf"
                # Try alternate naming pattern
                if not pdf_source.exists():
                    # Try with full filename from directory
                    yaml_file = self.source_dir / "descriptors" / "yaml" / f"{descriptor.get('reference', module_code)}.yaml"
                    pdf_name = yaml_file.stem.replace('.yaml', '.pdf')
                    for pdf_file in (self.source_dir / "descriptors" / "pdf").glob(f"{module_code}*.pdf"):
                        pdf_source = pdf_file
                        break

                if pdf_source.exists():
                    shutil.copy(pdf_source, archives_dir / f"{module_code}.pdf")

                # Generate note.md (pass cluster_name for icon inheritance)
                markdown = self.generate_module_markdown(module_code, cluster_name)
                with open(note_dir / "note.md", 'w') as f:
                    f.write(markdown)

        print(f"Generated {len(sorted_clusters)} clusters with modules")

    def generate_all_modules(self):
        """Generate alphabetical all-modules view with web links to cluster notes"""
        print("\nGenerating all modules view...")

        # Create all-modules container directory
        all_modules_dir = self.output_dir / "topic-03-all-modules"
        all_modules_dir.mkdir(exist_ok=True)

        # Create all-modules topic.md with icon
        with open(all_modules_dir / "topic.md", 'w') as f:
            f.write("---\n")
            f.write("icon:\n")
            f.write("  type: mdi:sort-alphabetical-ascending\n")
            f.write("  color: 1976D2\n")
            f.write("---\n\n")
            f.write("# All Modules\n\n")
            f.write("All modules listed alphabetically.\n")

        # Collect all modules with their titles for sorting
        all_modules = []
        for module_code, descriptor in self.descriptors.items():
            full_title = descriptor.get('full_title', module_code)
            all_modules.append((module_code, full_title, descriptor))

        # Sort alphabetically by title
        all_modules.sort(key=lambda x: x[1])

        # Generate web objects for each module
        for idx, (module_code, full_title, descriptor) in enumerate(all_modules, 1):
            module_name = self.sanitize_filename(full_title)
            web_dir = all_modules_dir / f"web-{idx:03d}-web-{idx:03d}-{module_name}"
            web_dir.mkdir(exist_ok=True)

            # Get cluster name for icon
            cluster_name = descriptor.get('cluster', 'Uncategorized')

            # Get icon (using same priority as modules)
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

            # Create link.md with icon, title, and first sentence
            short_title = descriptor.get('short_title', full_title)
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
            cluster_path = self.module_to_cluster_path.get(module_code, "#")
            with open(web_dir / "weburl", 'w') as f:
                f.write(cluster_path)

        print(f"Generated {len(all_modules)} module web links")

    def generate_programmes(self):
        """Generate programmes view with semesters and web links to cluster notes"""
        print("\nGenerating programmes view...")

        # Create programmes container directory
        programmes_container = self.output_dir / "topic-01-programmes"
        programmes_container.mkdir(exist_ok=True)

        # Create programmes topic.md with icon
        with open(programmes_container / "topic.md", 'w') as f:
            f.write("---\n")
            f.write("icon:\n")
            f.write("  type: mdi:school\n")
            f.write("  color: 2E7D32\n")
            f.write("---\n\n")
            f.write("# Programmes\n\n")
            f.write("Browse modules by programme and semester.\n")

        # Group programmes by department
        science_programmes = {}
        computing_programmes = {}

        for prog_code, prog_data in self.programmes.items():
            dept = prog_data.get('department', 'Unknown')
            if dept == 'Computing and Mathematics':
                computing_programmes[prog_code] = prog_data
            else:
                # All other departments go into Science unit
                science_programmes[prog_code] = prog_data

        # Create Unit 1: Science Department Programmes
        self._generate_programme_unit(
            programmes_container,
            unit_num=1,
            unit_name="Science Department Programmes",
            programmes=science_programmes,
            icon_type="mdi:flask",
            icon_color="00897B"
        )

        # Create Unit 2: Computing and Mathematics Department Programmes
        self._generate_programme_unit(
            programmes_container,
            unit_num=2,
            unit_name="Computing and Mathematics Department Programmes",
            programmes=computing_programmes,
            icon_type="mdi:laptop",
            icon_color="1976D2"
        )

        total_progs = len(science_programmes) + len(computing_programmes)
        print(f"Generated {total_progs} programmes ({len(science_programmes)} Science, {len(computing_programmes)} Computing & Maths)")

    def _generate_programme_unit(self, container_dir, unit_num, unit_name, programmes, icon_type, icon_color):
        """Helper method to generate a unit containing programmes"""
        # Create unit directory
        unit_dir = container_dir / f"unit-{unit_num}"
        unit_dir.mkdir(exist_ok=True)

        # Create unit topic.md
        with open(unit_dir / "topic.md", 'w') as f:
            f.write("---\n")
            f.write("icon:\n")
            f.write(f"  type: {icon_type}\n")
            f.write(f"  color: {icon_color}\n")
            f.write("---\n\n")
            f.write(f"# {unit_name}\n\n")
            f.write(f"{len(programmes)} programmes\n")

        # Sort programmes alphabetically by name
        sorted_programmes = sorted(programmes.items(), key=lambda x: x[1]['name'])

        for idx, (prog_code, prog_data) in enumerate(sorted_programmes):
            prog_name = prog_data['name']
            semesters = prog_data['semesters']

            # Create programme directory
            prog_dir = unit_dir / f"topic-{idx:02d}-{prog_code}"
            prog_dir.mkdir(exist_ok=True)

            # Create programme topic.md with icon
            # Get icon from programme-icons.yaml or use default
            icon_info = self.programme_icons.get(prog_code)
            if icon_info:
                icon_type = icon_info.get('type', 'mdi:book-education')
                icon_color = icon_info.get('color', '455A64')
            else:
                icon_type = 'mdi:book-education'
                icon_color = '455A64'

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

                # Create web objects for each module in semester
                for mod_idx, module_info in enumerate(semester_modules, 1):
                    module_code = module_info['code']
                    descriptor = module_info['descriptor']
                    status = module_info['status']

                    # Get module details
                    short_title = descriptor.get('short_title', descriptor.get('full_title', module_code))
                    full_title = descriptor.get('full_title', module_code)
                    module_name = self.sanitize_filename(full_title)

                    # Create web object directory
                    web_dir = semester_unit_dir / f"web-{mod_idx:02d}-web-{mod_idx:02d}-{module_name}"
                    web_dir.mkdir(exist_ok=True)

                    # Get cluster for icon
                    cluster_name = descriptor.get('cluster', 'Uncategorized')

                    # Get icon (same priority as all-modules)
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

                    # Create link.md with icon, title, and first sentence
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
                    cluster_path = self.module_to_cluster_path.get(module_code, "#")
                    with open(web_dir / "weburl", 'w') as f:
                        f.write(cluster_path)

    def generate(self):
        """Main generation process"""
        print("=" * 60)
        print("SETU Science Module Catalogue Generator - Master")
        print("=" * 60)

        # Load all data
        self.load_data()

        # Create course files first
        self.create_course_files()

        # Clean output (preserve certain files)
        print("\nCleaning output directory...")
        self.clean_output()

        # Generate structures (clusters first to build path mapping, then programmes, then all-modules)
        self.generate_clusters()
        self.generate_programmes()
        self.generate_all_modules()

        print("\n" + "=" * 60)
        print("Generation complete!")
        print("=" * 60)
        print(f"\nOutput directory: {self.output_dir}")
        print(f"- All Modules (alphabetical): {len(self.descriptors)}")
        print(f"- Clusters: {len(self.clusters)}")
        print(f"- Programmes: {len(self.programmes)}")
        print(f"- Total module notes: {len(self.descriptors)}")


if __name__ == "__main__":
    import sys
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "tutors-modules-master"
    generator = MasterCatalogueGenerator(output_dir=output_dir)
    generator.generate()
