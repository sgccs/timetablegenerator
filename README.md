# Timetable Generator

This project is a Python-based timetable generator that processes data from two PDF files and provides an interactive graphical interface to manage and view course schedules.
## Features

- **PDF Data Extraction**: Extracts time slots and course data from specified PDF files.
- **Timetable Mapping**: Maps extracted data to a dynamic timetable structure.
- **Interactive Interface**: Allows users to search, add, and remove courses using a graphical interface.
- **Conflict Detection**: Ensures no overlapping slots when selecting courses.

- ### Prerequisites

Before running the script(generator.py), ensure you have:
- **Python 3.7+** installed on your machine.
- Required Python packages installed (see [Requirements](#requirements)).

---

### Installation

1. Clone the repository or download the project files.
2. Navigate to the project directory.

   ```bash
   cd timetable-generator
3. Install the required packages using the requirements.txt file:

   ```bash
   pip install -r requirements.txt


### Usage
1. File Setup

You need two specific PDF files: (these are already included in the repo, they could be replaced with the updated files if required)

    time.pdf: This file contains the timetable slots.
    example.pdf: This file contains course data.

2. Run the script using Python:
   ```bash
   python generator.py

3. search for the desired courses in the search bar.

4. click on the `add` button to select that particular course.

5. All the selected courses are visible. They could be removed by clicking the `delete` button.

6. Once you have selected all the required courses, click on the `submit` button.
