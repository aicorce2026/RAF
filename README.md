# Arabic Library

Arabic Library is an Arabic-first RTL digital library project built with Django.

The V1 goal is to provide a simple subscription-based platform where users can:

- create an account
- log in
- browse books
- browse authors and categories
- search for books
- request a manual subscription
- upload a payment receipt
- read protected PDF books
- save favorite books
- resume reading from the last saved page

The project is intentionally developed incrementally.

## Current Status

Current phase:

Phase 01 - Django Project Bootstrap

Status:

NOT_STARTED

Phase 00 - Project Governance and Environment Preparation is complete.

The Django application itself has not been created yet.

## Technology Stack

Backend:

- Python 3.14
- Django 5.2 LTS

Frontend:

- Django Templates
- HTML5
- CSS
- Bootstrap 5 RTL
- Vanilla JavaScript

Database during local development:

- SQLite

PDF reader:

- PDF.js

Administration:

- Django Admin

Version control:

- Git

## V1 Django Applications

The planned Django applications are:

- core
- accounts
- catalog
- subscriptions
- reading

## V1 Main Models

The planned main models are:

- User (Django built-in)
- Author
- Category
- Book
- SubscriptionRequest
- Subscription
- Favorite
- ReadingProgress

## Development Environment

Project location on the current development machine:

D:\rafia\RAF

Virtual environment:

.venv

Activate the environment in Git Bash using:

source .venv/Scripts/activate

Verify Python using:

python --version

Verify Django using:

python -m django --version

## Install Dependencies

After activating the virtual environment:

python -m pip install -r requirements.txt

## Project Documentation

Important project continuity files:

- .agents/rules/project-constitution.md
- docs/PROJECT_STATE.md
- docs/PHASES.md
- docs/HANDOFF.md
- docs/DECISIONS.md
- docs/TEST_LOG.md

These documents are part of the project architecture.

The repository is the source of truth.

Do not rely on previous AI chat history when continuing development.

## Antigravity Continuity

Before a new Antigravity account modifies the project, it must read:

1. .agents/rules/project-constitution.md
2. README.md
3. docs/PROJECT_STATE.md
4. docs/PHASES.md
5. docs/HANDOFF.md
6. docs/DECISIONS.md
7. docs/TEST_LOG.md

It must then inspect:

pwd
git status
git branch --show-current
git log --oneline -5

If documentation and repository state disagree, implementation must stop until the inconsistency is resolved.

## Git Safety

Before significant Git operations:

pwd
git status

Do not use destructive Git commands without explicit approval.

The Git identity for this repository is configured locally so that unrelated Git training repositories remain independent.

## Deferred Features

The following are intentionally outside V1:

- EPUB
- audiobooks
- Arabic text-to-speech
- synchronized highlighting
- realistic page turning
- OCR
- online payment gateways
- native mobile applications
- AI recommendations
- AI book assistant
- advanced DRM

## Development Rule

Only one project phase should be implemented at a time.

A phase is complete only after:

- its acceptance criteria pass
- relevant checks/tests are executed
- PROJECT_STATE.md is updated
- HANDOFF.md is updated
- TEST_LOG.md is updated
- Git state is reviewed

Do not begin the next phase automatically.
