from flask import Blueprint, jsonify, request
from config import get_connection
from datetime import date

fines_bp = Blueprint('fines', __name__)

# GET all fines
@fines_bp.route('/', methods=['GET'])
def get_fines():
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            f.fine_id,
            m.full_name     AS member_name,
            b.title         AS book_title,
            f.amount,
            f.issued_date,
            f.paid,
            f.paid_date
        FROM fines f
        JOIN members m ON f.member_id = m.member_id
        JOIN loans   l ON f.loan_id   = l.loan_id
        JOIN books   b ON l.book_id   = b.book_id
        ORDER BY f.issued_date DESC
    """)
    fines = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(fines)

# GET single fine
@fines_bp.route('/<int:fine_id>', methods=['GET'])
def get_fine(fine_id):
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            f.fine_id,
            m.full_name     AS member_name,
            b.title         AS book_title,
            f.amount,
            f.issued_date,
            f.paid,
            f.paid_date
        FROM fines f
        JOIN members m ON f.member_id = m.member_id
        JOIN loans   l ON f.loan_id   = l.loan_id
        JOIN books   b ON l.book_id   = b.book_id
        WHERE f.fine_id = %s
    """, (fine_id,))
    fine = cursor.fetchone()
    cursor.close()
    conn.close()
    if not fine:
        return jsonify({'error': 'Fine not found'}), 404
    return jsonify(fine)

# PUT pay a fine
@fines_bp.route('/<int:fine_id>/pay', methods=['PUT'])
def pay_fine(fine_id):
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT fine_id, paid FROM fines WHERE fine_id = %s", (fine_id,))
    fine = cursor.fetchone()
    if not fine:
        return jsonify({'error': 'Fine not found'}), 404
    if fine['paid']:
        return jsonify({'error': 'Fine already paid'}), 400

    paid_date = date.today()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE fines
        SET paid = 1, paid_date = %s
        WHERE fine_id = %s
    """, (paid_date, fine_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({
        'message': 'Fine paid successfully',
        'paid_date': str(paid_date)
    })

# GET all unpaid fines
@fines_bp.route('/unpaid', methods=['GET'])
def get_unpaid_fines():
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            f.fine_id,
            m.full_name     AS member_name,
            m.email         AS member_email,
            b.title         AS book_title,
            f.amount,
            f.issued_date
        FROM fines f
        JOIN members m ON f.member_id = m.member_id
        JOIN loans   l ON f.loan_id   = l.loan_id
        JOIN books   b ON l.book_id   = b.book_id
        WHERE f.paid = 0
        ORDER BY f.amount DESC
    """)
    fines = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(fines)

# GET fine revenue summary by month
@fines_bp.route('/revenue', methods=['GET'])
def get_fine_revenue():
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            DATE_FORMAT(issued_date, '%Y-%m-01')            AS month,
            COUNT(fine_id)                                  AS fines_issued,
            SUM(amount)                                     AS total_fined,
            SUM(CASE WHEN paid = 1 THEN amount ELSE 0 END)  AS collected,
            SUM(CASE WHEN paid = 0 THEN amount ELSE 0 END)  AS outstanding
        FROM fines
        GROUP BY DATE_FORMAT(issued_date, '%Y-%m-01')
        ORDER BY month DESC
    """)
    revenue = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(revenue)