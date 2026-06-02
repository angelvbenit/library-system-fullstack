# List All Books
SELECT book_id, title, author, isbn, genre, year_published, total_copies, available_copies
FROM books
ORDER BY title ASC;

# Active Members Only
SELECT member_id, full_name, email, membership_type, expiry_date
FROM members
WHERE status = 'active'
AND expiry_date >= CURRENT_DATE
ORDER BY expiry_date ASC;

# Books in a Genre
SELECT title, author, year_published
FROM books
WHERE genre = 'Science Fiction'

UNION ALL

SELECT title, author, year_published
FROM books
WHERE LOWER(title) LIKE '%foundation%';

# Count Books per Genre
SELECT
    genre,
    COUNT(*)            AS total_books,
    SUM(total_copies)   AS total_copies,
    ROUND(AVG(year_published), 0) AS avg_pub_year
FROM books
GROUP BY genre
ORDER BY total_books DESC;

# Members Who Joined This Year
SELECT full_name, email, join_date, membership_type
FROM members
WHERE YEAR(join_date) = YEAR(CURRENT_DATE)
ORDER BY join_date DESC;

# Overdue Loans
SELECT
    l.loan_id,
    m.full_name         AS member_name,
    b.title             AS book_title,
    l.due_date,
    DATEDIFF(CURRENT_DATE, l.due_date) AS days_overdue
FROM loans l
JOIN members m ON l.member_id = m.member_id
JOIN books   b ON l.book_id   = b.book_id
WHERE l.return_date IS NULL
AND l.due_date < CURRENT_DATE
ORDER BY days_overdue DESC;

# Top 5 Most Borrowed Books
SELECT
    b.title,
    b.author,
    COUNT(l.loan_id) AS borrow_count
FROM books b
LEFT JOIN loans l ON b.book_id = l.book_id
GROUP BY b.book_id, b.title, b.author
ORDER BY borrow_count DESC
LIMIT 5;

# Members with Unpaid Fines
SELECT
    m.member_id,
    m.full_name,
    m.email,
    COUNT(f.fine_id)    AS open_fines,
    SUM(f.amount)       AS total_owed
FROM members m
JOIN fines f ON m.member_id = f.member_id
WHERE f.paid = 0
GROUP BY m.member_id, m.full_name, m.email
HAVING SUM(f.amount) > 0
ORDER BY total_owed DESC;

