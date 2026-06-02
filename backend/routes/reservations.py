from flask import Blueprint, jsonify, request
from config import get_connection
from datetime import date

reservations_bp = Blueprint('reservations', __name__)

# GET all reservations
@reservations_bp.route('/', methods=['GET'])
def get_reservations():
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            r.reservation_id,
            b.title         AS book_title,
            m.full_name     AS member_name,
            m.email         AS member_email,
            r.reserved_date,
            r.queue_position,
            r.notified
        FROM reservations r
        JOIN books   b ON r.book_id   = b.book_id
        JOIN members m ON r.member_id = m.member_id
        ORDER BY r.book_id, r.queue_position
    """)
    reservations = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(reservations)

# GET single reservation
@reservations_bp.route('/<int:reservation_id>', methods=['GET'])
def get_reservation(reservation_id):
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            r.reservation_id,
            b.title         AS book_title,
            m.full_name     AS member_name,
            m.email         AS member_email,
            r.reserved_date,
            r.queue_position,
            r.notified
        FROM reservations r
        JOIN books   b ON r.book_id   = b.book_id
        JOIN members m ON r.member_id = m.member_id
        WHERE r.reservation_id = %s
    """, (reservation_id,))
    reservation = cursor.fetchone()
    cursor.close()
    conn.close()
    if not reservation:
        return jsonify({'error': 'Reservation not found'}), 404
    return jsonify(reservation)

# POST create reservation
@reservations_bp.route('/', methods=['POST'])
def create_reservation():
    data = request.get_json()
    required = ['book_id', 'member_id']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing required fields'}), 400
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor(dictionary=True)

    # Check book exists
    cursor.execute("SELECT book_id FROM books WHERE book_id = %s", (data['book_id'],))
    if not cursor.fetchone():
        return jsonify({'error': 'Book not found'}), 404

    # Check member is active
    cursor.execute("SELECT status FROM members WHERE member_id = %s", (data['member_id'],))
    member = cursor.fetchone()
    if not member:
        return jsonify({'error': 'Member not found'}), 404
    if member['status'] != 'active':
        return jsonify({'error': 'Member is not active'}), 400

    # Check member hasn't already reserved this book
    cursor.execute("""
        SELECT reservation_id FROM reservations
        WHERE book_id = %s AND member_id = %s
    """, (data['book_id'], data['member_id']))
    if cursor.fetchone():
        return jsonify({'error': 'Member already has a reservation for this book'}), 400

    # Get next queue position
    cursor.execute("""
        SELECT COALESCE(MAX(queue_position), 0) + 1 AS next_position
        FROM reservations
        WHERE book_id = %s
    """, (data['book_id'],))
    next_position = cursor.fetchone()['next_position']

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO reservations (book_id, member_id, reserved_date, queue_position)
        VALUES (%s, %s, %s, %s)
    """, (data['book_id'], data['member_id'], date.today(), next_position))
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({
        'message': 'Reservation created successfully',
        'reservation_id': new_id,
        'queue_position': next_position
    }), 201

# PUT mark reservation as notified
@reservations_bp.route('/<int:reservation_id>/notify', methods=['PUT'])
def notify_reservation(reservation_id):
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT reservation_id, notified FROM reservations
        WHERE reservation_id = %s
    """, (reservation_id,))
    reservation = cursor.fetchone()
    if not reservation:
        return jsonify({'error': 'Reservation not found'}), 404
    if reservation['notified']:
        return jsonify({'error': 'Already notified'}), 400

    cursor = conn.cursor()
    cursor.execute("""
        UPDATE reservations SET notified = 1
        WHERE reservation_id = %s
    """, (reservation_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Member notified successfully'})

# DELETE cancel reservation
@reservations_bp.route('/<int:reservation_id>', methods=['DELETE'])
def cancel_reservation(reservation_id):
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT reservation_id, book_id, queue_position
        FROM reservations WHERE reservation_id = %s
    """, (reservation_id,))
    reservation = cursor.fetchone()
    if not reservation:
        return jsonify({'error': 'Reservation not found'}), 404

    cursor = conn.cursor()
    # Delete the reservation
    cursor.execute("DELETE FROM reservations WHERE reservation_id = %s", (reservation_id,))

    # Shift queue positions down for remaining reservations
    cursor.execute("""
        UPDATE reservations
        SET queue_position = queue_position - 1
        WHERE book_id = %s
        AND queue_position > %s
    """, (reservation['book_id'], reservation['queue_position']))

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Reservation cancelled successfully'})