# PROJECT PHASES

Project: Arabic Library
Version: V1

This file defines the official implementation order.

Rules:

- Work on one phase at a time.
- Do not skip phases.
- Do not implement features from future phases.
- A phase is COMPLETE only when all acceptance criteria pass.
- PROJECT_STATE.md determines the currently active phase.
- After completing a phase, update PROJECT_STATE.md, HANDOFF.md and TEST_LOG.md before continuing.

---

## Phase 00 - Project Governance and Environment Preparation

Status: COMPLETE

Goal:
Prepare a safe and repeatable development environment before creating the Django application.

Tasks:

- Verify Python.
- Create virtual environment.
- Install Django 5.2 LTS.
- Verify Git.
- Initialize repository.
- Configure repository-local Git identity.
- Create .gitignore.
- Create requirements.txt.
- Configure Antigravity Python interpreter.
- Create project constitution.
- Create project continuity documentation.
- Establish Git safety rules.

Acceptance Criteria:

- Python environment works.
- .venv is active and ignored by Git.
- Django is installed and version verified.
- Git repository is initialized.
- main branch exists.
- Initial Git commit exists.
- Antigravity uses .venv interpreter.
- project-constitution.md exists.
- PROJECT_STATE.md exists.
- PHASES.md exists.
- HANDOFF.md exists.
- DECISIONS.md exists.
- TEST_LOG.md exists.
- README.md exists.
- .env.example exists.
- Git working tree is reviewed before completion.

---

## Phase 01 - Django Project Bootstrap

Status: COMPLETE

Goal:
Create the base Django project.

Tasks:

- Create Django configuration package named config.
- Create manage.py.
- Configure base settings.
- Run initial Django migrations.
- Verify development server.
- Run Django system check.

Acceptance Criteria:

- manage.py exists.
- config package exists.
- Django development server starts.
- Initial migrations succeed.
- python manage.py check reports no errors.

---

## Phase 02 - Django Application Structure

Status: COMPLETE

Goal:
Create the approved Django application boundaries.

Applications:

- core
- accounts
- catalog
- subscriptions
- reading

Tasks:

- Create all five applications.
- Place applications under the approved project structure.
- Register applications in Django settings.
- Configure URL namespaces and inclusion structure.

Acceptance Criteria:

- All five applications load successfully.
- No unnecessary applications exist.
- URL configuration loads without errors.
- python manage.py check passes.

---

## Phase 03 - Authentication and User Accounts

Status: NOT_STARTED

Goal:
Implement the user system before business models depend on it.

Main Model:

User (Django built-in)

Tasks:

- Implement registration.
- Implement login.
- Implement logout.
- Implement basic profile page.
- Add authentication tests.

Acceptance Criteria:

- User registration works.
- Login works.
- Logout works.
- Passwords are hashed.
- Authentication tests pass.
- Django system check passes.

---

## Phase 04 - Catalog Data Models

Status: NOT_STARTED

Goal:
Create the core library data structure.

Models:

- Author
- Category
- Book

Tasks:

- Implement Author.
- Implement Category.
- Implement Book.
- Add model relationships.
- Create migrations.
- Test model relationships.

Acceptance Criteria:

- Migrations succeed.
- A Book can have multiple authors.
- A Book can have multiple categories.
- Model string representations are useful.
- Tests pass.
- Django system check passes.

---

## Phase 05 - Django Admin

Status: NOT_STARTED

Goal:
Use Django Admin as the V1 management interface.

Tasks:

- Register User.
- Register Author.
- Register Category.
- Register Book.
- Configure list displays.
- Configure search fields.
- Configure filters.
- Test cover upload.
- Test PDF upload.

Acceptance Criteria:

- Superuser can manage users.
- Superuser can manage authors.
- Superuser can manage categories.
- Superuser can create and edit books.
- Cover upload works locally.
- PDF upload works locally.

---

## Phase 06 - Arabic RTL Base Interface

Status: NOT_STARTED

Goal:
Create the shared Arabic RTL visual foundation.

Technologies:

- Django Templates
- HTML5
- Bootstrap 5 RTL
- CSS

Tasks:

- Create base.html.
- Create navbar.
- Create footer.
- Configure Arabic language direction.
- Create responsive page layout.
- Integrate authentication pages with base template.

Acceptance Criteria:

- HTML uses lang=ar.
- HTML uses dir=rtl.
- Desktop layout works.
- Mobile layout works.
- Shared navigation works.
- Existing pages use the base template.

---

## Phase 07 - Home Page and Catalog Listing

Status: NOT_STARTED

Goal:
Allow visitors to browse the library.

Tasks:

- Create home page.
- Display latest books.
- Display popular books.
- Display categories.
- Create book listing page.
- Show only published books.

Acceptance Criteria:

- Home page loads.
- Latest books display.
- Popular books display.
- Categories display.
- Published book list works.
- Unpublished books are hidden from ordinary users.

---

## Phase 08 - Book, Author and Category Detail Pages

Status: NOT_STARTED

Goal:
Provide detailed catalog navigation.

Tasks:

- Create book detail page.
- Create author detail page.
- Create category detail page.
- Configure named URLs.
- Handle missing objects correctly.

Acceptance Criteria:

- Book detail displays correctly.
- Author page lists related books.
- Category page lists related books.
- Missing objects return 404.
- Only published books appear to ordinary users.

---

## Phase 09 - Search and Filtering

Status: NOT_STARTED

Goal:
Allow users to find books easily.

Search Fields:

- Book title
- Author name
- Category name

Filters:

- Author
- Category

Acceptance Criteria:

- Title search works.
- Author search works.
- Category search works.
- Empty search is handled safely.
- Duplicate results are prevented.
- Only published books appear.

---

## Phase 10 - Subscription Data Models

Status: NOT_STARTED

Goal:
Create the data structure for manual subscriptions.

Models:

- SubscriptionRequest
- Subscription

Subscription Request Statuses:

- pending
- approved
- rejected

Tasks:

- Create models.
- Add payment receipt field.
- Add payment method.
- Add review information.
- Create subscription date logic.
- Create migrations.
- Add model tests.

Acceptance Criteria:

- Subscription request can be created.
- Status choices work.
- Subscription start and end dates work.
- Active status can be determined correctly.
- Expired status can be determined correctly.
- Tests pass.

---

## Phase 11 - Manual Subscription Workflow

Status: NOT_STARTED

Goal:
Allow users to request subscription activation manually.

User Flow:

- Choose subscription.
- Select payment method.
- Upload payment receipt.
- Wait for administrator review.

Administrator Flow:

- Review request.
- Approve request.
- Reject request.

Tasks:

- Create subscription forms and pages.
- Create subscription service functions.
- Create approval logic.
- Default approved subscription duration to 30 days.
- Prevent duplicate approval.

Acceptance Criteria:

- User can submit a request.
- Receipt can be uploaded.
- Request begins as pending.
- Administrator can approve.
- Approval creates a subscription.
- Administrator can reject.
- Duplicate approval is prevented.
- Tests pass.

---

## Phase 12 - Subscription Access Control

Status: NOT_STARTED

Goal:
Protect book reading using server-side authorization.

Rules:

- Anonymous users cannot read protected books.
- Logged-in users without subscription cannot read.
- Users with expired subscription cannot read.
- Users with active subscription may read.

Acceptance Criteria:

- All access scenarios work.
- Direct reader URL is protected.
- Frontend hiding is not the only protection.
- Access-control tests pass.

---

## Phase 13 - PDF Reader MVP

Status: NOT_STARTED

Goal:
Provide a basic protected PDF reader.

Technology:

PDF.js

Features:

- Load PDF.
- Display current page.
- Previous page.
- Next page.
- Current page number.
- Total pages.
- Zoom in.
- Zoom out.

Explicitly Deferred:

- Page flip animation.
- Two-page realistic layout.
- EPUB.
- Audio.
- TTS.
- Notes.
- Highlights.
- OCR.

Acceptance Criteria:

- Authorized user can open a book.
- Unauthorized user cannot open it.
- PDF renders correctly.
- Next and previous controls work.
- Zoom works.
- Basic desktop behavior works.
- Basic mobile behavior works.

---

## Phase 14 - Favorites

Status: NOT_STARTED

Goal:
Allow users to save books to their personal library.

Model:

Favorite

Tasks:

- Add favorite.
- Remove favorite.
- Show favorite state.
- Prevent duplicate favorites.

Acceptance Criteria:

- Add favorite works.
- Remove favorite works.
- Duplicate favorites cannot exist.
- Anonymous users cannot create favorites.
- Tests pass.

---

## Phase 15 - Reading Progress

Status: NOT_STARTED

Goal:
Remember the last page each user read.

Model:

ReadingProgress

Tasks:

- Save last page.
- Restore last page.
- Validate page numbers.
- Protect ownership of progress data.
- Keep one progress record per user and book.

Acceptance Criteria:

- Progress saves.
- Returning user resumes correctly.
- Duplicate progress records do not exist.
- Users cannot modify another user's progress.
- Tests pass.

---

## Phase 16 - My Library Dashboard

Status: NOT_STARTED

Goal:
Create the user's personal library area.

Display:

- Continue Reading.
- Favorites.
- Subscription status.

Acceptance Criteria:

- User sees only personal data.
- Favorites display correctly.
- Reading progress displays correctly.
- Subscription status displays correctly.
- Anonymous access is prevented.

---

## Phase 17 - Validation and Security Hardening

Status: NOT_STARTED

Goal:
Review V1 security before deployment.

Review Areas:

- Authentication.
- Authorization.
- CSRF.
- File uploads.
- PDF validation.
- Image validation.
- Receipt privacy.
- Subscription authorization.
- Object ownership.
- Environment variables.
- SECRET_KEY.
- DEBUG.
- ALLOWED_HOSTS.

Acceptance Criteria:

- No secrets are committed.
- Protected views enforce permissions.
- Payment receipts are private.
- File upload validation exists.
- Production configuration supports DEBUG=False.
- Security tests pass.

---

## Phase 18 - Full Test Suite and Regression Pass

Status: NOT_STARTED

Goal:
Verify all V1 functionality before deployment.

Test Areas:

- Registration.
- Login.
- Book visibility.
- Search.
- Subscription request.
- Subscription approval.
- Active subscription.
- Expired subscription.
- PDF access.
- Favorites.
- Reading progress.
- Object ownership.

Acceptance Criteria:

- python manage.py check passes.
- Full Django test suite passes.
- No known critical V1 regression remains.
- TEST_LOG.md contains results.

---

## Phase 19 - Production and Deployment Preparation

Status: NOT_STARTED

Goal:
Prepare the application for online deployment.

Tasks:

- Review requirements.txt.
- Review environment configuration.
- Configure SECRET_KEY externally.
- Configure DEBUG.
- Configure ALLOWED_HOSTS.
- Review static files.
- Review media files.
- Review migrations.
- Add error pages.
- Document deployment steps.

Acceptance Criteria:

- Fresh environment can install requirements.
- Production-like Django check succeeds.
- Secrets remain external.
- Deployment instructions exist.
- Migrations are current.

---

## Phase 20 - Free Demo Deployment and V1 Acceptance

Status: NOT_STARTED

Goal:
Deploy and verify the first online demonstration version.

Manual Acceptance Flow:

1. Register.
2. Login.
3. Browse books.
4. Search.
5. Submit subscription request.
6. Administrator approves request.
7. Open protected PDF.
8. Navigate pages.
9. Save favorite.
10. Save reading progress.
11. Logout.
12. Login again.
13. Confirm reading progress.
14. Confirm subscription status.

Acceptance Criteria:

- Demo deployment is accessible online.
- Main user journey works.
- Admin workflow works.
- Protected reader works.
- Persistence works.
- TEST_LOG.md contains final acceptance results.
- PROJECT_STATE.md marks V1 complete.

Do NOT begin V2 automatically.

---

# Deferred V2+ Features

The following features are intentionally outside V1:

- EPUB
- audiobooks
- Arabic text-to-speech
- synchronized word highlighting
- realistic page flipping
- two-page book layout
- OCR
- online payment gateways
- automatic recurring billing
- native Android application
- native iOS application
- AI recommendations
- AI book assistant
- advanced DRM
