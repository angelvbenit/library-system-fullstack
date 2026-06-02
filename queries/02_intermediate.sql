# Books Never Borrowed
SELECT b.book_id, b.title, b.author, b.year_published
FROM books b
LEFT JOIN loans l ON b.book_id = l.book_id
WHERE l.loan_id IS NULL
ORDER BY b.year_published ASC;

# Member Borrowing History
SELECT
    l.loan_id,
    b.title,
    b.genre,
    l.loan_date,
    l.due_date,
    l.return_date,
    CASE
        WHEN l.return_date IS NULL AND l.due_date < CURRENT_DATE THEN 'Overdue'
        WHEN l.return_date IS NULL THEN 'Active'
        ELSE 'Returned'
    END                     AS loan_status,
    COALESCE(f.amount, 0)   AS fine_amount
FROM loans l
JOIN books b    ON l.book_id  = b.book_id
LEFT JOIN fines f ON l.loan_id = f.loan_id
WHERE l.member_id = 2
ORDER BY l.loan_date DESC;

# Average Days to Return by Genre
SELECT
    b.genre,
    COUNT(l.loan_id)                                AS completed_loans,
    ROUND(AVG(DATEDIFF(l.return_date, l.loan_date)), 1) AS avg_days_kept,
    MIN(DATEDIFF(l.return_date, l.loan_date))           AS fastest_return,
    MAX(DATEDIFF(l.return_date, l.loan_date))           AS slowest_return
FROM loans l
JOIN books b ON l.book_id = b.book_id
WHERE l.return_date IS NOT NULL
GROUP BY b.genre
HAVING COUNT(l.loan_id) >= 1
ORDER BY avg_days_kept DESC;

# Monthly Loan Trend (Last 12 Months)
SELECT
    DATE_FORMAT(loan_date, '%Y-%m-01')  AS month,
    COUNT(*)                            AS loans_issued,
    COUNT(DISTINCT member_id)           AS unique_borrowers
FROM loans
WHERE loan_date >= DATE_SUB(CURRENT_DATE, INTERVAL 12 MONTH)
GROUP BY DATE_FORMAT(loan_date, '%Y-%m-01')
ORDER BY month ASC;

# Members with More Than 3 Overdue Loans
SELECT
    m.full_name,
    m.email,
    m.phone,
    overdue.overdue_count
FROM members m
JOIN (
    SELECT member_id, COUNT(*) AS overdue_count
    FROM loans
    WHERE return_date IS NULL
    AND due_date < CURRENT_DATE
    GROUP BY member_id
    HAVING COUNT(*) > 3
) overdue ON m.member_id = overdue.member_id
ORDER BY overdue.overdue_count DESC;

# Fine Revenue by Month
SELECT
    DATE_FORMAT(issued_date, '%Y-%m-01')    AS month,
    COUNT(fine_id)                          AS fines_issued,
    SUM(amount)                             AS total_fined,
    SUM(CASE WHEN paid = 1 THEN amount ELSE 0 END) AS collected,
    SUM(CASE WHEN paid = 0 THEN amount ELSE 0 END) AS outstanding
FROM fines
GROUP BY DATE_FORMAT(issued_date, '%Y-%m-01')
ORDER BY month DESC;

# Books Available Right Now
SELECT
    book_id,
    title,
    author,
    total_copies,
    available_copies,
    total_copies - available_copies         AS copies_on_loan,
    ROUND(available_copies / NULLIF(total_copies, 0) * 100, 1) AS availability_pct
FROM books
WHERE available_copies > 0
ORDER BY availability_pct ASC;

# Members Who Borrowed Every Genre
SELECT m.member_id, m.full_name
FROM members m
WHERE NOT EXISTS (
    SELECT 1 FROM (
        SELECT DISTINCT genre FROM books
    ) all_genres
    WHERE NOT EXISTS (
        SELECT 1
        FROM loans l
        JOIN books b ON l.book_id = b.book_id
        WHERE l.member_id = m.member_id
        AND b.genre = all_genres.genre
    )
);

# Members Who Borrowed the Same Book
SELECT DISTINCT
    m1.full_name    AS member_1,
    m2.full_name    AS member_2,
    b.title         AS shared_book
FROM loans l1
JOIN loans   l2 ON l1.book_id = l2.book_id AND l1.member_id < l2.member_id
JOIN members m1 ON l1.member_id = m1.member_id
JOIN members m2 ON l2.member_id = m2.member_id
JOIN books    b ON l1.book_id   = b.book_id
ORDER BY shared_book, member_1;