import React, { useEffect, useState } from 'react';
import { booksAPI } from '../api/axios';
import { membersAPI } from '../api/axios';
import { loansAPI } from '../api/axios';
import { finesAPI } from '../api/axios';
import libraryBg from '../styles/library-bg.jpg';

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalBooks: 0,
    totalMembers: 0,
    activeLoans: 0,
    unpaidFines: 0,
  });
  const [overdueLoans, setOverdueLoans] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [books, members, loans, fines, overdue] = await Promise.all([
          booksAPI.getAll(),
          membersAPI.getAll(),
          loansAPI.getAll(),
          finesAPI.getUnpaid(),
          loansAPI.getOverdue(),
        ]);

        setStats({
          totalBooks:   books.data.length,
          totalMembers: members.data.length,
          activeLoans:  loans.data.filter(l => l.loan_status === 'Active' || l.loan_status === 'Overdue').length,
          unpaidFines:  fines.data.length,
        });
        setOverdueLoans(overdue.data.slice(0, 5));
      } catch (err) {
        console.error('Dashboard load error:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <div style={{ color: 'var(--light)', padding: '32px' }}>Loading...</div>;

  return (
    <div>
      {/* Hero */}
      <div className="dashboard-hero">
        <img src={libraryBg} alt="Library" />
        <div className="dashboard-hero-text">
          <h1>Library Management</h1>
          <p>Welcome back! Here's what's happening today </p>
        </div>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-number">{stats.totalBooks}</div>
          <div className="stat-label"> Total Books</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{stats.totalMembers}</div>
          <div className="stat-label"> Members</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{stats.activeLoans}</div>
          <div className="stat-label"> Active Loans</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{stats.unpaidFines}</div>
          <div className="stat-label"> Unpaid Fines</div>
        </div>
      </div>

      {/* Overdue Loans Table */}
      <div className="card">
        <div className="page-header">
          <h1 style={{ fontSize: '1.4rem' }}> Overdue Loans</h1>
          <p>Books that are past their due date</p>
        </div>
        {overdueLoans.length === 0 ? (
          <p style={{ color: 'var(--light)' }}>No overdue loans right now.</p>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Member</th>
                  <th>Book</th>
                  <th>Due Date</th>
                  <th>Days Overdue</th>
                  <th>Fine So Far</th>
                </tr>
              </thead>
              <tbody>
                {overdueLoans.map(loan => (
                  <tr key={loan.loan_id}>
                    <td>{loan.member_name}</td>
                    <td>{loan.book_title}</td>
                    <td>{loan.due_date}</td>
                    <td>
                      <span className="badge badge-danger">
                        {loan.days_overdue} days
                      </span>
                    </td>
                    <td style={{ color: '#e0b06a' }}>
                      ${loan.fine_so_far}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;