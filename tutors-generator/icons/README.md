# Icons Package

Icon management system for the SETU Science Module Catalogue.

## Overview

This package provides icon utilities and mappings for all visual elements in the generated Tutors course. All icons are sourced from [Iconify](https://icon-sets.iconify.design/), primarily using Material Design Icons (mdi).

## Icon Files

### YAML Configuration Files

| File | Purpose | Count | Example |
|------|---------|-------|---------|
| `catalogue-icons.yaml` | Main topic icons (Programmes, Clusters, All Modules) | 3 | `programmes: {type: mdi:school, color: '2E7D32'}` |
| `cluster-icons.yaml` | Subject cluster icons | 37 | `Biology: {type: mdi:dna, color: '00897B'}` |
| `programme-icons.yaml` | Academic programme icons | 86 | `WD_KACCM_B: {type: mdi:laptop, color: '1976D2'}` |
| `module-icons.yaml` | Module-specific icon overrides | 0 | *Empty - modules inherit cluster icons* |

### Python Modules

- **`icon_utils.py`** - Core icon utilities
  - `load_icon_mappings()` - Load icons from YAML files
  - `get_icon_for_item()` - Retrieve icon with fallback logic
  - `create_icon_frontmatter()` - Generate Tutors YAML frontmatter

- **`__init__.py`** - Package initialization, exports public API

### Documentation

- **`CLUSTER_ICONS.md`** - Detailed cluster icon reference with rationale
- **`CLUSTER_ICONS_VISUAL.md`** - Visual reference grouped by theme

## Icon Inheritance

Icons are applied using a priority system:

```
Module Icon Priority:
1. module-icons.yaml (specific module override)
2. cluster-icons.yaml (cluster default)
3. Fallback: carbon:sys-provision

Programme Icon Priority:
1. programme-icons.yaml (programme code)
2. Fallback: mdi:book-education

Catalogue Topic Icons:
- catalogue-icons.yaml (fixed topics)
```

## Usage Example

```python
from icons import get_icon_for_item, create_icon_frontmatter

# Get icon for a module (with cluster fallback)
icon_type, icon_color = get_icon_for_item(
    'A12345',                    # module code
    module_icons,                # module-specific icons
    cluster_name='Biology',      # fallback cluster
    cluster_icons=cluster_icons  # cluster icon mappings
)

# Generate frontmatter
frontmatter = create_icon_frontmatter(icon_type, icon_color)
# Output:
# ---
# icon:
#   type: mdi:dna
#   color: 00897B
# ---
```

## Icon Selection Guidelines

### Cluster Icons
- Scientific symbols for Science clusters (DNA, flasks, molecules)
- Recognizable symbols that communicate subject matter
- Unique icon for each cluster (no duplicates)
- Colors from Material Design palette

### Programme Icons
- Academic/educational theme (books, graduation, school)
- Meaningful representation of programme type
- Consistent color families by discipline

### Catalogue Icons
- Clear navigation purpose (grid for clusters, A→Z for alphabetical)
- High contrast colors for visibility
- Aligned with Tutors theme colors

## Color Palette

Colors selected from Material Design palette, compatible with [tutors.css theme](https://github.com/tutors-sdk/tutors/blob/development/src/lib/services/themes/styles/tutors.css):

- **Blues**: Technology, Computing, IT (#1976D2, #0277BD, #283593)
- **Greens**: Agriculture, Environment (#689F38, #66BB6A, #2E7D32)
- **Teals**: Biology, Pharmaceutical (#00897B, #00ACC1)
- **Oranges**: Chemistry, Engineering (#E64A19, #F57C00)
- **Purples**: Science, Creative (#5E35B1, #7B1FA2)

## Statistics

- **Total clusters**: 37 (100% icon coverage)
- **Total programmes**: 86 (100% icon coverage)
- **Total modules**: 636 (inherit cluster icons)
- **Catalogue topics**: 3 (Programmes, Clusters, All Modules)

## Maintenance

To add or modify icons:

1. Edit the appropriate YAML file
2. Use Iconify search: https://icon-sets.iconify.design/
3. Select Material Design Icons (mdi:*) for consistency
4. Choose colors from Material Design palette
5. Test with: `python3 generate-all-science.py`

## Implementation

Icons are loaded by the `Catalogue` model at startup and passed to generators:

```python
from models import Catalogue

catalogue = Catalogue(source_dir=Path('.'))
# catalogue.module_icons
# catalogue.cluster_icons  
# catalogue.programme_icons
# catalogue.catalogue_icons
```

The `DepartmentGenerator` applies icons during content generation.
