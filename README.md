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
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Fonts | Google Fonts (Playfair Display + DM Sans) |
| Version Control | Git |

---

## 🗂️ Project Structure

```
library-management/
├── backend/
│   ├── main.py              # FastAPI application — all routes, validation, transactions
│   ├── requirements.txt     # Python dependencies
│   └── library.db           # SQLite database (auto-created on first run)
├── frontend/
│   └── index.html           # Single-page frontend application
├── sql/
│   ├── schema.sql           # Final 3NF DDL schema
│   └── seed.sql             # Sample data insertion
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

```sql
CREATE TABLE Users (
    user_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name      VARCHAR(100) NOT NULL,
    email     VARCHAR(100) NOT NULL UNIQUE,
    created_at DATE NOT NULL DEFAULT (date('now')),
    updated_at DATE NOT NULL DEFAULT (date('now'))
);

CREATE TABLE Books (
    book_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    title      VARCHAR(150) NOT NULL UNIQUE,
    author     VARCHAR(100) NOT NULL,
    genre      VARCHAR(50)  NOT NULL,
    total_copies    INTEGER NOT NULL DEFAULT 1,
    available_copies INTEGER NOT NULL DEFAULT 1,
    created_at DATE NOT NULL DEFAULT (date('now')),
    updated_at DATE NOT NULL DEFAULT (date('now'))
);

CREATE TABLE Loans (
    loan_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    book_id     INTEGER NOT NULL,
    loan_date   DATE NOT NULL DEFAULT (date('now')),
    due_date    DATE NOT NULL,
    return_date DATE,
    status      VARCHAR(20) NOT NULL DEFAULT 'Borrowed',
    fine_amount INTEGER,
    created_at  DATE NOT NULL DEFAULT (date('now')),
    updated_at  DATE NOT NULL DEFAULT (date('now')),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (book_id) REFERENCES Books(book_id)
);

CREATE TABLE Reviews (
    review_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    book_id    INTEGER NOT NULL,
    rating     INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
    comment    VARCHAR(255),
    created_at DATE NOT NULL DEFAULT (date('now')),
    updated_at DATE NOT NULL DEFAULT (date('now')),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (book_id) REFERENCES Books(book_id)
);
```

---

## 🚀 Usage

### Start the Backend Server

```bash
cd backend
uvicorn main:app --reload
```

The API runs at: **http://localhost:8000**

Interactive API docs (Swagger UI): **http://localhost:8000/docs**

ReDoc API docs: **http://localhost:8000/redoc**

### Launch the Frontend

**Option A — Open directly in browser:**
```
Open frontend/index.html in any modern browser
```

**Option B — Serve locally (recommended for CORS-free experience):**
```bash
cd frontend
python -m http.server 3000
```
Then navigate to **http://localhost:3000**

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
| Transaction Logic | ✅ | Borrow: decrements `available_copies` + creates loan record atomically. Return: increments `available_copies` + sets `returned_at` atomically. |
| Server-Side Validation | ✅ | Empty string check, rating range (1–5), email uniqueness, availability check, ISBN uniqueness |
| Summary Dashboard | ✅ | Uses COUNT, AVG, subqueries across all four tables |
| Fine Calculation | ✅ | Auto-calculated: (days beyond 7) × $2 |

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

## 👨‍💻 Git Commit Strategy

Minimum 5 incremental commits following this pattern:

```
1. init: project structure and .gitignore
2. feat: DDL schema and SQLite initialization
3. feat: FastAPI backend — books and members CRUD
4. feat: Loans and Reviews endpoints with transaction logic
5. feat: Frontend SPA — dashboard, books, members, borrows
6. docs: README, NORMALIZATION.md, AI_LOG.md
7. fix: server-side validation and fine calculation
```

---

## 📄 Related Documentation

- [`NORMALIZATION.md`](./NORMALIZATION.md) — Full 3NF audit with functional dependencies, anomaly analysis, and decomposition steps
- [`AI_LOG.md`](./AI_LOG.md) — Complete disclosure of all Generative AI assistance used in this project
