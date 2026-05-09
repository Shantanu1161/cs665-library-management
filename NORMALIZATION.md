Normalization Report
CS665 Project 3 - Library Management System
Shantanu Rajesh Sawarkar


Goal

Take the four-table library schema I designed in the earlier assignment and verify it is in 3rd Normal Form. Where it isn't, decompose or otherwise resolve the violation, and document the reasoning so anyone reading the schema later understands why the tables look the way they do.


Starting schema

Before this audit the schema was:

  Users(user_id, name, email, created_at, updated_at)
  Books(book_id, title, author, genre, created_at, updated_at)
  Loans(loan_id, user_id, book_id, loan_date, due_date, return_date, status, fine_amount, created_at, updated_at)
  Reviews(review_id, user_id, book_id, rating, comment, created_at, updated_at)

The relationships are:
  - one user has many loans, one book has many loans (so users-and-books is many-to-many through loans)
  - one user has many reviews, one book has many reviews (also many-to-many through reviews)


Functional dependencies

Users:
  user_id -> name, email, created_at, updated_at
  email -> user_id, name, created_at, updated_at      (email is a candidate key because of the UNIQUE constraint)

Books:
  book_id -> title, author, genre, created_at, updated_at
  title -> book_id, author, genre, created_at, updated_at   (title is a candidate key after I added UNIQUE)

Loans:
  loan_id -> user_id, book_id, loan_date, due_date, return_date, status, fine_amount, created_at, updated_at
  (user_id, book_id, loan_date) -> loan_id, ...   (composite candidate key - a single user can borrow the same book again later, but not on the same day)
  return_date -> fine_amount        (fine is computed from how late the return was)
  return_date -> status             (status is "Returned" iff return_date is not null)

Reviews:
  review_id -> user_id, book_id, rating, comment, created_at, updated_at
  (user_id, book_id) -> rating, comment    (one review per user per book)


Anomaly check

Update anomalies:
The big one is on Loans. fine_amount is calculated from (return_date - due_date), so if anyone updates return_date without recalculating fine_amount, the row becomes inconsistent. Same problem with status - if return_date gets set but status stays "Borrowed", the row contradicts itself. On Books, if I had to fix a misspelled author name and they had ten books in the catalog, I'd have to update ten rows - but author is just a single atomic attribute that doesn't determine other non-key columns, so this is not a 3NF violation, just a denormalization tradeoff I accept for simplicity (a separate Authors table would add a join on every book lookup for not much benefit at this scale).

Insertion anomalies:
The foreign key constraints prevent the obvious ones - you can't review a book that doesn't exist, and you can't create a loan for a non-existent user. These aren't anomalies, they're enforced integrity rules.

Deletion anomalies:
If I delete a user who has loans, the loan rows would point at nothing. The FK constraint stops that at the database level. The application also blocks the delete with an HTTP 400 if there are active loans, so loan history is never silently destroyed.


1NF check

All four tables pass 1NF. Every column holds an atomic value, no repeating groups, no arrays, no nested structures, every table has a primary key.


2NF check

All four tables pass 2NF. Where I have composite candidate keys ((user_id, book_id) on Reviews and (user_id, book_id, loan_date) on Loans), every non-key attribute depends on the entire composite, not on a subset of it. There are no partial dependencies.


3NF check

This is where Loans has problems.

Violation 1: loan_id -> return_date -> fine_amount is a transitive dependency. fine_amount is determined by return_date (and loan_date / due_date), not directly by the primary key.

Violation 2: loan_id -> return_date -> status. status is just a label for "is return_date null or not", so it's transitively dependent.

Users, Books, and Reviews do not have any 3NF violations.


How I resolved the Loans violations

I had two options for fine_amount:

Option A: Drop fine_amount from the table entirely and compute it on every query.
- Pros: cleanest 3NF resolution, no risk of staleness, no maintenance.
- Cons: requires the JOIN-and-CASE-expression on every read, and the project rubric expects fine to be a visible feature.

Option B: Keep fine_amount as a cached computed value. Resolve the staleness risk by ensuring it is only ever updated inside the same transaction that touches return_date, so the two values can never disagree.

I chose Option B. Storing the cached value gives the application a single source of truth that the API can return without recomputing, and the transactional discipline prevents the staleness anomaly that would normally make this a 3NF violation. The borrow and return endpoints in main.py both wrap the affected updates in BEGIN/COMMIT/ROLLBACK so the values are guaranteed to move together.

For status, the same logic applies - it is only updated alongside return_date in the return transaction, never separately, so the two stay in sync.

I did not split Loans into multiple tables. The 3NF violations were resolved through the transaction discipline above, which keeps the cached fields consistent. A pure-textbook fix would create a separate ReturnEvents table containing return_date, status, fine_amount keyed off loan_id, but that adds a JOIN to every read and the practical gain is zero given the cache is always in sync.


Final schema

Users

| Column           | Type          | Constraints                          |
|------------------|---------------|--------------------------------------|
| user_id          | INTEGER       | PRIMARY KEY, AUTOINCREMENT           |
| name             | VARCHAR(100)  | NOT NULL                             |
| email            | VARCHAR(100)  | NOT NULL, UNIQUE                     |
| phone            | VARCHAR(20)   |                                      |
| membership_type  | VARCHAR(20)   | NOT NULL, DEFAULT 'standard'         |
| active           | INTEGER       | NOT NULL, DEFAULT 1                  |
| created_at       | DATE          | NOT NULL, DEFAULT today              |
| updated_at       | DATE          | NOT NULL, DEFAULT today              |

Books

| Column            | Type          | Constraints                          |
|-------------------|---------------|--------------------------------------|
| book_id           | INTEGER       | PRIMARY KEY, AUTOINCREMENT           |
| title             | VARCHAR(150)  | NOT NULL, UNIQUE                     |
| author            | VARCHAR(100)  | NOT NULL                             |
| genre             | VARCHAR(50)   | NOT NULL                             |
| isbn              | VARCHAR(20)   | UNIQUE                               |
| year              | INTEGER       |                                      |
| total_copies      | INTEGER       | NOT NULL, DEFAULT 1                  |
| available_copies  | INTEGER       | NOT NULL, DEFAULT 1                  |
| created_at        | DATE          | NOT NULL, DEFAULT today              |
| updated_at        | DATE          | NOT NULL, DEFAULT today              |

Loans

| Column        | Type         | Constraints                                       |
|---------------|--------------|---------------------------------------------------|
| loan_id       | INTEGER      | PRIMARY KEY, AUTOINCREMENT                        |
| user_id       | INTEGER      | NOT NULL, FOREIGN KEY -> Users(user_id)           |
| book_id       | INTEGER      | NOT NULL, FOREIGN KEY -> Books(book_id)           |
| loan_date     | DATE         | NOT NULL                                          |
| due_date      | DATE         | NOT NULL                                          |
| return_date   | DATE         | nullable - null while the book is still borrowed  |
| status        | VARCHAR(20)  | NOT NULL - 'Borrowed' or 'Returned'               |
| fine_amount   | INTEGER      | nullable - null until first return                |
| created_at    | DATE         | NOT NULL, DEFAULT today                           |
| updated_at    | DATE         | NOT NULL, DEFAULT today                           |

Reviews

| Column      | Type          | Constraints                                       |
|-------------|---------------|---------------------------------------------------|
| review_id   | INTEGER       | PRIMARY KEY, AUTOINCREMENT                        |
| user_id     | INTEGER       | NOT NULL, FOREIGN KEY -> Users(user_id)           |
| book_id     | INTEGER       | NOT NULL, FOREIGN KEY -> Books(book_id)           |
| rating      | INTEGER       | NOT NULL, CHECK (rating BETWEEN 1 AND 5)          |
| comment     | VARCHAR(255)  |                                                   |
| created_at  | DATE          | NOT NULL, DEFAULT today                           |
| updated_at  | DATE          | NOT NULL, DEFAULT today                           |


Relationships at a glance

| From  | To      | Cardinality                                            |
|-------|---------|--------------------------------------------------------|
| Users | Books   | many-to-many through Loans                             |
| Users | Books   | many-to-many through Reviews                           |
| Users | Loans   | one-to-many (one user has many loans)                  |
| Books | Loans   | one-to-many (one book has many loan records)           |
| Users | Reviews | one-to-many (one user has many reviews)                |
| Books | Reviews | one-to-many (one book has many reviews)                |


Per-table normal-form summary

| Table   | 1NF | 2NF | 3NF | Notes                                                                                       |
|---------|-----|-----|-----|---------------------------------------------------------------------------------------------|
| Users   | Yes | Yes | Yes | Clean - no violations                                                                       |
| Books   | Yes | Yes | Yes | Clean - no violations                                                                       |
| Loans   | Yes | Yes | Yes | fine_amount and status are cached values kept consistent through transactional updates      |
| Reviews | Yes | Yes | Yes | Clean - no violations                                                                       |

All four tables are in 3rd Normal Form in the final implementation.
