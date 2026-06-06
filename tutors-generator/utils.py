"""
Utility functions for SETU catalogue generators.

This module contains general-purpose functions that can be used by different
catalogue generators, regardless of how they organize the content.
"""

import re
import yaml
from pathlib import Path
from typing import Dict, Optional


# ============================================================================
# Text Processing Utilities
# ============================================================================

def sanitize_filename(text: str) -> str:
    """
    Convert text to a safe filename format.

    Args:
        text: The text to sanitize

    Returns:
        Sanitized filename string (spaces to underscores, special chars removed)
    """
    text = text.replace(' ', '_')
    text = re.sub(r'[^\w\-]', '', text)
    return text


def convert_latex_to_markdown(text: str) -> str:
    """
    Convert LaTeX formatting to markdown.

    Currently handles:
    - \\emph{text} -> *text*

    Args:
        text: Text with LaTeX formatting

    Returns:
        Text with markdown formatting
    """
    if not text:
        return text
    text = re.sub(r'\\emph\{([^}]+)\}', r'*\1*', text)
    return text


def extract_first_sentence(text: str) -> str:
    """
    Extract the first sentence from a text block.

    Handles edge cases like abbreviations (e.g., "B.Sc.", "Dr.").

    Args:
        text: The text to extract from

    Returns:
        First sentence with proper punctuation
    """
    if not text:
        return ""

    # Look for sentence boundary (period followed by space and capital letter)
    # This regex avoids breaking on abbreviations like "B.Sc." or "Dr."
    match = re.search(r'(?<![A-Z]\d)\.(?:\s+[A-Z]|[A-Z](?=[a-z]))', text)

    if match:
        first_sentence = text[:match.start() + 1].strip()
    else:
        first_sentence = text.strip()
        if not first_sentence.endswith('.'):
            first_sentence += '.'

    return first_sentence


# ============================================================================
# File Loading Utilities
# ============================================================================

def load_yaml_file(file_path: Path, default: Optional[dict] = None) -> dict:
    """
    Load a YAML file safely with error handling.

    Args:
        file_path: Path to the YAML file
        default: Default value to return if file doesn't exist or is empty

    Returns:
        Loaded YAML data as dictionary, or default value
    """
    if default is None:
        default = {}

    if not file_path.exists():
        return default

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data if data is not None else default
    except yaml.YAMLError as e:
        print(f"Warning: Error loading {file_path}: {e}")
        return default


# Note: Icon-related functions moved to icons.py module
# - load_icon_mappings()
# - get_icon_for_item()
# - create_icon_frontmatter()


# ============================================================================
# Path Utilities
# ============================================================================

def get_tutors_weburl_path(course_id: str, *path_parts: str) -> str:
    """
    Generate a Tutors weburl path.

    Args:
        course_id: The Tutors course identifier
        *path_parts: Path components (e.g., 'unit-1', 'topic-02-clusters', 'note-01-...')

    Returns:
        Full weburl path for Tutors (e.g., '/note/course-id/unit-1/topic-02/note-01')
    """
    # Determine the type from the last path component
    last_part = path_parts[-1] if path_parts else ""

    if last_part.startswith('note-'):
        url_type = 'note'
    elif last_part.startswith('topic-'):
        url_type = 'topic'
    elif last_part.startswith('talk-'):
        url_type = 'talk'
    elif last_part.startswith('lab-'):
        url_type = 'lab'
    else:
        url_type = 'topic'  # default

    # Build the path
    path = '/'.join([course_id] + list(path_parts))
    return f"/{url_type}/{path}"


# ============================================================================
# String Formatting Utilities
# ============================================================================

def format_module_status(status: str) -> str:
    """
    Format module status for display.

    Args:
        status: Status code (e.g., 'M', 'E')

    Returns:
        Full status name (e.g., 'Mandatory', 'Elective')
    """
    status_map = {
        'M': 'Mandatory',
        'E': 'Elective',
        'C': 'Core',
        'O': 'Optional'
    }
    return status_map.get(status, status)


def format_learning_outcomes_list(outcomes: list, start_num: int = 1) -> str:
    """
    Format learning outcomes as a numbered markdown list.

    Args:
        outcomes: List of learning outcome strings
        start_num: Starting number for the list

    Returns:
        Formatted markdown string
    """
    if not outcomes:
        return ""

    lines = []
    for i, outcome in enumerate(outcomes, start_num):
        lines.append(f"{i}. {convert_latex_to_markdown(outcome)}")

    return '\n'.join(lines)
