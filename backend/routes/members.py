from flask import Blueprint, jsonify, request
from config import get_connection
from datetime import date, timedelta

members_bp = Blueprint('members', __name__)

@members_bp.route('/', methods=['GET'])
def get_members():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM members ORDER BY full_name ASC")
    members = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(members)

@members_bp.route('/', methods=['POST'])
def add_member():
    try:
        data = request.get_json()
        conn = get_connection()
        cursor = conn.cursor()
        
        expiry = data.get('expiry_date')
        if not expiry or str(expiry).strip() == "": 
            # Auto-calculate exactly 1 year from today if left blank
            expiry = (date.today() + timedelta(days=365)).strftime('%Y-%m-%d')
        
        cursor.execute("""
            INSERT INTO members (full_name, email, phone, expiry_date, membership_type, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (data.get('full_name'), data.get('email'), data.get('phone'), expiry, data.get('membership_type', 'standard'), data.get('status', 'active')))
        conn.commit()
        new_id = cursor.lastrowid
        return jsonify({'message': 'Member added successfully', 'member_id': new_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        cursor.close()
        conn.close()

@members_bp.route('/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        data = request.get_json()
        
        expiry = data.get('expiry_date')
        if not expiry or str(expiry).strip() == "": 
            # Auto-calculate exactly 1 year from today if left blank on edit
            expiry = (date.today() + timedelta(days=365)).strftime('%Y-%m-%d')

        cursor.execute("""
            UPDATE members SET full_name=%s, email=%s, phone=%s, expiry_date=%s, membership_type=%s, status=%s WHERE member_id=%s
        """, (data.get('full_name'), data.get('email'), data.get('phone'), expiry, data.get('membership_type'), data.get('status'), member_id))
        conn.commit()
        return jsonify({'message': 'Member updated successfully'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@members_bp.route('/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM fines WHERE member_id = %s", (member_id,))
        cursor.execute("DELETE FROM reservations WHERE member_id = %s", (member_id,))
        cursor.execute("DELETE FROM loans WHERE member_id = %s", (member_id,))
        cursor.execute("DELETE FROM members WHERE member_id = %s", (member_id,))
        conn.commit()
        return jsonify({'message': 'Member deleted successfully.'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@members_bp.route('/<int:member_id>/history', methods=['GET'])
def get_member_history(member_id):
    conn = get_connection()
    if not conn: return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT l.loan_id, b.title, b.genre, l.loan_date, l.due_date, l.return_date,
        CASE
            WHEN l.return_date IS NULL AND l.due_date < CURRENT_DATE THEN 'Overdue'
            WHEN l.return_date IS NULL THEN 'Active'
            ELSE 'Returned'
        END AS loan_status,
        COALESCE(f.amount, 0) AS fine_amount
        FROM loans l
        JOIN books b ON l.book_id = b.book_id
        LEFT JOIN fines f ON l.loan_id = f.loan_id
        WHERE l.member_id = %s
        ORDER BY l.loan_date DESC
    """, (member_id,))
    history = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(history)

@members_bp.route('/unpaid-fines', methods=['GET'])
def get_members_unpaid_fines():
    conn = get_connection()
    if not conn: return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT m.member_id, m.full_name, m.email, COUNT(f.fine_id) AS open_fines, SUM(f.amount) AS total_owed
        FROM members m
        JOIN fines f ON m.member_id = f.member_id
        WHERE f.paid = 0
        GROUP BY m.member_id, m.full_name, m.email
        HAVING SUM(f.amount) > 0
        ORDER BY total_owed DESC
    """)
    members = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(members)