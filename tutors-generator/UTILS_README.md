# Catalogue Generator Utilities

This document describes the utility modules available for building SETU catalogue generators.

## Overview

The utility modules (`utils.py`, `icons.py`, and `markdown.py`) provide general-purpose functions that can be used by different catalogue generators, regardless of how they organize content. This promotes code reuse and consistency across different generator implementations.

## Modules

- **`utils.py`**: General text processing, file loading, and path utilities
- **`icons.py`**: Icon loading, selection, and formatting utilities
- **`markdown.py`**: Module markdown content generation

## Modules

### Text Processing Utilities

#### `sanitize_filename(text: str) -> str`
Convert text to a safe filename format.
- Replaces spaces with underscores
- Removes special characters
- Keeps alphanumeric, hyphens, and underscores

**Example:**
```python
sanitize_filename("Web Development 1")  # Returns: "Web_Development_1"
```

#### `convert_latex_to_markdown(text: str) -> str`
Convert LaTeX formatting to markdown.
- Currently handles: `\emph{text}` → `*text*`
- Returns original text if None or empty

**Example:**
```python
convert_latex_to_markdown(r"\emph{important}")  # Returns: "*important*"
```

#### `extract_first_sentence(text: str) -> str`
Extract the first sentence from a text block.
- Handles abbreviations (e.g., "B.Sc.", "Dr.")
- Ensures proper punctuation

**Example:**
```python
text = "This is first. This is second."
extract_first_sentence(text)  # Returns: "This is first."
```

### File Loading Utilities

#### `load_yaml_file(file_path: Path, default: Optional[dict] = None) -> dict`
Load a YAML file safely with error handling.
- Returns default if file doesn't exist
- Catches and reports YAML errors
- Returns empty dict by default

**Example:**
```python
data = load_yaml_file(Path("config.yaml"), default={})
```

## Icon Utilities (icons.py)

### Icon Loading

#### `load_icon_mappings(icons_dir: Path, icon_type: str) -> dict`
Load icon mappings from the icons directory.
- Supports types: 'cluster', 'programme', 'module'
- Prints loading status
- Returns empty dict if not found

**Example:**
```python
from icons import load_icon_mappings

icons_dir = Path(__file__).parent / "icons"
cluster_icons = load_icon_mappings(icons_dir, 'cluster')
```

### Icon Selection

#### `get_icon_for_item(...) -> tuple[str, str]`
Get icon type and color for an item with fallback priority.

**Priority:**
1. Item-specific icon
2. Cluster icon (if provided)
3. Default icon

**Parameters:**
- `item_code`: Code of the item (module, programme)
- `item_icons`: Item-specific icon mappings
- `cluster_name`: Optional cluster name for fallback
- `cluster_icons`: Optional cluster icon mappings
- `default_icon`: Default icon type (default: "carbon:sys-provision")
- `default_color`: Default icon color (default: "014771")

**Returns:** Tuple of `(icon_type, icon_color)`

**Example:**
```python
from icons import get_icon_for_item

icon_type, icon_color = get_icon_for_item(
    "A12345",
    module_icons,
    cluster_name="IT",
    cluster_icons=cluster_icons
)
```

### Icon Formatting

#### `create_icon_frontmatter(icon_type: str, icon_color: str) -> str`
Create YAML frontmatter for Tutors icons.

**Example:**
```python
from icons import create_icon_frontmatter

frontmatter = create_icon_frontmatter("mdi:laptop", "1976D2")
# Returns:
# ---
# icon:
#   type: mdi:laptop
#   color: 1976D2
# ---
```

### Path Utilities

#### `get_tutors_weburl_path(course_id: str, *path_parts: str) -> str`
Generate a Tutors weburl path.
- Auto-detects type (note, topic, talk, lab) from last component
- Constructs proper Tutors URL format

**Example:**
```python
path = get_tutors_weburl_path(
    "setu-sci-modules",
    "unit-1",
    "topic-02-clusters",
    "note-01-module-name"
)
# Returns: "/note/setu-sci-modules/unit-1/topic-02-clusters/note-01-module-name"
```

### String Formatting Utilities

#### `format_module_status(status: str) -> str`
Format module status code to full name.
- M → Mandatory
- E → Elective
- C → Core
- O → Optional

**Example:**
```python
format_module_status('M')  # Returns: "Mandatory"
```

#### `format_learning_outcomes_list(outcomes: list, start_num: int = 1) -> str`
Format learning outcomes as a numbered markdown list.
- Applies LaTeX to markdown conversion
- Customizable starting number

**Example:**
```python
outcomes = ["Understand X", "Apply Y"]
formatted = format_learning_outcomes_list(outcomes)
# Returns:
# 1. Understand X
# 2. Apply Y
```

## Usage in Generators

### Import utilities:
```python
from utils import (
    sanitize_filename,
    convert_latex_to_markdown,
    extract_first_sentence,
    load_yaml_file,
    get_tutors_weburl_path,
    format_module_status
)

from icons import (
    load_icon_mappings,
    load_icon_mappings_from_paths,
    get_icon_for_item,
    create_icon_frontmatter
)

from markdown import generate_module_markdown
```

### Use in generator class:
```python
from icons import load_icon_mappings, get_icon_for_item, create_icon_frontmatter
from utils import sanitize_filename
from markdown import generate_module_markdown

class MyCatalogueGenerator:
    def __init__(self):
        icons_dir = Path(__file__).parent / "icons"
        self.cluster_icons = load_icon_mappings(icons_dir, 'cluster')
        self.module_icons = load_icon_mappings(icons_dir, 'module')
    
    def create_module_file(self, module_code, descriptor):
        # Generate complete markdown content
        markdown_content = generate_module_markdown(
            module_code,
            descriptor,
            self.module_icons,
            self.cluster_icons,
            cluster_name=descriptor.get('cluster')
        )
        
        # Write to file
        filename = sanitize_filename(descriptor.get('full_title', module_code))
        with open(f"{filename}.md", 'w') as f:
            f.write(markdown_content)
```

## Markdown Utilities (markdown.py)

### Module Markdown Generation

#### `generate_module_markdown(...) -> str`
Generate complete markdown content for a module from its descriptor.

**Parameters:**
- `module_code`: The module code (e.g., "A12345")
- `descriptor`: Module descriptor dictionary (from YAML)
- `module_icons`: Dictionary of module-specific icon mappings
- `cluster_icons`: Dictionary of cluster icon mappings
- `cluster_name`: Optional cluster name for icon fallback

**Returns:** Complete markdown content as string

**Sections generated:**
- Icon frontmatter
- Module title and summary (first sentence of aim)
- PDF link
- Module information table
- Module aim
- Learning outcomes
- Indicative content
- Learning and teaching methods (with contact hours table)
- Assessment methods
- Assessment criteria
- Pre-requisites and co-requisites
- Recommended reading
- Programme information table
- Resources required
- Footer with module and timetable codes

**Example:**
```python
from markdown import generate_module_markdown

markdown_content = generate_module_markdown(
    "A12345",
    descriptor_dict,
    module_icons,
    cluster_icons,
    cluster_name="IT"
)

# Write to file
with open("module.md", 'w') as f:
    f.write(markdown_content)
```

## Benefits

- **Code Reuse**: Common functions available to all generators
- **Consistency**: Same formatting across different catalogue views
- **Maintainability**: Fix once, benefit everywhere
- **Testability**: Utilities can be unit tested independently
- **Flexibility**: Mix and match utilities as needed
- **Separation of Concerns**: Markdown generation isolated from generator logic

## Future Extensions

Potential additions:
- Programme markdown generation templates
- PDF handling utilities
- CSV/data parsing helpers
- Additional text formatting functions
- Validation utilities
- Alternative markdown templates for different views
