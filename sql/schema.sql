-- ============================================================
-- Library Management System — Final 3NF Schema
-- CS665 Project 3
-- Database: SQLite
-- ============================================================

-- Drop tables in reverse dependency order to avoid FK conflicts
DROP TABLE IF EXISTS Reviews;
DROP TABLE IF EXISTS Loans;
DROP TABLE IF EXISTS Books;
DROP TABLE IF EXISTS Users;

-- ────────────────────────────────────────────────────────────
-- USERS TABLE
-- Stores registered library members
-- ────────────────────────────────────────────────────────────
CREATE TABLE Users (
    user_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name       VARCHAR(100) NOT NULL,
    email      VARCHAR(100) NOT NULL UNIQUE,
    phone      VARCHAR(20),
    membership_type VARCHAR(20) NOT NULL DEFAULT 'standard',
    active     INTEGER NOT NULL DEFAULT 1,
    created_at DATE NOT NULL DEFAULT (date('now')),
    updated_at DATE NOT NULL DEFAULT (date('now'))
);

-- ────────────────────────────────────────────────────────────
-- BOOKS TABLE
-- Stores the library catalog
-- title is UNIQUE to satisfy 3NF candidate key and prevent duplicates
-- ────────────────────────────────────────────────────────────
CREATE TABLE Books (
    book_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title            VARCHAR(150) NOT NULL UNIQUE,
    author           VARCHAR(100) NOT NULL,
    genre            VARCHAR(50)  NOT NULL,
    isbn             VARCHAR(20)  UNIQUE,
    year             INTEGER,
    total_copies     INTEGER NOT NULL DEFAULT 1,
    available_copies INTEGER NOT NULL DEFAULT 1,
    created_at       DATE NOT NULL DEFAULT (date('now')),
    updated_at       DATE NOT NULL DEFAULT (date('now'))
);

-- ────────────────────────────────────────────────────────────
-- LOANS TABLE
-- Tracks book borrowing transactions
-- 3NF Note: fine_amount is a cached computed value synced
-- transactionally on every return event to resolve the
-- transitive dependency: loan_id → return_date → fine_amount
-- ────────────────────────────────────────────────────────────
CREATE TABLE Loans (
    loan_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    book_id     INTEGER NOT NULL,
    loan_date   DATE    NOT NULL DEFAULT (date('now')),
    due_date    DATE    NOT NULL,
    return_date DATE,
    status      VARCHAR(20) NOT NULL DEFAULT 'Borrowed',
    fine_amount INTEGER,
    created_at  DATE NOT NULL DEFAULT (date('now')),
    updated_at  DATE NOT NULL DEFAULT (date('now')),

    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (book_id) REFERENCES Books(book_id)
);

-- ────────────────────────────────────────────────────────────
-- REVIEWS TABLE
-- Stores user book reviews
-- rating is constrained to 1-5 via CHECK
-- ────────────────────────────────────────────────────────────
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

-- ────────────────────────────────────────────────────────────
-- Indexes for query performance
-- ────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_loans_user_id  ON Loans(user_id);
CREATE INDEX IF NOT EXISTS idx_loans_book_id  ON Loans(book_id);
CREATE INDEX IF NOT EXISTS idx_loans_status   ON Loans(status);
CREATE INDEX IF NOT EXISTS idx_reviews_book   ON Reviews(book_id);
CREATE INDEX IF NOT EXISTS idx_reviews_user   ON Reviews(user_id);
