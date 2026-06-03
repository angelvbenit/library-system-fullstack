from flask import Blueprint, jsonify
from config import get_connection

system_bp = Blueprint('system', __name__)

undo_stack = []
saved_session_state = None

def get_all_data(cursor):
    data = {}
    for table in ['books', 'members', 'loans', 'fines', 'reservations']:
        cursor.execute(f"SELECT * FROM {table}")
        data[table] = cursor.fetchall()
    return data

def restore_data(cursor, data):
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    for table in ['fines', 'reservations', 'loans', 'members', 'books']:
        cursor.execute(f"DELETE FROM {table}")
        if data.get(table) and len(data[table]) > 0:
            cols = data[table][0].keys()
            placeholders = ', '.join(['%s'] * len(cols))
            col_names = ', '.join(cols)
            query = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"
            for row in data[table]:
                cursor.execute(query, tuple(row.values()))
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

@system_bp.route('/snapshot', methods=['POST'])
def snapshot():
    global undo_stack
    try:
        conn = get_connection()
        if not conn: return jsonify({'error': 'DB error'}), 500
        cursor = conn.cursor(dictionary=True)
        undo_stack.append(get_all_data(cursor))
        if len(undo_stack) > 15:
            undo_stack.pop(0)
        cursor.close()
        conn.close()
        return jsonify({"message": "Snapshot saved"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@system_bp.route('/save-state', methods=['POST'])
def save_state():
    global saved_session_state
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    saved_session_state = get_all_data(cursor)
    cursor.close()
    conn.close()
    return jsonify({"message": "Current state saved as checkpoint."})

@system_bp.route('/undo', methods=['POST'])
def undo():
    global undo_stack
    if not undo_stack:
        return jsonify({"error": "No actions left to undo."}), 400
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    previous_data = undo_stack.pop()
    restore_data(cursor, previous_data)
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Undo successful"})

@system_bp.route('/restore-state', methods=['POST'])
def restore_state():
    global saved_session_state
    if not saved_session_state:
        return jsonify({"error": "No saved checkpoint found."}), 400
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    restore_data(cursor, saved_session_state)
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Restored to last saved checkpoint."})

@system_bp.route('/reset-default', methods=['POST'])
def reset_default():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        
        # Wipe tables and strictly reset the auto-increment counters back to 1
        for table in ['fines', 'reservations', 'loans', 'members', 'books']:
            cursor.execute(f"DELETE FROM {table}")
            cursor.execute(f"ALTER TABLE {table} AUTO_INCREMENT = 1")
            
        queries = [
            """INSERT INTO books (isbn, title, author, genre, year_published, total_copies, available_copies) VALUES 
            ('9780061096006', 'To Kill a Mockingbird', 'Harper Lee', 'Fiction', 1960, 3, 3),
            ('9780743273565', 'The Great Gatsby', 'F. Scott Fitzgerald', 'Fiction', 1925, 2, 2),
            ('9780451524935', '1984', 'George Orwell', 'Science Fiction', 1949, 4, 4),
            ('9780061120084', 'To Kill a Mockingbird 2', 'Harper Lee', 'Fiction', 1960, 2, 2),
            ('9780345391803', 'The Hitchhikers Guide', 'Douglas Adams', 'Science Fiction', 1979, 3, 3),
            ('9780743477123', 'Dune', 'Frank Herbert', 'Science Fiction', 1965, 3, 3),
            ('9780385490818', 'The Handmaids Tale', 'Margaret Atwood', 'Fiction', 1985, 2, 2),
            ('9780679783268', 'Crime and Punishment', 'Fyodor Dostoevsky', 'Classic', 1866, 2, 2),
            ('9780141439518', 'Pride and Prejudice', 'Jane Austen', 'Classic', 1813, 3, 3),
            ('9780316769174', 'The Catcher in the Rye', 'J.D. Salinger', 'Fiction', 1951, 2, 2),
            ('9780553293357', 'Foundation', 'Isaac Asimov', 'Science Fiction', 1951, 3, 3),
            ('9780062316097', 'Sapiens', 'Yuval Noah Harari', 'Non-Fiction', 2011, 4, 4),
            ('9781501156700', 'Thinking Fast and Slow', 'Daniel Kahneman', 'Non-Fiction', 2011, 3, 3),
            ('9780385333481', 'The Selfish Gene', 'Richard Dawkins', 'Science', 1976, 2, 2),
            ('9780679601685', 'A Brief History of Time', 'Stephen Hawking', 'Science', 1988, 3, 3)""",

            """INSERT INTO members (full_name, email, phone, join_date, expiry_date, membership_type, status) VALUES
            ('Arjun Sharma', 'arjun.sharma@email.com', '9876543210', '2023-01-15', '2025-01-15', 'standard', 'active'),
            ('Priya Nair', 'priya.nair@email.com', '9845012345', '2023-03-20', '2025-03-20', 'premium', 'active'),
            ('Rohit Shetty', 'rohit.shetty@email.com', '9731245678', '2023-06-10', '2024-06-10', 'student', 'expired'),
            ('Sneha Patel', 'sneha.patel@email.com', '9632587410', '2024-01-05', '2026-01-05', 'premium', 'active'),
            ('Kiran Rao', 'kiran.rao@email.com', '9512345678', '2024-02-14', '2026-02-14', 'standard', 'active'),
            ('Divya Menon', 'divya.menon@email.com', '9423156789', '2024-04-01', '2025-04-01', 'student', 'suspended'),
            ('Aditya Kumar', 'aditya.kumar@email.com', '9314567890', '2024-06-20', '2026-06-20', 'standard', 'active'),
            ('Lakshmi Iyer', 'lakshmi.iyer@email.com', '9205678901', '2024-08-11', '2026-08-11', 'premium', 'active')""",

            """INSERT INTO loans (book_id, member_id, loan_date, due_date, return_date, renewed_count) VALUES
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
            (6, 2, '2024-03-22', '2024-04-05', NULL, 0)""",

            """INSERT INTO fines (loan_id, member_id, amount, issued_date, paid, paid_date) VALUES
            (3, 2, 3.50, '2024-02-06', 1, '2024-02-10'),
            (8, 5, 4.50, '2024-03-11', 1, '2024-03-15'),
            (13, 8, 3.50, '2024-02-21', 0, NULL),
            (18, 6, 5.50, '2024-01-31', 0, NULL),
            (10, 6, 2.00, '2024-02-09', 1, '2024-02-12')""",

            """INSERT INTO reservations (book_id, member_id, reserved_date, queue_position, notified) VALUES
            (3, 4, '2024-03-20', 1, 0),
            (6, 1, '2024-03-23', 1, 0),
            (9, 7, '2024-03-25', 1, 1),
            (11, 3, '2024-03-26', 1, 0)"""
        ]

        for q in queries:
            cursor.execute(q)

        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()
        return jsonify({'message': 'Database reset to original seed data successfully.'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()