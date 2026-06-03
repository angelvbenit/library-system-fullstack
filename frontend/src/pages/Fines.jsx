import React, { useEffect, useState } from 'react';
import { finesAPI } from '../api/axios';

const Fines = () => {
  const [fines, setFines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');
  const [message, setMessage] = useState(null);
  const [revenue, setRevenue] = useState([]);

  const fetchAll = async () => {
    try {
      const [finesRes, revenueRes] = await Promise.all([
        finesAPI.getAll(),
        finesAPI.getRevenue(),
      ]);
      setFines(finesRes.data);
      setRevenue(revenueRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAll(); }, []);

  const handlePay = async (fine_id) => {
    try {
      await finesAPI.pay(fine_id);
      setMessage({ type: 'success', text: 'Fine marked as paid.' });
      fetchAll();
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.error || 'Failed to process payment.' });
    }
  };

  const filtered = fines.filter(f => {
    const matchSearch =
      (f.member_name || '').toLowerCase().includes(search.toLowerCase()) ||
      (f.book_title || '').toLowerCase().includes(search.toLowerCase());
      
    // Fix: robustly parse the TINYINT from database
    const isPaid = Number(f.paid) === 1 || f.paid === true;
    
    const matchFilter =
      filter === 'all' ? true :
      filter === 'paid' ? isPaid :
      !isPaid;
      
    return matchSearch && matchFilter;
  });

  const totalCollected   = fines.filter(f => Number(f.paid) === 1 || f.paid === true).reduce((sum, f) => sum + parseFloat(f.amount), 0);
  const totalOutstanding = fines.filter(f => Number(f.paid) === 0 && f.paid !== true).reduce((sum, f) => sum + parseFloat(f.amount), 0);

  if (loading) return <div style={{ color: 'var(--light)', padding: '32px' }}>Loading...</div>;

  return (
    <div>
      <div className="page-header">
        <h1>Fines</h1>
        <p>Track and collect overdue fines</p>
      </div>

      <div className="stats-grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)', marginBottom: '24px' }}>
        <div className="stat-card">
          <div className="stat-number">{fines.length}</div>
          <div className="stat-label">Total Fines</div>
        </div>
        <div className="stat-card">
          <div className="stat-number" style={{ color: '#8fbf8f' }}>${totalCollected.toFixed(2)}</div>
          <div className="stat-label">Collected</div>
        </div>
        <div className="stat-card">
          <div className="stat-number" style={{ color: '#d48888' }}>${totalOutstanding.toFixed(2)}</div>
          <div className="stat-label">Outstanding</div>
        </div>
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
          placeholder="Search by member or book..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <select
          value={filter}
          onChange={e => setFilter(e.target.value)}
          style={{
            padding: '10px 14px',
            background: 'var(--dark)',
            border: '1px solid var(--medium)',
            borderRadius: '8px',
            color: 'var(--cream)',
            fontSize: '0.9rem',
            fontFamily: 'Inter, sans-serif',
          }}
        >
          <option value="all">All Fines</option>
          <option value="unpaid">Unpaid Only</option>
          <option value="paid">Paid Only</option>
        </select>
      </div>

      <div className="table-wrapper" style={{ marginBottom: '32px' }}>
        <table>
          <thead>
            <tr>
              <th>Member</th>
              <th>Book</th>
              <th>Amount</th>
              <th>Issued Date</th>
              <th>Status</th>
              <th>Paid Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(fine => {
              const isPaid = Number(fine.paid) === 1 || fine.paid === true;
              return (
                <tr key={fine.fine_id}>
                  <td>{fine.member_name}</td>
                  <td>{fine.book_title}</td>
                  <td style={{ color: '#e0b06a' }}>${parseFloat(fine.amount).toFixed(2)}</td>
                  <td>{fine.issued_date}</td>
                  <td>
                    <span className={`badge ${isPaid ? 'badge-success' : 'badge-danger'}`}>
                      {isPaid ? 'Paid' : 'Unpaid'}
                    </span>
                  </td>
                  <td>{fine.paid_date || '—'}</td>
                  <td>
                    {!isPaid ? (
                      <button
                        className="btn btn-success btn-sm"
                        onClick={() => handlePay(fine.fine_id)}
                      >Mark Paid</button>
                    ) : (
                      <span style={{ color: 'var(--medium)', fontSize: '0.8rem' }}>Settled</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="card">
        <div className="page-header" style={{ marginBottom: '16px' }}>
          <h1 style={{ fontSize: '1.4rem' }}>Revenue by Month</h1>
          <p>Fine collection breakdown</p>
        </div>
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Month</th>
                <th>Fines Issued</th>
                <th>Total Fined</th>
                <th>Collected</th>
                <th>Outstanding</th>
              </tr>
            </thead>
            <tbody>
              {revenue.map((row, i) => (
                <tr key={i}>
                  <td>{row.month?.slice(0, 7)}</td>
                  <td>{row.fines_issued}</td>
                  <td style={{ color: '#e0b06a' }}>${parseFloat(row.total_fined).toFixed(2)}</td>
                  <td style={{ color: '#8fbf8f' }}>${parseFloat(row.collected).toFixed(2)}</td>
                  <td style={{ color: '#d48888' }}>${parseFloat(row.outstanding).toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Fines;