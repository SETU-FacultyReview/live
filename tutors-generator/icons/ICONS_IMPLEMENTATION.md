# Icons Implementation Summary

## Overview

Cluster icons have been successfully implemented in the science module catalogue generator. Icons are applied at two levels:
1. **Cluster topic pages** - Each of the 37 clusters has its own distinctive icon
2. **Module notes** - All 636 modules inherit their cluster's icon (unless overridden)

## Implementation Details

### Icon Priority System

The generator applies icons using a 3-tier priority system:

1. **Module-specific icons** (highest priority)
   - From computing catalogue (`../computing/module-catalogue/module-icons.yaml`)
   - 225 modules have custom icons
   - Example: Embedded Systems uses `fluent:wrench-screwdriver-24-regular`

2. **Cluster icons** (medium priority)
   - From `tutors-generator/cluster-icons.yaml`
   - 37 unique icons for all clusters
   - ~411 modules inherit cluster icons
   - Example: Biology modules use `mdi:dna`

3. **Default icon** (fallback)
   - `carbon:sys-provision` with color `014771`
   - Only used if both above fail

### Code Changes

**File:** `tutors-generator/generate-master.py`

1. Added `load_cluster_icons()` method
2. Updated `__init__()` to load cluster icons
3. Modified `generate_module_markdown()` to accept `cluster_name` parameter
4. Updated icon selection logic with 3-tier priority
5. Modified `generate_clusters()` to:
   - Add icon frontmatter to cluster `topic.md` files
   - Pass cluster name to module generation

### Configuration File

**File:** `tutors-generator/cluster-icons.yaml`

Format:
```yaml
"Cluster Name":
  type: mdi:icon-name
  color: 'HEXCODE'
  description: Icon rationale
```

**Important:** Cluster names must match EXACTLY as they appear in module descriptors (including spaces, commas, capitalization).

## Coverage Statistics

### Cluster Topics
- **37 of 37** cluster topics have icons (100%)
- All use Material Design Icons (mdi) set

### Modules
- **225 modules** use computing-specific icons (35%)
- **~411 modules** use cluster icons (65%)
- **636 total modules** with icons (100%)

## Icon Distribution by Cluster

| Cluster | Icon | Color | Modules |
|---------|------|-------|---------|
| Agriculture | `mdi:tractor` | 🟢 #689F38 | 24 |
| Biology | `mdi:dna` | 🟦 #00897B | 24 |
| Chemistry | `mdi:test-tube` | 🟠 #E64A19 | 13 |
| IT | `mdi:monitor` | 🔵 #0277BD | 25 |
| Mathematics and Physics | `mdi:math-compass` | 🔷 #00838F | 50 |
| Food Science | `mdi:food-apple-outline` | 🔴 #EF5350 | 33 |
| Game Development | `mdi:gamepad-variant-outline` | 🟣 #7B1FA2 | 13 |
| Engineering | `mdi:cog` | ⚫ #546E7A | 22 |
| ... | ... | ... | ... |

## Examples

### Cluster Topic with Icon

**File:** `tutors-modules-master/topic-02-Agriculture/topic.md`

```markdown
---
icon:
  type: mdi:tractor
  color: 689F38
---

# Agriculture
```

### Module with Cluster Icon

**File:** `tutors-modules-master/topic-18-Food_Science/note-02-note-02-Food_Analysis/note.md`

```markdown
---
icon:
  type: mdi:food-apple-outline
  color: EF5350
---

# Food Analysis
```

### Module with Computing Override

**File:** `tutors-modules-master/topic-04-Automotive_Automation_and_IoT/note-09-note-09-Embedded_Systems/note.md`

```markdown
---
icon:
  type: fluent:wrench-screwdriver-24-regular
  color: 1975BE
---

# Embedded Systems
```

(Uses computing icon instead of automotive cluster icon)

## Testing & Verification

### Verified Scenarios

✅ Cluster topics all have icons  
✅ Modules inherit cluster icons  
✅ Computing icons override cluster icons  
✅ Icon frontmatter format is correct  
✅ Colors render without # prefix  
✅ YAML validation passes  

### Sample Tests

```bash
# Verify cluster icon
head -10 tutors-modules-master/topic-05-Biology/topic.md
# Shows: mdi:dna with color 00897B

# Verify module inherits cluster icon
head -10 tutors-modules-master/topic-05-Biology/note-01-.../note.md
# Shows: mdi:dna with color 00897B

# Verify computing override
head -10 tutors-modules-master/topic-04-Automotive_.../note-09-Embedded_Systems/note.md
# Shows: fluent:wrench-screwdriver-24-regular (not mdi:car-connected)
```

## Maintenance

### Adding New Cluster Icons

If new clusters are added:

1. Add to `tutors-generator/cluster-icons.yaml`:
   ```yaml
   "New Cluster Name":
     type: mdi:appropriate-icon
     color: 'HEXCODE'
     description: Why this icon
   ```

2. Regenerate:
   ```bash
   ./generate-master
   ```

### Changing Cluster Icons

1. Edit `tutors-generator/cluster-icons.yaml`
2. Regenerate catalogue
3. Icons will update for both cluster topics and all modules in that cluster

### Module-Specific Icons

To override cluster icon for a specific module:

1. Add to `module-catalogue/module-icons.yaml` (if creating one)
2. Or rely on computing catalogue overlap

## Color Palette

Icons follow a domain-based color strategy:

- 🟢 **Green** (#2E7D32-#7CB342): Agriculture, environment
- 🔵 **Blue** (#0277BD-#1976D2): Technology, IT
- ⚫ **Grey** (#455A64-#78909C): Engineering
- 🟣 **Purple** (#5E35B1-#7B1FA2): Business, creative
- 🟠 **Orange** (#E64A19-#FFA000): Science, energy
- 🔴 **Red** (#C62828-#EF5350): Food, security

## Icon Sources

All icons from **Iconify**: https://icon-sets.iconify.design/

Primary set: **Material Design Icons (mdi)**
- 7,000+ icons
- Consistent style
- Well-maintained
- Good browser support

## Future Enhancements

Potential improvements:

- [ ] Add cluster topic images (hero banners)
- [ ] Create science-specific module icons (for non-computing modules)
- [ ] Add level-based icon variations (Introductory/Advanced/Postgraduate)
- [ ] Visual icon preview in documentation
- [ ] Automated icon validation in generator

## Files Modified/Created

### Modified
- `tutors-generator/generate-master.py` - Added cluster icon support

### Created
- `tutors-generator/cluster-icons.yaml` - 37 cluster icon definitions
- `tutors-generator/CLUSTER_ICONS.md` - Icon documentation
- `tutors-generator/CLUSTER_ICONS_VISUAL.md` - Visual reference
- `tutors-generator/ICONS_IMPLEMENTATION.md` - This file

## Regeneration

To apply icons to existing or updated content:

```bash
cd science
./generate-master
```

All icons will be automatically applied based on current configuration.
