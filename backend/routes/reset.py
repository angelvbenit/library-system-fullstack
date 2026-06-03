from flask import Blueprint, jsonify, request
from config import get_connection
from datetime import date

reset_bp = Blueprint('reset', __name__)

# ── SEED DATA ──────────────────────────────────────────────────────────────────
# This is your original seed data. Edit these lists if you ever change the seed.

SEED_BOOKS = [
    (1,  '978-0-06-112008-4',  'To Kill a Mockingbird',              'Harper Lee',          'Fiction',          1960, 4, 4),
    (2,  '978-0-7432-7356-5',  'The Great Gatsby',                   'F. Scott Fitzgerald',  'Fiction',          1925, 3, 3),
    (3,  '978-0-14-028329-7',  '1984',                               'George Orwell',        'Science Fiction',  1949, 5, 5),
    (4,  '978-0-7432-7357-2',  'Pride and Prejudice',                'Jane Austen',          'Classic',          1813, 3, 3),
    (5,  '978-0-06-093546-9',  'To Kill a Mockingbird (Special Ed)', 'Harper Lee',          'Fiction',          1960, 2, 2),
    (6,  '978-0-14-303943-3',  'The Catcher in the Rye',             'J.D. Salinger',        'Fiction',          1951, 3, 3),
    (7,  '978-0-618-34399-7',  'The Lord of the Rings',              'J.R.R. Tolkien',       'Fiction',          1954, 4, 4),
    (8,  '978-0-7432-7358-9',  'Brave New World',                    'Aldous Huxley',        'Science Fiction',  1932, 3, 3),
    (9,  '978-0-06-112009-1',  'The Alchemist',                      'Paulo Coelho',         'Fiction',          1988, 4, 4),
    (10, '978-0-14-028330-3',  'Animal Farm',                        'George Orwell',        'Classic',          1945, 3, 3),
    (11, '978-0-553-29335-7',  'Foundation',                         'Isaac Asimov',         'Science Fiction',  1951, 3, 3),
    (12, '978-0-06-093548-3',  'Sapiens',                            'Yuval Noah Harari',    'Non-Fiction',      2011, 3, 3),
    (13, '978-0-7432-7359-6',  'A Brief History of Time',            'Stephen Hawking',      'Science',          1988, 2, 2),
    (14, '978-0-14-028331-0',  'The Selfish Gene',                   'Richard Dawkins',      'Science',          1976, 2, 2),
    (15, '978-0-06-112010-7',  'Thinking, Fast and Slow',            'Daniel Kahneman',      'Non-Fiction',      2011, 3, 3),
]

SEED_MEMBERS = [
    (1,  'Arjun Sharma',    'arjun.sharma@email.com',    '9876543210', '2023-01-15', '2024-01-15', 'premium',  'active'),
    (2,  'Priya Nair',      'priya.nair@email.com',      '9876543211', '2023-02-20', '2024-02-20', 'standard', 'active'),
    (3,  'Ravi Kumar',      'ravi.kumar@email.com',      '9876543212', '2023-03-10', '2025-03-10', 'student',  'active'),
    (4,  'Sneha Reddy',     'sneha.reddy@email.com',     '9876543213', '2023-04-05', '2025-04-05', 'premium',  'active'),
    (5,  'Vikram Singh',    'vikram.singh@email.com',    '9876543214', '2023-05-12', '2024-05-12', 'standard', 'suspended'),
    (6,  'Divya Menon',     'divya.menon@email.com',     '9876543215', '2023-06-18', '2024-06-18', 'student',  'active'),
    (7,  'Kiran Patel',     'kiran.patel@email.com',     '9876543216', '2023-07-22', '2025-07-22', 'premium',  'active'),
    (8,  'Aditya Joshi',    'aditya.joshi@email.com',    '9876543217', '2023-08-30', '2025-08-30', 'standard', 'active'),
    (9,  'Lakshmi Iyer',    'lakshmi.iyer@email.com',    '9876543218', '2023-09-14', '2024-09-14', 'student',  'active'),
    (10, 'Rahul Gupta',     'rahul.gupta@email.com',     '9876543219', '2023-10-25', '2024-10-25', 'standard', 'expired'),
]

SEED_LOANS = [
    (1,  1,  1,  '2024-01-10', '2024-01-24', '2024-01-22', 0),
    (2,  2,  2,  '2024-01-15', '2024-01-29', '2024-02-05', 0),
    (3,  3,  3,  '2024-02-01', '2024-02-15', None,          0),
    (4,  1,  4,  '2024-02-10', '2024-02-24', '2024-02-20', 0),
    (5,  2,  5,  '2024-02-15', '2024-03-01', None,          1),
    (6,  4,  6,  '2024-03-01', '2024-03-15', '2024-03-10', 0),
    (7,  3,  7,  '2024-03-05', '2024-03-19', None,          0),
    (8,  5,  8,  '2024-03-10', '2024-03-24', '2024-03-20', 0),
    (9,  1,  9,  '2024-03-15', '2024-03-29', None,          2),
    (10, 6,  10, '2024-04-01', '2024-04-15', '2024-04-12', 0),
    (11, 2,  11, '2024-04-05', '2024-04-19', None,          0),
    (12, 7,  12, '2024-04-10', '2024-04-24', '2024-04-22', 0),
    (13, 3,  13, '2024-04-15', '2024-04-29', None,          1),
    (14, 8,  1,  '2024-05-01', '2024-05-15', '2024-05-10', 0),
    (15, 9,  2,  '2024-05-05', '2024-05-19', None,          0),
]

SEED_FINES = [
    (1, 2,  2,  2.50, '2024-02-05', 0, None),
    (2, 3,  9,  3.00, '2024-03-15', 1, '2024-03-20'),
    (3, 6,  13, 3.00, '2024-05-15', 1, '2024-05-18'),
    (4, 9,  15, 1.00, '2024-05-19', 0, None),
    (5, 6,  2,  2.50, '2024-02-10', 0, None),
]

SEED_RESERVATIONS = [
    (1, 3, 6, '2024-03-20', 1, 0),
    (2, 4, 7, '2024-04-10', 2, 0),
    (3, 5, 3, '2024-04-15', 1, 1),
    (4, 6, 3, '2024-04-20', 2, 0),
]


# ── RESET TO DEFAULT (wipe everything, re-insert seed) ────────────────────────
@reset_bp.route('/reset-to-default', methods=['POST'])
def reset_to_default():
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor()
    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

        cursor.execute("TRUNCATE TABLE reservations")
        cursor.execute("TRUNCATE TABLE fines")
        cursor.execute("TRUNCATE TABLE loans")
        cursor.execute("TRUNCATE TABLE members")
        cursor.execute("TRUNCATE TABLE books")

        cursor.executemany("""
            INSERT INTO books
              (book_id, isbn, title, author, genre, year_published, total_copies, available_copies)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, SEED_BOOKS)

        cursor.executemany("""
            INSERT INTO members
              (member_id, full_name, email, phone, join_date, expiry_date, membership_type, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, SEED_MEMBERS)

        cursor.executemany("""
            INSERT INTO loans
              (loan_id, book_id, member_id, loan_date, due_date, return_date, renewed_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, SEED_LOANS)

        cursor.executemany("""
            INSERT INTO fines
              (fine_id, member_id, loan_id, amount, issued_date, paid, paid_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, SEED_FINES)

        cursor.executemany("""
            INSERT INTO reservations
              (reservation_id, book_id, member_id, reserved_date, queue_position, notified)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, SEED_RESERVATIONS)

        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()

    except Exception as e:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({'error': f'Reset failed: {str(e)}'}), 500

    cursor.close()
    conn.close()
    return jsonify({'message': 'Database reset to default seed data successfully'})