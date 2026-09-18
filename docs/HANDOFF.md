# PROJECT HANDOFF

Project: Arabic Library

Purpose:
This file allows a new Antigravity agent or account to continue the project safely without relying on previous chat history.

The repository is the source of truth.

---

## Mandatory Recovery Procedure

When a new Antigravity session starts, DO NOT modify code immediately.

Read these files in this exact order:

1. .agents/rules/project-constitution.md
2. README.md
3. docs/PROJECT_STATE.md
4. docs/PHASES.md
5. docs/HANDOFF.md
6. docs/DECISIONS.md
7. docs/TEST_LOG.md
8. requirements.txt

Then inspect the repository using:

pwd
git status
git branch --show-current
git log --oneline -5

If Django files already exist, inspect the files relevant to the current phase.

Compare the documentation with the actual repository.

If documentation and repository state disagree:

STOP.

Report the inconsistency before making changes.

---

## Current Project State

Current phase:

Phase: 15 - Reading Progress Tracking

Current phase status:

NOT_STARTED

Current branch:

main

Current HEAD:

Do not hard-code the current HEAD in this document.

Always determine the current HEAD using:

git log --oneline -1

Historical baseline commit:

8f7e792 chore: initialize project repository

Phase 00 governance completion commit:

37ea6f3 docs: establish project governance and continuity

---

## Current Environment

Operating system:

Windows

Terminal:

Git Bash

Python:

3.14.7

Virtual environment:

.venv

Django:

5.2.17

Git:

2.45.1.windows.1

---

## Current Situation

The Python environment is ready.
Django is installed.
Git is initialized.

The base Django project has been created in the repository root.
The configuration package is named `config`.
The development server starts successfully and the default page is reachable.
The SQLite database `db.sqlite3` has been created and initial migrations applied.

The five Django applications (core, accounts, catalog, subscriptions, reading) have been created in the `apps` package.
They are registered in `INSTALLED_APPS` and their URL namespaces are included in the root `urls.py`.
Basic authentication (registration, login, POST logout, protected profile) is implemented using Django's built-in User model.
No custom User model or project migrations were created for accounts. Authentication tests passed.
Catalog data models (Author, Category, Book) are created with PROTECT foreign keys and a FileField for PDF storage.
Catalog migration was successfully created and applied locally. All catalog and regression tests passed.
Django Admin is configured with AuthorAdmin, CategoryAdmin, and BookAdmin, providing appropriate list displays, filters, and search functionality.
The project uses an Arabic RTL base interface powered by Bootstrap 5 RTL, with shared navigation and a minimal home page. All authentication templates extend this base.
The home page and /books/ listing view now use real database catalog queries (filtering only for published books and using select_related). No PDF links are exposed.
Book, Author, and Category detail pages are implemented and public, enforcing is_published=True visibility.
A robust, case-insensitive book search and filtering system is available on the book listing page using Django Q objects.
SubscriptionRequest and Subscription data models are fully implemented in apps/subscriptions with migration 0001_initial applied.
Manual subscription workflow: users submit requests via /subscriptions/request/, view status at /subscriptions/. Admins approve/reject via Django Admin actions. Approval creates exactly one 30-day Subscription.
Subscription access control: has_active_subscription() in services.py, active_subscription_required decorator in decorators.py. Public catalog pages remain fully public.
Protected PDF reader in apps/reading: /read/<pk>/ (reader page), /read/<pk>/file/ (streaming endpoint). Direct /media/books/pdfs/ access is blocked by a 403-returning URL interceptor in config/urls.py. PDF.js loaded via CDN. Favorites feature is fully implemented, allowing users to add and remove books from their favorites.

---

## Governance Files Completed So Far

Completed:

- .agents/rules/project-constitution.md
- docs/PROJECT_STATE.md
- docs/PHASES.md

Completed and reviewed:

- docs/HANDOFF.md
- docs/DECISIONS.md
- docs/TEST_LOG.md
- README.md
- .env.example

---

## Current Objective

Phase 14 is complete.

The next implementation phase is:

Phase 15 - Reading Progress Tracking

Do not begin Phase 15 until the user explicitly approves continuing.

---

## Exact Next Action

Wait for explicit user approval.

After approval, begin:

Phase 15 - Reading Progress Tracking

Do not implement any later phase.

---

## Important Restrictions

Do NOT:

- create Django applications yet
- create a custom User model (use Django's built-in User instead)
- create models yet
- create database migrations yet
- install additional packages
- add React, Node.js, Docker or other frameworks
- change the approved V1 architecture
- delete the virtual environment
- reset Git history
- delete migrations in future phases
- push automatically to a remote repository

---

## Git Safety

Before important Git operations always run:

pwd
git status

The expected project location is:

D:\rafia\RAF

The expected Git branch during the current phase is:

main

Do not execute destructive Git commands without explicit user approval.

---

## Session Handoff Procedure

Before changing to another Antigravity account:

1. Stop implementing new work.
2. Run git status.
3. Inspect git diff.
4. Run relevant tests or checks.
5. Update docs/PROJECT_STATE.md.
6. Update this HANDOFF.md.
7. Update docs/TEST_LOG.md.
8. Update docs/DECISIONS.md if an architectural decision changed.
9. Record the exact unfinished task.
10. Record known errors.
11. Record the last verified commit.
12. Suggest an appropriate Git commit message.

Never mark work complete merely because code was written.

---

## New Account Startup Procedure

A new Antigravity account must:

1. Read the project constitution.
2. Read all project state documentation.
3. Inspect git status.
4. Inspect current branch.
5. Inspect recent commits.
6. Inspect relevant project files.
7. Report its understanding before modifying files.

The new agent must report:

- Current phase
- Current phase status
- Current branch
- Current HEAD commit reported by git log
- Completed work
- Remaining work
- Known issues
- Relevant files
- Exact next action

The new agent must wait for user approval before continuing implementation.

---

## Known Issues

No known project application issues.

The application has not been created yet.

---

## Last Handoff Verification

Handoff prepared during:

Phase 00 - Project Governance and Environment Preparation

Repository status at the time of this document creation:

Governance files were committed successfully in commit 37ea6f3.
