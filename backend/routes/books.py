from flask import Blueprint, jsonify, request
from config import get_connection

books_bp = Blueprint('books', __name__)

@books_bp.route('/available', methods=['GET'])
def get_available_books():
    conn = get_connection()
    if not conn: return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT book_id, title, author, genre, available_copies, total_copies FROM books WHERE available_copies > 0 ORDER BY title ASC")
    books = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(books)

@books_bp.route('/', methods=['GET'])
def get_books():
    conn = get_connection()
    if not conn: return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT book_id, title, author, isbn, genre, year_published, total_copies, available_copies FROM books ORDER BY title ASC")
    books = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(books)

@books_bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
    book = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(book) if book else (jsonify({'error': 'Not found'}), 404)

@books_bp.route('/', methods=['POST'])
def add_book():
    try:
        data = request.get_json()
        conn = get_connection()
        cursor = conn.cursor()
        
        year = data.get('year_published')
        year = int(year) if year and str(year).strip() != "" else None
        total = int(data.get('total_copies', 1))
        
        cursor.execute("""
            INSERT INTO books (isbn, title, author, genre, year_published, total_copies, available_copies)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (data.get('isbn'), data.get('title'), data.get('author'), data.get('genre'), year, total, total))
        conn.commit()
        new_id = cursor.lastrowid
        return jsonify({'message': 'Book added successfully', 'book_id': new_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        cursor.close()
        conn.close()

@books_bp.route('/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        data = request.get_json()
        cursor.execute("SELECT total_copies, available_copies FROM books WHERE book_id = %s", (book_id,))
        current = cursor.fetchone()
        if not current:
            return jsonify({'error': 'Book not found'}), 404
            
        new_total = int(data.get('total_copies', current['total_copies']))
        year = data.get('year_published')
        year = int(year) if year and str(year).strip() != "" else None
        
        diff = new_total - current['total_copies']
        new_available = current['available_copies'] + diff
        
        if new_available < 0:
            return jsonify({'error': 'Cannot reduce total copies below currently issued copies.'}), 400

        cursor.execute("""
            UPDATE books SET title=%s, author=%s, genre=%s, year_published=%s, total_copies=%s, available_copies=%s WHERE book_id=%s
        """, (data.get('title'), data.get('author'), data.get('genre'), year, new_total, new_available, book_id))
        conn.commit()
        return jsonify({'message': 'Book updated successfully'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@books_bp.route('/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Override strict constraints to allow the requested cascading deletion
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("DELETE FROM fines WHERE loan_id IN (SELECT loan_id FROM loans WHERE book_id = %s)", (book_id,))
        cursor.execute("DELETE FROM reservations WHERE book_id = %s", (book_id,))
        cursor.execute("DELETE FROM loans WHERE book_id = %s", (book_id,))
        cursor.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()
        return jsonify({'message': 'Book deleted successfully.'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()