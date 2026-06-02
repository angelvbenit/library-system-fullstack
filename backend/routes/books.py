from flask import Blueprint, jsonify, request
from config import get_connection

books_bp = Blueprint('books', __name__)

# GET all books
@books_bp.route('/', methods=['GET'])
def get_books():
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT book_id, title, author, isbn, genre, 
               year_published, total_copies, available_copies
        FROM books
        ORDER BY title ASC
    """)
    books = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(books)

# GET single book
@books_bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT book_id, title, author, isbn, genre,
               year_published, total_copies, available_copies
        FROM books
        WHERE book_id = %s
    """, (book_id,))
    book = cursor.fetchone()
    cursor.close()
    conn.close()
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    return jsonify(book)

# POST add new book
@books_bp.route('/', methods=['POST'])
def add_book():
    data = request.get_json()
    required = ['isbn', 'title', 'author', 'genre', 'year_published', 'total_copies']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing required fields'}), 400
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO books (isbn, title, author, genre, year_published, total_copies, available_copies)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        data['isbn'], data['title'], data['author'],
        data['genre'], data['year_published'],
        data['total_copies'], data['total_copies']
    ))
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({'message': 'Book added successfully', 'book_id': new_id}), 201

# PUT update book
@books_bp.route('/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.get_json()
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE books
        SET title = %s, author = %s, genre = %s,
            year_published = %s, total_copies = %s
        WHERE book_id = %s
    """, (
        data['title'], data['author'], data['genre'],
        data['year_published'], data['total_copies'], book_id
    ))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Book updated successfully'})

# DELETE book
@books_bp.route('/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Book deleted successfully'})

# GET available books only
@books_bp.route('/available', methods=['GET'])
def get_available_books():
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT book_id, title, author, genre,
               available_copies, total_copies
        FROM books
        WHERE available_copies > 0
        ORDER BY title ASC
    """)
    books = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(books)