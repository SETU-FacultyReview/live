You are an experienced Python developer, who value the [Zen of Python](https://peps.python.org/pep-0020/) and also [Pep 8 style guide](https://peps.python.org/pep-0008/). You are a TypeScript deveoper, and tend to see problems through the lens of elegant type systems. I am an expert on the [Tutors course format](https://tutors-reference-manual.netlify.app/llms/tutors-reference-manual-complete-llms.txt) and I have develloped a set of scripts for managing the [SETU Science Faculty Module Catalogue](https://github.com/SETU-FacultyReview/core)

The tutors generator (this project) generates a tutors course from the yaml, pdf, and csv resources of the SETU Science Faculty Module Catalogue is to be refactored towards a more modular, cohenent and extensible set of classes and objects. This project is the be the basis of a number of experimental tutors course generators. The focus on this refactor is to reimplement generate-by-dept to perform exactly as it currently functions.

Each of the numbered refactorings is to be carried out in turn, check back with me for feedback before proceeding to the next refactoring.

The refactorings:

(1) A new "Catalogue" class (in models/catalogue.py), responsible for loading a complete catalogue, including

- the programme registry
- all module descriotiors
- all clustors
- all icon mappings

This catalogue should be loaded once as the generator starts up. The relative paths to find the catalogue should be passed to the constructor.

(2) A "Department" class (in models/department.py) that is passed a Catalogue object when it is created, from which it retrieves:

- its programmes
- its modules
- it clusters

The appropriate filters should be passed to the constructor along with the Catalogue object.

(4) A Markdown generator class (in generators/markdown_generator.py), responsible for generating markdown content. It should have a single method for them moment:

- generateModuleDescriptor: generate a markdown version of a module desciriptor. This is currently implemented in markdown.py

(5) A DepartmentGenerator class (in generators/department_generator.py), that is passed a Department object when it created + a reference to an icon mapping object/table. It has these public methods:

- generateClusters: this should produce a Topic containing all clusters + the module descriptors (+pdf). This should match the current behviour
- generateAllModules: this should generate all modules for the department, sorted alphabetically. Again, follow current implememntation
- generateProgrammes: same again, match current implementation. Make user to implement the "tutors-programme-id" env pattern as currently implemented

Also passed to the constructor should be the tutors-module-id to be used in the generationp of the weburl link to the module descriptors

(6) A TutorsCatalogue class (in models/tutors_catalogue.py), which will use the above objects to produce a tutors course. It should have the following methods:

- A constructor. This should create a Catalogue object, and then the Department objects "Science" and "Computing & Maths".
- generateTutorsCourse method: this should generate a tutors course that matches the current tutors-module-by-dept course

(7) A top level "generate-all-science" script, that creates and invokes a TutorsCatalogue to generate the tutors-course
