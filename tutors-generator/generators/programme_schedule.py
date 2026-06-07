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

    def __init__(self, department, programme_code: str):
        """
        Initialize the programme schedule generator.

        Args:
            department: Department object containing programme data
            programme_code: The programme code (e.g., 'WD_KACCM_B')
        """
        self.department = department
        self.programme_code = programme_code

        # Get programme data
        if programme_code not in department.programmes:
            raise ValueError(f"Programme {programme_code} not found in department")

        self.programme_data = department.programmes[programme_code]

    def generate_schedule(self, output_dir: Path):
        """
        Generate the programme schedule panelnote.

        Creates a panelnote with a markdown table showing modules by semester.

        Args:
            output_dir: Directory where the panelnote should be created
        """
        # Create panelnote directory
        panelnote_dir = output_dir / "panelnote-00-schedule"
        panelnote_dir.mkdir(exist_ok=True)

        # Organize modules by semester
        modules_by_semester = self._organize_modules_by_semester()

        # Generate the markdown table
        markdown_content = self._generate_markdown_table(modules_by_semester)

        # Write panelnote.md
        with open(panelnote_dir / "panelnote.md", 'w') as f:
            f.write(f"# Programme Schedule\n\n")
            f.write(f"**{self.programme_data['name']}**\n\n")
            f.write(markdown_content)

    def _organize_modules_by_semester(self) -> dict:
        """
        Organize modules by semester.

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
                    'status': status_label
                })

        return modules_by_semester

    def _generate_markdown_table(self, modules_by_semester: dict) -> str:
        """
        Generate markdown table from modules organized by semester.

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

        # Header row
        semester_labels = []
        for sem in semesters:
            if sem == 0:
                semester_labels.append("Any Semester")
            else:
                semester_labels.append(f"Semester {sem}")

        header = "| " + " | ".join(semester_labels) + " |"
        lines.append(header)

        # Separator row
        separator = "|" + "|".join(["----------" for _ in semesters]) + "|"
        lines.append(separator)

        # Data rows
        for row_idx in range(max_modules):
            row_cells = []
            for sem in semesters:
                modules = modules_by_semester[sem]
                if row_idx < len(modules):
                    mod = modules[row_idx]
                    cell = f"{mod['title']} ({mod['credits']}) {mod['status']}"
                    row_cells.append(cell)
                else:
                    row_cells.append("")  # Empty cell

            row = "| " + " | ".join(row_cells) + " |"
            lines.append(row)

        return "\n".join(lines) + "\n"
