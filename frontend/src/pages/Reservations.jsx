import React, { useEffect, useState } from 'react';
import { reservationsAPI, booksAPI, membersAPI } from '../api/axios';

const Reservations = () => {
  const [reservations, setReservations] = useState([]);
  const [books, setBooks] = useState([]);
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ book_id: '', member_id: '' });
  const [message, setMessage] = useState(null);

  const fetchAll = async () => {
    try {
      const [resRes, booksRes, membersRes] = await Promise.all([
        reservationsAPI.getAll(),
        booksAPI.getAll(),
        membersAPI.getAll(),
      ]);
      setReservations(resRes.data);
      setBooks(booksRes.data);
      setMembers(membersRes.data.filter(m => m.status === 'active'));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAll(); }, []);

  const handleCreate = async () => {
    try {
      const res = await reservationsAPI.create(form);
      setMessage({
        type: 'success',
        text: `Reservation created. Queue position: ${res.data.queue_position}`
      });
      setShowModal(false);
      fetchAll();
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.error || 'Failed to create reservation.' });
    }
  };

  const handleNotify = async (id) => {
    try {
      await reservationsAPI.notify(id);
      setMessage({ type: 'success', text: 'Member notified successfully.' });
      fetchAll();
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.error || 'Failed to notify member.' });
    }
  };

  const handleCancel = async (id) => {
    if (!window.confirm('Cancel this reservation?')) return;
    try {
      await reservationsAPI.cancel(id);
      setMessage({ type: 'success', text: 'Reservation cancelled.' });
      fetchAll();
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to cancel reservation.' });
    }
  };

  const filtered = reservations.filter(r =>
    r.member_name.toLowerCase().includes(search.toLowerCase()) ||
    r.book_title.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) return <div style={{ color: 'var(--light)', padding: '32px' }}>Loading...</div>;

  return (
    <div>
      <div className="page-header">
        <h1> Reservations</h1>
        <p>Manage the book waitlist queue</p>
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
          >✕</button>
        </div>
      )}

      <div style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
        <input
          className="search-bar"
          style={{ margin: 0, flex: 1 }}
          placeholder="Search by member or book..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>+ New Reservation</button>
      </div>

      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Book</th>
              <th>Member</th>
              <th>Reserved Date</th>
              <th>Queue Position</th>
              <th>Notified</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(r => (
              <tr key={r.reservation_id}>
                <td>{r.book_title}</td>
                <td>{r.member_name}</td>
                <td>{r.reserved_date}</td>
                <td>
                  <span className="badge badge-neutral">#{r.queue_position}</span>
                </td>
                <td>
                  <span className={`badge ${r.notified ? 'badge-success' : 'badge-warning'}`}>
                    {r.notified ? 'Notified' : 'Pending'}
                  </span>
                </td>
                <td style={{ display: 'flex', gap: '6px' }}>
                  {!r.notified && (
                    <button
                      className="btn btn-primary btn-sm"
                      onClick={() => handleNotify(r.reservation_id)}
                    >Notify</button>
                  )}
                  <button
                    className="btn btn-danger btn-sm"
                    onClick={() => handleCancel(r.reservation_id)}
                  >Cancel</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h2>New Reservation</h2>
            <div className="form-group">
              <label>SELECT BOOK</label>
              <select
                value={form.book_id}
                onChange={e => setForm({ ...form, book_id: e.target.value })}
              >
                <option value="">— Choose a book —</option>
                {books.map(b => (
                  <option key={b.book_id} value={b.book_id}>
                    {b.title} ({b.available_copies} available)
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>SELECT MEMBER</label>
              <select
                value={form.member_id}
                onChange={e => setForm({ ...form, member_id: e.target.value })}
              >
                <option value="">— Choose a member —</option>
                {members.map(m => (
                  <option key={m.member_id} value={m.member_id}>
                    {m.full_name} ({m.membership_type})
                  </option>
                ))}
              </select>
            </div>
            <div className="modal-actions">
              <button className="btn btn-danger" onClick={() => setShowModal(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={handleCreate}>Create Reservation</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Reservations;