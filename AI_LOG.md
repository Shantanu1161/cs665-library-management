AI Assistance Log
CS665 Project 3 - Library Management System
Shantanu Rajesh Sawarkar


Overview

This file documents the Generative AI assistance I used while building this project. The course AI policy requires disclosure of every AI interaction along with the prompt, the output, and what I changed. I used Claude (claude.ai and the Claude Code CLI) throughout most phases of the project. Rather than try to recall every single chat turn, I have organized the log by phase and by the artifact AI helped me produce. For each entry I describe what I asked, what the AI gave me, and what I did with it.

Tools used: Claude (Anthropic, web app and CLI), occasional inline code suggestions in my IDE.


Phase 1 - Database design and normalization

I started with the four-table schema I had designed in an earlier assignment - Users, Books, Loans, Reviews. Before writing any code I wanted to make sure the schema was clean and in 3NF.

Prompt I used (paraphrased from a longer back-and-forth):
"Here is my Loans table: loan_id, user_id, book_id, loan_date, due_date, return_date, status, fine_amount. Are there any 3NF violations and how should I fix them?"

What the AI gave me:
It pointed out that fine_amount has a transitive dependency through return_date - the fine is calculated as a function of (return_date - loan_date) so storing it as a column means it can fall out of sync if return_date is ever changed without recalculating. It also said status (Borrowed vs Returned) is derivable from whether return_date is null, which is the same problem. It offered two fixes - either drop the columns and compute on the fly every query, or keep them as cached values that get re-synced inside the same transaction that touches return_date.

What I did:
I went with the cached/transactional option because the rubric expects fine calculation to be a visible feature. I wrote the NORMALIZATION.md document myself - the AI only flagged the violation, I wrote the actual analysis section, the anomaly walkthrough (update/insert/delete), the 1NF/2NF/3NF check, and the final ER diagram. I also added candidate-key analysis for the Reviews table that wasn't in the AI response.

The DDL itself I asked Claude to draft as a starting point and then I edited it. The version that ended up in schema.sql adds created_at and updated_at columns to every table (not in the AI's first draft), the phone and membership_type columns on Users, and the due_date column on Loans. I also removed CASCADE deletes that the AI had suggested because I wanted explicit application-level guards instead of silent destruction of loan history.


Phase 2 - Backend (FastAPI)

I asked Claude to help me with the backend in stages. The biggest single contribution was the overall route layout and the transaction patterns.

Prompt:
"I want a FastAPI backend for this library system using sqlite3 (no SQLAlchemy). What route layout would you recommend for books CRUD, members CRUD, loan issue/return, reviews, and a dashboard?"

Output:
Resource-based routes - /books, /members, /borrows, /reviews, /dashboard. Pydantic for request validation. A startup hook that creates and seeds the database. Use sqlite3.Row as the row factory so I can treat rows like dicts.

Modifications:
I added a /genres endpoint that wasn't in the AI's suggestion - I needed it for the genre filter dropdown on the frontend. I also wrote the dashboard SQL myself. The dashboard query uses COUNT, AVG, SUM, GROUP BY genre, and a subquery for top-borrowed books. The AI did not write that query - I wrote it from scratch based on what I needed the frontend to display, then iterated until the numbers looked right.

I dropped the AI's suggestion of wrapping everything in a Database class. For a single-file backend it just added boilerplate. A flat get_db() function is easier to read.

For the borrow transaction I asked specifically about the SQLite transaction pattern in Python:

Prompt:
"In sqlite3, how do I make a borrow operation atomic - check available_copies, insert into Loans, decrement available_copies on Books, all-or-nothing?"

Output:
Use BEGIN/COMMIT/ROLLBACK explicitly inside try/except. The sqlite3 module wraps things in implicit transactions but being explicit is clearer. On any exception, rollback. The example just had INSERT + UPDATE in the same transaction.

Modifications:
The AI's example only checked book availability. I added: a check that the member exists, a check that the member is active (active = 1), and a guard that rejects the borrow if the member already has an unreturned copy of the same book. The due_date calculation (today + timedelta(days=req.days)) is mine, with days configurable per loan. The whole return endpoint and the fine recalculation logic - max(0, (return_date - due_date).days) * 2 - I wrote myself, modelled on the same transaction structure.

For validation I asked what makes sense for a system like this:

Prompt:
"What server-side validation should I add to a library API? I want to use Pydantic where it fits."

Output:
min_length on required strings, ge/gt on numeric fields, EmailStr for email (which needs the email-validator package), Field(ge=1, le=5) for ratings.

Modifications:
I skipped EmailStr because it adds a dependency and I'd rather use the UNIQUE constraint on email plus a try/except on sqlite3.IntegrityError to catch duplicates - simpler. I added the cross-field rule that available_copies cannot exceed total_copies, the deletion guards (you can't delete a book or member with active loans - returns HTTP 400), and the email lowercasing for case-insensitive uniqueness. None of those were in the AI response.


Phase 3 - Frontend

The frontend is a single-page app served as static files - index.html, css/styles.css, js/app.js - that talks to the FastAPI backend over fetch.

Prompt for the design direction:
"I want a clean admin frontend for a library system. Five pages - Dashboard, Books, Members, Borrows, Reviews. Suggest a visual style and a layout."

Output:
A dark sidebar with gold accents to evoke a classic library feel. Playfair Display for headings, DM Sans for body. Stat cards on the dashboard. Modal dialogs for CRUD instead of separate pages. A toast notification system. Debounced search inputs.

Modifications:
This was just a direction, no code yet. The actual color values, the badge system (green/orange/red for available/limited/unavailable), the genre bar chart (built with plain divs, no chart library), and the overall layout decisions are mine.

For the actual code I asked Claude Code to scaffold the SPA based on the direction above. It produced a first pass of the HTML structure, the CSS, and the JS. I then did the following on top of that scaffold:

- Added the API health-check pill in the topbar (green when connected, red when offline)
- Added the fine display in the toast on book return ("Book returned. Fine: $14")
- Filtered the borrow modal to only show books with available_copies > 0 - prevents the user from picking a book that can't be borrowed
- Filtered both the borrow and review modals to only show active members
- Made sure all the inputs use parseInt with fallbacks before sending to the API
- Tested the XSS escape function with titles containing quotes and angle brackets
- Refactored the single-file SPA into separate index.html, css/styles.css, and js/app.js for grading clarity

I considered the AI's suggestion to add Esc-to-close and click-outside-to-close on modals, and I rejected the click-outside part because it leads to accidental data loss in CRUD forms. I kept the explicit close button.


Phase 4 - Documentation

The README.md skeleton was drafted with AI help. I gave it the project description, the tech stack, and the route list, and asked it to put the README together with sections for install, database setup, usage, and a rubric checklist. I wrote in all the actual content - my name, the dependency versions, the sample data counts, the commit strategy, the data integrity section. The checklist that maps each rubric item to the implementation file/function is mine because I wanted each row to point at a specific place in the code.

The NORMALIZATION.md is my own writing as noted above.

This AI_LOG file is also my own writing.


Summary

Things that came primarily from AI:
- The route layout suggestion for the backend
- The SQLite transaction pattern (BEGIN/COMMIT/ROLLBACK with try/except)
- The first draft of the SPA HTML/CSS/JS scaffold
- The README skeleton

Things that are my own work:
- The NORMALIZATION.md analysis
- The dashboard SQL queries
- The /genres endpoint
- The cross-field validation rules and deletion guards
- The fine calculation logic
- The duplicate-loan guard and the active-member check on borrow
- The frontend filtering of modal dropdowns
- The fine-amount toast on return
- The API health pill
- The decision to reject click-outside-to-close on modals
- The split of the SPA into separate HTML/CSS/JS files
- The git commit strategy
- All design colors, badge logic, and the genre bar chart


Bugs I caught and fixed during testing

While clicking through the running app I noticed the dashboard's "Most Borrowed Books" panel showed Harry Potter with 6 borrows even though the Borrows page only listed 3 loans for that book. That mismatch should not be possible if the queries are consistent, so I went and read the SQL behind the dashboard.

The query I had originally accepted from the AI looked like this:

  SELECT b.title, COUNT(l.loan_id) AS borrow_count, ROUND(AVG(r.rating), 1) AS avg_rating
  FROM Books b
  LEFT JOIN Loans l ON b.book_id = l.book_id
  LEFT JOIN Reviews r ON b.book_id = r.book_id
  GROUP BY b.book_id
  ORDER BY borrow_count DESC

The bug is a classic SQL "fan trap". Joining one table (Books) to two siblings (Loans and Reviews) in the same statement produces a Cartesian product per book. A book with N loans and M reviews ends up with N*M rows in the joined set, so COUNT(loan_id) reports N*M instead of N. Harry Potter had 3 loans and 2 reviews after I added some test reviews, which is exactly why the count became 6.

I rewrote the query using two independent correlated subqueries, one for each aggregate, so neither count contaminates the other:

  SELECT b.title,
         (SELECT COUNT(*)              FROM Loans   l WHERE l.book_id = b.book_id) AS borrow_count,
         (SELECT ROUND(AVG(rating), 1) FROM Reviews r WHERE r.book_id = b.book_id) AS avg_rating
  FROM Books b
  ORDER BY borrow_count DESC, b.title ASC
  LIMIT 5

After the fix I cross-checked the dashboard against the /borrows endpoint and the counts now match exactly. The fix is in commit 8d1990a.

Lesson for myself: AI-generated SQL involving multiple joins and aggregates needs a sanity check against the raw data before I trust the dashboard numbers. From here on I plan to verify any aggregate panel against an independent count of the underlying rows.


Statement

I have read every line of code that ended up in this submission. I can explain any function, query, or transaction in this codebase if asked. The AI accelerated the scaffolding but the architectural decisions, the database design, the validation rules, and the integration of all the pieces are mine.

Shantanu Rajesh Sawarkar
