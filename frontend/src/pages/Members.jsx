import React, { useEffect, useState } from 'react';
import { membersAPI } from '../api/axios';

const Members = () => {
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editMember, setEditMember] = useState(null);
  const [message, setMessage] = useState(null);
  
  const [form, setForm] = useState({
    full_name: '', email: '', phone: '',
    expiry_date: '', membership_type: 'standard', status: 'active'
  });

  const fetchMembers = async () => {
    try {
      const res = await membersAPI.getAll();
      setMembers(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchMembers(); }, []);

  const openAdd = () => {
    setEditMember(null);
    
    // Auto-calculate exactly 1 year from today for user convenience
    const nextYear = new Date();
    nextYear.setFullYear(nextYear.getFullYear() + 1);
    const defaultExpiry = nextYear.toISOString().split('T')[0];

    setForm({ 
      full_name: '', 
      email: '', 
      phone: '', 
      expiry_date: defaultExpiry, 
      membership_type: 'standard', 
      status: 'active' // Hardcoded to active for new members
    });
    setShowModal(true);
  };

  const openEdit = (member) => {
    setEditMember(member);
    
    let parsedDate = '';
    if (member.expiry_date) {
      parsedDate = new Date(member.expiry_date).toISOString().split('T')[0];
    }
    
    setForm({
      full_name:       member.full_name || '',
      email:           member.email || '',
      phone:           member.phone || '',
      expiry_date:     parsedDate,
      membership_type: member.membership_type || 'standard',
      status:          member.status || 'active',
    });
    setShowModal(true);
  };

  const handleSubmit = async () => {
    try {
      if (editMember) {
        await membersAPI.update(editMember.member_id, form);
        setMessage({ type: 'success', text: 'Member details saved successfully.' });
      } else {
        await membersAPI.create(form);
        setMessage({ type: 'success', text: 'Member added successfully.' });
      }
      setShowModal(false);
      fetchMembers();
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.error || 'Something went wrong.' });
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this member? This will completely wipe their library history.')) return;
    try {
      await membersAPI.delete(id);
      setMessage({ type: 'success', text: 'Member deleted successfully.' });
      fetchMembers();
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.error || 'Failed to delete.' });
    }
  };

  // New quick-action toggle for suspending/activating members
  const handleToggleStatus = async (member) => {
    const newStatus = member.status === 'active' ? 'suspended' : 'active';
    const actionText = newStatus === 'suspended' ? 'Suspend' : 'Activate';
    
    if (!window.confirm(`${actionText} ${member.full_name}?`)) return;
    
    try {
      // Re-use the update API, just flipping the status flag
      const updatedData = { ...member, status: newStatus };
      
      // Fix date format for the backend if it exists
      if (updatedData.expiry_date) {
        updatedData.expiry_date = new Date(updatedData.expiry_date).toISOString().split('T')[0];
      }

      await membersAPI.update(member.member_id, updatedData);
      setMessage({ type: 'success', text: `Member account has been ${newStatus}.` });
      fetchMembers();
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.error || 'Failed to update status.' });
    }
  };

  const getStatusBadge = (status) => {
    if (status === 'active')    return 'badge-success';
    if (status === 'suspended') return 'badge-warning';
    return 'badge-danger';
  };

  const filtered = members.filter(m =>
    (m.full_name || '').toLowerCase().includes(search.toLowerCase()) ||
    (m.email || '').toLowerCase().includes(search.toLowerCase()) ||
    (m.membership_type || '').toLowerCase().includes(search.toLowerCase())
  );

  if (loading) return <div style={{ color: 'var(--light)', padding: '32px' }}>Loading...</div>;

  return (
    <div>
      <div className="page-header">
        <h1>Members</h1>
        <p>Manage library memberships</p>
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
          placeholder="Search by name, email or membership type..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <button className="btn btn-primary" onClick={openAdd}>Add Member</button>
      </div>

      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Phone</th>
              <th>Type</th>
              <th>Expiry</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(member => (
              <tr key={member.member_id}>
                <td>{member.full_name}</td>
                <td>{member.email}</td>
                <td>{member.phone || 'None'}</td>
                <td>
                  <span className="badge badge-neutral">{member.membership_type}</span>
                </td>
                <td>{member.expiry_date || 'None'}</td>
                <td>
                  <span className={`badge ${getStatusBadge(member.status)}`}>
                    {member.status}
                  </span>
                </td>
                <td style={{ display: 'flex', gap: '8px' }}>
                  <button className="btn btn-primary btn-sm" onClick={() => openEdit(member)}>Edit</button>
                  <button 
                    className="btn btn-warning btn-sm" 
                    onClick={() => handleToggleStatus(member)}
                    style={{ backgroundColor: member.status === 'active' ? '#e0b06a' : '#6b8f6b', borderColor: 'transparent', color: '#121212' }}
                  >
                    {member.status === 'active' ? 'Suspend' : 'Activate'}
                  </button>
                  <button className="btn btn-danger btn-sm" onClick={() => handleDelete(member.member_id)}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h2>{editMember ? 'Edit Member' : 'Add New Member'}</h2>
            
            <div className="form-group">
              <label>FULL NAME</label>
              <input type="text" value={form.full_name} onChange={e => setForm({ ...form, full_name: e.target.value })} />
            </div>
            <div className="form-group">
              <label>EMAIL</label>
              <input type="text" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
            </div>
            <div className="form-group">
              <label>PHONE</label>
              <input type="text" value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })} />
            </div>
            <div className="form-group">
              <label>EXPIRY DATE</label>
              <input type="date" value={form.expiry_date} onChange={e => setForm({ ...form, expiry_date: e.target.value })} />
            </div>

            <div className="form-group">
              <label>MEMBERSHIP TYPE</label>
              <select value={form.membership_type} onChange={e => setForm({ ...form, membership_type: e.target.value })}>
                <option value="standard">Standard</option>
                <option value="premium">Premium</option>
                <option value="student">Student</option>
              </select>
            </div>
            
            {/* ONLY show the status dropdown if we are editing an existing member */}
            {editMember && (
              <div className="form-group">
                <label>STATUS</label>
                <select value={form.status} onChange={e => setForm({ ...form, status: e.target.value })}>
                  <option value="active">Active</option>
                  <option value="suspended">Suspended</option>
                  <option value="expired">Expired</option>
                </select>
              </div>
            )}
            
            <div className="modal-actions">
              <button className="btn btn-danger" onClick={() => setShowModal(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={handleSubmit}>
                {editMember ? 'Save Changes' : 'Add Member'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Members;