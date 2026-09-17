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

Phase 01 - Django Project Bootstrap

Current phase status:

NOT_STARTED

Current branch:

main

Last verified commit:

8f7e792 chore: initialize project repository

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

The first repository commit exists.

The project governance structure is currently being prepared.

The Django project itself has NOT been created yet.

No Django applications exist yet.

No database has been created yet.

No migrations have been run yet.

No business models exist yet.

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

Phase 00 is complete and committed.

The next implementation phase is:

Phase 01 - Django Project Bootstrap

Do not begin Phase 01 until the user explicitly approves continuing.

---

## Exact Next Action

Wait for explicit user approval.

After approval, begin:

Phase 01 - Django Project Bootstrap

Do not implement any later phase.

---

## Important Restrictions

Do NOT:

- create Django applications yet
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
- Last verified commit
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
