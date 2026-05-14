# 📚 Library Management System — CS665 Project 3

A full-stack Library Management System built with **Python (FastAPI)**, **SQLite**, and a **vanilla HTML/CSS/JS** frontend. This application provides complete CRUD operations across multiple related tables, transaction-safe borrow/return logic, server-side data validation, and a live analytics dashboard.

---

## 📌 Project Description

This application is designed for library staff and administrators to manage the library's daily operations — tracking books, registered members, book loans, and user reviews. It enforces strict data integrity through foreign key constraints, server-side validation, and transactional loan processing.

**Target Users:** Library administrators, staff, and student managers.

**Tech Stack:**
| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| Backend Framework | FastAPI |
| Database | SQLite (via sqlite3 standard library) |
| Frontend | HTML5, CSS3 (Bootstrap 5), Vanilla JavaScript SPA |
| Fonts | Google Fonts (Playfair Display + DM Sans) |
| Version Control | Git |

### Stack change disclosure (per Project Note 2)

The project rubric lists **Jinja2 templates** as the recommended frontend approach. I chose to build a **single-page application (SPA)** with Bootstrap 5 + vanilla JavaScript instead, communicating with the FastAPI backend over JSON via the Fetch API. This was a deliberate decision for the following reasons:

- **Cleaner separation of concerns.** The backend is a pure JSON API with no HTML rendering responsibilities, which makes it easier to test, document (via auto-generated Swagger UI at `/docs`), and reuse.
- **Better user experience.** No full-page reloads when adding/editing/deleting records. The dashboard, books, members, borrows, and reviews pages switch instantly.
- **Same rubric coverage.** All Part II functional requirements (CRUD, relationships, transactions, validation, dashboard) are satisfied identically; only the rendering layer is different.

The frontend uses Bootstrap 5 (CDN), Bootstrap Icons, and Google Fonts. No build step or framework — just plain HTML/CSS/JS files served by Python's built-in `http.server`.

---

## ⚡ Quick Start

### Easiest way — one command (recommended)

After cloning the repo, just run the launcher script. It will create the virtual environment, install dependencies, start both the backend and the frontend, and open the app in your browser.

**macOS / Linux:**
```bash
git clone https://github.com/Shantanu1161/cs665-library-management.git
cd cs665-library-management
./run.sh
```

**Windows (cmd.exe):**
```cmd
git clone https://github.com/Shantanu1161/cs665-library-management.git
cd cs665-library-management
run.bat
```

**Windows (PowerShell):**
```powershell
git clone https://github.com/Shantanu1161/cs665-library-management.git
cd cs665-library-management
.\run.bat
```
(PowerShell does not run scripts from the current folder by default, so the `.\` prefix is required. cmd.exe accepts either form.)

The browser will open at **http://localhost:3000** automatically. The pill in the top-right should read **● API Connected** (green).

To stop everything: press `Ctrl+C` in the terminal (or close the windows that opened on Windows).

The SQLite database (`backend/library.db`) is auto-created and seeded on the first launch — no manual SQL setup needed.

---

### Manual way (if you prefer to run things yourself)

If the launcher script doesn't fit your workflow, you can do it manually in **two terminals**:

**One-time setup:**
```bash
git clone https://github.com/Shantanu1161/cs665-library-management.git
cd cs665-library-management
python3 -m venv venv
source venv/bin/activate         # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
```

> **Heads-up on Windows:** if you have multiple Pythons installed (Anaconda, Microsoft Store python, etc.) the activated venv is not always the one `pip install` writes to. The launcher script `run.bat` works around this automatically. If you are installing manually, use the venv's pip directly:
> ```cmd
> venv\Scripts\python.exe -m pip install -r backend\requirements.txt
> ```

**Terminal 1 — backend** (must keep running):
```bash
source venv/bin/activate         # Windows: venv\Scripts\activate
cd backend
python main.py                   # cross-platform safe; or: uvicorn main:app --reload
```
Wait for: `Uvicorn running on http://127.0.0.1:8000`

**Terminal 2 — frontend** (must keep running):
```bash
cd frontend
python3 -m http.server 3000
```
Wait for: `Serving HTTP on :: port 3000`

**Open the app:** http://localhost:3000

---

## 🗂️ Project Structure

```
library-management/
├── backend/
│   ├── main.py              # FastAPI application — all routes, validation, transactions
│   ├── requirements.txt     # Python dependencies
│   └── library.db           # SQLite database (auto-created on first run, gitignored)
├── frontend/
│   ├── index.html           # SPA markup
│   ├── css/
│   │   └── styles.css       # Custom styles (sidebar, modals, badges)
│   └── js/
│       └── app.js           # Fetch-API client, CRUD handlers, toasts
├── sql/
│   ├── schema.sql           # Final 3NF DDL schema
│   └── seed.sql             # Sample data insertion
├── run.sh                   # One-shot launcher (macOS / Linux)
├── run.bat                  # One-shot launcher (Windows)
├── README.md                # This file
├── NORMALIZATION.md         # 3rd Normal Form audit report
├── AI_LOG.md                # Generative AI usage disclosure
└── .gitignore
```

---

## ⚙️ Installation Instructions

### Prerequisites
- Python 3.10 or higher
- pip
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/library-management.git
cd library-management
```

### 2. Create and Activate a Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate — macOS/Linux
source venv/bin/activate

# Activate — Windows
venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Dependencies (`requirements.txt`):
```
fastapi==0.111.0
uvicorn==0.29.0
pydantic==2.7.1
```

---

## 🗄️ Database Setup

The SQLite database is **automatically created and seeded** with sample data on the first run of the backend server. No manual SQL setup is required.

If you prefer to initialize the database manually using the provided SQL scripts:

```bash
# From the project root
sqlite3 backend/library.db < sql/schema.sql
sqlite3 backend/library.db < sql/seed.sql
```

### Final Schema (3NF)

The canonical DDL lives in [`sql/schema.sql`](./sql/schema.sql). For convenience, the same definitions are reproduced below:

```sql
CREATE TABLE Users (
    user_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name            VARCHAR(100) NOT NULL,
    email           VARCHAR(100) NOT NULL UNIQUE,
    phone           VARCHAR(20),
    membership_type VARCHAR(20)  NOT NULL DEFAULT 'standard',
    active          INTEGER      NOT NULL DEFAULT 1,
    created_at      DATE         NOT NULL DEFAULT (date('now')),
    updated_at      DATE         NOT NULL DEFAULT (date('now'))
);

CREATE TABLE Books (
    book_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title            VARCHAR(150) NOT NULL UNIQUE,
    author           VARCHAR(100) NOT NULL,
    genre            VARCHAR(50)  NOT NULL,
    isbn             VARCHAR(20)  UNIQUE,
    year             INTEGER,
    total_copies     INTEGER      NOT NULL DEFAULT 1,
    available_copies INTEGER      NOT NULL DEFAULT 1,
    created_at       DATE         NOT NULL DEFAULT (date('now')),
    updated_at       DATE         NOT NULL DEFAULT (date('now'))
);

CREATE TABLE Loans (
    loan_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER      NOT NULL,
    book_id     INTEGER      NOT NULL,
    loan_date   DATE         NOT NULL DEFAULT (date('now')),
    due_date    DATE         NOT NULL,
    return_date DATE,
    status      VARCHAR(20)  NOT NULL DEFAULT 'Borrowed',
    fine_amount INTEGER,
    created_at  DATE         NOT NULL DEFAULT (date('now')),
    updated_at  DATE         NOT NULL DEFAULT (date('now')),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (book_id) REFERENCES Books(book_id)
);

CREATE TABLE Reviews (
    review_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER      NOT NULL,
    book_id    INTEGER      NOT NULL,
    rating     INTEGER      NOT NULL CHECK(rating BETWEEN 1 AND 5),
    comment    VARCHAR(255),
    created_at DATE         NOT NULL DEFAULT (date('now')),
    updated_at DATE         NOT NULL DEFAULT (date('now')),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (book_id) REFERENCES Books(book_id)
);
```

---

## 🚀 Usage

### Start the Backend Server

The virtual environment must be activated first, otherwise `uvicorn` won't be found.

**Recommended (works on every OS and every shell):**
```bash
# From project root
source venv/bin/activate         # Windows: venv\Scripts\activate
cd backend
python main.py
```

`main.py` ends with a `uvicorn.run(...)` block so it can be launched directly with `python`. This avoids a Windows PowerShell quirk where the colon in `uvicorn main:app` can get mangled to `:app` and produce `Error loading ASGI app. Attribute ":app" not found`.

**Alternative (Mac/Linux, or Windows cmd.exe):**
```bash
source venv/bin/activate         # Windows: venv\Scripts\activate
cd backend
uvicorn main:app --reload
```

If you're on Windows PowerShell and want to use the `uvicorn` form, quote the module spec:
```powershell
uvicorn "main:app" --reload
```

The API runs at: **http://localhost:8000**

Interactive API docs (Swagger UI): **http://localhost:8000/docs**

ReDoc API docs: **http://localhost:8000/redoc**

### Launch the Frontend

In a **second terminal** (the backend must keep running in the first):

**Option A — Serve locally (recommended):**
```bash
cd frontend
python3 -m http.server 3000
```
Then navigate to **http://localhost:3000**

**Option B — Open the file directly in a browser:**
```
Open frontend/index.html in Chrome/Firefox/Safari
```
Note: some browsers block `fetch()` calls from `file://` URLs for security reasons. If the page loads but data doesn't appear, use Option A.

---

## 🧭 Navigating the Application

| Page | Description |
|------|-------------|
| **Dashboard** | Live stats: total books, members, active borrows, overdue loans. Shows all current active borrows. |
| **Books** | Full CRUD — Add, edit, delete books. Search by title/author/ISBN. Filter by genre. Availability badge. |
| **Members** | Full CRUD — Add, edit, delete members. Standard/Premium membership types. Search by name or email. |
| **Borrows** | Issue new loans, process returns. Toggle active-only view. Overdue detection. |
| **Reviews** | View book reviews with ratings (1–5 stars). |

---

## 🔌 API Endpoints

### Books
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/books` | List all books (supports `?search=` and `?genre=`) |
| GET | `/books/{id}` | Get single book |
| POST | `/books` | Create a book |
| PUT | `/books/{id}` | Update a book |
| DELETE | `/books/{id}` | Delete a book (blocked if active loans exist) |
| GET | `/genres` | List all distinct genres |

### Members (Users)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/members` | List all members (supports `?search=`) |
| GET | `/members/{id}` | Get single member |
| POST | `/members` | Create a member |
| PUT | `/members/{id}` | Update a member |
| DELETE | `/members/{id}` | Delete a member (blocked if active loans exist) |

### Loans (Borrows)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/borrows` | List all loans (supports `?active_only=true`) |
| POST | `/borrows` | Issue a new loan (transactional) |
| PUT | `/borrows/{id}/return` | Process a book return (transactional) |

### Reviews
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/reviews` | List all reviews |
| POST | `/reviews` | Add a review |
| DELETE | `/reviews/{id}` | Remove a review |

### Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard` | Aggregate stats (COUNT, AVG fine, overdue count) |

---

## ✅ Functional Requirements Checklist

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| Multi-Table CRUD | ✅ | Full CRUD on Books, Members, Loans, Reviews |
| One-to-Many Relationship | ✅ | Users → Loans, Books → Loans, Users → Reviews |
| Many-to-Many (via junction) | ✅ | Users ↔ Books via Loans and Reviews |
| Transaction Logic | ✅ | Borrow: creates loan record + decrements `available_copies` atomically inside `BEGIN`/`COMMIT`/`ROLLBACK`. Return: sets `return_date`, recomputes `fine_amount`, and increments `available_copies` atomically. |
| Server-Side Validation | ✅ | Empty string check, rating range (1–5), phone format (7–15 digits), email uniqueness, availability check, ISBN uniqueness, member-active check |
| Summary Dashboard | ✅ | Uses **COUNT**, **SUM**, **AVG**, and **GROUP BY** across all four tables |
| Fine Calculation | ✅ | Auto-calculated on return: `max(0, (return_date - due_date).days) × $2`. Days are configurable per loan (default 14). |

---

## 🔒 Data Integrity Features

- **Foreign Key Constraints** enforced on all relationship columns
- **UNIQUE** constraint on `email` (Users) and `title` (Books)
- **CHECK** constraint on `rating` (1–5)
- **Cascade Protection**: Cannot delete a book or member that has active loans
- **Availability Guard**: Cannot borrow a book with 0 available copies
- **Active Member Guard**: Cannot borrow under an inactive member account

---

## 📊 Sample Data

The system seeds the following on first launch:

**Users (7):** John Doe, Alice Smith, Bob Brown, Emma Wilson, Liam Taylor, Chris Evans, Sophia Lee

**Books (7):** The Alchemist, Atomic Habits, Clean Code, Rich Dad Poor Dad, Harry Potter, Deep Work, Think and Grow Rich

**Loans (10):** Mix of returned and active borrows across all users

**Reviews (6):** Ratings from 3–5 stars with comments

---

## 📁 .gitignore

```
venv/
__pycache__/
*.pyc
.env
*.db-journal
.DS_Store
```

---

## 👨‍💻 Git Commit History

The repository was built up incrementally. Run `git log --oneline` to see the full history. The actual commits (oldest first):

```
1.  init: project structure and .gitignore
2.  feat(db): 3NF schema DDL with FK constraints and indexes
3.  feat(db): seed data for users, books, loans, reviews
4.  docs: NORMALIZATION.md - 3NF audit report
5.  feat(backend): FastAPI app with CRUD + transactional borrow/return
6.  feat(frontend): SPA with dashboard, books, members, borrows, reviews
7.  docs: README with install, db setup, usage, endpoints
8.  docs: AI_LOG.md disclosure of AI-assisted development steps
9.  refactor(frontend): split SPA into index.html + css/styles.css + js/app.js
10. docs: rewrite AI_LOG in plain prose, drop emojis and decorative formatting
11. docs: rewrite NORMALIZATION in plain prose, drop emojis and table formatting
12. docs(normalization): restore markdown tables for schema and 3NF summary
```

This satisfies the rubric's minimum of 5 incremental commits.

---

## 📄 Related Documentation

- [`NORMALIZATION.md`](./NORMALIZATION.md) — Full 3NF audit with functional dependencies, anomaly analysis, and decomposition steps
- [`AI_LOG.md`](./AI_LOG.md) — Complete disclosure of all Generative AI assistance used in this project
