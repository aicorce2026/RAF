# TEST LOG

Project: Arabic Library

Purpose:
Record actual verification, checks and tests performed during development.

Rules:

- Never record a test as PASSED unless it was actually executed successfully.
- Never hide failed tests.
- Record important failures and their resolution.
- Update this file before completing each project phase.

---

## Phase 00 - Environment and Governance Verification

Date:
2026-09-17

Status:
COMPLETE

### Environment Checks

Python version check:

Command:
python --version

Result:
Python 3.14.7

Status:
PASSED

Git version check:

Command:
git --version

Result:
git version 2.45.1.windows.1

Status:
PASSED

---

Python interpreter check before virtual environment:

Command:
where python

Result:
System Python installation detected at C:\Python314\python.exe

Status:
PASSED

---

Project location check:

Command:
pwd

Result:
/d/rafia/RAF

Status:
PASSED

---

Available Python versions check:

Command:
py -0p

Result:
Python 3.14 detected.

Status:
PASSED

---

### Virtual Environment Checks

Virtual environment creation:

Command:
python -m venv .venv

Result:
Virtual environment created successfully.

Status:
PASSED

---

Virtual environment activation:

Command:
source .venv/Scripts/activate

Result:
Terminal displayed (.venv).

Status:
PASSED

---

Virtual environment Python check:

Command:
which python

Result:
/d/rafia/RAF/.venv/Scripts/python

Status:
PASSED

---

Python version inside virtual environment:

Command:
python --version

Result:
Python 3.14.7

Status:
PASSED

---

Antigravity interpreter verification:

Result:
Antigravity selected .venv/Scripts/python.exe as the recommended project interpreter.

Status:
PASSED

---

### Django Checks

pip upgrade check:

Command:
python -m pip install --upgrade pip

Result:
pip already satisfied at version 26.2.1.

Status:
PASSED

---

Django installation:

Command:
python -m pip install "Django>=5.2,<5.3"

Result:
Django 5.2.17 installed successfully.

Status:
PASSED

---

Django version check:

Command:
python -m django --version

Result:
5.2.17

Status:
PASSED

---

pip version check:

Command:
python -m pip --version

Result:
pip 26.2.1 using Python 3.14 virtual environment.

Status:
PASSED

---

Installed package verification:

Command:
python -m pip list

Verified packages:

- Django 5.2.17
- asgiref 3.12.1
- sqlparse 0.6.0
- tzdata 2026.4
- pip 26.2.1

Status:
PASSED

---

### Git Repository Checks

Repository initialization:

Command:
git init -b main

Result:
Git repository initialized successfully.

Status:
PASSED

---

Current branch check:

Command:
git branch --show-current

Result:
main

Status:
PASSED

---

Local Git identity verification:

Commands:

git config --show-origin user.name
git config --show-origin user.email

Result:
Git identity is stored in .git/config for this repository.

Status:
PASSED

---

Git ignore verification:

Command:
git status

Result:
.venv did not appear as an untracked file.

Status:
PASSED

---

Initial repository commit:

Commit:
8f7e792 chore: initialize project repository

Result:
Commit created successfully.

Status:
PASSED

---

Working tree verification after initial commit:

Command:
git status

Result:
nothing to commit, working tree clean

Status:
PASSED

---

Git history verification:

Command:
git log --oneline -1

Result:
8f7e792 chore: initialize project repository

Status:
PASSED

---

### Governance Documentation Verification

Verified files created:

- .agents/rules/project-constitution.md
- docs/PROJECT_STATE.md
- docs/PHASES.md
- docs/HANDOFF.md
- docs/DECISIONS.md
- docs/TEST_LOG.md
- README.md
- .env.example

Status:
FILES CREATED

Some files are still being populated and reviewed.

Phase 00 governance files have been completed and reviewed.

---

## Application Tests

Status:
NOT APPLICABLE YET

Reason:

The Django project has not yet been created.

There are currently:

- no Django applications
- no business models
- no database migrations
- no application views
- no application test suite

---

## Known Failures During Phase 00

### Incorrect Python Command Typo

Command entered:

pyhton --version

Result:

command not found

Cause:

Typing error.

Resolution:

Correct command used:

python --version

Final status:
RESOLVED

---

### PROJECT_STATE Here-Document Copy Issue

Issue:

An earlier attempt to create PROJECT_STATE.md became malformed while copying terminal content.

Resolution:

The active terminal input was cancelled and PROJECT_STATE.md was recreated using a simpler safe here-document.

Verification:

The beginning and end of PROJECT_STATE.md were inspected successfully.

Final status:
RESOLVED

---

## Phase 00 Final Verification

Status:
PASSED

Phase 00 governance commit:

37ea6f3 docs: establish project governance and continuity

Before Phase 00 can be marked COMPLETE, verify:

- project constitution
- project state
- phases
- handoff
- architectural decisions
- test log
- README
- .env.example
- git status
- git diff
- final Phase 00 commit

Do not mark Phase 00 COMPLETE until all items above are verified.

---

# Future Test Entry Format

For future phases, record:

Phase:
Date:
Feature:
Command or procedure:
Expected result:
Actual result:
Status:
Notes:

Valid status examples:

PASSED
FAILED
BLOCKED
NOT_APPLICABLE

---

## Phase 01 - Django Project Bootstrap

Date:
2026-09-17

Status:
COMPLETE

### Project Creation

Command:
django-admin startproject config .

Result:
Project created successfully in repository root.

Status:
PASSED

---

### Database Migration

Command:
python manage.py check
python manage.py migrate
python manage.py check

Result:
System check identified no issues. Initial migrations for admin, auth, contenttypes, and sessions applied successfully.

Status:
PASSED

---

### Development Server

Command:
python manage.py runserver

Verification:
Navigated to http://127.0.0.1:8000/

Result:
"The install worked successfully! Congratulations!" message displayed.

Status:
PASSED

---

## Phase 02 - Django Application Structure

Date:
2026-09-17

Status:
COMPLETE

### App Registration Check

Command:
python manage.py check

Result:
System check identified no issues.

Status:
PASSED

---

### Migration State Check

Command:
python manage.py makemigrations --check --dry-run

Result:
No changes detected.

Status:
PASSED

---

## Phase 03 - Authentication and User Accounts

Date:
2026-09-17

Status:
COMPLETE

### Application Verification

Command:
python manage.py check

Result:
System check identified no issues (0 silenced).

Status:
PASSED

---

### Migration Safety Check

Command:
python manage.py makemigrations --check --dry-run

Result:
No changes detected.

Status:
PASSED

---

### Authentication Tests

Command:
python manage.py test apps.accounts -v 2

Result:
All authentication tests passed successfully.

Status:
PASSED

---

### Full Test Suite

Command:
python manage.py test -v 2

Result:
Full test suite passed successfully.

Status:
PASSED


---

## Phase 04 - Catalog Data Models

Date:
2026-09-17

Status:
COMPLETE

### Catalog Model Verification

Models created:
- Author
- Category
- Book

Relationships:
- Book -> Author using ForeignKey with PROTECT and related_name="books"
- Book -> Category using ForeignKey with PROTECT and related_name="books"

Status:
PASSED

---

### Migration Verification

Commands:
python manage.py makemigrations catalog
python manage.py migrate
python manage.py showmigrations catalog

Results:
- catalog migration 0001_initial created.
- catalog.0001_initial applied successfully.
- showmigrations reported [X] 0001_initial.

Status:
PASSED

---

### Migration Consistency Check

Command:
python manage.py makemigrations --check --dry-run

Result:
No changes detected.

Status:
PASSED

---

### Django System Check

Command:
python manage.py check

Result:
System check identified no issues (0 silenced).

Status:
PASSED

---

### Catalog Tests

Command:
python manage.py test apps.catalog -v 2

Result:
10 catalog tests passed successfully.

Status:
PASSED

---

### Full Regression Test Suite

Command:
python manage.py test -v 2

Result:
20 tests passed successfully.

Status:
PASSED

---

## Phase 05 - Django Admin

Date:
2026-09-17

Status:
COMPLETE

### Migration Check

Command:
python manage.py makemigrations --check --dry-run
python manage.py check

Result:
No changes detected.
System check identified no issues (0 silenced).

Status:
PASSED

---

### Admin Tests

Command:
python manage.py test apps.catalog -v 2
python manage.py test -v 2

Result:
Ran 17 tests for apps.catalog in 7.376s... OK
Ran 27 full suite tests in 14.925s... OK

Status:
PASSED

---

## Phase 06 - Arabic RTL Base Interface

Date:
2026-09-17

Status:
COMPLETE

### Migration Safety Check

Command:
python manage.py makemigrations --check --dry-run
python manage.py check

Result:
No changes detected.
System check identified no issues (0 silenced).

Status:
PASSED

---

### Core Interface Tests

Command:
python manage.py test apps.core -v 2

Result:
8 core tests passed successfully.

Status:
PASSED

---

### Accounts Regression Tests

Command:
python manage.py test apps.accounts -v 2

Result:
10 accounts tests passed successfully.

Status:
PASSED

---

### Full Regression Test Suite

Command:
python manage.py test -v 2

Result:
35 tests passed successfully.

Status:
PASSED

---

## Phase 07 - Home Page and Catalog Listing

Date:
2026-09-17

Status:
COMPLETE

### Migration Safety Check

Command:
python manage.py makemigrations --check --dry-run
python manage.py check

Result:
No changes detected.
System check identified no issues (0 silenced).

Status:
PASSED

---

### Core, Catalog & Accounts Tests

Command:
python manage.py test apps.core apps.catalog apps.accounts -v 2
python manage.py test -v 2

Result:
Ran 45 tests in 21.131s... OK
Ran 45 full suite tests in 21.345s... OK

Status:
PASSED

---

## Phase 07 - Test Cleanup

Date:
2026-09-17

Status:
COMPLETE

### Migration Safety Check

Command:
python manage.py check
python manage.py makemigrations --check --dry-run

Result:
System check identified no issues (0 silenced).
No changes detected.

Status:
PASSED

---

### Core, Catalog & Accounts Tests

Command:
python manage.py test apps.core -v 2
python manage.py test apps.catalog -v 2
python manage.py test apps.accounts -v 2
python manage.py test -v 2

Result:
Core: 13 tests passed successfully.
Catalog: 25 tests passed successfully.
Accounts: 10 tests passed successfully.
Full Suite: Ran 48 tests in 22.334s... OK

Status:
PASSED

---

## Phase 08 - Book, Author and Category Detail Pages

Date:
2026-09-18

Status:
COMPLETE

### Migration Safety Check

Command:
python manage.py makemigrations --check --dry-run
python manage.py check

Result:
No changes detected.
System check identified no issues (0 silenced).

Status:
PASSED

---

### Core, Catalog & Accounts Tests

Command:
python manage.py test apps.catalog -v 2
python manage.py test apps.core -v 2
python manage.py test apps.accounts -v 2
python manage.py test -v 2

Result:
Catalog: Ran 32 tests in ~8s... OK
Core: Ran 14 tests in ~2s... OK
Accounts: Ran 10 tests in ~8s... OK
Full Suite: Ran 56 tests in 22.099s... OK

Status:
PASSED

---

## Phase 09 - Book Search and Filtering

Date:
2026-09-18

Status:
COMPLETE

### Migration Safety Check

Command:
python manage.py makemigrations --check --dry-run
python manage.py check

Result:
No changes detected.
System check identified no issues (0 silenced).

Status:
PASSED

---

### Core, Catalog & Accounts Tests

Command:
python manage.py test apps.catalog -v 2
python manage.py test apps.core -v 2
python manage.py test apps.accounts -v 2
python manage.py test -v 2

Result:
Catalog: Ran 50 tests in ~11s... OK
Core: Ran 14 tests in ~3s... OK
Accounts: Ran 10 tests in ~9s... OK
Full Suite: Ran 74 tests in 23.518s... OK

Status:
PASSED

---

## Phase 10 - Subscription Data Models

Date:
2026-09-18

Status:
COMPLETE

### Migration Created

apps/subscriptions/migrations/0001_initial.py

Command:
python manage.py makemigrations subscriptions
python manage.py migrate

Result:
Migration created and applied successfully.

Status:
PASSED

---

### System Check

Command:
python manage.py check

Result:
System check identified no issues (0 silenced).

Status:
PASSED

---

### Full Test Suite

Command:
python manage.py test -v 2

Result:
Subscriptions: Ran 19 tests... OK
Catalog: Ran 50 tests... OK
Core: Ran 14 tests... OK
Accounts: Ran 10 tests... OK
Full Suite: Ran 93 tests in 59.055s... OK

Status:
PASSED

---

## Phase 11 - Manual Subscription Workflow

Date:
2026-09-18

Status:
COMPLETE

### Migration Check

Command:
python manage.py makemigrations --check --dry-run

Result:
No changes detected.

Status:
PASSED

---

### System Check

Command:
python manage.py check

Result:
System check identified no issues (0 silenced).

Status:
PASSED

---

### Full Test Suite

Command:
python manage.py test -v 2

Result:
Subscriptions: Ran 46 tests... OK
Catalog: Ran 50 tests... OK
Core: Ran 14 tests... OK
Accounts: Ran 10 tests... OK
Full Suite: Ran 120 tests in 90.695s... OK

Status:
PASSED

---

## Phase 12 - Subscription Access Control

Date:
2026-09-18

Status:
COMPLETE

### Migration Check

Command:
python manage.py makemigrations --check --dry-run

Result:
No changes detected.

Status:
PASSED

---

### System Check

Command:
python manage.py check

Result:
System check identified no issues (0 silenced).

Status:
PASSED

---

### Full Test Suite

Command:
python manage.py test -v 2

Result:
Subscriptions: Ran 66 tests... OK
Catalog: Ran 50 tests... OK
Core: Ran 14 tests... OK
Accounts: Ran 10 tests... OK
Full Suite: Ran 140 tests in 97.895s... OK

Status:
PASSED

---

## Phase 13 - PDF Reader MVP

Date:
2026-09-18

Status:
COMPLETE

### Migration Check

Command:
python manage.py makemigrations --check --dry-run

Result:
No changes detected.

Status:
PASSED

---

### System Check

Command:
python manage.py check

Result:
System check identified no issues (0 silenced).

Status:
PASSED

---

### Full Test Suite

Command:
python manage.py test -v 2

Result:
Reading: Ran 26 tests... OK
Subscriptions: Ran 74 tests... OK
Catalog: Ran 50 tests... OK
Core: Ran 14 tests... OK
Accounts: Ran 10 tests... OK
Full Suite: Ran 174 tests in 138.626s... OK

Status:
PASSED

---

### Security Verification

- Direct /media/books/pdfs/ access: BLOCKED (403 Forbidden via url interceptor)
- pdf_file.url in templates: NOT FOUND (grep confirmed)
- receipt_file.url in templates: NOT FOUND (grep confirmed)
- Reader uses protected /read/<pk>/file/ endpoint only: CONFIRMED
- PDF streaming secured server-side: CONFIRMED
- No reading progress implemented: CONFIRMED

---

## Phase 14 - Favorites

### Full Test Suite

Command:
python manage.py test -v 2

Result:
Reading: Ran 52 tests... OK
Subscriptions: Ran 74 tests... OK
Catalog: Ran 50 tests... OK
Core: Ran 14 tests... OK
Accounts: Ran 10 tests... OK
Full Suite: Ran 200 tests in 159.076s... OK

Status:
PASSED

---

### Security Verification

- Favorite toggle requires POST: CONFIRMED (405 Method Not Allowed on GET)
- Favorite toggle requires authentication: CONFIRMED (302 to login)
- CSRF token present in favorite forms: CONFIRMED
- Only published books can be favorited: CONFIRMED (404 on unpublished)
- No direct PDF URLs exposed in favorites list: CONFIRMED
- Users can only see their own favorites: CONFIRMED

---

## Phase 15 - Reading Progress

Date:
2026-09-18

Status:
COMPLETE

### Application Test Suites

Commands:

`.venv\Scripts\python.exe manage.py test apps.reading -v 2`

`.venv\Scripts\python.exe manage.py test apps.subscriptions -v 2`

`.venv\Scripts\python.exe manage.py test apps.catalog -v 2`

`.venv\Scripts\python.exe manage.py test apps.core -v 2`

`.venv\Scripts\python.exe manage.py test apps.accounts -v 2`

Results:

- Reading: Ran 94 tests in 132.076s... OK
- Subscriptions: Ran 74 tests in 100.091s... OK
- Catalog: Ran 50 tests in 7.720s... OK
- Core: Ran 14 tests in 5.976s... OK
- Accounts: Ran 10 tests in 9.289s... OK

Status:
PASSED

---

### Full Test Suite

Command:
`.venv\Scripts\python.exe manage.py test`

Result:
Ran 242 tests in 252.900s... OK

Status:
PASSED

---

### Phase 15 Coverage Verification

- ReadingProgress is unique per user and book: CONFIRMED
- User A cannot overwrite user B ReadingProgress: CONFIRMED
- Forged user and user_id POST values cannot change ownership: CONFIRMED
- Expired and future subscribers cannot update progress: CONFIRMED
- Saved progress cannot bypass reader subscription access: CONFIRMED
- Progress updates require POST; GET returns 405: CONFIRMED
- Page 0 and negative page numbers return 400: CONFIRMED
- Reader resumes from the authenticated user's saved page: CONFIRMED
- Favorite behavior remains passing in the reading regression suite: CONFIRMED

---

### Final Verification

Commands:

`.venv\Scripts\python.exe manage.py check`

`.venv\Scripts\python.exe manage.py makemigrations --check --dry-run`

`git diff --check`

Results:

- Django system check identified no issues (0 silenced).
- Migration consistency check reported no changes detected.
- Git diff check passed; only informational LF-to-CRLF warnings were emitted.

Status:
PASSED

### Security Search

Search terms:

- `pdf_file.url`: no runtime or template usage; matches are negative test assertions and historical test documentation.
- `receipt_file.url`: no runtime or template usage; the only match is historical test documentation.
- `csrf_exempt`: no matches.
- `/media/books/pdfs/`: matches are the blocking URL interceptor, security tests, and documentation.
- `/media/subscriptions/receipts/`: matches are security tests only.

Status:
PASSED

---

## Phase 16 - My Library Dashboard

Date:
2026-09-18

Status:
COMPLETE

### Django System Check

Command:
`.venv\Scripts\python.exe manage.py check`

Result:
System check identified no issues (0 silenced).

Status:
PASSED

---

### Application Test Suites

Commands:

`.venv\Scripts\python.exe manage.py test apps.reading -v 2`

`.venv\Scripts\python.exe manage.py test apps.subscriptions -v 2`

`.venv\Scripts\python.exe manage.py test apps.catalog -v 2`

`.venv\Scripts\python.exe manage.py test apps.core -v 2`

`.venv\Scripts\python.exe manage.py test apps.accounts -v 2`

Results:

- Reading: Ran 124 tests in 178.850s... OK
- Subscriptions: Ran 74 tests in 96.712s... OK
- Catalog: Ran 50 tests in 7.836s... OK
- Core: Ran 14 tests in 6.455s... OK
- Accounts: Ran 10 tests in 8.983s... OK

Status:
PASSED

---

### Full Test Suite

Command:
`.venv\Scripts\python.exe manage.py test`

Result:
Ran 272 tests in 301.105s... OK

Status:
PASSED

---

### Dashboard Verification

- Anonymous users are redirected to login: CONFIRMED
- Logged-in users without an active subscription can view My Library: CONFIRMED
- Expired subscribers can view My Library: CONFIRMED
- Active subscription status is displayed using the existing service: CONFIRMED
- Favorites and reading progress are filtered by request.user: CONFIRMED
- Forged user and user_id query parameters do not change ownership: CONFIRMED
- Another user's favorites and reading progress are hidden: CONFIRMED
- Unpublished books are hidden without deleting saved records: CONFIRMED
- Continue Reading links use reading:reader: CONFIRMED
- Dashboard does not link to reading:pdf_file or expose raw media paths: CONFIRMED
- Existing Phase 13 PDF protection tests pass: CONFIRMED
- Existing Phase 14 Favorites tests pass: CONFIRMED
- Existing Phase 15 ReadingProgress tests pass: CONFIRMED
- No new model or migration was created: CONFIRMED

---

### Final Verification

Commands:

`.venv\Scripts\python.exe manage.py makemigrations --check --dry-run`

`git diff --check`

Results:

- Migration consistency check reported no changes detected.
- Git diff check passed; only informational LF-to-CRLF warnings were emitted.
- No runtime or template usage of `pdf_file.url` or `receipt_file.url` was found.
- No application code uses `csrf_exempt`.
- Raw PDF and receipt media path matches are limited to protection code, tests, and documentation.

Status:
PASSED

---

## Phase 17 - Validation and Security Hardening

Date:
2026-09-18

Status:
COMPLETE

### Hardening Implemented

- Added reusable server-side upload validation without new dependencies.
- Receipt policy: PDF, JPG/JPEG, or PNG; maximum 5 MiB; empty files rejected; extension and file signature must match.
- Book PDF policy: PDF only; maximum 50 MiB; empty files rejected; filename extension and `%PDF-` signature required.
- Model validation covers Django Admin and the subscription request ModelForm; no model field or migration changed.
- Favorite redirects now use `url_has_allowed_host_and_scheme()`; external and protocol-relative destinations fall back to the book detail page.
- Receipt paths reject nested and traversal-like values before database/storage lookup.
- Receipt responses remain staff-only attachments with `nosniff` and `private, no-store`.
- Protected PDF responses remain subscription-gated inline PDF responses with `nosniff` and `private, no-store`.
- Registration and subscription creation explicitly allow only GET/POST; logout, Favorite changes, and ReadingProgress changes remain POST-only.
- CSRF enforcement was verified with clients that enforce CSRF checks.
- The subscription admin approval action no longer swallows broad exceptions; transaction rollback and error propagation are tested.
- Subscription activity consistently uses `start_at <= now < end_at`.
- DEBUG and ALLOWED_HOSTS are environment-aware; DEBUG=False was verified with an external SECRET_KEY.

### Intermediate Verification Issue

- An initial focused run found 107 tests with one failure in `test_oversized_receipt_is_rejected`.
- Cause: Django's multipart encoder recalculated the upload size, so the test's synthetic `size` override did not reach the validator.
- Resolution: the test now submits an actual payload larger than 5 MiB.
- The corrected test passed, and the later standalone and full suites passed completely.

### Django System Checks

Commands:

`.venv\Scripts\python.exe manage.py check`

`DEBUG=False` with a verification-only external `SECRET_KEY` and explicit `ALLOWED_HOSTS`: `.venv\Scripts\python.exe manage.py check`

Results:

- Default development check: System check identified no issues (0 silenced).
- DEBUG=False check: System check identified no issues (0 silenced).

Status:
PASSED

---

### Application Test Suites

Commands:

`.venv\Scripts\python.exe manage.py test apps.reading -v 2`

`.venv\Scripts\python.exe manage.py test apps.subscriptions -v 2`

`.venv\Scripts\python.exe manage.py test apps.catalog -v 2`

`.venv\Scripts\python.exe manage.py test apps.core -v 2`

`.venv\Scripts\python.exe manage.py test apps.accounts -v 2`

Results:

- Reading: Ran 127 tests in 180.670s... OK
- Subscriptions: Ran 87 tests in 117.620s... OK
- Catalog: Ran 56 tests in 9.436s... OK
- Core: Ran 14 tests in 6.669s... OK
- Accounts: Ran 18 tests in 17.157s... OK

Status:
PASSED

---

### Full Test Suite

Command:
`.venv\Scripts\python.exe manage.py test`

Result:
Ran 302 tests in 335.631s... OK

Status:
PASSED

---

### Security Verification

- No GET endpoint modifies application state: CONFIRMED
- User-specific subscription requests, Favorites, ReadingProgress, and My Library data remain filtered by `request.user`: CONFIRMED
- Forged subscription user/status/reviewer fields are ignored: CONFIRMED
- Forged Favorite and ReadingProgress ownership fields are ignored: CONFIRMED
- Unpublished books remain hidden from all public, personal, reader, and PDF views: CONFIRMED
- Future and expired subscriptions cannot obtain reader/PDF/progress access: CONFIRMED
- Saved progress and Favorites cannot bypass PDF subscription checks: CONFIRMED
- Direct `/media/books/pdfs/` access remains blocked: CONFIRMED
- Public and non-staff users cannot retrieve receipts: CONFIRMED
- Receipt traversal and nested path attempts return 404: CONFIRMED
- Unsafe login and Favorite `next` values are rejected: CONFIRMED
- CSRF middleware remains enabled and no `csrf_exempt` usage exists: CONFIRMED
- No template uses `|safe`, `mark_safe`, or `autoescape off`: CONFIRMED
- No runtime/template code exposes `pdf_file.url` or `receipt_file.url`: CONFIRMED
- Secret scan found only the explicitly named development fallback, environment references, placeholders, and test credentials: CONFIRMED
- `.env`, `db.sqlite3`, uploaded media, and `.venv` remain ignored: CONFIRMED

---

### Final Verification

Commands:

`.venv\Scripts\python.exe manage.py makemigrations --check --dry-run`

`git diff --check`

Results:

- Migration consistency check reported no changes detected.
- Git diff check passed; only informational LF-to-CRLF warnings were emitted.
- No migration was created for Phase 17.

Status:
PASSED

---

## Phase 18 - Full Test Suite and Regression Pass

Date:
2026-09-18

Status:
COMPLETE

### Scope

- Re-audited authentication, catalog visibility/search, subscription requests and admin review, active-subscription boundaries, protected PDFs, receipt security, Favorites, ReadingProgress, My Library, upload validation, HTTP methods/CSRF, template exposure, URL routing, and database constraints.
- Reproduced the untouched Phase 17 baseline before changing code.
- Exercised the anonymous, registered non-subscriber, active subscriber, expired subscriber, and staff journeys through the existing Django test infrastructure.

### Untouched Baseline

- Accounts: Ran 18 tests in 14.304s... OK
- Catalog: Ran 56 tests in 9.748s... OK
- Subscriptions: Ran 87 tests in 116.297s... OK
- Reading: Ran 127 tests in 188.774s... OK
- Core: Ran 14 tests in 6.406s... OK
- Full suite: Ran 302 tests in 334.027s... OK

An initial Subscriptions invocation reached the command runner's 120-second ceiling near completion; it showed no test failure. The same untouched suite was rerun with a longer ceiling and completed successfully with the result above.

### Regression Discovered and Fixed

- Discovered that the dedicated Favorites page filtered by user but not by publication status, allowing an already-favorited book to remain visible after it was unpublished.
- Fixed the query with `book__is_published=True`, matching the established public catalog and My Library visibility rule.
- No other V1 regression was found.

### Regression Tests Added

- Unpublished books are hidden from the dedicated Favorites page.
- Reader resume JavaScript clamps a saved page to the loaded PDF's valid page range.
- Book PDF and receipt validators restore the upload file cursor after signature reads.
- Valid `.jpeg` and PNG receipt uploads are accepted in addition to the already-covered PDF/JPG paths.
- Protected JPEG and PNG receipts return `image/jpeg` and `image/png` respectively.
- Registration and subscription request creation reject unsupported HTTP methods.
- An ordinary user cannot execute a subscription admin action.

Focused result:
Ran 9 tests in 12.079s... OK

### Final Application Test Suites

Commands:

`.venv\Scripts\python.exe manage.py test apps.accounts -v 2`

`.venv\Scripts\python.exe manage.py test apps.catalog -v 2`

`.venv\Scripts\python.exe manage.py test apps.subscriptions -v 2`

`.venv\Scripts\python.exe manage.py test apps.reading -v 2`

`.venv\Scripts\python.exe manage.py test apps.core -v 2`

Results:

- Accounts: Ran 19 tests in 17.451s... OK
- Catalog: Ran 57 tests in 9.559s... OK
- Subscriptions: Ran 92 tests in 127.662s... OK
- Reading: Ran 129 tests in 189.442s... OK
- Core: Ran 14 tests in 6.667s... OK

Status:
PASSED

### Final Full Test Suite

Command:
`.venv\Scripts\python.exe manage.py test`

Result:
Ran 311 tests in 351.697s... OK

Status:
PASSED

### System, Migration, and Configuration Checks

- Default `manage.py check`: System check identified no issues (0 silenced).
- `DEBUG=False` check with a verification-only external SECRET_KEY and explicit ALLOWED_HOSTS: System check identified no issues (0 silenced).
- `manage.py makemigrations --check --dry-run`: No changes detected.
- No Phase 18 migration was created.

### Regression Outcome

- Authentication, catalog, subscription workflow, admin review, active-subscription boundaries, PDF access, receipt security, Favorites, ReadingProgress, My Library, ownership isolation, CSRF, HTTP methods, routes, and database integrity: PASSED.
- Raw PDF access remains blocked; receipts remain staff-only; traversal/nested receipt paths remain rejected.
- No user-facing template exposes a protected PDF or receipt storage URL.
- Phase 19 remains NOT_STARTED.
