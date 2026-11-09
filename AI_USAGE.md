# AI Usage Documentation

## Student / Project
- **Student:** Elijah Sterling
- **Course:** COP4751
- **Project:** Job Application Tracker

## Tools Used
- **ChatGPT (GPT-6):** Assisted with project architecture, SQL schema planning, Flask route scaffolding, HTML template structure, responsive CSS, skill matching logic, setup documentation, and troubleshooting checklists.

## Key Prompts
1. “Build the entire Job Application Tracker project from scratch using MySQL, Python Flask, HTML/CSS, all four tables, CRUD, and Job Match functionality.”
2. “Create a MySQL schema with companies, jobs, applications, and contacts, with foreign keys and JSON fields per the course specification.”
3. “Implement Flask CRUD routes for all four entities using parameterized SQL and form validation.”
4. “Create a skill matching feature that ranks jobs by percentage of required skills matched and displays missing skills.”
5. “Create a responsive dashboard UI with navigation, statistics cards, tables, forms, and status indicators.”
6. “Write a README with fresh-clone setup instructions and AI_USAGE.md documenting AI assistance.”

## What Worked Well
- AI was useful for drafting repetitive CRUD route and form patterns consistently.
- AI helped translate the relational schema into foreign-key-aware form dropdowns.
- AI suggested a simple explainable matching metric: matched unique skills divided by required unique skills.
- AI generated a first-pass visual style and setup documentation that accelerated the project foundation.

## What Was Changed / Customized
- Field names, data types, ENUM options, and relationships were aligned with the COP4751 specification.
- Database credentials were moved to environment variables rather than hard-coded in source.
- Parameterized SQL was used for form values; SQL table and column identifiers come from fixed application configuration.
- Form validation was added for required fields, nonnegative salary values, salary range consistency, and JSON format.
- Job Match handles JSON arrays and a `skills` property in JSON objects, compares case-insensitively, and displays matched and missing skills.
- The UI content and attribution were personalized to Elijah Sterling and COP4751.

## Lessons Learned
- Generated code must be read, tested, and adjusted to the actual assignment schema and environment.
- CRUD patterns can be reused, but foreign-key relationships and delete behavior require thoughtful design.
- Parameterized SQL protects submitted values from SQL injection; secrets should be kept out of version control.
- JSON data needs validation and a consistent format for reliable matching.
- Percentages are only meaningful when the required skills list is populated and normalized.
- Testing should include both normal paths and edge cases (empty forms, invalid JSON, duplicate entries where applicable, foreign-key deletes, and no skill overlap).

## Testing / Verification Note
This documentation describes AI assistance and the intended validation strategy. Before submission, the student should run the application against their own MySQL server, verify all CRUD operations, capture genuine screenshots/video, and update this file with the actual tests run and any further modifications.
