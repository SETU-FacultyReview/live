# Top-Level Topic Icons

Documentation for the two main navigation topic icons in the science catalogue.

## Icon Selections

### 1. All Modules (Alphabetical View)

**Topic:** `topic-01-all-modules`

```yaml
icon:
  type: mdi:sort-alphabetical-ascending
  color: 1976D2
```

**Details:**
- **Icon:** `mdi:sort-alphabetical-ascending` - Material Design Icons
- **Color:** `#1976D2` (blue)
- **Visual:** A→Z with ascending arrow
- **Rationale:** Clearly represents alphabetical sorting/ordering
- **Preview:** https://icon-sets.iconify.design/mdi/sort-alphabetical-ascending/

### 2. All Modules by Cluster (Categorical View)

**Topic:** `topic-02-clusters`

```yaml
icon:
  type: mdi:view-grid
  color: 5E35B1
```

**Details:**
- **Icon:** `mdi:view-grid` - Material Design Icons
- **Color:** `#5E35B1` (purple)
- **Visual:** Grid/tile layout
- **Rationale:** Represents organized categories/grouping
- **Preview:** https://icon-sets.iconify.design/mdi/view-grid/

## Design Rationale

### Color Choices

**Blue (`#1976D2`)** for All Modules:
- Associated with organization and order
- Commonly used for list/sort interfaces
- Contrasts well with content

**Purple (`#5E35B1`)** for Clusters:
- Distinct from blue (easy differentiation)
- Associated with creativity and categorization
- Matches the purple used in Business/Creative clusters

### Icon Style

Both icons:
- ✅ From Material Design Icons (mdi) set
- ✅ Simple, recognizable shapes
- ✅ Work well at small sizes
- ✅ Clear semantic meaning
- ✅ Consistent with 37 cluster icons

## Visual Hierarchy

```
Root (no icon)
├── 📘 All Modules (blue A→Z)
│   └── 636 web objects (module/cluster icons)
└── 🟣 All Modules by Cluster (purple grid)
    └── 37 clusters (cluster icons)
        └── 636 notes (module/cluster icons)
```

## Implementation

**Generator method:** `generate_all_modules()`
```python
f.write("---\n")
f.write("icon:\n")
f.write("  type: mdi:sort-alphabetical-ascending\n")
f.write("  color: 1976D2\n")
f.write("---\n\n")
```

**Generator method:** `generate_clusters()`
```python
f.write("---\n")
f.write("icon:\n")
f.write("  type: mdi:view-grid\n")
f.write("  color: 5E35B1\n")
f.write("---\n\n")
```

## Alternative Icon Options Considered

### For All Modules (Alphabetical)
- ❌ `mdi:format-list-bulleted` - Too generic
- ❌ `mdi:order-alphabetical-ascending` - Similar but less common
- ✅ `mdi:sort-alphabetical-ascending` - **Selected** (clear intent)

### For Clusters (Categorical)
- ❌ `mdi:apps` - Too app-focused
- ❌ `mdi:grid` - Less descriptive
- ✅ `mdi:view-grid` - **Selected** (clear categorization)

## Total Icon Coverage

| Level | Count | Type |
|-------|-------|------|
| Top-level topics | 2 | Navigation icons |
| Cluster topics | 37 | Subject-specific icons |
| Module notes | 636 | Module/cluster icons |
| Web objects | 636 | Same as module notes |
| **Total unique icons** | **675** | Material Design Icons |

## Consistency with Catalogue

All icons follow the same pattern established for cluster icons:
- Material Design Icons (mdi) set
- Hex color codes (no `#` prefix in YAML)
- Icon frontmatter at top of topic.md
- Descriptive, semantic icon choices

## User Experience

**Navigation clarity:**
- Users immediately understand the two browsing modes
- Blue A→Z = "Find by name"
- Purple grid = "Browse by subject"

**Visual consistency:**
- All icons in the same design system
- Clear color coding throughout
- Hierarchical icon application (topics → clusters → modules)

## Regeneration

Icons are automatically applied when running:
```bash
./generate-master
```

The generator creates both topic.md files with icon frontmatter during the generation process.

## Related Documentation

- `cluster-icons.yaml` - 37 cluster topic icons
- `CLUSTER_ICONS.md` - Cluster icon documentation
- `ICONS_IMPLEMENTATION.md` - Complete icon implementation guide
