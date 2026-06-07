"""
Generators package - Content generation for Tutors courses.

This package contains classes for generating Tutors content from catalogue data.
"""

from .markdown_generator import MarkdownGenerator
from .department_generator import DepartmentGenerator
from .programme_schedule import ProgrammeSchedule

__all__ = ['MarkdownGenerator', 'DepartmentGenerator', 'ProgrammeSchedule']
