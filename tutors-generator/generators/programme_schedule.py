"""
ProgrammeSchedule - Generates programme schedule tables.

This class creates a programme schedule note showing modules
organized by semester in a table format.
"""

import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))


class ProgrammeSchedule:
    """
    Generates a programme schedule table for a specific programme.

    The schedule shows modules organized by semester with credits and
    mandatory/elective status.
    """

    def __init__(self, department, programme_code: str, module_to_cluster_path: dict,
                 icon_type: str = None, icon_color: str = None):
        """
        Initialize the programme schedule generator.

        Args:
            department: Department object containing programme data
            programme_code: The programme code (e.g., 'WD_KACCM_B')
            module_to_cluster_path: Dictionary mapping module codes to weburl paths
            icon_type: Optional icon type for the schedule note
            icon_color: Optional icon color for the schedule note
        """
        self.department = department
        self.programme_code = programme_code
        self.module_to_cluster_path = module_to_cluster_path
        self.icon_type = icon_type
        self.icon_color = icon_color

        # Get programme data
        if programme_code not in department.programmes:
            raise ValueError(f"Programme {programme_code} not found in department")

        self.programme_data = department.programmes[programme_code]

    def generate_schedule(self, output_dir: Path):
        """
        Generate the programme schedule note.

        Creates a unit-0 directory containing a note-00-schedule note
        with note.md containing a heading and a markdown table showing
        modules by semester.

        Args:
            output_dir: Directory where the schedule should be created
        """
        # Create unit-0 directory
        unit_0_dir = output_dir / "unit-0"
        unit_0_dir.mkdir(exist_ok=True)

        # Create unit-0 topic.md
        with open(unit_0_dir / "topic.md", 'w') as f:
            f.write("# Programme Schedule\n")

        # Create schedule note directory inside unit-0
        schedule_note_dir = unit_0_dir / "note-00-schedule"
        schedule_note_dir.mkdir(exist_ok=True)

        # Organize modules by semester
        modules_by_semester = self._organize_modules_by_semester()

        # Generate the markdown table
        table_content = self._generate_markdown_table(modules_by_semester)

        # Write note.md with icon frontmatter, heading, "Modules by semester", and table
        with open(schedule_note_dir / "note.md", 'w') as f:
            # Add icon frontmatter if icon is provided
            if self.icon_type and self.icon_color:
                from icons import create_icon_frontmatter
                f.write(create_icon_frontmatter(self.icon_type, self.icon_color))

            f.write("# Programme Schedule\n\n")
            f.write("Modules by semester\n\n")
            f.write(table_content)

    def _organize_modules_by_semester(self) -> dict:
        """
        Organize modules by semester.

        Modules are sorted within each semester with mandatory modules first,
        followed by elective modules.

        Returns:
            Dictionary mapping semester number to list of module info dicts
        """
        modules_by_semester = defaultdict(list)

        for semester_num, modules in self.programme_data['semesters'].items():
            for module_info in modules:
                module_code = module_info['code']
                descriptor = module_info['descriptor']
                status = module_info['status']

                # Get module details
                short_title = descriptor.get('short_title', descriptor.get('full_title', module_code))
                # Normalize credits to string (can be int or str in YAML)
                credits_raw = descriptor.get('credits', 5)
                credits = str(credits_raw)

                # Determine status label (M or E)
                status_label = 'M' if status in ['M', 'C'] else 'E'

                # Get cluster name for grouping
                cluster_name = descriptor.get('cluster', 'Uncategorized')

                modules_by_semester[semester_num].append({
                    'title': short_title,
                    'credits': credits,
                    'status': status_label,
                    'code': module_code,
                    'cluster': cluster_name
                })

        # Sort modules within each semester:
        # - Mandatory: alphabetically by title
        # - Elective: by cluster first, then alphabetically by title within cluster
        for semester_num in modules_by_semester:
            modules_by_semester[semester_num].sort(
                key=lambda m: (
                    0 if m['status'] == 'M' else 1,  # Mandatory first
                    m['cluster'] if m['status'] == 'E' else '',  # Group electives by cluster
                    m['title']  # Then alphabetically by title
                )
            )

        return modules_by_semester

    def _generate_markdown_table(self, modules_by_semester: dict) -> str:
        """
        Generate markdown table from modules organized by semester.

        New format: Each semester gets 3 columns (Module | Credits | Status)
        directly adjacent to each other with no separator columns.

        Rows are organized with all mandatory modules first (across all semesters),
        followed by all elective modules on new rows below.

        Args:
            modules_by_semester: Dictionary mapping semester to module list

        Returns:
            Markdown table string
        """
        if not modules_by_semester:
            return "*No modules scheduled*\n"

        # Get sorted list of semesters (convert to int for proper numeric sorting)
        semesters = sorted(modules_by_semester.keys(), key=lambda x: int(x) if str(x).isdigit() else 0)

        # Separate mandatory and elective modules for each semester
        mandatory_by_semester = {}
        elective_by_semester = {}

        for sem in semesters:
            mandatory_by_semester[sem] = [m for m in modules_by_semester[sem] if m['status'] == 'M']
            elective_by_semester[sem] = [m for m in modules_by_semester[sem] if m['status'] == 'E']

        # Find max rows needed for mandatory and elective sections
        max_mandatory = max((len(mandatory_by_semester[sem]) for sem in semesters), default=0)
        max_elective = max((len(elective_by_semester[sem]) for sem in semesters), default=0)

        # Build table
        lines = []

        # Header row - each semester gets 3 columns
        header_parts = []
        for sem in semesters:
            if sem == 0:
                semester_label = "Any Semester"
            else:
                semester_label = f"Semester {sem}"

            header_parts.append(semester_label)
            header_parts.append("")  # Credits column (no header)
            header_parts.append("")  # Status column (no header)

        header = "| " + " | ".join(header_parts) + " |"
        lines.append(header)

        # Separator row
        separator_parts = []
        for sem in semesters:
            separator_parts.extend(["-" * 17, "-" * 3, "-" * 3])

        separator = "| " + " | ".join(separator_parts) + " |"
        lines.append(separator)

        # Mandatory module rows
        for row_idx in range(max_mandatory):
            row_parts = []
            for sem in semesters:
                modules = mandatory_by_semester[sem]
                if row_idx < len(modules):
                    mod = modules[row_idx]
                    # Create markdown link if weburl path exists
                    module_code = mod['code']
                    if module_code in self.module_to_cluster_path:
                        weburl = self.module_to_cluster_path[module_code]
                        module_title = f"[{mod['title']}]({weburl})"
                    else:
                        module_title = mod['title']

                    row_parts.append(module_title)
                    row_parts.append(str(mod['credits']))
                    row_parts.append(mod['status'])
                else:
                    row_parts.extend(["", "", ""])  # Empty cells

            row = "| " + " | ".join(row_parts) + " |"
            lines.append(row)

        # Elective module rows (below mandatory rows)
        for row_idx in range(max_elective):
            row_parts = []
            for sem in semesters:
                modules = elective_by_semester[sem]
                if row_idx < len(modules):
                    mod = modules[row_idx]
                    # Create markdown link if weburl path exists
                    module_code = mod['code']
                    if module_code in self.module_to_cluster_path:
                        weburl = self.module_to_cluster_path[module_code]
                        module_title = f"[{mod['title']}]({weburl})"
                    else:
                        module_title = mod['title']

                    row_parts.append(module_title)
                    row_parts.append(str(mod['credits']))
                    row_parts.append(mod['status'])
                else:
                    row_parts.extend(["", "", ""])  # Empty cells

            row = "| " + " | ".join(row_parts) + " |"
            lines.append(row)

        return "\n".join(lines) + "\n"
