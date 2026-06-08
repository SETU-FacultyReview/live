#!/usr/bin/env python3
"""
Convert programmes.csv to programmes.yaml

Groups programmes by department and level according to the following rules:
- Level 6: programme title contains "certificate" or "cert"
- Level 7: programme title has Bachelor, BSc, BA but not (H) or (Hons)
- Level 8: programme title has Bachelor with (H)/(Hons), or Diploma/HDip/Higher Diploma
- Level 9: programme title has MSc, Master, Postgrad
- Level 10: programme title has PhD
- Other: programme has "Independent", "Socrates", or doesn't match above
"""

import csv
import yaml
from pathlib import Path
from collections import defaultdict


def categorize_level(title: str) -> str:
    """
    Categorize programme level based on title.

    Args:
        title: Programme title

    Returns:
        Level category as string
    """
    title_lower = title.lower()

    # Level 10: PhD (check first)
    if 'phd' in title_lower:
        return 'level_10'

    # Level 6: Certificate (including Higher Certificate) - check early
    if 'certificate' in title_lower or 'cert' in title_lower:
        return 'level_6'

    # Level 8: ALL Diplomas (Diploma, Dip, HDip, Higher Diploma, Postgrad Diploma, PG Diploma)
    # Check before Level 9 to ensure all diplomas are Level 8
    # Use word boundary check for 'dip' to avoid matching words like "diplom"
    if 'diploma' in title_lower or 'hdip' in title_lower or ' dip ' in title_lower or title_lower.startswith('dip '):
        return 'level_8'

    # Level 9: MSc, Master (excluding anything with Diploma which is already caught above)
    if 'msc' in title_lower or 'masters' in title_lower or 'master of' in title_lower:
        return 'level_9'

    # Level 8: Honours Bachelor degrees
    if ('(h)' in title_lower or '(hons)' in title_lower or 'honours' in title_lower) and \
       ('bachelor' in title_lower or 'bsc' in title_lower or 'ba ' in title_lower):
        return 'level_8'

    # Level 7: Non-honours Bachelor degrees
    if ('bachelor' in title_lower or 'bsc' in title_lower or 'ba ' in title_lower):
        return 'level_7'

    # Other: Independent, Socrates, or unmatched
    if 'independent' in title_lower or 'socrates' in title_lower:
        return 'other'

    # Default to other if no match
    return 'other'


def main():
    """Main conversion function."""
    # Paths (script is now in data directory)
    data_dir = Path(__file__).parent
    input_csv = data_dir / "programmes.csv"
    output_yaml = data_dir / "programmes.yaml"

    if not input_csv.exists():
        print(f"Error: {input_csv} not found")
        return

    # Data structure: departments -> levels -> programmes
    departments = defaultdict(lambda: defaultdict(list))

    # Read CSV and categorize
    with open(input_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get('code'):
                continue

            dept = row.get('department', 'Unknown')
            title = row.get('title', '')
            code = row.get('code', '')
            category = row.get('category', '')
            faculty = row.get('faculty', '')

            level = categorize_level(title)

            programme_data = {
                'code': code,
                'title': title,
                'category': category,
                'faculty': faculty
            }

            departments[dept][level].append(programme_data)

    # Convert to regular dicts for YAML output with custom level ordering
    # Order: level_6, level_7, level_8, level_9, level_10, other
    level_order = {'level_6': 1, 'level_7': 2, 'level_8': 3, 'level_9': 4, 'level_10': 5, 'other': 6}

    output_data = {'departments': {}}
    for dept, levels in sorted(departments.items()):
        output_data['departments'][dept] = {}
        # Sort levels by custom order
        for level in sorted(levels.keys(), key=lambda x: level_order.get(x, 99)):
            programmes = levels[level]
            output_data['departments'][dept][level] = sorted(programmes, key=lambda p: p['title'])

    # Write YAML
    with open(output_yaml, 'w', encoding='utf-8') as f:
        yaml.dump(output_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    # Print summary
    print(f"✓ Converted {input_csv.name} to {output_yaml.name}")
    print(f"\nSummary:")
    total_programmes = 0
    for dept, levels in sorted(departments.items()):
        dept_total = sum(len(progs) for progs in levels.values())
        total_programmes += dept_total
        print(f"  {dept}: {dept_total} programmes")
        for level, programmes in sorted(levels.items()):
            print(f"    - {level}: {len(programmes)} programmes")
    print(f"\nTotal: {total_programmes} programmes")


if __name__ == "__main__":
    main()
