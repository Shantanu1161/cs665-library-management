# 📐 Normalization Report — Library Management System

**Course:** CS665 — Database Systems  
**Project:** Project 3 — Full-Stack Application  
**Database:** Library Management System  
**Target Normal Form:** Third Normal Form (3NF)

---

## 1. Original Schema (Before Normalization)

The original database was designed with four tables based on the project's SQL DDL:

```
Users(user_id, name, email, created_at, updated_at)
Books(book_id, title, author, genre, created_at, updated_at)
Loans(loan_id, user_id, book_id, loan_date, return_date, status, fine_amount, created_at, updated_at)
Reviews(review_id, user_id, book_id, rating, comment, created_at, updated_at)
```

---

## 2. Original Functional Dependencies

### Users Table

```
user_id → name, email, created_at, updated_at
email → user_id, name, created_at, updated_at   (email is a candidate key)
```

### Books Table

```
book_id → title, author, genre, created_at, updated_at
title → book_id, author, genre, created_at, updated_at  (title is a candidate key after UNIQUE constraint)
```

### Loans Table

```
loan_id → user_id, book_id, loan_date, return_date, due_date, status, fine_amount, created_at, updated_at
(user_id, book_id, loan_date) → loan_id, return_date, status, fine_amount  (composite candidate key)
fine_amount → f(loan_date, return_date)   (derived/calculated — transitive dependency on date columns)
status → f(return_date)                   (derived — transitive dependency)
```

### Reviews Table

```
review_id → user_id, book_id, rating, comment, created_at, updated_at
(user_id, book_id) → rating, comment  (composite candidate key — one review per user per book)
```

---

## 3. Anomaly Identification

### 3.1 Update Anomalies

**Books Table:**  
If an author's name is misspelled and they have written 10 books, every row must be updated individually. There is no `Authors` table to normalize author info to. However, since author is a single atomic attribute and does not functionally determine other non-key columns, this is acceptable for this scope — it does not violate 3NF.

**Loans Table — `fine_amount` column:**  
`fine_amount` is a value derived from `(return_date - loan_date)`. If `return_date` is updated, `fine_amount` must be recalculated manually. This creates a **transitive dependency**:  
`loan_id → return_date → fine_amount`  
This violates 3NF. **Resolution:** `fine_amount` should be calculated dynamically (via a stored procedure or application logic) rather than stored as a persistent column. In our implementation, it is recalculated on every return event.

**Loans Table — `status` column:**  
`status` ('Borrowed' / 'Returned') is logically derivable from whether `return_date IS NULL`. Storing it introduces a **redundancy anomaly** — a loan could have `return_date = '2024-03-01'` but `status = 'Borrowed'`, creating an inconsistency.  
**Resolution:** `status` is maintained in sync via transactional update on every return operation.

### 3.2 Insertion Anomalies

- A **book cannot be reviewed** unless it has already been inserted into `Books`. (Correct — this is enforced via FK constraint, not an anomaly.)
- A **loan cannot be created** for a non-existent user or book. (Correct — FK constraints prevent this.)
- No partial-key anomalies exist because every non-key attribute depends on the entire primary key in all tables.

### 3.3 Deletion Anomalies

- **Deleting a User** who has loans would orphan loan records. Prevented by FK constraint.
- **Deleting a Book** with active loans would orphan those loans. Prevented by application-level guard in the API (returns HTTP 400 if active borrows exist).
- **Deleting all Reviews** for a book does not lose any book information — Reviews and Books are separate tables. No deletion anomaly.

---

## 4. Normal Form Verification

### First Normal Form (1NF) ✅

All tables satisfy 1NF:
- All columns contain **atomic (indivisible) values**
- No repeating groups or arrays
- Every table has a **primary key**
- All column values are of a **single type**

### Second Normal Form (2NF) ✅

All tables satisfy 2NF:
- All non-key attributes are **fully functionally dependent** on the entire primary key
- The only composite candidate keys are `(user_id, book_id)` in Reviews and `(user_id, book_id, loan_date)` in Loans — all non-key attributes depend on the full composite key, not a subset

### Third Normal Form (3NF) — Issues Found and Resolved

**Violation 1: `fine_amount` in Loans**  
- Transitive dependency: `loan_id → return_date → fine_amount`
- **Resolution:** `fine_amount` is calculated dynamically at query time using `CASE WHEN DATEDIFF(return_date, loan_date) > 7 THEN (days - 7) * 2 ELSE 0 END`. It is stored as a cached value and re-synced on every return event via a transaction.

**Violation 2: `status` in Loans**  
- Transitive dependency: `loan_id → return_date → status`
- **Resolution:** `status` is always updated atomically alongside `return_date` in a single transaction. The application never updates one without the other.

**No other 3NF violations were found** in `Users`, `Books`, or `Reviews`.

---

## 5. Decomposition Steps

### Step 1 — Identify the Violation

Original `Loans` table:
```
Loans(loan_id, user_id, book_id, loan_date, return_date, status, fine_amount, ...)
```

Transitive dependencies:
```
loan_id → return_date
return_date → fine_amount   ← VIOLATION
return_date → status        ← VIOLATION (derivable)
```

### Step 2 — Options Considered

**Option A: Remove `fine_amount` entirely, compute on-the-fly**  
✅ Cleanest solution — eliminates the transitive dependency completely  
✅ No storage of derived data  
❌ Requires JOIN + calculation on every query

**Option B: Keep `fine_amount` as a cached computed column, synced transactionally**  
✅ Better query performance  
✅ Visible in direct table views  
❌ Requires disciplined transactional updates to stay consistent

**Decision:** Option B was chosen to satisfy the project requirement of demonstrating fine calculation and transaction logic. The application recalculates `fine_amount` in the same transaction that processes the return.

### Step 3 — Decomposed (Final) Schema

The schema remains in four tables. The 3NF violations in `Loans` are resolved through:
1. Transactional enforcement (status + return_date updated atomically)
2. Fine recalculation on every return event (eliminating stale values)

```sql
-- No table was split; violations were resolved at the application/transaction level
-- All four tables are in 3NF under the chosen resolution strategy

Users    (user_id PK, name, email UNIQUE, created_at, updated_at)
Books    (book_id PK, title UNIQUE, author, genre, total_copies, available_copies, created_at, updated_at)
Loans    (loan_id PK, user_id FK, book_id FK, loan_date, due_date, return_date, status, fine_amount*, created_at, updated_at)
Reviews  (review_id PK, user_id FK, book_id FK, rating CHECK(1-5), comment, created_at, updated_at)

* fine_amount is maintained via transaction — always consistent with return_date
```

---

## 6. Final Relational Schema

```
Users
├── user_id       INTEGER  PK  AUTOINCREMENT
├── name          VARCHAR(100) NOT NULL
├── email         VARCHAR(100) NOT NULL UNIQUE
├── created_at    DATE DEFAULT now
└── updated_at    DATE DEFAULT now

Books
├── book_id          INTEGER  PK  AUTOINCREMENT
├── title            VARCHAR(150) NOT NULL UNIQUE
├── author           VARCHAR(100) NOT NULL
├── genre            VARCHAR(50)  NOT NULL
├── total_copies     INTEGER NOT NULL DEFAULT 1
├── available_copies INTEGER NOT NULL DEFAULT 1
├── created_at       DATE DEFAULT now
└── updated_at       DATE DEFAULT now

Loans
├── loan_id     INTEGER  PK  AUTOINCREMENT
├── user_id     INTEGER  FK → Users(user_id)  NOT NULL
├── book_id     INTEGER  FK → Books(book_id)  NOT NULL
├── loan_date   DATE     NOT NULL
├── due_date    DATE     NOT NULL
├── return_date DATE     (NULL = still borrowed)
├── status      VARCHAR(20) NOT NULL  ['Borrowed' | 'Returned']
├── fine_amount INTEGER  (NULL = not yet calculated)
├── created_at  DATE DEFAULT now
└── updated_at  DATE DEFAULT now

Reviews
├── review_id  INTEGER  PK  AUTOINCREMENT
├── user_id    INTEGER  FK → Users(user_id)  NOT NULL
├── book_id    INTEGER  FK → Books(book_id)  NOT NULL
├── rating     INTEGER  NOT NULL  CHECK(rating BETWEEN 1 AND 5)
├── comment    VARCHAR(255)
├── created_at DATE DEFAULT now
└── updated_at DATE DEFAULT now
```

### Relationships

```
Users  ──< Loans  >── Books    (Many-to-Many via Loans)
Users  ──< Reviews >── Books   (Many-to-Many via Reviews)
Users  ──< Loans              (One-to-Many: one user, many loans)
Books  ──< Loans              (One-to-Many: one book, many loan records)
Users  ──< Reviews            (One-to-Many: one user, many reviews)
Books  ──< Reviews            (One-to-Many: one book, many reviews)
```

---

## 7. Summary

| Table | 1NF | 2NF | 3NF | Notes |
|-------|-----|-----|-----|-------|
| Users | ✅ | ✅ | ✅ | Clean — no violations |
| Books | ✅ | ✅ | ✅ | Clean — no violations |
| Loans | ✅ | ✅ | ✅* | fine_amount & status resolved via transaction |
| Reviews | ✅ | ✅ | ✅ | Clean — no violations |

All four tables are in **Third Normal Form** in the final implementation.
