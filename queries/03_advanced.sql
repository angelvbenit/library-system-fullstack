# Running Total of Fines per Member
SELECT
    m.full_name,
    f.issued_date,
    f.amount                        AS fine_this_row,
    SUM(f.amount) OVER (
        PARTITION BY f.member_id
        ORDER BY f.issued_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    )                               AS running_total
FROM fines f
JOIN members m ON f.member_id = m.member_id
ORDER BY m.full_name, f.issued_date;

# Rank Members by Total Borrows
SELECT
    full_name,
    total_loans,
    RANK()          OVER (ORDER BY total_loans DESC) AS rank_with_gaps,
    DENSE_RANK()    OVER (ORDER BY total_loans DESC) AS rank_no_gaps,
    ROW_NUMBER()    OVER (ORDER BY total_loans DESC) AS row_num
FROM (
    SELECT m.full_name, COUNT(l.loan_id) AS total_loans
    FROM members m
    LEFT JOIN loans l ON m.member_id = l.member_id
    GROUP BY m.member_id, m.full_name
) ranked
ORDER BY rank_with_gaps;

# Moving 3-Month Average Loans
WITH monthly AS (
    SELECT
        DATE_FORMAT(loan_date, '%Y-%m-01') AS month,
        COUNT(*) AS loan_count
    FROM loans
    GROUP BY DATE_FORMAT(loan_date, '%Y-%m-01')
)
SELECT
    month,
    loan_count,
    ROUND(AVG(loan_count) OVER (
        ORDER BY month
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 1) AS rolling_3m_avg
FROM monthly
ORDER BY month;

# First and Last Loan per Member
SELECT DISTINCT
    m.full_name,
    FIRST_VALUE(b.title) OVER (
        PARTITION BY l.member_id
        ORDER BY l.loan_date ASC
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS first_book,
    FIRST_VALUE(b.title) OVER (
        PARTITION BY l.member_id
        ORDER BY l.loan_date DESC
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS latest_book
FROM loans l
JOIN members m ON l.member_id = m.member_id
JOIN books   b ON l.book_id   = b.book_id;

# Gap Between Borrows per Member
SELECT
    m.full_name,
    l.loan_date,
    b.title,
    LAG(l.loan_date) OVER (
        PARTITION BY l.member_id ORDER BY l.loan_date
    )                                               AS prev_loan_date,
    DATEDIFF(l.loan_date, LAG(l.loan_date) OVER (
        PARTITION BY l.member_id ORDER BY l.loan_date
    ))                                              AS days_since_prev_loan
FROM loans l
JOIN members m ON l.member_id = m.member_id
JOIN books   b ON l.book_id   = b.book_id
ORDER BY m.full_name, l.loan_date;

# Percentile of Member Fine Amounts
SELECT
    m.full_name,
    total_fined,
    NTILE(4)        OVER (ORDER BY total_fined DESC) AS quartile,
    ROUND(PERCENT_RANK() OVER
        (ORDER BY total_fined) * 100, 1)             AS percentile
FROM (
    SELECT member_id, SUM(amount) AS total_fined
    FROM fines
    GROUP BY member_id
) fine_totals
JOIN members m ON fine_totals.member_id = m.member_id
ORDER BY total_fined DESC;

# Recursive CTE: Reservation Waitlist
WITH RECURSIVE waitlist AS (
    SELECT
        r.reservation_id,
        r.member_id,
        m.full_name,
        r.book_id,
        r.queue_position,
        1 AS depth
    FROM reservations r
    JOIN members m ON r.member_id = m.member_id
    WHERE r.queue_position = 1

    UNION ALL

    SELECT
        r.reservation_id,
        r.member_id,
        m.full_name,
        r.book_id,
        r.queue_position,
        w.depth + 1
    FROM reservations r
    JOIN members m ON r.member_id = m.member_id
    JOIN waitlist w ON r.book_id = w.book_id
    AND r.queue_position = w.queue_position + 1
)
SELECT * FROM waitlist ORDER BY book_id, queue_position;

# Pivot: Genre Borrows by Quarter
SELECT
    b.genre,
    SUM(CASE WHEN QUARTER(l.loan_date) = 1 THEN 1 ELSE 0 END) AS q1,
    SUM(CASE WHEN QUARTER(l.loan_date) = 2 THEN 1 ELSE 0 END) AS q2,
    SUM(CASE WHEN QUARTER(l.loan_date) = 3 THEN 1 ELSE 0 END) AS q3,
    SUM(CASE WHEN QUARTER(l.loan_date) = 4 THEN 1 ELSE 0 END) AS q4,
    COUNT(*)                                                    AS annual_total
FROM loans l
JOIN books b ON l.book_id = b.book_id
WHERE YEAR(l.loan_date) = YEAR(CURRENT_DATE)
GROUP BY b.genre
ORDER BY annual_total DESC;



# Books with Above Average Borrow Rate
SELECT
    b.title,
    b.author,
    b.genre,
    loan_counts.cnt AS borrow_count
FROM books b
JOIN (
    SELECT book_id, COUNT(*) AS cnt
    FROM loans
    GROUP BY book_id
) loan_counts ON b.book_id = loan_counts.book_id
WHERE loan_counts.cnt > (
    SELECT AVG(cnt)
    FROM (
        SELECT COUNT(*) AS cnt
        FROM loans
        GROUP BY book_id
    ) avg_sub
)
ORDER BY borrow_count DESC;

# Fine Accumulation Forecast
SELECT
    m.full_name,
    b.title,
    l.due_date,
    DATEDIFF(CURRENT_DATE, l.due_date)          AS days_overdue,
    DATEDIFF(CURRENT_DATE, l.due_date) * 0.50   AS fine_so_far,
    (DATEDIFF(CURRENT_DATE, l.due_date) + 7) * 0.50 AS fine_in_1_week
FROM loans l
JOIN members m ON l.member_id = m.member_id
JOIN books   b ON l.book_id   = b.book_id
WHERE l.return_date IS NULL
AND l.due_date < CURRENT_DATE
ORDER BY fine_so_far DESC;

# Full Text Search Across Books and Members
WITH search_term AS (
    SELECT '%tolkien%' AS term
)
SELECT
    'book'      AS result_type,
    b.book_id   AS id,
    b.title     AS name,
    b.author    AS detail
FROM books b, search_term s
WHERE LOWER(b.title)  LIKE s.term
OR    LOWER(b.author) LIKE s.term

UNION ALL

SELECT
    'member',
    m.member_id,
    m.full_name,
    m.email
FROM members m, search_term s
WHERE LOWER(m.full_name) LIKE s.term
OR    LOWER(m.email)     LIKE s.term
ORDER BY result_type, name;

# Cohort Retention: Members Still Active After 1 Year
WITH cohorts AS (
    SELECT
        member_id,
        DATE_FORMAT(join_date, '%Y-%m-01') AS cohort_month
    FROM members
    WHERE join_date IS NOT NULL
),
active_after_year AS (
    SELECT
        c.cohort_month,
        COUNT(DISTINCT c.member_id)     AS cohort_size,
        COUNT(DISTINCT l.member_id)     AS still_active
    FROM cohorts c
    LEFT JOIN loans l
        ON c.member_id = l.member_id
        AND l.loan_date >= DATE_ADD(c.cohort_month, INTERVAL 1 YEAR)
        AND l.loan_date <  DATE_ADD(c.cohort_month, INTERVAL 15 MONTH)
    GROUP BY c.cohort_month
)
SELECT
    cohort_month,
    cohort_size,
    still_active,
    ROUND(still_active / cohort_size * 100, 1) AS retention_pct
FROM active_after_year
ORDER BY cohort_month;

# Detect Duplicate ISBNs
SELECT
    isbn,
    COUNT(*)                            AS duplicate_count,
    GROUP_CONCAT(title SEPARATOR ' | ') AS conflicting_titles,
    GROUP_CONCAT(book_id SEPARATOR ', ') AS book_ids
FROM books
GROUP BY isbn
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;

# 7-Day Rolling Fine Revenue
WITH daily_fines AS (
    SELECT
        issued_date         AS day,
        SUM(amount)         AS daily_amount
    FROM fines
    WHERE paid = 1
    GROUP BY issued_date
)
SELECT
    day,
    daily_amount,
    SUM(daily_amount) OVER (
        ORDER BY day
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_7d_revenue
FROM daily_fines
ORDER BY day;

# Members with Consecutive Monthly Loans
WITH member_months AS (
    SELECT DISTINCT
        member_id,
        DATE_FORMAT(loan_date, '%Y-%m-01') AS loan_month
    FROM loans
),
with_lag AS (
    SELECT
        member_id,
        loan_month,
        LAG(loan_month) OVER (
            PARTITION BY member_id ORDER BY loan_month
        ) AS prev_month,
        CASE
            WHEN PERIOD_DIFF(
                DATE_FORMAT(loan_month, '%Y%m'),
                DATE_FORMAT(LAG(loan_month) OVER (
                    PARTITION BY member_id ORDER BY loan_month
                ), '%Y%m')
            ) = 1 THEN 1 ELSE 0
        END AS is_consecutive
    FROM member_months
)
SELECT member_id, COUNT(*) AS consecutive_months
FROM with_lag
WHERE is_consecutive = 1
GROUP BY member_id
HAVING COUNT(*) >= 2
ORDER BY consecutive_months DESC;