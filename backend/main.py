"""
Library Management System — CS665 Project 3
Backend: FastAPI + SQLite (sqlite3)
Author: Shantanu Rajesh Sawarkar
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
import sqlite3
import os
import re
from datetime import datetime, timedelta, date

# ── App Setup ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="Library Management System",
    description="CS665 Project 3 — Full-Stack Library Management App",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(os.path.dirname(__file__), "library.db")

# ── Database Helpers ─────────────────────────────────────────────────────────

def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def row_to_dict(row) -> dict:
    return dict(row) if row else None


def rows_to_list(rows) -> list:
    return [dict(r) for r in rows]


# ── Database Initialization + Seeding ────────────────────────────────────────

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS Users (
            user_id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name            VARCHAR(100) NOT NULL,
            email           VARCHAR(100) NOT NULL UNIQUE,
            phone           VARCHAR(20),
            membership_type VARCHAR(20)  NOT NULL DEFAULT 'standard',
            active          INTEGER      NOT NULL DEFAULT 1,
            created_at      DATE         NOT NULL DEFAULT (date('now')),
            updated_at      DATE         NOT NULL DEFAULT (date('now'))
        );

        CREATE TABLE IF NOT EXISTS Books (
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

        CREATE TABLE IF NOT EXISTS Loans (
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

        CREATE TABLE IF NOT EXISTS Reviews (
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

        CREATE INDEX IF NOT EXISTS idx_loans_user_id ON Loans(user_id);
        CREATE INDEX IF NOT EXISTS idx_loans_book_id ON Loans(book_id);
        CREATE INDEX IF NOT EXISTS idx_loans_status  ON Loans(status);
        CREATE INDEX IF NOT EXISTS idx_reviews_book  ON Reviews(book_id);
        CREATE INDEX IF NOT EXISTS idx_reviews_user  ON Reviews(user_id);
    """)
    conn.commit()

    cur = conn.execute("SELECT COUNT(*) FROM Users")
    if cur.fetchone()[0] == 0:
        _seed(conn)

    conn.close()


def _seed(conn: sqlite3.Connection):
    conn.executescript("""
        INSERT INTO Users (name, email, phone, membership_type, active) VALUES
        ('John Doe',     'john@example.com',   '555-1001', 'premium',  1),
        ('Alice Smith',  'alice@example.com',  '555-1002', 'standard', 1),
        ('Bob Brown',    'bob@example.com',    '555-1003', 'standard', 1),
        ('Emma Wilson',  'emma@example.com',   '555-1004', 'premium',  1),
        ('Liam Taylor',  'liam@example.com',   '555-1005', 'standard', 1),
        ('Chris Evans',  'chris@example.com',  '555-1006', 'standard', 1),
        ('Sophia Lee',   'sophia@example.com', '555-1007', 'premium',  1),
        ('Marcus Reed',  'marcus@example.com', '555-1008', 'standard', 1),
        ('Priya Patel',  'priya@example.com',  '555-1009', 'standard', 1),
        ('James Carter', 'james@example.com',  '555-1010', 'premium',  1);

        INSERT INTO Books (title, author, genre, isbn, year, total_copies, available_copies) VALUES
        ('The Alchemist',                       'Paulo Coelho',        'Fiction',      '9780062315007', 1988, 4, 3),
        ('Atomic Habits',                       'James Clear',         'Self-Help',    '9780735211292', 2018, 3, 2),
        ('Clean Code',                          'Robert Martin',       'Programming',  '9780132350884', 2008, 2, 1),
        ('Rich Dad Poor Dad',                   'Robert Kiyosaki',     'Finance',      '9781612680194', 1997, 3, 2),
        ('Harry Potter and the Sorcerers Stone','J.K. Rowling',        'Fantasy',      '9780439708180', 1997, 5, 4),
        ('Deep Work',                           'Cal Newport',         'Productivity', '9781455586691', 2016, 2, 1),
        ('Think and Grow Rich',                 'Napoleon Hill',       'Finance',      '9781585424337', 1937, 3, 3),
        ('The Great Gatsby',                    'F. Scott Fitzgerald', 'Fiction',      '9780743273565', 1925, 2, 2),
        ('1984',                                'George Orwell',       'Dystopian',    '9780451524935', 1949, 4, 4),
        ('Dune',                                'Frank Herbert',       'Sci-Fi',       '9780441013593', 1965, 2, 2),
        ('Sapiens',                             'Yuval Noah Harari',   'Non-Fiction',  '9780062316110', 2011, 3, 2),
        ('To Kill a Mockingbird',               'Harper Lee',          'Fiction',      '9780061935466', 1960, 2, 2),
        ('The Pragmatic Programmer',            'Andrew Hunt',         'Programming',  '9780135957059', 2019, 1, 1),
        ('Good to Great',                       'Jim Collins',         'Business',     '9780066620992', 2001, 2, 2),
        ('Educated',                            'Tara Westover',       'Memoir',       '9780399590504', 2018, 2, 2);

        INSERT INTO Loans (user_id, book_id, loan_date, due_date, return_date, status, fine_amount) VALUES
        (1,  1,  '2024-02-01', '2024-02-15', '2024-02-10', 'Returned', 0),
        (2,  2,  '2024-02-02', '2024-02-16', '2024-02-20', 'Returned', 8),
        (3,  3,  '2024-02-03', '2024-02-17', '2024-02-12', 'Returned', 0),
        (4,  4,  '2024-02-04', '2024-02-18', NULL,         'Borrowed', NULL),
        (5,  5,  '2024-02-05', '2024-02-19', '2024-02-15', 'Returned', 0),
        (1,  2,  '2024-02-06', '2024-02-20', '2024-02-14', 'Returned', 0),
        (1,  3,  '2024-02-07', '2024-02-21', NULL,         'Borrowed', NULL),
        (2,  1,  '2024-02-08', '2024-02-22', '2024-02-16', 'Returned', 0),
        (3,  1,  '2024-02-09', '2024-02-23', NULL,         'Borrowed', NULL),
        (6,  6,  '2024-02-10', '2024-02-24', NULL,         'Borrowed', NULL),
        (7,  9,  '2024-02-11', '2024-02-25', '2024-02-28', 'Returned', 6),
        (8,  10, '2024-02-12', '2024-02-26', '2024-02-26', 'Returned', 0),
        (9,  11, '2024-02-13', '2024-02-27', NULL,         'Borrowed', NULL),
        (10, 8,  '2024-02-14', '2024-02-28', '2024-03-05', 'Returned', 14);

        INSERT INTO Reviews (user_id, book_id, rating, comment) VALUES
        (1,  1,  5, 'A timeless classic that changed my perspective on life.'),
        (2,  2,  4, 'Very practical and easy to apply. Highly recommended.'),
        (3,  3,  5, 'Essential reading for every software developer.'),
        (4,  4,  3, 'Good financial insights, some parts feel repetitive.'),
        (5,  5,  5, 'Amazing story — pure magic from the very first page.'),
        (6,  6,  4, 'Incredibly productive framework. Changed how I work.'),
        (7,  7,  5, 'Highly motivating. A must-read for anyone ambitious.'),
        (1,  9,  5, 'A chilling dystopia that feels more relevant than ever.'),
        (2,  8,  4, 'Beautifully written. Fitzgeralds prose is extraordinary.'),
        (3,  11, 4, 'A fascinating journey through human history.'),
        (8,  10, 5, 'A sci-fi epic unlike anything I have read before.'),
        (9,  12, 5, 'Profound and deeply moving. A genuine masterpiece.'),
        (10, 14, 4, 'Essential for anyone running or studying a business.');
    """)
    conn.commit()


# ── Pydantic Models ──────────────────────────────────────────────────────────

class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)
    author: str = Field(..., min_length=1, max_length=100)
    genre: str = Field(..., min_length=1, max_length=50)
    isbn: Optional[str] = Field(None, max_length=20)
    year: Optional[int] = Field(None, ge=1000, le=2100)
    total_copies: int = Field(1, ge=1)
    available_copies: int = Field(1, ge=0)

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=150)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    genre: Optional[str] = Field(None, min_length=1, max_length=50)
    isbn: Optional[str] = Field(None, max_length=20)
    year: Optional[int] = Field(None, ge=1000, le=2100)
    total_copies: Optional[int] = Field(None, ge=1)
    available_copies: Optional[int] = Field(None, ge=0)

def _validate_phone(v):
    """Phone validation shared by MemberCreate and MemberUpdate.
    Accepts digits with optional separators (space, dash, plus, parens, dot).
    Requires 7-15 actual digits. Empty string is treated as no phone."""
    if v is None or v == "":
        return None
    cleaned = re.sub(r"[\s\-\+\(\)\.]", "", v)
    if not cleaned.isdigit():
        raise ValueError("must contain only digits and optional separators (- + ( ) . space)")
    if len(cleaned) < 7 or len(cleaned) > 15:
        raise ValueError("must have between 7 and 15 digits")
    return v.strip()


class MemberCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=5, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    membership_type: str = Field("standard", pattern="^(standard|premium)$")

    @field_validator("phone")
    @classmethod
    def check_phone(cls, v):
        return _validate_phone(v)


class MemberUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, min_length=5, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    membership_type: Optional[str] = Field(None, pattern="^(standard|premium)$")
    active: Optional[int] = Field(None, ge=0, le=1)

    @field_validator("phone")
    @classmethod
    def check_phone(cls, v):
        return _validate_phone(v)

class BorrowCreate(BaseModel):
    user_id: int = Field(..., ge=1)
    book_id: int = Field(..., ge=1)
    days: int = Field(14, ge=1, le=60)

class ReviewCreate(BaseModel):
    user_id: int = Field(..., ge=1)
    book_id: int = Field(..., ge=1)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=255)


# ── Startup ──────────────────────────────────────────────────────────────────

@app.on_event("startup")
def startup():
    init_db()


# ── Dashboard ────────────────────────────────────────────────────────────────

@app.get("/dashboard")
def get_dashboard():
    conn = get_db()
    stats = {}

    stats["total_books"]   = conn.execute("SELECT COUNT(*) FROM Books").fetchone()[0]
    stats["total_members"] = conn.execute("SELECT COUNT(*) FROM Users WHERE active = 1").fetchone()[0]
    stats["active_loans"]  = conn.execute("SELECT COUNT(*) FROM Loans WHERE status = 'Borrowed'").fetchone()[0]
    stats["total_loans"]   = conn.execute("SELECT COUNT(*) FROM Loans").fetchone()[0]
    stats["total_reviews"] = conn.execute("SELECT COUNT(*) FROM Reviews").fetchone()[0]

    avg = conn.execute(
        "SELECT ROUND(AVG(rating), 2) FROM Reviews"
    ).fetchone()[0]
    stats["avg_rating"] = avg or 0.0

    overdue = conn.execute("""
        SELECT COUNT(*) FROM Loans
        WHERE status = 'Borrowed' AND due_date < date('now')
    """).fetchone()[0]
    stats["overdue_loans"] = overdue

    total_fines = conn.execute(
        "SELECT COALESCE(SUM(fine_amount), 0) FROM Loans WHERE fine_amount IS NOT NULL"
    ).fetchone()[0]
    stats["total_fines_collected"] = total_fines

    genre_stats = rows_to_list(conn.execute("""
        SELECT genre, COUNT(*) AS count,
               SUM(total_copies) AS total_copies,
               SUM(available_copies) AS available_copies
        FROM Books
        GROUP BY genre
        ORDER BY count DESC
    """).fetchall())
    stats["books_by_genre"] = genre_stats

    active_borrows = rows_to_list(conn.execute("""
        SELECT l.loan_id, u.name AS member_name, b.title AS book_title,
               l.loan_date, l.due_date,
               CASE WHEN l.due_date < date('now') THEN 1 ELSE 0 END AS overdue
        FROM Loans l
        JOIN Users u ON l.user_id = u.user_id
        JOIN Books b ON l.book_id = b.book_id
        WHERE l.status = 'Borrowed'
        ORDER BY l.due_date ASC
        LIMIT 10
    """).fetchall())
    stats["active_borrows"] = active_borrows

    # NOTE: borrow_count and avg_rating are computed in independent subqueries.
    # Joining both Loans and Reviews directly to Books would produce a Cartesian
    # product and inflate COUNT(loan_id) by the number of reviews per book.
    top_books = rows_to_list(conn.execute("""
        SELECT b.title,
               (SELECT COUNT(*)         FROM Loans   l WHERE l.book_id = b.book_id) AS borrow_count,
               (SELECT ROUND(AVG(rating), 1) FROM Reviews r WHERE r.book_id = b.book_id) AS avg_rating
        FROM Books b
        ORDER BY borrow_count DESC, b.title ASC
        LIMIT 5
    """).fetchall())
    stats["top_books"] = top_books

    conn.close()
    return stats


# ── Books ────────────────────────────────────────────────────────────────────

@app.get("/books")
def list_books(search: str = "", genre: str = ""):
    conn = get_db()
    query = "SELECT * FROM Books WHERE 1=1"
    params = []
    if search:
        query += " AND (title LIKE ? OR author LIKE ? OR isbn LIKE ?)"
        like = f"%{search}%"
        params += [like, like, like]
    if genre:
        query += " AND genre = ?"
        params.append(genre)
    query += " ORDER BY title"
    books = rows_to_list(conn.execute(query, params).fetchall())
    conn.close()
    return books


@app.get("/books/{book_id}")
def get_book(book_id: int):
    conn = get_db()
    book = row_to_dict(conn.execute(
        "SELECT * FROM Books WHERE book_id = ?", (book_id,)
    ).fetchone())
    if not book:
        conn.close()
        raise HTTPException(status_code=404, detail="Book not found")

    book["reviews"] = rows_to_list(conn.execute("""
        SELECT r.*, u.name AS reviewer_name
        FROM Reviews r JOIN Users u ON r.user_id = u.user_id
        WHERE r.book_id = ?
        ORDER BY r.created_at DESC
    """, (book_id,)).fetchall())

    conn.close()
    return book


@app.post("/books", status_code=201)
def create_book(req: BookCreate):
    if req.available_copies > req.total_copies:
        raise HTTPException(status_code=422, detail="available_copies cannot exceed total_copies")

    conn = get_db()
    try:
        cur = conn.execute("""
            INSERT INTO Books (title, author, genre, isbn, year, total_copies, available_copies)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (req.title.strip(), req.author.strip(), req.genre.strip(),
              req.isbn, req.year, req.total_copies, req.available_copies))
        conn.commit()
        book = row_to_dict(conn.execute(
            "SELECT * FROM Books WHERE book_id = ?", (cur.lastrowid,)
        ).fetchone())
        conn.close()
        return book
    except sqlite3.IntegrityError as e:
        conn.close()
        msg = str(e)
        if "title" in msg:
            raise HTTPException(status_code=409, detail="A book with this title already exists")
        if "isbn" in msg:
            raise HTTPException(status_code=409, detail="A book with this ISBN already exists")
        raise HTTPException(status_code=409, detail="Duplicate entry")


@app.put("/books/{book_id}")
def update_book(book_id: int, req: BookUpdate):
    conn = get_db()
    book = row_to_dict(conn.execute(
        "SELECT * FROM Books WHERE book_id = ?", (book_id,)
    ).fetchone())
    if not book:
        conn.close()
        raise HTTPException(status_code=404, detail="Book not found")

    new_total     = req.total_copies     if req.total_copies     is not None else book["total_copies"]
    new_available = req.available_copies if req.available_copies is not None else book["available_copies"]
    if new_available > new_total:
        conn.close()
        raise HTTPException(status_code=422, detail="available_copies cannot exceed total_copies")

    fields = {
        "title":            req.title.strip()  if req.title  else None,
        "author":           req.author.strip() if req.author else None,
        "genre":            req.genre.strip()  if req.genre  else None,
        "isbn":             req.isbn,
        "year":             req.year,
        "total_copies":     req.total_copies,
        "available_copies": req.available_copies,
    }
    updates = {k: v for k, v in fields.items() if v is not None}
    if not updates:
        conn.close()
        return book

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [book_id]
    try:
        conn.execute(f"UPDATE Books SET {set_clause}, updated_at = date('now') WHERE book_id = ?", values)
        conn.commit()
        updated = row_to_dict(conn.execute(
            "SELECT * FROM Books WHERE book_id = ?", (book_id,)
        ).fetchone())
        conn.close()
        return updated
    except sqlite3.IntegrityError as e:
        conn.close()
        raise HTTPException(status_code=409, detail="Title or ISBN already exists")


@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    conn = get_db()
    book = conn.execute("SELECT * FROM Books WHERE book_id = ?", (book_id,)).fetchone()
    if not book:
        conn.close()
        raise HTTPException(status_code=404, detail="Book not found")

    active = conn.execute(
        "SELECT COUNT(*) FROM Loans WHERE book_id = ? AND status = 'Borrowed'", (book_id,)
    ).fetchone()[0]
    if active > 0:
        conn.close()
        raise HTTPException(status_code=400, detail="Cannot delete — book has active loans")

    conn.execute("DELETE FROM Reviews WHERE book_id = ?", (book_id,))
    conn.execute("DELETE FROM Loans   WHERE book_id = ?", (book_id,))
    conn.execute("DELETE FROM Books   WHERE book_id = ?", (book_id,))
    conn.commit()
    conn.close()
    return {"message": "Book deleted successfully"}


@app.get("/genres")
def list_genres():
    conn = get_db()
    rows = conn.execute("SELECT DISTINCT genre FROM Books ORDER BY genre").fetchall()
    conn.close()
    return [r[0] for r in rows]


# ── Members ──────────────────────────────────────────────────────────────────

@app.get("/members")
def list_members(search: str = ""):
    conn = get_db()
    query = "SELECT * FROM Users WHERE 1=1"
    params = []
    if search:
        query += " AND (name LIKE ? OR email LIKE ? OR phone LIKE ?)"
        like = f"%{search}%"
        params += [like, like, like]
    query += " ORDER BY name"
    members = rows_to_list(conn.execute(query, params).fetchall())
    conn.close()
    return members


@app.get("/members/{user_id}")
def get_member(user_id: int):
    conn = get_db()
    member = row_to_dict(conn.execute(
        "SELECT * FROM Users WHERE user_id = ?", (user_id,)
    ).fetchone())
    if not member:
        conn.close()
        raise HTTPException(status_code=404, detail="Member not found")

    member["loans"] = rows_to_list(conn.execute("""
        SELECT l.*, b.title AS book_title
        FROM Loans l JOIN Books b ON l.book_id = b.book_id
        WHERE l.user_id = ?
        ORDER BY l.loan_date DESC
    """, (user_id,)).fetchall())

    conn.close()
    return member


@app.post("/members", status_code=201)
def create_member(req: MemberCreate):
    email = req.email.strip().lower()
    if "@" not in email or "." not in email:
        raise HTTPException(status_code=422, detail="Invalid email address")

    conn = get_db()
    try:
        cur = conn.execute("""
            INSERT INTO Users (name, email, phone, membership_type)
            VALUES (?, ?, ?, ?)
        """, (req.name.strip(), email, req.phone, req.membership_type))
        conn.commit()
        member = row_to_dict(conn.execute(
            "SELECT * FROM Users WHERE user_id = ?", (cur.lastrowid,)
        ).fetchone())
        conn.close()
        return member
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=409, detail="A member with this email already exists")


@app.put("/members/{user_id}")
def update_member(user_id: int, req: MemberUpdate):
    conn = get_db()
    member = row_to_dict(conn.execute(
        "SELECT * FROM Users WHERE user_id = ?", (user_id,)
    ).fetchone())
    if not member:
        conn.close()
        raise HTTPException(status_code=404, detail="Member not found")

    if req.email:
        email = req.email.strip().lower()
        if "@" not in email or "." not in email:
            conn.close()
            raise HTTPException(status_code=422, detail="Invalid email address")
        req.email = email

    fields = {
        "name":            req.name.strip() if req.name else None,
        "email":           req.email,
        "phone":           req.phone,
        "membership_type": req.membership_type,
        "active":          req.active,
    }
    updates = {k: v for k, v in fields.items() if v is not None}
    if not updates:
        conn.close()
        return member

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [user_id]
    try:
        conn.execute(f"UPDATE Users SET {set_clause}, updated_at = date('now') WHERE user_id = ?", values)
        conn.commit()
        updated = row_to_dict(conn.execute(
            "SELECT * FROM Users WHERE user_id = ?", (user_id,)
        ).fetchone())
        conn.close()
        return updated
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=409, detail="Email already in use by another member")


@app.delete("/members/{user_id}")
def delete_member(user_id: int):
    conn = get_db()
    member = conn.execute("SELECT * FROM Users WHERE user_id = ?", (user_id,)).fetchone()
    if not member:
        conn.close()
        raise HTTPException(status_code=404, detail="Member not found")

    active = conn.execute(
        "SELECT COUNT(*) FROM Loans WHERE user_id = ? AND status = 'Borrowed'", (user_id,)
    ).fetchone()[0]
    if active > 0:
        conn.close()
        raise HTTPException(status_code=400, detail="Cannot delete — member has active loans")

    conn.execute("DELETE FROM Reviews WHERE user_id = ?", (user_id,))
    conn.execute("DELETE FROM Loans   WHERE user_id = ?", (user_id,))
    conn.execute("DELETE FROM Users   WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return {"message": "Member deleted successfully"}


# ── Loans / Borrows ──────────────────────────────────────────────────────────

@app.get("/borrows")
def list_borrows(active_only: bool = False):
    conn = get_db()
    query = """
        SELECT l.*,
               u.name  AS member_name,
               b.title AS book_title,
               CASE WHEN l.due_date < date('now') AND l.status = 'Borrowed'
                    THEN 1 ELSE 0 END AS overdue
        FROM Loans l
        JOIN Users u ON l.user_id = u.user_id
        JOIN Books b ON l.book_id = b.book_id
    """
    if active_only:
        query += " WHERE l.status = 'Borrowed'"
    query += " ORDER BY l.loan_date DESC"
    loans = rows_to_list(conn.execute(query).fetchall())
    conn.close()
    return loans


@app.post("/borrows", status_code=201)
def borrow_book(req: BorrowCreate):
    """
    TRANSACTION: Atomically inserts a Loan record AND decrements available_copies.
    Rolls back if any step fails.
    """
    conn = get_db()
    try:
        # Validate member
        member = conn.execute(
            "SELECT * FROM Users WHERE user_id = ?", (req.user_id,)
        ).fetchone()
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        if not member["active"]:
            raise HTTPException(status_code=400, detail="Member account is inactive")

        # Validate book
        book = conn.execute(
            "SELECT * FROM Books WHERE book_id = ?", (req.book_id,)
        ).fetchone()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        if book["available_copies"] < 1:
            raise HTTPException(status_code=400, detail="No copies available for this book")

        # Check for existing active loan of same book by same member
        existing = conn.execute("""
            SELECT loan_id FROM Loans
            WHERE user_id = ? AND book_id = ? AND status = 'Borrowed'
        """, (req.user_id, req.book_id)).fetchone()
        if existing:
            raise HTTPException(status_code=400, detail="Member already has an active loan for this book")

        loan_date = date.today()
        due_date  = loan_date + timedelta(days=req.days)

        # BEGIN TRANSACTION — insert loan + decrement copies atomically
        conn.execute("BEGIN")
        cur = conn.execute("""
            INSERT INTO Loans (user_id, book_id, loan_date, due_date, status)
            VALUES (?, ?, ?, ?, 'Borrowed')
        """, (req.user_id, req.book_id, str(loan_date), str(due_date)))

        conn.execute("""
            UPDATE Books SET available_copies = available_copies - 1,
                             updated_at = date('now')
            WHERE book_id = ?
        """, (req.book_id,))
        conn.commit()

        loan = row_to_dict(conn.execute("""
            SELECT l.*, u.name AS member_name, b.title AS book_title
            FROM Loans l
            JOIN Users u ON l.user_id = u.user_id
            JOIN Books b ON l.book_id = b.book_id
            WHERE l.loan_id = ?
        """, (cur.lastrowid,)).fetchone())
        conn.close()
        return loan

    except HTTPException:
        conn.rollback()
        conn.close()
        raise
    except Exception as e:
        conn.rollback()
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/borrows/{loan_id}/return")
def return_book(loan_id: int):
    """
    TRANSACTION: Atomically updates the loan (return_date, status, fine_amount)
    AND increments available_copies on Books.
    """
    conn = get_db()
    try:
        loan = conn.execute(
            "SELECT * FROM Loans WHERE loan_id = ?", (loan_id,)
        ).fetchone()
        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found")
        if loan["status"] == "Returned":
            raise HTTPException(status_code=400, detail="Book has already been returned")

        return_date = date.today()
        due_date    = date.fromisoformat(loan["due_date"])

        # Fine: $2 per day beyond the due date
        overdue_days = (return_date - due_date).days
        fine = max(0, overdue_days) * 2

        # BEGIN TRANSACTION — update loan + increment copies atomically
        conn.execute("BEGIN")
        conn.execute("""
            UPDATE Loans
            SET return_date = ?, status = 'Returned', fine_amount = ?,
                updated_at = date('now')
            WHERE loan_id = ?
        """, (str(return_date), fine, loan_id))

        conn.execute("""
            UPDATE Books SET available_copies = available_copies + 1,
                             updated_at = date('now')
            WHERE book_id = ?
        """, (loan["book_id"],))
        conn.commit()

        updated = row_to_dict(conn.execute("""
            SELECT l.*, u.name AS member_name, b.title AS book_title
            FROM Loans l
            JOIN Users u ON l.user_id = u.user_id
            JOIN Books b ON l.book_id = b.book_id
            WHERE l.loan_id = ?
        """, (loan_id,)).fetchone())
        conn.close()
        return updated

    except HTTPException:
        conn.rollback()
        conn.close()
        raise
    except Exception as e:
        conn.rollback()
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))


# ── Reviews ──────────────────────────────────────────────────────────────────

@app.get("/reviews")
def list_reviews(book_id: Optional[int] = None):
    conn = get_db()
    query = """
        SELECT r.*, u.name AS reviewer_name, b.title AS book_title
        FROM Reviews r
        JOIN Users u ON r.user_id = u.user_id
        JOIN Books b ON r.book_id = b.book_id
    """
    params = []
    if book_id:
        query += " WHERE r.book_id = ?"
        params.append(book_id)
    query += " ORDER BY r.created_at DESC"
    reviews = rows_to_list(conn.execute(query, params).fetchall())
    conn.close()
    return reviews


@app.post("/reviews", status_code=201)
def add_review(req: ReviewCreate):
    conn = get_db()

    member = conn.execute("SELECT user_id FROM Users WHERE user_id = ?", (req.user_id,)).fetchone()
    if not member:
        conn.close()
        raise HTTPException(status_code=404, detail="Member not found")

    book = conn.execute("SELECT book_id FROM Books WHERE book_id = ?", (req.book_id,)).fetchone()
    if not book:
        conn.close()
        raise HTTPException(status_code=404, detail="Book not found")

    comment = req.comment.strip() if req.comment else None

    try:
        cur = conn.execute("""
            INSERT INTO Reviews (user_id, book_id, rating, comment)
            VALUES (?, ?, ?, ?)
        """, (req.user_id, req.book_id, req.rating, comment))
        conn.commit()
        review = row_to_dict(conn.execute("""
            SELECT r.*, u.name AS reviewer_name, b.title AS book_title
            FROM Reviews r
            JOIN Users u ON r.user_id = u.user_id
            JOIN Books b ON r.book_id = b.book_id
            WHERE r.review_id = ?
        """, (cur.lastrowid,)).fetchone())
        conn.close()
        return review
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/reviews/{review_id}")
def delete_review(review_id: int):
    conn = get_db()
    review = conn.execute("SELECT * FROM Reviews WHERE review_id = ?", (review_id,)).fetchone()
    if not review:
        conn.close()
        raise HTTPException(status_code=404, detail="Review not found")
    conn.execute("DELETE FROM Reviews WHERE review_id = ?", (review_id,))
    conn.commit()
    conn.close()
    return {"message": "Review deleted successfully"}
