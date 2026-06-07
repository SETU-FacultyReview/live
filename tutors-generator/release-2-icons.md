Rework the icons used for all

- modules
- clusters
- programmes

The icons are to be selected from the [Iconify Repository](https://icon-sets.iconify.design/)

The icons are to be managed in:

- catalogue-icons.yaml
- cluster-icons.yaml
- programme-icons.yaml

with the following constraints:

- cluster-icon: identify a suitable icons from across the Iconify repository for the cluster, based on your interpretation of the cluster name. For clusters in Science, lead towards Scienctific symbols - except where obvious symbols come to mind. All cluster icons must be unique.
- programme-icons: again, attempt to find suitable icon from across the Icon set. Lean towards "academic" symbols.
- catalogue-icons: select suitabl icons for "Academic Programmes", "Module Clusters" and "All modules". these icons are to be used by the department-generator module

In the generators, make sure that all modules use the cluster icon (for the cluster the module belongs to) as the module icon

For the icon colours, this is the CSS theme currently in use in tutors:

- [tutors.css](https://github.com/tutors-sdk/tutors/blob/development/src/lib/services/themes/styles/tutors.css)

Select colours that align with the choices above.
