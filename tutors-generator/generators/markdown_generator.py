"""
MarkdownGenerator - Responsible for generating markdown content.

This class handles the generation of markdown content for module descriptors
and other catalogue entities.
"""

import sys
from pathlib import Path
from typing import Optional
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import convert_latex_to_markdown, extract_first_sentence, format_module_status
from icons import get_icon_for_item, create_icon_frontmatter


class MarkdownGenerator:
    """
    Generates markdown content for catalogue entities.

    This class is responsible for converting catalogue data (module descriptors, etc.)
    into formatted markdown suitable for Tutors content.
    """

    def __init__(self, module_icons: dict, cluster_icons: dict):
        """
        Initialize the markdown generator.

        Args:
            module_icons: Dictionary of module-specific icon mappings
            cluster_icons: Dictionary of cluster icon mappings
        """
        self.module_icons = module_icons
        self.cluster_icons = cluster_icons

    def generate_module_descriptor(
        self,
        module_code: str,
        descriptor: dict,
        cluster_name: Optional[str] = None,
        programme_to_topic_path: Optional[dict] = None,
        cluster_to_topic_path: Optional[dict] = None
    ) -> str:
        """
        Generate markdown content for a module from its descriptor.

        Args:
            module_code: The module code (e.g., "A12345")
            descriptor: Module descriptor dictionary
            cluster_name: Optional cluster name for icon fallback
            programme_to_topic_path: Optional dict mapping programme codes to topic weburl paths
            cluster_to_topic_path: Optional dict mapping cluster names to topic weburl paths

        Returns:
            Complete markdown content for the module
        """
        if not descriptor:
            return f"# {module_code}\n\nModule data not available."

        md = []

        # Get icon with fallback priority: module-specific -> cluster -> default
        icon_type, icon_color = get_icon_for_item(
            module_code,
            self.module_icons,
            cluster_name=cluster_name,
            cluster_icons=self.cluster_icons
        )

        # Add icon frontmatter
        frontmatter = create_icon_frontmatter(icon_type, icon_color)
        md.append(frontmatter.rstrip())  # Remove trailing newline as we control spacing
        md.append(f"# {descriptor.get('short_title', descriptor.get('full_title', module_code))}")
        md.append("")

        # Aim - extract first sentence only for the summary
        if 'aim' in descriptor:
            aim_text = descriptor['aim']
            first_sentence = extract_first_sentence(aim_text)
            md.append(first_sentence)
        md.append("")
        md.append(f'<p><a href="./archives/{module_code}.pdf" target="_blank" rel="noopener noreferrer" style="display: inline-flex; align-items: center; text-decoration: none;"><img src="https://upload.wikimedia.org/wikipedia/commons/6/60/Adobe_Acrobat_Reader_icon_%282020%29.svg" width="20" height="20" style="margin-right: 4px;" alt="Adobe Acrobat Icon"><span>Module Descriptor (PDF)</span></a></p>')
        md.append("")

        # Module information table
        md.append("## Module Information")
        md.append("")
        md.append("| **Field** | **Details** |")
        md.append("|-----------|-------------|")
        # Get cluster name and create link if available
        cluster = descriptor.get('cluster', 'N/A')
        if cluster_to_topic_path and cluster in cluster_to_topic_path:
            cluster_link = f"[{cluster}]({cluster_to_topic_path[cluster]})"
        else:
            cluster_link = cluster

        md.append(f"| **Module Code** | {module_code} |")
        md.append(f"| **Module Title** | {descriptor.get('full_title', 'N/A')} |")
        md.append(f"| **Short Title** | {descriptor.get('short_title', 'N/A')} |")
        md.append(f"| **Credits** | {descriptor.get('credits', 'N/A')} ECTS |")
        md.append(f"| **Level** | {descriptor.get('level', 'N/A')} |")
        md.append(f"| **School** | {descriptor.get('school', 'N/A')} |")
        md.append(f"| **Department** | {descriptor.get('department', 'N/A')} |")
        md.append(f"| **Module Author** | {descriptor.get('author', 'N/A')} |")
        md.append(f"| **Cluster** | {cluster_link} |")
        md.append("")
        md.append("---")
        md.append("")

        # Module aim
        if 'aim' in descriptor:
            md.append("## Module Aim")
            md.append("")
            md.append(convert_latex_to_markdown(descriptor['aim']))
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
                md.append(f"{i}. {convert_latex_to_markdown(outcome)}")
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
                md.append(f"- {convert_latex_to_markdown(topic)}")
            md.append("")
            md.append("---")
            md.append("")

        # Learning and teaching methods
        if 'learning_and_teaching_methods' in descriptor:
            md.append("## Learning and Teaching Methods")
            md.append("")
            for method in descriptor['learning_and_teaching_methods']:
                md.append(convert_latex_to_markdown(method))
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
                criterion_text = convert_latex_to_markdown(criterion)
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
                md.append(f"- {convert_latex_to_markdown(material)}")
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
                md.append(f"- {convert_latex_to_markdown(material)}")
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
                    status = format_module_status(prog_info.get('status', ''))

                    # Create links for programme code and title if path available
                    if programme_to_topic_path and prog_code in programme_to_topic_path:
                        prog_url = programme_to_topic_path[prog_code]
                        prog_code_link = f"[{prog_code}]({prog_url})"
                        prog_title_link = f"[{prog_title}]({prog_url})"
                    else:
                        prog_code_link = prog_code
                        prog_title_link = prog_title

                    md.append(f"| {prog_code_link} | {prog_title_link} | {stage} | {semester} | {status} |")

            md.append("")
            md.append("---")
            md.append("")

        # Resources required
        if 'requested_resources' in descriptor:
            md.append("## Resources Required")
            md.append("")
            for resource in descriptor['requested_resources']:
                md.append(f"- {convert_latex_to_markdown(resource)}")
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
