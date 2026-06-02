from flask import Blueprint, jsonify, request
from config import get_connection
from datetime import date, timedelta

loans_bp = Blueprint('loans', __name__)

# GET all loans
@loans_bp.route('/', methods=['GET'])
def get_loans():
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            l.loan_id,
            b.title         AS book_title,
            m.full_name     AS member_name,
            l.loan_date,
            l.due_date,
            l.return_date,
            l.renewed_count,
            CASE
                WHEN l.return_date IS NULL AND l.due_date < CURRENT_DATE THEN 'Overdue'
                WHEN l.return_date IS NULL THEN 'Active'
                ELSE 'Returned'
            END             AS loan_status
        FROM loans l
        JOIN books b   ON l.book_id   = b.book_id
        JOIN members m ON l.member_id = m.member_id
        ORDER BY l.loan_date DESC
    """)
    loans = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(loans)

# GET single loan
@loans_bp.route('/<int:loan_id>', methods=['GET'])
def get_loan(loan_id):
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            l.loan_id,
            b.title         AS book_title,
            m.full_name     AS member_name,
            l.loan_date,
            l.due_date,
            l.return_date,
            l.renewed_count,
            CASE
                WHEN l.return_date IS NULL AND l.due_date < CURRENT_DATE THEN 'Overdue'
                WHEN l.return_date IS NULL THEN 'Active'
                ELSE 'Returned'
            END             AS loan_status
        FROM loans l
        JOIN books b   ON l.book_id   = b.book_id
        JOIN members m ON l.member_id = m.member_id
        WHERE l.loan_id = %s
    """, (loan_id,))
    loan = cursor.fetchone()
    cursor.close()
    conn.close()
    if not loan:
        return jsonify({'error': 'Loan not found'}), 404
    return jsonify(loan)

# POST issue a book
@loans_bp.route('/', methods=['POST'])
def issue_book():
    data = request.get_json()
    required = ['book_id', 'member_id']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing required fields'}), 400
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor(dictionary=True)

    # Check book is available
    cursor.execute("SELECT available_copies FROM books WHERE book_id = %s", (data['book_id'],))
    book = cursor.fetchone()
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    if book['available_copies'] < 1:
        return jsonify({'error': 'No copies available'}), 400

    # Check member is active
    cursor.execute("SELECT status FROM members WHERE member_id = %s", (data['member_id'],))
    member = cursor.fetchone()
    if not member:
        return jsonify({'error': 'Member not found'}), 404
    if member['status'] != 'active':
        return jsonify({'error': 'Member is not active'}), 400

    # Create loan — due date is 14 days from today
    loan_date = date.today()
    due_date = loan_date + timedelta(days=14)

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO loans (book_id, member_id, loan_date, due_date)
        VALUES (%s, %s, %s, %s)
    """, (data['book_id'], data['member_id'], loan_date, due_date))
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({
        'message': 'Book issued successfully',
        'loan_id': new_id,
        'due_date': str(due_date)
    }), 201

# PUT return a book
@loans_bp.route('/<int:loan_id>/return', methods=['PUT'])
def return_book(loan_id):
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor(dictionary=True)

    # Get loan details
    cursor.execute("""
        SELECT loan_id, book_id, member_id, due_date, return_date
        FROM loans WHERE loan_id = %s
    """, (loan_id,))
    loan = cursor.fetchone()
    if not loan:
        return jsonify({'error': 'Loan not found'}), 404
    if loan['return_date']:
        return jsonify({'error': 'Book already returned'}), 400

    return_date = date.today()

    # Update loan return date — trigger will increment available_copies
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE loans SET return_date = %s WHERE loan_id = %s
    """, (return_date, loan_id))

    # Calculate fine if overdue
    fine_amount = 0
    if return_date > loan['due_date']:
        days_overdue = (return_date - loan['due_date']).days
        fine_amount = round(days_overdue * 0.50, 2)
        cursor.execute("""
            INSERT INTO fines (loan_id, member_id, amount, issued_date)
            VALUES (%s, %s, %s, %s)
        """, (loan_id, loan['member_id'], fine_amount, return_date))

    conn.commit()
    cursor.close()
    conn.close()

    response = {'message': 'Book returned successfully', 'return_date': str(return_date)}
    if fine_amount > 0:
        response['fine_charged'] = fine_amount
    return jsonify(response)

# PUT renew a loan
@loans_bp.route('/<int:loan_id>/renew', methods=['PUT'])
def renew_loan(loan_id):
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT loan_id, due_date, return_date, renewed_count
        FROM loans WHERE loan_id = %s
    """, (loan_id,))
    loan = cursor.fetchone()
    if not loan:
        return jsonify({'error': 'Loan not found'}), 404
    if loan['return_date']:
        return jsonify({'error': 'Cannot renew a returned loan'}), 400
    if loan['renewed_count'] >= 2:
        return jsonify({'error': 'Maximum renewals reached'}), 400

    new_due_date = loan['due_date'] + timedelta(days=14)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE loans
        SET due_date = %s, renewed_count = renewed_count + 1
        WHERE loan_id = %s
    """, (new_due_date, loan_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({
        'message': 'Loan renewed successfully',
        'new_due_date': str(new_due_date)
    })

# GET all overdue loans
@loans_bp.route('/overdue', methods=['GET'])
def get_overdue_loans():
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            l.loan_id,
            m.full_name         AS member_name,
            m.email             AS member_email,
            b.title             AS book_title,
            l.due_date,
            DATEDIFF(CURRENT_DATE, l.due_date) AS days_overdue,
            DATEDIFF(CURRENT_DATE, l.due_date) * 0.50 AS fine_so_far
        FROM loans l
        JOIN members m ON l.member_id = m.member_id
        JOIN books   b ON l.book_id   = b.book_id
        WHERE l.return_date IS NULL
        AND l.due_date < CURRENT_DATE
        ORDER BY days_overdue DESC
    """)
    loans = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(loans)