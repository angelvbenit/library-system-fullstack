USE library_db;

-- Speeds up overdue loan queries (only indexes open loans)
CREATE INDEX idx_loans_overdue
ON loans(due_date);

-- Speeds up member borrowing history
CREATE INDEX idx_loans_member_date
ON loans(member_id, loan_date DESC);

-- Speeds up expiry campaign queries
CREATE INDEX idx_members_status_expiry
ON members(status, expiry_date);

-- Speeds up genre aggregations
CREATE INDEX idx_books_genre
ON books(genre);

-- Speeds up fine lookups by member
CREATE INDEX idx_fines_member
ON fines(member_id);

-- Speeds up unpaid fine queries
CREATE INDEX idx_fines_paid
ON fines(paid);
