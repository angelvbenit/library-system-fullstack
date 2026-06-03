import React from 'react';
import { NavLink } from 'react-router-dom';
import { systemAPI } from '../api/axios';

function Sidebar() {
  const handleAction = async (actionType) => {
    try {
      if (actionType === 'undo') {
        await systemAPI.undo();
        alert("Last action reversed successfully.");
        window.location.reload();
      } else if (actionType === 'save') {
        await systemAPI.saveState();
        alert("Checkpoint saved. You can restore to this state anytime.");
      } else if (actionType === 'restore') {
        if (!window.confirm("Restore to last saved checkpoint? All recent changes will be lost.")) return;
        await systemAPI.restoreState();
        window.location.reload();
      } else if (actionType === 'reset') {
        if (!window.confirm("WARNING: Wipe entirely and restore the Original Default Database?")) return;
        await systemAPI.factoryReset();
        alert("Database reset to original seed data.");
        window.location.reload();
      }
    } catch (err) {
      alert(err.response?.data?.error || "Action failed.");
    }
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
         Library
        <span>Management System</span>
      </div>
      
      <ul className="sidebar-nav">
        <li>
          <NavLink to="/" end>Dashboard</NavLink>
        </li>
        <li>
          <NavLink to="/books">Books</NavLink>
        </li>
        <li>
          <NavLink to="/members">Members</NavLink>
        </li>
        <li>
          <NavLink to="/loans">Loans</NavLink>
        </li>
        <li>
          <NavLink to="/fines">Fines</NavLink>
        </li>
        <li>
          <NavLink to="/reservations">Reservations</NavLink>
        </li>
      </ul>
      
      <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
         <button className="btn btn-primary btn-sm" onClick={() => handleAction('undo')}>
            Undo Last Action
         </button>
         <button className="btn btn-success btn-sm" onClick={() => handleAction('save')}>
            Save Session State
         </button>
         <button className="btn btn-success btn-sm" onClick={() => handleAction('restore')} style={{ opacity: 0.8 }}>
            Restore Saved State
         </button>
         <button className="btn btn-danger btn-sm" onClick={() => handleAction('reset')}>
            Reset to Default
         </button>
      </div>

      <div style={{ padding: '24px', borderTop: '1px solid #856d55', fontSize: '0.75rem', color: '#856d55' }}>
        Library System v1.1
      </div>
    </aside>
  );
}

export default Sidebar;