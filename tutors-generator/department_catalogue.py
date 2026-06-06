"""
Department catalogue data structure.

This module contains the DepartmentCatalogue class which encapsulates all the data
(modules, clusters, programmes) for a single academic department, along with
methods for generating the department's Tutors content.
"""

import shutil
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

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
from markdown import generate_module_markdown


class DepartmentCatalogue:
    """
    Encapsulates modules, clusters, and programmes for a single department.

    This class filters and organizes the complete catalogue data for one department,
    making it easier to generate department-specific views.
    """

    def __init__(
        self,
        name: str,
        filter_criteria: List[str],
        all_descriptors: dict,
        all_programmes: dict,
        all_clusters: dict,
        module_icons: dict,
        cluster_icons: dict,
        programme_icons: dict,
        source_dir: Path,
        tutors_course_id: str
    ):
        """
        Initialize a department catalogue.

        Args:
            name: Display name of the department (e.g., "Computing and Mathematics Department")
            filter_criteria: List of department names to include (e.g., ["Computing and Mathematics"])
                            Allows including multiple departments (e.g., Science + Land Sciences)
            all_descriptors: Dictionary of all module descriptors (module_code -> descriptor)
            all_programmes: Dictionary of all programmes (prog_code -> prog_data)
            all_clusters: Dictionary of all clusters (cluster_name -> [module_codes])
            module_icons: Dictionary of module icon mappings
            cluster_icons: Dictionary of cluster icon mappings
            programme_icons: Dictionary of programme icon mappings
            source_dir: Path to source directory (for finding PDFs)
            tutors_course_id: Tutors course ID for URL generation
        """
        self.name = name
        self.filter_criteria = filter_criteria if isinstance(filter_criteria, list) else [filter_criteria]

        # Filter data for this department
        self.descriptors = self._filter_descriptors(all_descriptors)
        self.programmes = self._filter_programmes(all_programmes)
        self.clusters = self._filter_clusters(all_clusters)

        # Icon mappings
        self.module_icons = module_icons
        self.cluster_icons = cluster_icons
        self.programme_icons = programme_icons

        # Configuration
        self.source_dir = source_dir
        self.tutors_course_id = tutors_course_id

    def _filter_descriptors(self, all_descriptors: dict) -> dict:
        """
        Filter module descriptors for this department.

        Args:
            all_descriptors: All module descriptors

        Returns:
            Dictionary of descriptors for this department only
        """
        # Use the first filter criterion as the primary department
        # (In most cases there's only one, except Science which includes Land Sciences)
        primary_dept = self.filter_criteria[0]

        return {
            code: desc for code, desc in all_descriptors.items()
            if desc.get('department') == primary_dept
        }

    def _filter_programmes(self, all_programmes: dict) -> dict:
        """
        Filter programmes for this department.

        Handles special case where a department can include programmes from multiple
        registry departments (e.g., Science unit includes both Science and Land Sciences).

        Args:
            all_programmes: All programmes data

        Returns:
            Dictionary of programmes for this department
        """
        return {
            code: prog for code, prog in all_programmes.items()
            if prog['department'] in self.filter_criteria
        }

    def _filter_clusters(self, all_clusters: dict) -> dict:
        """
        Filter clusters for this department.

        Only includes clusters that have at least one module from this department.

        Args:
            all_clusters: All cluster data (cluster_name -> [module_codes])

        Returns:
            Dictionary of clusters for this department with filtered module lists
        """
        dept_clusters = {}

        for cluster_name, module_codes in all_clusters.items():
            # Filter modules to only those in this department
            dept_modules = [code for code in module_codes if code in self.descriptors]

            # Only include cluster if it has modules from this department
            if dept_modules:
                dept_clusters[cluster_name] = dept_modules

        return dept_clusters

    def get_module_count(self) -> int:
        """Get the number of modules in this department."""
        return len(self.descriptors)

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
        """String representation of the department catalogue."""
        return (f"DepartmentCatalogue(name='{self.name}', "
                f"modules={self.get_module_count()}, "
                f"programmes={self.get_programme_count()}, "
                f"clusters={self.get_cluster_count()})")

    # ============================================================================
    # Generation Methods
    # ============================================================================

    def generate_unit(self, unit_dir: Path, icon_type: str, icon_color: str):
        """
        Generate the complete department unit content.

        Args:
            unit_dir: Directory for this unit
            icon_type: Icon type for the unit (e.g., "mdi:laptop")
            icon_color: Icon color for the unit (e.g., "1976D2")
        """
        # Create unit directory
        unit_dir.mkdir(exist_ok=True)

        # Create unit topic.md
        with open(unit_dir / "topic.md", 'w') as f:
            f.write(create_icon_frontmatter(icon_type, icon_color))
            f.write(f"# {self.name}\n\n")
            f.write("Browse programmes, clusters, and modules.\n")

        print(f"  {self.get_summary()}")

        # Generate the three topics (clusters first to build path mapping)
        module_to_cluster_path = self._generate_clusters_topic(unit_dir)
        self._generate_programmes_topic(unit_dir, module_to_cluster_path)
        self._generate_all_modules_topic(unit_dir, module_to_cluster_path)

    def _generate_programmes_topic(self, unit_dir: Path, module_to_cluster_path: dict):
        """Generate programmes topic for this department"""
        programmes_dir = unit_dir / "topic-01-programmes"
        programmes_dir.mkdir(exist_ok=True)

        # Create programmes topic.md
        with open(programmes_dir / "topic.md", 'w') as f:
            f.write(create_icon_frontmatter("mdi:school", "2E7D32"))
            f.write("# Programmes\n\n")
            f.write(f"{len(self.programmes)} programmes\n")

        # Sort programmes alphabetically
        sorted_programmes = sorted(self.programmes.items(), key=lambda x: x[1]['name'])

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
                    if module_code not in self.descriptors:
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

        print(f"    Generated {len(self.programmes)} programmes")

    def _generate_clusters_topic(self, unit_dir: Path) -> dict:
        """Generate clusters topic for this department and return module-to-path mapping"""
        clusters_dir = unit_dir / "topic-02-clusters"
        clusters_dir.mkdir(exist_ok=True)

        # Create clusters topic.md
        with open(clusters_dir / "topic.md", 'w') as f:
            f.write(create_icon_frontmatter("mdi:view-grid", "5E35B1"))
            f.write("# Clusters\n\n")
            f.write(f"{len(self.clusters)} subject clusters\n")

        module_to_cluster_path = {}

        # Sort clusters alphabetically
        sorted_clusters = sorted(self.clusters.items(), key=lambda x: x[0])

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
                descriptor = self.descriptors.get(module_code)
                if descriptor:
                    name = descriptor.get('full_title', module_code)
                    module_with_names.append((module_code, name))

            sorted_modules = [code for code, name in sorted(module_with_names, key=lambda x: x[1])]

            for mod_idx, module_code in enumerate(sorted_modules, 1):
                descriptor = self.descriptors.get(module_code)
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

        print(f"    Generated {len(self.clusters)} clusters with {len(module_to_cluster_path)} modules")
        return module_to_cluster_path

    def _generate_all_modules_topic(self, unit_dir: Path, module_to_cluster_path: dict):
        """Generate all-modules topic for this department"""
        all_modules_dir = unit_dir / "topic-03-all-modules"
        all_modules_dir.mkdir(exist_ok=True)

        # Create all-modules topic.md
        with open(all_modules_dir / "topic.md", 'w') as f:
            f.write(create_icon_frontmatter("mdi:sort-alphabetical-ascending", "1976D2"))
            f.write("# All Modules\n\n")
            f.write(f"{len(self.descriptors)} modules listed alphabetically\n")

        # Sort modules alphabetically by full title
        sorted_modules = sorted(
            self.descriptors.items(),
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

        print(f"    Generated {len(self.descriptors)} module web links")

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
