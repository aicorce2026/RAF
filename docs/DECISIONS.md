# ARCHITECTURAL DECISIONS

Project: Arabic Library

This file records important technical and architectural decisions.

Do not change an accepted decision without:
1. explaining the reason
2. getting explicit user approval
3. recording the new decision here

---

## ADR-001 - Backend Framework

Status: ACCEPTED

Decision:

Use Django 5.2 LTS as the backend framework.

Reason:

- Mature framework.
- Strong built-in authentication.
- Built-in Django Admin.
- Built-in ORM.
- Suitable for a beginner.
- Reduces the number of external tools required.
- Appropriate for the V1 project scope.

Rejected for V1:

- FastAPI
- Flask
- Node.js backend
- NestJS

---

## ADR-002 - Python Version

Status: ACCEPTED

Decision:

Use Python 3.14.7 for local development.

Reason:

Python 3.14.7 is already installed and working correctly in the project environment.

Current virtual environment:

.venv

---

## ADR-003 - Development Database

Status: ACCEPTED

Decision:

Use SQLite during local V1 development.

Reason:

- Included with Python/Django workflow.
- No separate database server required.
- Easier for learning and development.
- Sufficient for the first project version.

Future consideration:

PostgreSQL may be introduced for production if needed.

---

## ADR-004 - Frontend Strategy

Status: ACCEPTED

Decision:

Use Django Templates with:

- HTML5
- CSS
- Bootstrap 5 RTL
- Vanilla JavaScript

Reason:

The project does not require a separate frontend framework for V1.

Rejected for V1:

- React
- Next.js
- Vue
- Angular
- Tailwind CSS

---

## ADR-005 - Arabic Interface

Status: ACCEPTED

Decision:

The user interface will be Arabic-first and RTL.

Required HTML configuration:

lang="ar"
dir="rtl"

Programming identifiers remain English.

---

## ADR-006 - PDF Reader

Status: ACCEPTED

Decision:

Use PDF.js for the V1 book reader.

V1 reader features:

- display PDF
- previous page
- next page
- current page number
- total page count
- zoom in
- zoom out

Deferred:

- realistic page flipping
- two-page book layout
- annotations
- highlighting
- EPUB
- OCR

---

## ADR-007 - Subscription Model

Status: ACCEPTED

Decision:

V1 will use manual subscription activation.

Flow:

1. User selects subscription.
2. User chooses a manual payment method.
3. User uploads a payment receipt.
4. Administrator reviews the request.
5. Administrator approves or rejects.
6. Approved request creates a 30-day subscription.

Reason:

This avoids payment-gateway complexity during V1 while preserving proper subscription logic.

Deferred:

- Stripe
- PayTabs
- recurring card billing
- automatic online payment confirmation

---

## ADR-008 - Admin Interface

Status: ACCEPTED

Decision:

Use Django Admin for V1 administration.

Reason:

Django Admin already provides secure CRUD functionality and reduces development time.

Do not build a custom administration dashboard during V1 unless explicitly approved.

---

## ADR-009 - Approved Django Applications

Status: ACCEPTED

Decision:

Use exactly these V1 Django applications:

- core
- accounts
- catalog
- subscriptions
- reading

Reason:

Each application has one clear responsibility.

Do not create additional applications without explicit approval.

---

## ADR-010 - Main V1 Models

Status: ACCEPTED

Decision:

The intended main models are:

- User
- Author
- Category
- Book
- SubscriptionRequest
- Subscription
- Favorite
- ReadingProgress

Additional persistent models require justification and approval.

---

## ADR-011 - Custom User Model

Status: ACCEPTED

Decision:

Create a custom User model based on Django AbstractUser before other business models depend on users.

Reason:

Changing AUTH_USER_MODEL later is significantly more difficult.

The V1 custom User model should remain minimal.

---

## ADR-012 - Git Strategy

Status: ACCEPTED

Decision:

Use Git from the beginning of development.

Current default branch:

main

Important rules:

- Inspect pwd before significant Git operations.
- Inspect git status before significant Git operations.
- Do not force push automatically.
- Do not use destructive Git commands without approval.
- Do not push automatically to a remote repository.

The project Git identity is configured locally to avoid interfering with unrelated Git training repositories.

---

## ADR-013 - Antigravity Continuity

Status: ACCEPTED

Decision:

The repository is the source of truth between Antigravity accounts.

Do not rely on previous AI chat memory.

Continuity files:

- .agents/rules/project-constitution.md
- docs/PROJECT_STATE.md
- docs/PHASES.md
- docs/HANDOFF.md
- docs/DECISIONS.md
- docs/TEST_LOG.md

A new Antigravity account must read these files before modifying the project.

---

## ADR-014 - Dependency Policy

Status: ACCEPTED

Decision:

Keep external dependencies minimal.

Before installing a new package:

- verify Django/Python cannot reasonably solve the problem
- explain why the package is needed
- record it in requirements.txt
- document major dependency decisions

---

## ADR-015 - Development Order

Status: ACCEPTED

Decision:

Develop the project phase-by-phase.

Do not skip phases.

Do not implement future features early.

Each phase must satisfy its acceptance criteria before the next phase starts.

The current phase is defined by:

docs/PROJECT_STATE.md

---

## ADR-016 - Deferred Features

Status: ACCEPTED

The following features are intentionally deferred beyond V1:

- EPUB
- audiobooks
- Arabic text-to-speech
- synchronized text highlighting
- realistic page turning
- OCR
- online payment gateways
- native mobile applications
- AI recommendations
- AI book assistant
- advanced DRM

These features must not be introduced during V1 without explicit approval.
