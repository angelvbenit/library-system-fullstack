USE library_db;

-- BOOKS
INSERT INTO books (isbn, title, author, genre, year_published, total_copies, available_copies) VALUES
('9780061096006', 'To Kill a Mockingbird', 'Harper Lee', 'Fiction', 1960, 3, 3),
('9780743273565', 'The Great Gatsby', 'F. Scott Fitzgerald', 'Fiction', 1925, 2, 2),
('9780451524935', '1984', 'George Orwell', 'Science Fiction', 1949, 4, 4),
('9780061120084', 'To Kill a Mockingbird 2', 'Harper Lee', 'Fiction', 1960, 2, 2),
('9780345391803', 'The Hitchhiker\'s Guide', 'Douglas Adams', 'Science Fiction', 1979, 3, 3),
('9780743477123', 'Dune', 'Frank Herbert', 'Science Fiction', 1965, 3, 3),
('9780385490818', 'The Handmaid\'s Tale', 'Margaret Atwood', 'Fiction', 1985, 2, 2),
('9780679783268', 'Crime and Punishment', 'Fyodor Dostoevsky', 'Classic', 1866, 2, 2),
('9780141439518', 'Pride and Prejudice', 'Jane Austen', 'Classic', 1813, 3, 3),
('9780316769174', 'The Catcher in the Rye', 'J.D. Salinger', 'Fiction', 1951, 2, 2),
('9780553293357', 'Foundation', 'Isaac Asimov', 'Science Fiction', 1951, 3, 3),
('9780062316097', 'Sapiens', 'Yuval Noah Harari', 'Non-Fiction', 2011, 4, 4),
('9781501156700', 'Thinking Fast and Slow', 'Daniel Kahneman', 'Non-Fiction', 2011, 3, 3),
('9780385333481', 'The Selfish Gene', 'Richard Dawkins', 'Science', 1976, 2, 2),
('9780679601685', 'A Brief History of Time', 'Stephen Hawking', 'Science', 1988, 3, 3);

-- MEMBERS
INSERT INTO members (full_name, email, phone, join_date, expiry_date, membership_type, status) VALUES
('Arjun Sharma', 'arjun.sharma@email.com', '9876543210', '2023-01-15', '2025-01-15', 'standard', 'active'),
('Priya Nair', 'priya.nair@email.com', '9845012345', '2023-03-20', '2025-03-20', 'premium', 'active'),
('Rohit Shetty', 'rohit.shetty@email.com', '9731245678', '2023-06-10', '2024-06-10', 'student', 'expired'),
('Sneha Patel', 'sneha.patel@email.com', '9632587410', '2024-01-05', '2026-01-05', 'premium', 'active'),
('Kiran Rao', 'kiran.rao@email.com', '9512345678', '2024-02-14', '2026-02-14', 'standard', 'active'),
('Divya Menon', 'divya.menon@email.com', '9423156789', '2024-04-01', '2025-04-01', 'student', 'suspended'),
('Aditya Kumar', 'aditya.kumar@email.com', '9314567890', '2024-06-20', '2026-06-20', 'standard', 'active'),
('Lakshmi Iyer', 'lakshmi.iyer@email.com', '9205678901', '2024-08-11', '2026-08-11', 'premium', 'active');

-- LOANS
INSERT INTO loans (book_id, member_id, loan_date, due_date, return_date, renewed_count) VALUES
(1, 1, '2024-01-10', '2024-01-24', '2024-01-20', 0),
(2, 1, '2024-02-05', '2024-02-19', '2024-02-18', 0),
(3, 2, '2024-01-15', '2024-01-29', '2024-02-05', 1),
(4, 2, '2024-03-01', '2024-03-15', NULL, 0),
(5, 3, '2024-02-10', '2024-02-24', '2024-02-22', 0),
(6, 4, '2024-03-05', '2024-03-19', NULL, 0),
(7, 4, '2024-01-20', '2024-02-03', '2024-02-01', 0),
(8, 5, '2024-02-15', '2024-03-01', '2024-03-10', 0),
(9, 5, '2024-03-10', '2024-03-24', NULL, 1),
(10, 6, '2024-01-25', '2024-02-08', '2024-02-06', 0),
(11, 7, '2024-02-20', '2024-03-05', NULL, 0),
(12, 7, '2024-03-15', '2024-03-29', NULL, 0),
(13, 8, '2024-01-30', '2024-02-13', '2024-02-20', 0),
(14, 8, '2024-03-20', '2024-04-03', NULL, 0),
(15, 1, '2024-03-25', '2024-04-08', NULL, 0),
(1, 3, '2024-02-28', '2024-03-13', NULL, 0),
(2, 5, '2024-03-18', '2024-04-01', NULL, 0),
(3, 6, '2024-01-05', '2024-01-19', '2024-01-30', 0),
(5, 8, '2024-02-25', '2024-03-10', NULL, 0),
(6, 2, '2024-03-22', '2024-04-05', NULL, 0);

-- FINES
INSERT INTO fines (loan_id, member_id, amount, issued_date, paid, paid_date) VALUES
(3, 2, 3.50, '2024-02-06', 1, '2024-02-10'),
(8, 5, 4.50, '2024-03-11', 1, '2024-03-15'),
(13, 8, 3.50, '2024-02-21', 0, NULL),
(18, 6, 5.50, '2024-01-31', 0, NULL),
(10, 6, 2.00, '2024-02-09', 1, '2024-02-12');

-- RESERVATIONS
INSERT INTO reservations (book_id, member_id, reserved_date, queue_position, notified) VALUES
(3, 4, '2024-03-20', 1, 0),
(6, 1, '2024-03-23', 1, 0),
(9, 7, '2024-03-25', 1, 1),
(11, 3, '2024-03-26', 1, 0);

USE library_db;

SELECT 'books'        AS table_name, COUNT(*) AS total FROM books
UNION ALL
SELECT 'members',      COUNT(*) FROM members
UNION ALL
SELECT 'loans',        COUNT(*) FROM loans
UNION ALL
SELECT 'fines',        COUNT(*) FROM fines
UNION ALL
SELECT 'reservations', COUNT(*) FROM reservations;