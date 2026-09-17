# ARABIC LIBRARY — PROJECT CONSTITUTION

## 1. Project Identity

Project name: Arabic Library
Repository folder: RAF

This is an Arabic RTL digital library built incrementally with Django.

The developer is learning programming, so code must remain:
- readable
- explicit
- maintainable
- well organized
- easy to explain

Correctness and continuity are more important than speed.

---

## 2. Source of Truth

The current AI conversation is NOT the source of truth.

Before modifying code, always inspect:

1. `docs/PROJECT_STATE.md`
2. `docs/PHASES.md`
3. `docs/HANDOFF.md`
4. `docs/DECISIONS.md`
5. `docs/TEST_LOG.md`
6. `README.md`
7. relevant source files
8. `git status`
9. recent Git history

The repository is the source of truth.

Never assume that previous chat context is still accurate.

---

## 3. Locked V1 Technology Stack

Use:

- Python 3.14
- Django 5.2 LTS
- Django Templates
- HTML5
- CSS
- Bootstrap 5 RTL
- Vanilla JavaScript
- SQLite during local development
- PDF.js for PDF reading
- Django Admin
- Git

Do NOT introduce without explicit user approval:

- React
- Next.js
- Vue
- Angular
- Node.js backend
- Django REST Framework
- Tailwind CSS
- Docker
- Redis
- Celery
- Elasticsearch
- Microservices
- EPUB
- AI/TTS
- online payment gateways

Do not replace an approved technology simply because another technology is preferred.

---

## 4. Language Rules

All programming identifiers must be English.

Examples:

`book_title`
`current_page`
`approve_subscription`
`ReadingProgress`

User-facing interface text should be Arabic.

The website must support:

`lang="ar"`
`dir="rtl"`

Do not use Arabic for:

- Python variables
- class names
- model fields
- function names
- filenames
- database field names

---

## 5. Naming Conventions

Follow PEP 8.

Python variables and functions:

`snake_case`

Classes and Django models:

`PascalCase`

Constants:

`UPPER_SNAKE_CASE`

Templates:

`snake_case.html`

Django app names:

lowercase

Use descriptive names.

Avoid meaningless names such as:

`x`
`data1`
`temp2`
`final_code`
`new_final`

unless technically appropriate in a very small local expression.

---

## 6. Approved Django Applications

V1 applications are:

- `core`
- `accounts`
- `catalog`
- `subscriptions`
- `reading`

Responsibilities:

### core
Shared pages and common functionality.

### accounts
Users and authentication.

### catalog
Books, authors and categories.

### subscriptions
Manual subscription requests and subscription activation.

### reading
Favorites and reading progress.

Do not create additional Django applications without explicit approval.

---

## 7. Approved V1 Main Models

The intended main models are:

- `User`
- `Author`
- `Category`
- `Book`
- `SubscriptionRequest`
- `Subscription`
- `Favorite`
- `ReadingProgress`

Do not create extra persistent models unless required by the active phase and justified.

Do not casually rename completed models.

---

## 8. Phase Discipline

Only work on the phase marked as CURRENT in:

`docs/PROJECT_STATE.md`

Do not implement future phases.

Do not add extra features.

Do not redesign unrelated completed functionality.

If a useful future idea is discovered, record it under:

`Future Considerations`

in `docs/PROJECT_STATE.md`.

Then continue the current phase.

Never silently begin the next phase.

---

## 9. Before Editing Code

Before any implementation:

1. Read project documentation.
2. Inspect relevant source files.
3. Run `git status`.
4. Determine the active phase.
5. Identify what files will be changed.
6. Confirm the task belongs to the active phase.

If documentation and repository state disagree:

STOP.

Report the inconsistency before modifying code.

---

## 10. Change Control

Prefer the smallest correct change.

Do NOT:

- rewrite working modules unnecessarily
- perform unrelated refactoring
- rename unrelated files
- duplicate existing logic
- create multiple implementations of the same feature
- modify completed features without justification

If an architectural decision changes, record it in:

`docs/DECISIONS.md`

---

## 11. Git Safety

Before destructive or significant Git operations, inspect:

`pwd`

and:

`git status`

Never automatically execute destructive commands such as:

- `git reset --hard`
- `git clean -fd`
- force push
- deleting branches
- deleting tracked files

without explicit user approval.

Do not automatically push to remote repositories.

Do not change Git remotes without explicit approval.

---

## 12. Database Safety

Never solve migration problems by:

- deleting `db.sqlite3`
- deleting migrations
- resetting the database
- flushing data

unless explicitly approved.

For model changes:

1. inspect existing models
2. inspect migrations
3. create migration
4. inspect migration
5. run migration
6. run checks/tests

Never destroy data to hide a migration problem.

---

## 13. Dependency Control

Do not install packages unnecessarily.

Before adding a dependency:

1. check whether Django or Python already solves the problem
2. explain why the dependency is needed
3. add it to `requirements.txt`
4. document the decision if significant

Keep dependencies minimal.

---

## 14. Security Rules

Never commit:

- `.env`
- passwords
- tokens
- API keys
- production credentials
- secret keys

Use `.env.example` only for variable names and examples without secrets.

Do not disable:

- CSRF protection
- authentication
- authorization

just to make a feature work.

Frontend hiding is never sufficient access control.

Protected resources must also be validated by Django on the server.

---

## 15. Code Quality

Write code understandable by a beginner developer.

Prefer clear code over clever code.

Avoid:

- premature abstraction
- unnecessary inheritance
- magic values
- deeply nested logic
- duplicated business logic

Comments should explain WHY when needed, not merely translate obvious code.

---

## 16. Business Logic

Reusable business logic must not be duplicated across views.

For subscription business logic, prefer:

`apps/subscriptions/services.py`

Examples:

`get_active_subscription()`

`approve_subscription_request()`

Views should remain reasonably small.

---

## 17. URLs

Use Django URL namespaces.

Examples:

`catalog:book_list`

`catalog:book_detail`

`reading:my_library`

`subscriptions:create_request`

Use Django URL reversing.

Avoid hard-coded internal URLs when `{% url %}` or `reverse()` is appropriate.

---

## 18. Testing

For every implementation phase:

Run:

`python manage.py check`

Run relevant Django tests.

If models changed, inspect migrations and run them correctly.

Never claim that a test passed unless it was actually executed successfully.

Record significant results in:

`docs/TEST_LOG.md`

If something cannot be tested, state that explicitly.

---

## 19. Error Handling

Do not silently suppress errors.

Avoid:

`except Exception: pass`

Errors should be:

- handled meaningfully
- logged appropriately
- or remain visible during development

Never hide an error just to make the application appear functional.

---

## 20. File Upload Safety

Book PDFs, book covers and payment receipts are different types of uploaded files.

Validate:

- expected type
- reasonable size
- authentication
- authorization

Payment receipts must never be publicly accessible.

Protected books must eventually require server-side subscription authorization.

---

## 21. AI Agent Behavior

Do not fabricate results.

If a command fails, report the actual failure.

Do not state:

"tests passed"

unless tests actually passed.

Do not change project requirements to make implementation easier.

Do not generate unrelated sample features.

Do not continue automatically into another project phase.

---

## 22. End-of-Task Procedure

Before declaring a task complete:

1. run relevant checks
2. run relevant tests
3. inspect `git diff`
4. inspect `git status`
5. update `docs/PROJECT_STATE.md`
6. update `docs/HANDOFF.md`
7. update `docs/TEST_LOG.md` when relevant
8. update `docs/DECISIONS.md` when an architectural decision changed

Then report:

- Current phase
- Work completed
- Files created
- Files modified
- Migrations created
- Dependencies added
- Commands executed
- Tests executed
- Test results
- Known issues
- Exact next step
- Suggested Git commit message

STOP after completing the assigned task or phase.

Wait for user approval before continuing.
