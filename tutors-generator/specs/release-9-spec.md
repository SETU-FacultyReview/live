# Release 9: Refactor Programme Schedule Display

## Overview

The programme schedule is currently displayed in a `unit-00-schedule/` unit containing a `panelnote-00-schedule/` panelnote. This release refactors the schedule to be displayed as an ordinary note instead.

## Current Structure

```
<programme-topic>/
  ├── topic.md
  ├── unit-00-schedule/
  │   ├── topic.md                    (contains programme name)
  │   └── panelnote-00-schedule/
  │       └── panelnote.md            (contains schedule table)
  ├── unit-0/  (Any Semester modules - if present)
  ├── unit-1/  (Semester 1 modules)
  └── unit-2/  (Semester 2 modules)
```

## New Structure

```
<programme-topic>/
  ├── topic.md
  ├── unit-0/  (Any Semester modules - if present)
  │   └── note-00-schedule/
  │      └── note.md                     (contains schedule table with heading)
  ├── unit-1/  (Any Semester modules - if present)
  ├── unit-2/  (Semester 1 modules)
  └── unit-3/  (Semester 2 modules)
```

## Changes Required

### 1. Update `programme_schedule.py`

**Current behavior:**
- Creates `unit-00-schedule/` directory
- Creates `topic.md` with programme name
- Creates `panelnote-00-schedule/` subdirectory
- Creates `panelnote.md` with table only

**New behavior:**
- Creates `note-00-schedule/` directory
- Creates `note.md` with:
  - Heading: `# Programme Schedule`
  - The schedule table (same format as current `panelnote.md`)

### 2. File: `generators/programme_schedule.py`

**Method to update:** `generate_schedule(self, prog_dir: Path) -> None`

**Changes:**
1. Change directory name from `unit-00-schedule/` to `note-00-schedule/`
2. Remove creation of `topic.md` file
3. Change `panelnote-00-schedule/` to just create `note.md` in `note-00-schedule/`
4. Add heading `# Programme Schedule` to the top of `note.md`
5. Update the `_generate_markdown_table()` method to return the table content (no heading)
6. Combine heading + table in `note.md`

### 3. Content Format

**note.md content:**
```markdown
# Programme Schedule

Modules by semester

| Semester 0 |  |  | Semester 3 |  |  |
| ----------------- | --- | --- | ----------------- | --- | --- |
|  |  |  | [Dissertation](/note/...) | 20 | M |
| [Module Name](/note/...) | 10 | E |  |  |  |
...
```

## Implementation Notes

- The table format remains identical to the current implementation
- Module links remain unchanged
- Sorting logic (mandatory first, then electives, alphabetically) remains unchanged
- The change is purely structural: from a unit with panelnote to a note

## Testing

After implementation:
1. Generate all three courses
2. Verify each programme has `note-00-schedule/note.md` instead of `unit-00-schedule/`
3. Verify the schedule displays correctly in Tutors with the heading
4. Verify no `unit-00-schedule/` directories exist
5. Check that module links in the schedule still work correctly

## Benefits

- Simpler structure (one directory level instead of two)
- More appropriate learning object type (note vs panelnote)
- Consistent with other informational content in the catalogue
- Easier to maintain and understand
