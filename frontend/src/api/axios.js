import axios from 'axios';

const API = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

API.interceptors.request.use(async (config) => {
  if (['post', 'put', 'delete'].includes(config.method) && !config.url.includes('/system/')) {
    try {
      await axios.post('http://127.0.0.1:5000/api/system/snapshot', {}, {
        headers: { 'Content-Type': 'application/json' }
      });
    } catch (e) {
      console.error("Failed to register snapshot for undo", e);
    }
  }
  return config;
});

export const systemAPI = {
  undo:         () => API.post('/system/undo'),
  saveState:    () => API.post('/system/save-state'),
  restoreState: () => API.post('/system/restore-state'),
  factoryReset: () => API.post('/system/reset-default'),
};

export const booksAPI = {
  getAll:       () => API.get('/books/'),
  getOne:       (id) => API.get(`/books/${id}`),
  getAvailable: () => API.get('/books/available'),
  create:       (data) => API.post('/books/', data),
  update:       (id, data) => API.put(`/books/${id}`, data),
  delete:       (id) => API.delete(`/books/${id}`),
};

export const membersAPI = {
  getAll:         () => API.get('/members/'),
  getOne:         (id) => API.get(`/members/${id}`),
  getHistory:     (id) => API.get(`/members/${id}/history`),
  getUnpaidFines: () => API.get('/members/unpaid-fines'),
  create:         (data) => API.post('/members/', data),
  update:         (id, data) => API.put(`/members/${id}`, data),
  delete:         (id) => API.delete(`/members/${id}`),
};

export const loansAPI = {
  getAll:     () => API.get('/loans/'),
  getOne:     (id) => API.get(`/loans/${id}`),
  getOverdue: () => API.get('/loans/overdue'),
  issue:      (data) => API.post('/loans/', data),
  return:     (id) => API.put(`/loans/${id}/return`),
  renew:      (id) => API.put(`/loans/${id}/renew`),
};

export const finesAPI = {
  getAll:     () => API.get('/fines/'),
  getOne:     (id) => API.get(`/fines/${id}`),
  getUnpaid:  () => API.get('/fines/unpaid'),
  getRevenue: () => API.get('/fines/revenue'),
  pay:        (id) => API.put(`/fines/${id}/pay`),
};

export const reservationsAPI = {
  getAll:   () => API.get('/reservations/'),
  getOne:   (id) => API.get(`/reservations/${id}`),
  create:   (data) => API.post('/reservations/', data),
  notify:   (id) => API.put(`/reservations/${id}/notify`),
  cancel:   (id) => API.delete(`/reservations/${id}`),
};

export default API;