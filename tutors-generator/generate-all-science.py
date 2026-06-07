#!/usr/bin/env python3
"""
SETU Science Module Catalogue Generator - All Science Faculties

Top-level script that generates a complete Tutors course from the
SETU Science Faculty Module Catalogue.

This script creates the Catalogue and Department objects, then passes them
to TutorsCatalogue for generation of the tutors-modules-by-dept course structure.

Usage:
    python3 generate-all-science.py
"""

from pathlib import Path
from models import Catalogue, Department, TutorsCatalogue


def main():
    """
    Main entry point for course generation.

    Creates Catalogue and Department objects, then uses TutorsCatalogue
    to generate the complete Tutors course structure.
    """
    # Determine directories
    tutors_generator_dir = Path(__file__).parent  # tutors-generator/
    data_dir = tutors_generator_dir.parent         # repo root (live/)

    print("=" * 60)
    print("SETU Science Module Catalogue Generator - By Department")
    print("=" * 60)
    print()

    # Create catalogue (loads all data once)
    print("Loading catalogue data...")
    catalogue = Catalogue(source_dir=data_dir)
    print(f"  {catalogue.get_summary()}")
    print()

    # Create departments
    print("Creating departments...")
    computing_dept = Department(
        name="Computing and Mathematics Department",
        filter_criteria=["Computing and Mathematics"],
        catalogue=catalogue
    )
    print(f"  Computing: {computing_dept.get_summary()}")

    science_dept = Department(
        name="Science Department",
        filter_criteria=["Science", "Land Sciences"],
        catalogue=catalogue
    )
    print(f"  Science: {science_dept.get_summary()}")
    print()

    # Create list of departments with their icons
    departments = [
        {
            'department': computing_dept,
            'icon_type': 'mdi:laptop',
            'icon_color': '1976D2'
        },
        {
            'department': science_dept,
            'icon_type': 'mdi:flask',
            'icon_color': '00897B'
        }
    ]

    # Create course generator with the catalogue and departments
    course_generator = TutorsCatalogue(
        catalogue=catalogue,
        departments=departments,
        data_dir=data_dir,
        tutors_generator_dir=tutors_generator_dir
    )

    # Generate the complete Tutors course
    course_generator.generate_tutors_course()


if __name__ == "__main__":
    main()
