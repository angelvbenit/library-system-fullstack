import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Books from './pages/Books';
import Members from './pages/Members';
import Loans from './pages/Loans';
import Fines from './pages/Fines';
import Reservations from './pages/Reservations';
import './styles/theme.css';

function App() {
  return (
    <Router>
      <div className="app-layout">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/"             element={<Dashboard />} />
            <Route path="/books"        element={<Books />} />
            <Route path="/members"      element={<Members />} />
            <Route path="/loans"        element={<Loans />} />
            <Route path="/fines"        element={<Fines />} />
            <Route path="/reservations" element={<Reservations />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;