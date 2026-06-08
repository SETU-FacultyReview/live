"""
DepartmentGenerator - Generates Tutors content for a department.

This class is responsible for generating all Tutors topics and content
for a department (clusters, programmes, all-modules).
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Dict
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import (
    sanitize_filename,
    convert_latex_to_markdown,
    extract_first_sentence,
    get_tutors_weburl_path
)
from icons import (
    get_icon_for_item,
    create_icon_frontmatter
)
from generators.markdown_generator import MarkdownGenerator
from generators.programme_schedule import ProgrammeSchedule


class DepartmentGenerator:
    """
    Generates Tutors course content for a department.

    This class takes a Department object and generates all the Tutors topics
    (clusters, programmes, all-modules) according to the Tutors format.
    """

    def __init__(
        self,
        department,
        source_dir: Path,
        module_icons: dict,
        cluster_icons: dict,
        programme_icons: dict,
        catalogue_icons: dict,
        tutors_course_id: str
    ):
        """
        Initialize the department generator.

        Args:
            department: Department object containing filtered data
            source_dir: Path to source directory (for finding PDFs)
            module_icons: Dictionary of module icon mappings
            cluster_icons: Dictionary of cluster icon mappings
            programme_icons: Dictionary of programme icon mappings
            catalogue_icons: Dictionary of catalogue topic icon mappings
            tutors_course_id: Tutors course ID for weburl generation
        """
        self.department = department
        self.source_dir = source_dir
        self.module_icons = module_icons
        self.cluster_icons = cluster_icons
        self.programme_icons = programme_icons
        self.catalogue_icons = catalogue_icons
        self.tutors_course_id = tutors_course_id

        # Create markdown generator
        self.markdown_generator = MarkdownGenerator(
            module_icons=module_icons,
            cluster_icons=cluster_icons
        )

    def generate_clusters(self, output_dir: Path, programme_to_topic_path: dict = None) -> tuple:
        """
        Generate clusters topic containing all clusters + module descriptors + PDFs.

        This matches the current implementation's cluster generation behavior.

        Args:
            output_dir: Directory where clusters topic should be created
            programme_to_topic_path: Optional dict mapping programme codes to topic weburl paths

        Returns:
            Tuple of (module_to_cluster_path dict, cluster_to_topic_path dict)
        """
        clusters_dir = output_dir / "topic-02-clusters"
        clusters_dir.mkdir(exist_ok=True)

        # Create clusters topic.md
        clusters_icon = self.catalogue_icons.get('clusters', {})
        icon_type = clusters_icon.get('type', 'mdi:view-grid')
        icon_color = clusters_icon.get('color', '5E35B1')

        with open(clusters_dir / "topic.md", 'w') as f:
            f.write(create_icon_frontmatter(icon_type, icon_color))
            f.write("# Clusters\n\n")
            f.write(f"{len(self.department.clusters)} subject clusters\n")

        module_to_cluster_path = {}
        cluster_to_topic_path = {}

        # Sort clusters alphabetically
        sorted_clusters = sorted(self.department.clusters.items(), key=lambda x: x[0])

        for idx, (cluster_name, module_codes) in enumerate(sorted_clusters, 1):
            cluster_dir_name = sanitize_filename(cluster_name)
            cluster_dir = clusters_dir / f"topic-{idx:02d}-{cluster_dir_name}"
            cluster_dir.mkdir(exist_ok=True)

            # Create cluster topic.md with icon
            with open(cluster_dir / "topic.md", 'w') as f:
                if cluster_name in self.cluster_icons:
                    icon_type, icon_color = get_icon_for_item(
                        cluster_name,
                        self.cluster_icons
                    )
                    f.write(create_icon_frontmatter(icon_type, icon_color))
                f.write(f"# {cluster_name}\n\n\n")

            # Build cluster topic path
            cluster_topic_path = get_tutors_weburl_path(
                self.tutors_course_id,
                output_dir.name,
                "topic-02-clusters",
                f"topic-{idx:02d}-{cluster_dir_name}"
            )
            cluster_to_topic_path[cluster_name] = cluster_topic_path

            # Sort modules alphabetically by full title
            module_with_names = []
            for module_code in module_codes:
                descriptor = self.department.modules.get(module_code)
                if descriptor:
                    name = descriptor.get('full_title', module_code)
                    module_with_names.append((module_code, name))

            sorted_modules = [code for code, name in sorted(module_with_names, key=lambda x: x[1])]

            # Generate each module's note
            for mod_idx, module_code in enumerate(sorted_modules, 1):
                descriptor = self.department.modules.get(module_code)
                if not descriptor:
                    continue

                module_name = sanitize_filename(descriptor.get('full_title', module_code))
                note_dir_name = f"note-{mod_idx:02d}-note-{mod_idx:02d}-{module_name}"
                note_dir = cluster_dir / note_dir_name
                note_dir.mkdir(exist_ok=True)

                # Store the weburl path for this module
                cluster_path = get_tutors_weburl_path(
                    self.tutors_course_id,
                    output_dir.name,
                    "topic-02-clusters",
                    f"topic-{idx:02d}-{cluster_dir_name}",
                    note_dir_name
                )
                module_to_cluster_path[module_code] = cluster_path

                # Create archives directory and copy PDF
                archives_dir = note_dir / "archives"
                archives_dir.mkdir(exist_ok=True)

                self._copy_module_pdf(module_code, descriptor, archives_dir)

                # Generate module markdown using MarkdownGenerator
                markdown_content = self.markdown_generator.generate_module_descriptor(
                    module_code=module_code,
                    descriptor=descriptor,
                    cluster_name=cluster_name,
                    programme_to_topic_path=programme_to_topic_path,
                    cluster_to_topic_path=cluster_to_topic_path
                )

                # Write note.md
                with open(note_dir / "note.md", 'w') as f:
                    f.write(markdown_content)

        print(f"    Generated {len(self.department.clusters)} clusters with {len(module_to_cluster_path)} modules")
        return module_to_cluster_path, cluster_to_topic_path

    def generate_all_modules(self, output_dir: Path, module_to_cluster_path: dict):
        """
        Generate all modules topic sorted alphabetically.

        This matches the current implementation's all-modules generation behavior.

        Args:
            output_dir: Directory where all-modules topic should be created
            module_to_cluster_path: Mapping of module codes to weburl paths
        """
        all_modules_dir = output_dir / "topic-03-all-modules"
        all_modules_dir.mkdir(exist_ok=True)

        # Create all-modules topic.md
        all_modules_icon = self.catalogue_icons.get('all-modules', {})
        icon_type = all_modules_icon.get('type', 'mdi:sort-alphabetical-ascending')
        icon_color = all_modules_icon.get('color', '1976D2')

        with open(all_modules_dir / "topic.md", 'w') as f:
            f.write(create_icon_frontmatter(icon_type, icon_color))
            f.write("# All Modules\n\n")
            f.write(f"{len(self.department.modules)} modules listed alphabetically\n")

        # Sort modules alphabetically by full title
        sorted_modules = sorted(
            self.department.modules.items(),
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

        print(f"    Generated {len(self.department.modules)} module web links")

    def generate_programmes(self, output_dir: Path, module_to_cluster_path: dict) -> dict:
        """
        Generate programmes organized by level (6, 7, 8, 9, 10).

        Creates a unit for each level containing programmes at that level.

        Args:
            output_dir: Directory where programmes topic should be created
            module_to_cluster_path: Mapping of module codes to weburl paths

        Returns:
            Dictionary mapping programme_code -> weburl topic path
        """
        programmes_dir = output_dir / "topic-01-programmes"
        programmes_dir.mkdir(exist_ok=True)

        # Create programmes topic.md
        programmes_icon = self.catalogue_icons.get('programmes', {})
        icon_type = programmes_icon.get('type', 'mdi:school')
        icon_color = programmes_icon.get('color', '2E7D32')

        with open(programmes_dir / "topic.md", 'w') as f:
            f.write(create_icon_frontmatter(icon_type, icon_color))
            f.write("# Programmes\n\n")
            f.write(f"{len(self.department.programmes)} programmes organized by level\n")

        # Dictionary to store programme code -> topic weburl path
        programme_to_topic_path = {}

        # Group programmes by level
        programmes_by_level = self._group_programmes_by_level()

        # Generate units for each level (6 to 10)
        level_order = ['level_6', 'level_7', 'level_8', 'level_9', 'level_10']
        level_names = {
            'level_6': 'Level 6',
            'level_7': 'Level 7',
            'level_8': 'Level 8',
            'level_9': 'Level 9',
            'level_10': 'Level 10'
        }

        for unit_num, level_key in enumerate(level_order, 1):
            if level_key not in programmes_by_level or not programmes_by_level[level_key]:
                continue  # Skip levels with no programmes

            level_programme_paths = self._generate_level_unit(
                programmes_dir,
                unit_num,
                level_key,
                level_names[level_key],
                programmes_by_level[level_key],
                module_to_cluster_path
            )
            # Merge the paths from this level
            programme_to_topic_path.update(level_programme_paths)

        print(f"    Generated {len(self.department.programmes)} programmes across {len(programmes_by_level)} levels")
        return programme_to_topic_path

    def _group_programmes_by_level(self) -> dict:
        """
        Group programmes by their level.

        Returns:
            Dictionary mapping level keys to lists of (prog_code, prog_data) tuples
        """
        from collections import defaultdict
        programmes_by_level = defaultdict(list)

        for prog_code, prog_data in self.department.programmes.items():
            # Get level from catalogue registry
            if prog_code in self.department.catalogue.programme_registry:
                level = self.department.catalogue.programme_registry[prog_code].get('level', 'other')
                programmes_by_level[level].append((prog_code, prog_data))

        return programmes_by_level

    def _generate_level_unit(
        self,
        programmes_dir: Path,
        unit_num: int,
        level_key: str,
        level_name: str,
        programmes: list,
        module_to_cluster_path: dict
    ) -> dict:
        """
        Generate a unit for a specific level containing its programmes.

        Args:
            programmes_dir: Parent programmes directory
            unit_num: Unit number
            level_key: Level key (e.g., 'level_6')
            level_name: Display name (e.g., 'Level 6')
            programmes: List of (prog_code, prog_data) tuples for this level
            module_to_cluster_path: Mapping of module codes to weburl paths

        Returns:
            Dictionary mapping programme_code -> weburl topic path for this level
        """
        # Create level unit directory
        level_unit_dir = programmes_dir / f"unit-{unit_num:02d}-{level_key}"
        level_unit_dir.mkdir(exist_ok=True)

        # Create level unit topic.md
        with open(level_unit_dir / "topic.md", 'w') as f:
            f.write(f"# {level_name}\n\n")
            f.write(f"{len(programmes)} programmes at {level_name}\n")

        # Dictionary to store programme paths for this level
        programme_paths = {}

        # Sort programmes alphabetically by name
        sorted_programmes = sorted(programmes, key=lambda x: x[1]['name'])

        # Generate topics for each programme in this level
        for idx, (prog_code, prog_data) in enumerate(sorted_programmes, 1):
            prog_name = prog_data['name']
            semesters = prog_data['semesters']

            # Create programme directory within this level unit
            prog_dir = level_unit_dir / f"topic-{idx:02d}-{prog_code}"
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

            # Generate programme schedule panelnote
            schedule_generator = ProgrammeSchedule(self.department, prog_code, module_to_cluster_path)
            schedule_generator.generate_schedule(prog_dir)

            # Build weburl path for this programme
            from utils import get_tutors_weburl_path
            # programmes_dir parent is the output_dir (department unit)
            department_unit_name = programmes_dir.parent.name
            prog_topic_path = get_tutors_weburl_path(
                self.tutors_course_id,
                department_unit_name,
                "topic-01-programmes",
                f"unit-{unit_num:02d}-{level_key}",
                f"topic-{idx:02d}-{prog_code}"
            )
            programme_paths[prog_code] = prog_topic_path

            # Create semester units
            for semester_num in sorted(semesters.keys()):
                semester_modules = semesters[semester_num]

                # Create semester unit directory
                semester_unit_dir = prog_dir / f"unit-{semester_num}"
                semester_unit_dir.mkdir(exist_ok=True)

                # Create semester topic.md
                # Semester 0 = "Any Semester"
                semester_label = "Any Semester" if semester_num == 0 else f"Semester {semester_num}"

                with open(semester_unit_dir / "topic.md", 'w') as f:
                    f.write(f"# {semester_label}\n\n")
                    f.write(f"{len(semester_modules)} modules\n")

                # Create web objects for each module
                for mod_idx, module_info in enumerate(semester_modules, 1):
                    module_code = module_info['code']
                    descriptor = module_info['descriptor']

                    # Skip if not in this department's modules
                    if module_code not in self.department.modules:
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

        return programme_paths

    def _copy_module_pdf(self, module_code: str, descriptor: dict, archives_dir: Path):
        """
        Copy module PDF to archives directory.

        Args:
            module_code: The module code
            descriptor: Module descriptor
            archives_dir: Directory to copy PDF to
        """
        pdf_dir = self.source_dir / "Descriptors" / "pdf"
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

        if pdf_source and pdf_source.exists():
            shutil.copy(pdf_source, archives_dir / f"{module_code}.pdf")
        else:
            print(f"      Warning: PDF not found for {module_code}")
