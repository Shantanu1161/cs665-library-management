# 🤖 AI Assistance Log — CS665 Project 3

**Student:** Shantanu Rajesh Sawarkar
**Course:** CS665 — Database Management Systems
**Project:** Project 3 — Full-Stack Library Management System
**Date Range:** April 2026 – May 2026

---

## 0. Compliance Statement & Methodology

The use of Generative AI tools was **permitted** for this project as a research, brainstorming, and coding assistant. Per the project specification, every AI-assisted interaction must be disclosed.

I emailed Prof. Cody Farlow on **April 28, 2026** to clarify documentation expectations for an AI-assisted ("vibe-coding") workflow. His reply on the same day:

> *"Great question! My answer is to provide a step-by-step process. The more you use Gen AI the more documentation is needed. Overdocument to remove as much ambiguity as possible."*

Following his guidance, this log documents **every meaningful AI interaction** during the build of this project, in chronological order, with the **exact prompt**, the **AI's output summary**, and **my own modifications, verifications, and additions**.

### Tools Used

| Tool | Vendor | Used For |
|------|--------|----------|
| Claude (claude.ai desktop) | Anthropic | Architecture brainstorming, normalization audit |
| Claude Code (CLI) | Anthropic | Backend/frontend code generation, debugging |
| Antigravity (AI IDE) | Google | In-IDE refactoring suggestions |

---

## 1. Phase 1 — Schema Design & Normalization Audit

### Entry 1.1
**Date:** April 18, 2026
**Tool:** Claude (claude.ai)
**Phase:** Database Design

**Prompt:**
> "I have a Library Management System database with four tables: Users, Books, Loans, Reviews. Help me identify any 3rd Normal Form (3NF) violations in this schema and explain how to resolve them. The Loans table has columns: loan_id, user_id, book_id, loan_date, due_date, return_date, status, fine_amount."

**AI Output Summary:**
Claude identified two 3NF violations in the Loans table:
1. `fine_amount` has a transitive dependency: `loan_id → return_date → fine_amount` (since the fine is calculated as a function of return_date – loan_date).
2. `status` is derivable from whether `return_date IS NULL`, also a transitive dependency.

It recommended either (Option A) removing `fine_amount` entirely and computing it on every query, or (Option B) keeping it as a cached column that is synced transactionally on every return event.

**My Modifications:**
- Chose **Option B** because the project rubric explicitly requires demonstrating fine calculation as a visible, persistent feature.
- Wrote the entire `NORMALIZATION.md` document **myself** — Claude only provided the conceptual identification of the violations. The full anomaly section (update / insertion / deletion), 1NF/2NF/3NF verification table, and final ER relationships diagram are my own writing based on lecture notes.
- Added the candidate-key analysis (e.g., `(user_id, book_id)` in Reviews) myself.

---

### Entry 1.2
**Date:** April 19, 2026
**Tool:** Claude (claude.ai)
**Phase:** SQL DDL

**Prompt:**
> "Generate the SQLite DDL for these four normalized tables: Users (with email UNIQUE, membership_type, active flag), Books (with title UNIQUE, ISBN UNIQUE, year, total_copies, available_copies), Loans (with FK to users/books, status, fine_amount), Reviews (rating CHECK 1-5). Include FK constraints and helpful indexes."

**AI Output Summary:**
Claude produced a CREATE TABLE statement for each of the four tables with PRIMARY KEY AUTOINCREMENT, FOREIGN KEY constraints, and CHECK constraints on rating. It also suggested several indexes on FK columns.

**My Modifications:**
- Added `created_at` and `updated_at` DATE columns with `DEFAULT (date('now'))` to **every** table (not in AI output).
- Added the `phone` and `membership_type` columns to Users myself for richer member profiles.
- Added the `due_date` column to Loans (Claude's version only had loan_date and return_date).
- Replaced Claude's suggested CASCADE delete with explicit application-level guards in the API (so deleting a Book with active loans returns HTTP 400 instead of silently destroying loan history).

---

## 2. Phase 2 — Backend Architecture (FastAPI)

### Entry 2.1
**Date:** April 22, 2026
**Tool:** Claude (claude.ai)
**Phase:** Backend Planning

**Prompt:**
> "I am building a Library Management System backend in FastAPI with SQLite (using the built-in sqlite3 module, no SQLAlchemy). What route structure would you recommend for: books CRUD, members CRUD, loans (borrow/return), reviews, and a dashboard?"

**AI Output Summary:**
Claude proposed grouping endpoints by resource:
- `/books`, `/books/{id}` (GET, POST, PUT, DELETE)
- `/members`, `/members/{id}` (CRUD, with `/members` instead of `/users` to avoid confusion)
- `/borrows` for loan list, `POST /borrows` for issue, `PUT /borrows/{id}/return` for return
- `/reviews`
- `/dashboard` for aggregate stats

It also recommended Pydantic models for request validation, `sqlite3.Row` for dict-like row access, and an `init_db()` startup hook.

**My Modifications:**
- Added a **`/genres`** endpoint (not suggested by AI) to power the genre dropdown filter on the frontend.
- Replaced Claude's `Database` class wrapper with a flat `get_db()` function — simpler and more readable for a project of this scope.
- Designed the `/dashboard` aggregate query (COUNT, AVG, SUM, GROUP BY genre, top-borrowed books subquery) **myself** — Claude did not write the dashboard SQL.
- Added the active-only filter on `/borrows` myself (`?active_only=true`).

---

### Entry 2.2
**Date:** April 23, 2026
**Tool:** Claude Code (CLI)
**Phase:** Backend — Transaction Logic

**Prompt:**
> "In my FastAPI app I need a borrow endpoint that does these things atomically: 1) verify the member exists and is active, 2) verify the book has available_copies > 0, 3) insert a Loan row, 4) decrement available_copies on Books. Show the SQLite transaction pattern in Python's sqlite3 module."

**AI Output Summary:**
Claude explained that Python's `sqlite3` module by default opens an implicit transaction on the first DML statement and commits with `conn.commit()`. It suggested explicit `BEGIN` / `COMMIT` / `ROLLBACK` in a `try/except` block for clarity, and showed a pattern combining INSERT into Loans and UPDATE on Books inside one commit.

**My Modifications:**
- Added the `member.active` check (Claude only checked existence).
- Added a **duplicate-loan guard**: rejects the borrow if the member already has an unreturned copy of the same book (not in AI output).
- Added the `due_date = today + timedelta(days=req.days)` calculation myself, where `days` is configurable per loan.
- Wrote the parallel `/borrows/{id}/return` transaction myself, including the **fine recalculation** logic: `max(0, (return_date - due_date).days) * 2`.
- All `HTTPException` re-raise + `conn.rollback()` error handling was added by me to satisfy the rubric's requirement that "no bad data enter the database."

---

### Entry 2.3
**Date:** April 24, 2026
**Tool:** Claude Code (CLI)
**Phase:** Backend — Validation

**Prompt:**
> "What server-side validation should every endpoint in a library management FastAPI backend have? I want to prevent bad data and stay within Pydantic's built-in validators where possible."

**AI Output Summary:**
Claude listed: `min_length=1` for required strings, `ge=0` / `gt=0` for non-negative numeric fields, `EmailStr` for email validation (requires `email-validator` package), `pattern=` for enum-like fields (e.g., membership_type), and `Field(ge=1, le=5)` for ratings.

**My Modifications:**
- Chose **not** to use Pydantic's `EmailStr` because it adds an external dependency (`email-validator`) that complicates the install. I used a simple `"@" in email and "." in email` check plus the `UNIQUE` constraint on the email column with a `try/except sqlite3.IntegrityError` to catch duplicates.
- Added the **business-rule validations** myself that Claude did not mention:
  - `available_copies <= total_copies` (cross-field validation)
  - Cannot delete a book or member with an active loan (returns HTTP 400)
  - Borrow rejected if `available_copies < 1` even though the column itself allows 0
  - Borrow rejected if member is inactive (`active = 0`)
- Added the email lowercasing (`.lower()`) myself for case-insensitive uniqueness.

---

## 3. Phase 3 — Frontend (Single-Page App)

### Entry 3.1
**Date:** April 26, 2026
**Tool:** Claude (claude.ai)
**Phase:** UI/UX Design Direction

**Prompt:**
> "I want to design a single-page admin frontend for a Library Management System. Suggest a visual design language and layout pattern. The audience is library staff."

**AI Output Summary:**
Claude suggested:
- A dark sidebar with gold accent colors to evoke a "classic library" feel
- A serif font (Playfair Display) for headings, sans-serif (DM Sans) for body
- Card-based stat tiles on the dashboard (Books / Members / Active Loans / Overdue)
- Modal dialogs for CRUD operations rather than separate pages
- A toast notification system for action feedback
- A search-with-debounce pattern for filtering tables

**My Modifications:**
- The high-level direction was used; **all HTML, CSS, and JavaScript code was written from scratch** by me / Claude Code together (logged separately below in Entry 3.2). Claude.ai produced no actual code in this entry.
- Designed the badge color system myself: green/orange/red for available/limited/unavailable.
- Designed the genre breakdown bar chart myself (HTML divs + CSS, no chart library).
- Picked the exact color palette myself (`--gold: #c9a84c`, `--sidebar-bg: #0f1117`).

---

### Entry 3.2
**Date:** April 27, 2026
**Tool:** Claude Code (CLI)
**Phase:** Frontend Build

**Prompt:**
> "Generate a single-file `frontend/index.html` SPA for a library management system. Use Bootstrap 5 + Bootstrap Icons + custom CSS. It needs five pages — Dashboard, Books, Members, Borrows, Reviews — toggled by a sidebar nav. All CRUD operations use modal dialogs. Use the Fetch API to call a FastAPI backend at http://localhost:8000. Include toast notifications, debounced search, and XSS-safe HTML escaping."

**AI Output Summary:**
Claude Code produced a single `index.html` containing:
- Sidebar with five nav links and active-state styling
- Dashboard page with 6 stat cards, an active-borrows table, a genre bar chart, and a top-books table
- Books / Members / Borrows / Reviews pages each with a search toolbar and table
- 4 modal dialogs (Book, Member, Borrow, Review) with form validation
- An `api()` helper, `toast()` helper, `esc()` XSS-guard, and a `debounce()` utility
- A simple page navigation function `navigate(page)`

**My Modifications:**
- Verified the `api()` helper handles non-JSON error responses correctly (added `.catch(() => ({}))`).
- Added the **API health-check pill** in the topbar (green = connected, red = offline) — not in AI output.
- Added the **fine display in toast** on book return (e.g., "Book returned. Fine: $14") — my own UX touch.
- Added the **filter to only show available books in the borrow modal dropdown** (`books.filter(b => b.available_copies > 0)`) — prevents users from trying to borrow a book with 0 copies.
- Added the **filter to only show active members in dropdowns** (`members.filter(m => m.active)`).
- Verified all numeric inputs use `parseInt` with fallbacks before sending to the API.
- Tested that XSS escaping works correctly when book titles or member names contain quotes or angle brackets.

---

### Entry 3.3
**Date:** April 28, 2026
**Tool:** Antigravity (AI IDE inline suggestions)
**Phase:** Frontend Refinement

**Prompt:**
> *(In-IDE inline suggestion)* — "Suggest improvements for the modal close UX in this `closeModal(id)` function."

**AI Output Summary:**
Suggested adding `Esc` key listener and `click-outside-to-close` behavior on modal overlays.

**My Modifications:**
- Reviewed the suggestion. Decided **not** to add click-outside behavior because it leads to accidental data loss in CRUD forms. I kept the explicit X-button and Cancel-button approach for safety. I did add a small CSS animation (`@keyframes slideUp`) myself for visual polish.

---

## 4. Phase 4 — Documentation

### Entry 4.1
**Date:** April 29, 2026
**Tool:** Claude (claude.ai)
**Phase:** README

**Prompt:**
> "Help me draft a professional README.md for this Library Management System project. It should include project description, tech stack table, setup instructions, database setup, usage, API endpoints, functional requirements checklist, and contributor information."

**AI Output Summary:**
Claude provided a structured Markdown README skeleton with sections for overview, tech stack, install, database, usage, endpoint table, and a checklist mapping each rubric requirement to its implementation.

**My Modifications:**
- Filled in all the actual content (project description, my name, exact dependency versions) myself.
- Added the **3NF requirements checklist** with explicit ✅ markers tied to my specific implementation (transaction location, validation type, etc.) — Claude's version was generic.
- Wrote the **Git Commit Strategy** section listing the 7 incremental commits I planned, based on the rubric's "minimum 5 commits" rule.
- Added the **Sample Data** section listing the seeded users/books/loans counts myself.

---

## 5. Summary Table

| # | Tool | Phase | What AI Contributed | What I Did |
|---|------|-------|---------------------|------------|
| 1.1 | Claude.ai | Normalization | Identified 3NF violations in Loans (fine_amount, status) | Wrote full NORMALIZATION.md, anomaly analysis, ER diagram |
| 1.2 | Claude.ai | DDL | Initial CREATE TABLE statements | Added timestamps, phone/membership cols, due_date, removed CASCADE |
| 2.1 | Claude.ai | Routing | Suggested resource-based route layout | Added /genres, dashboard SQL, active-only filter |
| 2.2 | Claude Code | Transactions | Borrow transaction pattern | Added active check, dup-loan guard, fine calc, return endpoint |
| 2.3 | Claude Code | Validation | Pydantic validator suggestions | Added cross-field rules, deletion guards, email lowercasing |
| 3.1 | Claude.ai | UI direction | Color/font/layout suggestions | All design decisions and palette myself |
| 3.2 | Claude Code | Frontend code | Generated full index.html SPA | Verified, added health pill, fine toast, filter logic |
| 3.3 | Antigravity | UX polish | Suggested Esc-to-close & click-outside | Rejected click-outside (data loss risk), added animation |
| 4.1 | Claude.ai | README | Document skeleton | Wrote all real content, checklist, commit plan |

---

## 6. Attestation

I attest that:

1. **Every AI interaction** that produced any artifact in this submission is documented above.
2. I **read, understood, and verified** every line of AI-generated code before including it.
3. I made **substantive personal additions** to every AI-generated artifact — none of the deliverables are unmodified AI output.
4. I can **explain and defend** every design decision, transaction, validation, and SQL query in this project on request.
5. The normalization analysis, the dashboard SQL, the transaction-rollback handling, the cross-field validation rules, the fine calculation logic, and all UX safety decisions are **my own work**.

— Shantanu Rajesh Sawarkar
