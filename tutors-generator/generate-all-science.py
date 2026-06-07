#!/usr/bin/env python3
"""
SETU Science Module Catalogue Generator - All Science Faculties

Top-level script that generates a complete Tutors course from the
SETU Science Faculty Module Catalogue.

This script creates a GenerateTutorsCourse object and invokes its
generate_tutors_course() method to produce the tutors-modules-by-dept
course structure.

Usage:
    python3 generate-all-science.py
"""

from pathlib import Path
from generate_tutors_course import GenerateTutorsCourse


def main():
    """
    Main entry point for course generation.

    Creates a GenerateTutorsCourse instance and generates the complete
    Tutors course structure.
    """
    # Create course generator
    # Uses default paths (parent dir for source, ../tutors-modules-by-dept for output)
    course_generator = GenerateTutorsCourse()

    # Generate the complete Tutors course
    course_generator.generate_tutors_course()


if __name__ == "__main__":
    main()
