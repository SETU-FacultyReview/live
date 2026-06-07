"""
Models package - Data structures for the catalogue system.

This package contains classes for loading and filtering catalogue data,
as well as the main TutorsCatalogue orchestrator.
"""

from .catalogue import Catalogue
from .department import Department
from .tutors_catalogue import TutorsCatalogue

__all__ = ['Catalogue', 'Department', 'TutorsCatalogue']
