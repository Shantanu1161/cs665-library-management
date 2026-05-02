-- ============================================================
-- Library Management System — Seed Data
-- CS665 Project 3
-- ============================================================

-- ─── Users ───────────────────────────────────────────────────
INSERT INTO Users (name, email, phone, membership_type, active) VALUES
('John Doe',       'john@example.com',    '555-1001', 'premium',  1),
('Alice Smith',    'alice@example.com',   '555-1002', 'standard', 1),
('Bob Brown',      'bob@example.com',     '555-1003', 'standard', 1),
('Emma Wilson',    'emma@example.com',    '555-1004', 'premium',  1),
('Liam Taylor',    'liam@example.com',    '555-1005', 'standard', 1),
('Chris Evans',    'chris@example.com',   '555-1006', 'standard', 1),
('Sophia Lee',     'sophia@example.com',  '555-1007', 'premium',  1),
('Marcus Reed',    'marcus@example.com',  '555-1008', 'standard', 1),
('Priya Patel',    'priya@example.com',   '555-1009', 'standard', 1),
('James Carter',   'james@example.com',   '555-1010', 'premium',  1);

-- ─── Books ───────────────────────────────────────────────────
INSERT INTO Books (title, author, genre, isbn, year, total_copies, available_copies) VALUES
('The Alchemist',              'Paulo Coelho',       'Fiction',      '9780062315007', 1988, 4, 4),
('Atomic Habits',              'James Clear',        'Self-help',    '9780735211292', 2018, 3, 3),
('Clean Code',                 'Robert Martin',      'Programming',  '9780132350884', 2008, 2, 2),
('Rich Dad Poor Dad',          'Robert Kiyosaki',    'Finance',      '9781612680194', 1997, 3, 3),
('Harry Potter and the Sorcerer''s Stone', 'J.K. Rowling', 'Fantasy', '9780439708180', 1997, 5, 5),
('Deep Work',                  'Cal Newport',        'Productivity', '9781455586691', 2016, 2, 2),
('Think and Grow Rich',        'Napoleon Hill',      'Finance',      '9781585424337', 1937, 3, 3),
('The Great Gatsby',           'F. Scott Fitzgerald','Fiction',      '9780743273565', 1925, 2, 2),
('1984',                       'George Orwell',      'Dystopian',    '9780451524935', 1949, 4, 4),
('Dune',                       'Frank Herbert',      'Sci-Fi',       '9780441013593', 1965, 2, 2),
('Sapiens',                    'Yuval Noah Harari',  'Non-Fiction',  '9780062316110', 2011, 3, 3),
('To Kill a Mockingbird',      'Harper Lee',         'Fiction',      '9780061935466', 1960, 2, 2),
('The Pragmatic Programmer',   'Andrew Hunt',        'Programming',  '9780135957059', 2019, 1, 1),
('Good to Great',              'Jim Collins',        'Business',     '9780066620992', 2001, 2, 2),
('Educated',                   'Tara Westover',      'Memoir',       '9780399590504', 2018, 2, 2);

-- ─── Loans ───────────────────────────────────────────────────
INSERT INTO Loans (user_id, book_id, loan_date, due_date, return_date, status, fine_amount) VALUES
(1, 1,  '2024-02-01', '2024-02-15', '2024-02-10', 'Returned', 0),
(2, 2,  '2024-02-02', '2024-02-16', '2024-02-20', 'Returned', 8),
(3, 3,  '2024-02-03', '2024-02-17', '2024-02-12', 'Returned', 0),
(4, 4,  '2024-02-04', '2024-02-18', NULL,          'Borrowed', NULL),
(5, 5,  '2024-02-05', '2024-02-19', '2024-02-15', 'Returned', 0),
(1, 2,  '2024-02-06', '2024-02-20', '2024-02-14', 'Returned', 0),
(1, 3,  '2024-02-07', '2024-02-21', NULL,          'Borrowed', NULL),
(2, 1,  '2024-02-08', '2024-02-22', '2024-02-16', 'Returned', 0),
(3, 1,  '2024-02-09', '2024-02-23', NULL,          'Borrowed', NULL),
(6, 6,  '2024-02-10', '2024-02-24', NULL,          'Borrowed', NULL),
(7, 9,  '2024-02-11', '2024-02-25', '2024-02-28', 'Returned', 6),
(8, 10, '2024-02-12', '2024-02-26', '2024-02-26', 'Returned', 0),
(9, 11, '2024-02-13', '2024-02-27', NULL,          'Borrowed', NULL),
(10, 8, '2024-02-14', '2024-02-28', '2024-03-05', 'Returned', 14);

-- Update available_copies to reflect active borrows
UPDATE Books SET available_copies = available_copies - 1 WHERE book_id IN (4, 3, 1, 6, 11);

-- ─── Reviews ─────────────────────────────────────────────────
INSERT INTO Reviews (user_id, book_id, rating, comment) VALUES
(1, 1, 5, 'A timeless classic that changed my perspective on life.'),
(2, 2, 4, 'Very practical and easy to apply. Highly recommended.'),
(3, 3, 5, 'Essential reading for every software developer.'),
(4, 4, 3, 'Good financial insights, some parts feel repetitive.'),
(5, 5, 5, 'Amazing story — pure magic from the very first page.'),
(6, 6, 4, 'Incredibly productive framework. Changed how I work.'),
(7, 7, 5, 'Highly motivating. A must-read for anyone ambitious.'),
(1, 9, 5, 'A chilling dystopia that feels more relevant than ever.'),
(2, 8, 4, 'Beautifully written. Fitzgerald''s prose is extraordinary.'),
(3, 11, 4, 'A fascinating journey through human history.'),
(8, 10, 5, 'A sci-fi epic unlike anything I have read before.'),
(9, 12, 5, 'Profound and deeply moving. A genuine masterpiece.'),
(10, 14, 4, 'Essential for anyone running or studying a business.');
