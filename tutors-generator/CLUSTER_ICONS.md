# Cluster Topic Icons

This document describes the icon strategy for the 37 subject clusters in the science catalogue.

## Icon Selection Criteria

Each cluster icon was selected to:
1. **Visually represent** the subject matter
2. **Use recognizable symbols** that immediately communicate the topic
3. **Maintain consistency** with Material Design Icon (mdi) set for cohesive appearance
4. **Choose appropriate colors** that reinforce the subject (green for nature, blue for technology, etc.)

## Complete Icon Mapping

| # | Cluster | Icon | Color | Rationale |
|---|---------|------|-------|-----------|
| 1 | AgriFoodICT | `mdi:barley` | Green | Combines agriculture/food with technology |
| 2 | Agriculture | `mdi:tractor` | Green | Classic symbol of farming |
| 3 | Analytical Science | `mdi:flask-outline` | Blue | Laboratory analysis equipment |
| 4 | Automotive, Automation and IoT | `mdi:car-connected` | Grey | Connected vehicle technology |
| 5 | Biology | `mdi:dna` | Teal | DNA helix - fundamental biology symbol |
| 6 | Business | `mdi:briefcase-outline` | Purple | Professional business symbol |
| 7 | Chemistry | `mdi:test-tube` | Orange-Red | Chemical laboratory equipment |
| 8 | Creativity and Innovation | `mdi:lightbulb-on-outline` | Yellow | Ideas and innovation |
| 9 | Data Communications | `mdi:swap-horizontal` | Blue | Data flow and exchange |
| 10 | Database and Analytics | `mdi:database-search` | Indigo | Data storage and querying |
| 11 | Discipline Specific Technologies | `mdi:tools` | Grey | Specialized technical tools |
| 12 | Electrical Engineering | `mdi:flash` | Amber | Electrical power/energy |
| 13 | Electronics | `mdi:chip` | Orange | Microchips and circuits |
| 14 | Engineering | `mdi:cog` | Blue-Grey | General engineering/mechanics |
| 15 | Engineering Practise | `mdi:hammer-wrench` | Blue-Grey | Practical engineering work |
| 16 | English Language | `mdi:alphabetical-variant` | Brown | Language and letters |
| 17 | Environmental Science | `mdi:leaf` | Green | Nature and ecology |
| 18 | Food Science | `mdi:food-apple-outline` | Red | Food and nutrition |
| 19 | Forensics and Security | `mdi:shield-lock-outline` | Dark Red | Protection and security |
| 20 | Forestry | `mdi:pine-tree` | Dark Green | Trees and forest management |
| 21 | Game Development | `mdi:gamepad-variant-outline` | Purple | Gaming and interactive media |
| 22 | Graphic Design and Animation | `mdi:palette-outline` | Pink | Visual arts and design |
| 23 | Horticulture | `mdi:flower-tulip-outline` | Green | Plant cultivation |
| 24 | Humanities | `mdi:book-open-variant` | Brown | Literature and culture |
| 25 | Information Systems and Modelling | `mdi:sitemap` | Blue | System architecture |
| 26 | IT | `mdi:monitor` | Blue | Computing technology |
| 27 | Mathematics and Physics | `mdi:math-compass` | Cyan | Mathematical tools |
| 28 | Media Production | `mdi:video-vintage` | Pink | Video/audio production |
| 29 | Networks and Cloud | `mdi:cloud-outline` | Light Blue | Cloud computing |
| 30 | Pharmaceutical Science | `mdi:pill` | Cyan | Medication and pharmaceuticals |
| 31 | Placement and Projects | `mdi:clipboard-text-outline` | Grey | Work documentation |
| 32 | Professional Skills | `mdi:account-tie` | Grey | Professional development |
| 33 | Quality, Regulatory and Compliance | `mdi:certificate-outline` | Teal | Certification and standards |
| 34 | Science and Mathematics | `mdi:flask-round-bottom` | Purple | Laboratory science |
| 35 | Software and Information Systems | `mdi:application-brackets-outline` | Indigo | Software coding |
| 36 | Software and Web Development | `mdi:code-tags` | Blue | Web development |
| 37 | Sports Technology | `mdi:run-fast` | Orange | Athletic performance |

## Color Palette Strategy

Colors were chosen based on subject domains:

- **🟢 Green shades** (#2E7D32 - #7CB342): Nature, agriculture, environment
- **🔵 Blue shades** (#0277BD - #1976D2): Technology, IT, computing
- **🟣 Purple shades** (#5E35B1 - #7B1FA2): Business, creative fields
- **🟤 Brown shades** (#6D4C41 - #8D6E63): Humanities, language
- **🔴 Red/Orange** (#C62828 - #F4511E): Food, security, sports
- **⚫ Grey shades** (#455A64 - #78909C): Engineering, professional skills

## Usage

### In Tutors Course Generation

The cluster icons will be applied to cluster topic pages in the `tutors-modules-master` output.

To implement:

1. Update generator to load `tutors-generator/cluster-icons.yaml`
2. Apply icon frontmatter to cluster `topic.md` files:

```markdown
---
icon:
  type: mdi:dna
  color: 00897B
---

# Biology

...
```

### Manual Application

To add icons to existing cluster topics:

```bash
# For each cluster topic directory
# Add icon frontmatter to topic.md files
```

## Icon Source

All icons are from **Material Design Icons (mdi)** via Iconify:
- Browse: https://icon-sets.iconify.design/mdi/
- Consistent style across all 37 clusters
- Well-maintained, extensive icon set
- Good recognition and clarity

## Alternative Icon Sets

If you prefer different styles, consider:

| Icon Set | Style | Example Use |
|----------|-------|-------------|
| `carbon:` | IBM Carbon | Technical/enterprise |
| `lucide:` | Lucide | Modern, clean |
| `heroicons:` | Heroicons | Web-focused |
| `tabler:` | Tabler | Minimalist |
| `fa6-solid:` | Font Awesome | Popular, varied |

## Visual Preview

To preview these icons before implementation:

1. Visit https://icon-sets.iconify.design/
2. Search for icon name (e.g., "mdi:dna")
3. View in different sizes and colors

## Implementation Checklist

- [x] Icon mapping file created (`tutors-generator/cluster-icons.yaml`)
- [ ] Update generator to load cluster icons
- [ ] Apply icons to cluster topic.md files
- [ ] Test Tutors build with icons
- [ ] Verify icon appearance in browser
- [ ] Document any customizations

## Future Enhancements

Consider adding:
- **Cluster topic images**: Hero images for each cluster (PNG/SVG)
- **Module category icons**: Sub-categorize within clusters
- **Programme icons**: Icons for different degree programmes
- **Level indicators**: Visual badges for Introductory/Intermediate/Advanced/Postgraduate

## Notes

- Icons use hex color codes without `#` prefix (Tutors format)
- Color codes are quoted in YAML to preserve leading zeros
- All icon types prefixed with `mdi:` for Material Design Icons
- Descriptions included for documentation and future reference
