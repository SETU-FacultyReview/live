"""
GenerateTutorsCourse - Orchestrates generation of the complete Tutors course.

This class creates a Catalogue, creates Department objects, and uses
DepartmentGenerator to produce a complete Tutors course matching the
current tutors-modules-by-dept structure.
"""

import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

from models import Catalogue, Department
from generators import DepartmentGenerator
from icons import create_icon_frontmatter


# Load environment variables
load_dotenv()


class GenerateTutorsCourse:
    """
    Orchestrates the generation of a complete Tutors course.

    This class coordinates the creation of all components needed to generate
    a Tutors course from the SETU Science Faculty Module Catalogue.
    """

    def __init__(self, source_dir: Path = None, output_dir: Path = None):
        """
        Initialize the course generator.

        This creates the Catalogue and Department objects needed for generation.

        Args:
            source_dir: Path to source directory (defaults to parent of script)
            output_dir: Path to output directory (defaults to ../tutors-modules-by-dept)
        """
        # Set paths
        if source_dir is None:
            source_dir = Path(__file__).parent.parent
        if output_dir is None:
            output_dir = source_dir / "tutors-modules-by-dept"

        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)

        # Load Tutors course ID from environment
        self.tutors_course_id = os.getenv('TUTORS_COURSE_ID', 'setu-science-modules')

        print("=" * 60)
        print("SETU Science Module Catalogue Generator - By Department")
        print("=" * 60)
        print()

        # Create catalogue (loads all data once)
        print("Loading catalogue data...")
        self.catalogue = Catalogue(source_dir=self.source_dir)
        print(f"  {self.catalogue.get_summary()}")
        print()

        # Create departments
        print("Creating departments...")
        self.computing = Department(
            name="Computing and Mathematics Department",
            filter_criteria=["Computing and Mathematics"],
            catalogue=self.catalogue
        )
        print(f"  Computing: {self.computing.get_summary()}")

        self.science = Department(
            name="Science Department",
            filter_criteria=["Science", "Land Sciences"],
            catalogue=self.catalogue
        )
        print(f"  Science: {self.science.get_summary()}")
        print()

    def generate_tutors_course(self):
        """
        Generate the complete Tutors course.

        This creates a course structure matching the current tutors-modules-by-dept
        implementation, with two units (Computing and Science).
        """
        # Create course files
        self._create_course_files()

        # Clean output directory (except course files we just created)
        self._clean_output()

        # Generate Unit 1: Computing and Mathematics
        self._generate_department_unit(
            unit_num=1,
            department=self.computing,
            icon_type="mdi:laptop",
            icon_color="1976D2"
        )

        # Generate Unit 2: Science Department
        self._generate_department_unit(
            unit_num=2,
            department=self.science,
            icon_type="mdi:flask",
            icon_color="00897B"
        )

        # Print completion message
        print()
        print("=" * 60)
        print("Generation complete!")
        print("=" * 60)
        print(f"\nOutput directory: {self.output_dir}")
        print(f"- Unit 1: Computing and Mathematics Department")
        print(f"- Unit 2: Science Department")

    def _generate_department_unit(
        self,
        unit_num: int,
        department: Department,
        icon_type: str,
        icon_color: str
    ):
        """
        Generate a complete department unit.

        Args:
            unit_num: Unit number (1 for Computing, 2 for Science)
            department: Department object
            icon_type: Icon type for unit
            icon_color: Icon color for unit
        """
        print(f"\nGenerating Unit {unit_num}: {department.name}...")

        # Create unit directory
        unit_dir = self.output_dir / f"unit-{unit_num}"
        unit_dir.mkdir(exist_ok=True)

        # Create unit topic.md
        with open(unit_dir / "topic.md", 'w') as f:
            f.write(create_icon_frontmatter(icon_type, icon_color))
            f.write(f"# {department.name}\n\n")
            f.write("Browse programmes, clusters, and modules.\n")

        print(f"  {department.get_summary()}")

        # Create department generator
        dept_gen = DepartmentGenerator(
            department=department,
            source_dir=self.source_dir,
            module_icons=self.catalogue.module_icons,
            cluster_icons=self.catalogue.cluster_icons,
            programme_icons=self.catalogue.programme_icons,
            tutors_course_id=self.tutors_course_id
        )

        # Generate content (clusters first to build path mapping)
        module_to_cluster_path = dept_gen.generate_clusters(unit_dir)
        dept_gen.generate_programmes(unit_dir, module_to_cluster_path)
        dept_gen.generate_all_modules(unit_dir, module_to_cluster_path)

    def _create_course_files(self):
        """Create required course files (course.md, properties.yaml, course.png)"""
        print("Setting up course files...")

        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Get script directory for source files
        script_dir = Path(__file__).parent
        tutors_files_dir = script_dir / "tutors-files"

        # Copy course.md
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

        # Copy properties.yaml
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

        # Copy course.png
        source_png = tutors_files_dir / "course.png"
        dest_png = self.output_dir / "course.png"
        if source_png.exists():
            shutil.copy(source_png, dest_png)
            print("  Copied course.png")
        else:
            print("  Warning: course.png not found in tutors-files directory")

        print()

    def _clean_output(self):
        """Clean the output directory (preserving course files that were just created)"""
        if self.output_dir.exists():
            keep_files = ['properties.yaml', 'course.md', 'course.png', 'topic.md']

            for item in self.output_dir.iterdir():
                if item.name not in keep_files:
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
