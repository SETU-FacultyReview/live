Each module descriptor has a table "Programme Information" which lists the modules credits, programmes the module appears, its semester and stage (year) + whether it is mandatory or elective.

Write a Class "ProgrammeSchedule" which takes a Department as a constructor parameter + a programme code. It should have a method:

- generateSchedule

This should generate a tutors "panelnote" (see [tutors panelnote](https://tutors.dev/note/tutors-reference-manual/unit-2-panels-and-videos/note-a-resources#panelnote) documentation). This panelnote should have a table which shows the "Programme Schedule" for the programme.

**Table Format:**
- Each column represents a semester (Semester 1, Semester 2, etc.)
- Within each column, list all modules for that semester (stacked vertically)
- Each module entry includes:
  - Module name
  - Credits (in parentheses)
  - Status: M (Mandatory) or E (Elective)

**Example:**

| Semester 1 | Semester 2 | Semester 3 | Semester 4 |
|------------|------------|------------|------------|
| Database Design (5) M | Web Development (5) M | Design Patterns (5) M | Final Year Project (10) M |
| Programming (5) M | Data Structures (5) M | Software Engineering (5) M | Machine Learning (5) E |
| Mathematics (5) M | Algorithms (5) M | Networks (5) M | Security (5) E |
| Computer Systems (5) M | Operating Systems (5) E | | Cloud Computing (5) E |

Use generateSchedule to place this panelnote in the topic for the programme
