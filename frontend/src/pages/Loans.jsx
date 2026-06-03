import React, { useEffect, useState } from 'react';
import { loansAPI, booksAPI, membersAPI } from '../api/axios';

const Loans = () => {
  const [loans, setLoans] = useState([]);
  const [books, setBooks] = useState([]);
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ book_id: '', member_id: '' });
  const [message, setMessage] = useState(null);

  const fetchAll = async () => {
    try {
      const [loansRes, booksRes, membersRes] = await Promise.all([
        loansAPI.getAll(),
        booksAPI.getAll(),
        membersAPI.getAll(),
      ]);
      setLoans(loansRes.data);
      setBooks(booksRes.data);
      setMembers(membersRes.data.filter(m => m.status === 'active'));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAll(); }, []);

  const openIssueModal = () => {
    setForm({ book_id: '', member_id: '' });
    setShowModal(true);
  };

  const handleIssue = async () => {
    try {
      const res = await loansAPI.issue(form);
      setMessage({ type: 'success', text: res.data.message });
      setShowModal(false);
      fetchAll();
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.error || 'Failed to issue book.' });
    }
  };

  const handleReturn = async (loan_id) => {
    try {
      const res = await loansAPI.return(loan_id);
      const msg = res.data.fine_charged
        ? `Book returned. Fine charged: $${res.data.fine_charged}`
        : 'Book returned successfully.';
      
      setMessage({ type: 'success', text: msg });
      fetchAll();
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.error || 'Failed to return book.' });
    }
  };

  const handleRenew = async (loan_id) => {
    try {
      const res = await loansAPI.renew(loan_id);
      setMessage({ type: 'success', text: res.data.message });
      fetchAll();
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.error || 'Failed to renew loan.' });
    }
  };

  const getStatusBadge = (status) => {
    if (status === 'Active')   return 'badge-success';
    if (status === 'Overdue')  return 'badge-danger';
    return 'badge-neutral';
  };

  const filtered = loans.filter(l =>
    (l.member_name || '').toLowerCase().includes(search.toLowerCase()) ||
    (l.book_title || '').toLowerCase().includes(search.toLowerCase()) ||
    (l.loan_status || '').toLowerCase().includes(search.toLowerCase())
  );

  if (loading) return <div style={{ color: 'var(--light)', padding: '32px' }}>Loading...</div>;

  return (
    <div>
      <div className="page-header">
        <h1>Loans</h1>
        <p>Issue, return and renew books</p>
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
          placeholder="Search by member, book or status..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <button className="btn btn-primary" onClick={openIssueModal}>Issue Book</button>
      </div>

      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Member</th>
              <th>Book</th>
              <th>Loan Date</th>
              <th>Due Date</th>
              <th>Status</th>
              <th>Renewals</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(loan => (
              <tr key={loan.loan_id}>
                <td>{loan.member_name}</td>
                <td>{loan.book_title}</td>
                <td>{loan.loan_date}</td>
                <td>{loan.due_date}</td>
                <td>
                  <span className={`badge ${getStatusBadge(loan.loan_status)}`}>
                    {loan.loan_status}
                  </span>
                </td>
                <td>{loan.renewed_count}</td>
                <td style={{ display: 'flex', gap: '6px' }}>
                  {loan.loan_status !== 'Returned' && (
                    <>
                      <button
                        className="btn btn-success btn-sm"
                        onClick={() => handleReturn(loan.loan_id)}
                      >Return</button>
                      <button
                        className="btn btn-primary btn-sm"
                        onClick={() => handleRenew(loan.loan_id)}
                      >Renew</button>
                    </>
                  )}
                  {loan.loan_status === 'Returned' && (
                    <span style={{ color: 'var(--medium)', fontSize: '0.8rem' }}>Completed</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h2>Issue a Book</h2>
            
            <div className="form-group">
              <label>SELECT BOOK</label>
              <select
                value={form.book_id}
                onChange={e => setForm({ ...form, book_id: e.target.value })}
              >
                <option value="">— Choose a book —</option>
                {books.map(b => {
                  const isTaken = b.available_copies < 1;
                  return (
                    <option 
                      key={b.book_id} 
                      value={b.book_id} 
                      disabled={isTaken}
                      style={{ color: isTaken ? '#856d55' : 'inherit' }}
                    >
                      {b.title} ({isTaken ? 'Not available - Taken' : `${b.available_copies} available`})
                    </option>
                  );
                })}
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

            <div style={{ backgroundColor: 'var(--dark)', padding: '12px', borderRadius: '6px', marginTop: '12px', border: '1px solid var(--medium)' }}>
              <p style={{ color: 'var(--cream)', fontSize: '0.85rem', margin: '0 0 6px 0', fontWeight: 'bold' }}>
                Borrowing Periods:
              </p>
              <ul style={{ color: 'var(--light)', fontSize: '0.8rem', margin: 0, paddingLeft: '20px' }}>
                <li>Standard: 14 days</li>
                <li>Student: 21 days</li>
                <li>Premium: 30 days</li>
              </ul>
            </div>

            <div className="modal-actions" style={{ marginTop: '20px' }}>
              <button className="btn btn-danger" onClick={() => setShowModal(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={handleIssue}>Issue Book</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Loans;