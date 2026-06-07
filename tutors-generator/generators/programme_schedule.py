"""
ProgrammeSchedule - Generates programme schedule tables.

This class creates a programme schedule panelnote showing modules
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

    def __init__(self, department, programme_code: str, module_to_cluster_path: dict):
        """
        Initialize the programme schedule generator.

        Args:
            department: Department object containing programme data
            programme_code: The programme code (e.g., 'WD_KACCM_B')
            module_to_cluster_path: Dictionary mapping module codes to weburl paths
        """
        self.department = department
        self.programme_code = programme_code
        self.module_to_cluster_path = module_to_cluster_path

        # Get programme data
        if programme_code not in department.programmes:
            raise ValueError(f"Programme {programme_code} not found in department")

        self.programme_data = department.programmes[programme_code]

    def generate_schedule(self, output_dir: Path):
        """
        Generate the programme schedule panelnote.

        Creates a unit with a topic.md "Programme Schedule" containing
        a panelnote with a markdown table showing modules by semester.

        Args:
            output_dir: Directory where the schedule unit should be created
        """
        # Create schedule unit directory
        schedule_unit_dir = output_dir / "unit-00-schedule"
        schedule_unit_dir.mkdir(exist_ok=True)

        # Create unit topic.md
        with open(schedule_unit_dir / "topic.md", 'w') as f:
            f.write("# Programme Schedule\n")

        # Create panelnote directory inside the unit
        panelnote_dir = schedule_unit_dir / "panelnote-00-schedule"
        panelnote_dir.mkdir(exist_ok=True)

        # Organize modules by semester
        modules_by_semester = self._organize_modules_by_semester()

        # Generate the markdown table
        markdown_content = self._generate_markdown_table(modules_by_semester)

        # Write panelnote.md (just the table, no headers)
        with open(panelnote_dir / "panelnote.md", 'w') as f:
            f.write(markdown_content)

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
                credits = descriptor.get('credits', 5)

                # Determine status label (M or E)
                status_label = 'M' if status in ['M', 'C'] else 'E'

                modules_by_semester[semester_num].append({
                    'title': short_title,
                    'credits': credits,
                    'status': status_label,
                    'code': module_code
                })

        # Sort modules within each semester: Mandatory first, then Elective
        for semester_num in modules_by_semester:
            modules_by_semester[semester_num].sort(
                key=lambda m: (0 if m['status'] == 'M' else 1, m['title'])
            )

        return modules_by_semester

    def _generate_markdown_table(self, modules_by_semester: dict) -> str:
        """
        Generate markdown table from modules organized by semester.

        New format: Each semester gets 3 columns (Module | Credits | Status)
        directly adjacent to each other with no separator columns.

        Args:
            modules_by_semester: Dictionary mapping semester to module list

        Returns:
            Markdown table string
        """
        if not modules_by_semester:
            return "*No modules scheduled*\n"

        # Get sorted list of semesters
        semesters = sorted(modules_by_semester.keys())

        # Find maximum number of modules in any semester (for rows)
        max_modules = max(len(modules_by_semester[sem]) for sem in semesters)

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

        # Data rows
        for row_idx in range(max_modules):
            row_parts = []
            for sem in semesters:
                modules = modules_by_semester[sem]
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
