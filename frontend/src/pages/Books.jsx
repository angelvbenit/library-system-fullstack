import React, { useEffect, useState } from 'react';
import { booksAPI } from '../api/axios';

const Books = () => {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editBook, setEditBook] = useState(null);
  const [message, setMessage] = useState(null);
  
  const [form, setForm] = useState({
    isbn: '', title: '', author: '',
    genre: '', year_published: '', total_copies: 1
  });

  const fetchBooks = async () => {
    try {
      const res = await booksAPI.getAll();
      setBooks(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchBooks(); }, []);

  const openAdd = () => {
    setEditBook(null);
    setForm({ isbn: '', title: '', author: '', genre: '', year_published: '', total_copies: 1 });
    setShowModal(true);
  };

  const openEdit = (book) => {
    setEditBook(book);
    setForm({
      isbn:           book.isbn || '',
      title:          book.title || '',
      author:         book.author || '',
      genre:          book.genre || '',
      year_published: book.year_published || '',
      total_copies:   book.total_copies || '',
    });
    setShowModal(true);
  };

  const handleSubmit = async () => {
    try {
      const payload = {
        ...form,
        year_published: form.year_published ? parseInt(form.year_published, 10) : null,
        total_copies:   form.total_copies ? parseInt(form.total_copies, 10) : 1,
      };

      if (editBook) {
        await booksAPI.update(editBook.book_id, payload);
        setMessage({ type: 'success', text: 'Changes saved successfully.' });
      } else {
        await booksAPI.create(payload);
        setMessage({ type: 'success', text: 'Book added successfully.' });
      }
      setShowModal(false);
      fetchBooks();
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.error || 'Something went wrong.' });
    }
  };

  const handleDelete = async (book) => {
    if (!window.confirm(`Delete "${book.title}"? This will also wipe its loan history.`)) return;
    try {
      await booksAPI.delete(book.book_id);
      setMessage({ type: 'success', text: `Book deleted successfully.` });
      fetchBooks();
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.error || 'Failed to delete.' });
    }
  };

  const filtered = books.filter(b =>
    (b.title || '').toLowerCase().includes(search.toLowerCase()) ||
    (b.author || '').toLowerCase().includes(search.toLowerCase()) ||
    (b.genre || '').toLowerCase().includes(search.toLowerCase())
  );

  if (loading) return <div style={{ color: 'var(--light)', padding: '32px' }}>Loading...</div>;

  return (
    <div>
      <div className="page-header">
        <h1>Books</h1>
        <p>Manage the library catalogue</p>
      </div>
      
      {message && (
        <div className="card" style={{
          borderColor: message.type === 'success' ? '#6b8f6b' : '#9b4444',
          marginBottom: '20px',
          padding: '14px 20px',
          color: message.type === 'success' ? '#8fbf8f' : '#d48888'
        }}>
          {message.text}
          <button
            onClick={() => setMessage(null)}
            style={{ float: 'right', background: 'none', border: 'none', color: 'inherit', cursor: 'pointer' }}
          >Close</button>
        </div>
      )}
      
      <div style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
        <input
          className="search-bar"
          style={{ margin: 0, flex: 1 }}
          placeholder="Search by title, author or genre..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <button className="btn btn-primary" onClick={openAdd}>Add Book</button>
      </div>

      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Title</th>
              <th>Author</th>
              <th>Genre</th>
              <th>Year</th>
              <th>Available</th>
              <th>Total</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(book => (
              <tr key={book.book_id}>
                <td>{book.title}</td>
                <td>{book.author}</td>
                <td><span className="badge badge-neutral">{book.genre}</span></td>
                <td>{book.year_published}</td>
                <td>
                  <span className={`badge ${book.available_copies > 0 ? 'badge-success' : 'badge-danger'}`}>
                    {book.available_copies}
                  </span>
                </td>
                <td>{book.total_copies}</td>
                <td style={{ display: 'flex', gap: '8px' }}>
                  <button className="btn btn-primary btn-sm" onClick={() => openEdit(book)}>Edit</button>
                  <button className="btn btn-danger btn-sm" onClick={() => handleDelete(book)}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h2>{editBook ? `Edit "${editBook.title}"` : 'Add New Book'}</h2>
            {['isbn', 'title', 'author', 'genre', 'year_published', 'total_copies'].map(field => (
              <div className="form-group" key={field}>
                <label>{field.replace(/_/g, ' ').toUpperCase()}</label>
                <input
                  type={['year_published', 'total_copies'].includes(field) ? 'number' : 'text'}
                  value={form[field]}
                  onChange={e => setForm({ ...form, [field]: e.target.value })}
                />
              </div>
            ))}
            <div className="modal-actions">
              <button className="btn btn-danger" onClick={() => setShowModal(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={handleSubmit}>
                {editBook ? 'Save Changes' : 'Add Book'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Books;