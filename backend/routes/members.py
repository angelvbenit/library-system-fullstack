from flask import Blueprint, jsonify, request
from config import get_connection

members_bp = Blueprint('members', __name__)

# GET all members
@members_bp.route('/', methods=['GET'])
def get_members():
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT member_id, full_name, email, phone,
               join_date, expiry_date, membership_type, status
        FROM members
        ORDER BY full_name ASC
    """)
    members = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(members)

# GET single member
@members_bp.route('/<int:member_id>', methods=['GET'])
def get_member(member_id):
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT member_id, full_name, email, phone,
               join_date, expiry_date, membership_type, status
        FROM members
        WHERE member_id = %s
    """, (member_id,))
    member = cursor.fetchone()
    cursor.close()
    conn.close()
    if not member:
        return jsonify({'error': 'Member not found'}), 404
    return jsonify(member)

# POST add new member
@members_bp.route('/', methods=['POST'])
def add_member():
    data = request.get_json()
    required = ['full_name', 'email', 'expiry_date']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing required fields'}), 400
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO members (full_name, email, phone, expiry_date, membership_type, status)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        data['full_name'],
        data['email'],
        data.get('phone', None),
        data['expiry_date'],
        data.get('membership_type', 'standard'),
        data.get('status', 'active')
    ))
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({'message': 'Member added successfully', 'member_id': new_id}), 201

# PUT update member
@members_bp.route('/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    data = request.get_json()
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE members
        SET full_name = %s, email = %s, phone = %s,
            expiry_date = %s, membership_type = %s, status = %s
        WHERE member_id = %s
    """, (
        data['full_name'], data['email'], data.get('phone', None),
        data['expiry_date'], data['membership_type'],
        data['status'], member_id
    ))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Member updated successfully'})

# DELETE member
@members_bp.route('/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor()
    cursor.execute("DELETE FROM members WHERE member_id = %s", (member_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Member deleted successfully'})

# GET member borrowing history
@members_bp.route('/<int:member_id>/history', methods=['GET'])
def get_member_history(member_id):
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
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
        WHERE l.member_id = %s
        ORDER BY l.loan_date DESC
    """, (member_id,))
    history = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(history)

# GET members with unpaid fines
@members_bp.route('/unpaid-fines', methods=['GET'])
def get_members_unpaid_fines():
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
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
        ORDER BY total_owed DESC
    """)
    members = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(members)