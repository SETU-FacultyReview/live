#!/usr/bin/env python3
"""
SETU Science Module Catalogue Generator - All Science Faculties

Top-level script that generates three separate Tutors courses from the
SETU Science Faculty Module Catalogue:
1. tutors-science-faculty: Combined course with both departments
2. tutors-science-dept: Science department only
3. tutors-computing-maths-dept: Computing & Mathematics department only

Usage:
    python3 generate-all-science.py
"""

from pathlib import Path
from models import Catalogue, Department, TutorsCatalogue


def main():
    """
    Main entry point for course generation.

    Creates Catalogue and Department objects, then generates three separate
    Tutors courses with different department combinations.
    """
    # Determine directories
    tutors_generator_dir = Path(__file__).parent  # tutors-generator/
    data_dir = tutors_generator_dir.parent         # repo root (live/)

    print("=" * 60)
    print("SETU Science Module Catalogue Generator")
    print("Generating 3 Tutors Courses")
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

    # Course 1: Science Faculty (both departments combined)
    print("\n" + "=" * 60)
    print("COURSE 1: Science Faculty (Combined)")
    print("=" * 60)

    faculty_departments = [
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

    faculty_generator = TutorsCatalogue(
        catalogue=catalogue,
        departments=faculty_departments,
        data_dir=data_dir,
        tutors_generator_dir=tutors_generator_dir,
        output_dir=data_dir / "tutors-science-faculty",
        tutors_course_id="setu-science-faculty",
        course_title="SETU Science Faculty",
        course_description="Complete catalogue of approved modules for the Science Faculty, organized by department.",
        llm_notebook_url="https://notebooklm.google.com/notebook/cb07f2c3-dda5-4f44-8de2-8cc884d7590f"
    )
    faculty_generator.generate_tutors_course()

    # Course 2: Science Department only
    print("\n" + "=" * 60)
    print("COURSE 2: Science Department Only")
    print("=" * 60)

    science_departments = [
        {
            'department': science_dept,
            'icon_type': 'mdi:flask',
            'icon_color': '00897B'
        }
    ]

    science_generator = TutorsCatalogue(
        catalogue=catalogue,
        departments=science_departments,
        data_dir=data_dir,
        tutors_generator_dir=tutors_generator_dir,
        output_dir=data_dir / "tutors-science-dept",
        tutors_course_id="setu-science-dept",
        course_title="SETU Science Department",
        course_description="Complete catalogue of approved modules for the Science Department.",
        llm_notebook_url="https://notebooklm.google.com/notebook/cb07f2c3-dda5-4f44-8de2-8cc884d7590f"
    )
    science_generator.generate_tutors_course()

    # Course 3: Computing & Mathematics Department only
    print("\n" + "=" * 60)
    print("COURSE 3: Computing & Mathematics Department Only")
    print("=" * 60)

    computing_departments = [
        {
            'department': computing_dept,
            'icon_type': 'mdi:laptop',
            'icon_color': '1976D2'
        }
    ]

    computing_generator = TutorsCatalogue(
        catalogue=catalogue,
        departments=computing_departments,
        data_dir=data_dir,
        tutors_generator_dir=tutors_generator_dir,
        output_dir=data_dir / "tutors-computing-maths-dept",
        tutors_course_id="setu-computing-maths-dept",
        course_title="SETU Computing & Maths Department",
        course_description="Complete catalogue of approved modules for the Computing & Mathematics Department.",
        llm_notebook_url="https://notebooklm.google.com/notebook/fc382e1b-fbc0-4f98-a0c3-20656d5a869a"
    )
    computing_generator.generate_tutors_course()

    # Final summary
    print("\n" + "=" * 60)
    print("ALL COURSES GENERATED SUCCESSFULLY")
    print("=" * 60)
    print(f"\n1. Science Faculty: {data_dir / 'tutors-science-faculty'}")
    print(f"2. Science Dept:    {data_dir / 'tutors-science-dept'}")
    print(f"3. Computing Dept:  {data_dir / 'tutors-computing-maths-dept'}")
    print()


if __name__ == "__main__":
    main()
