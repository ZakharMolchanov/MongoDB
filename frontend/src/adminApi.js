import api from './api';

// Use shared api instance (coreApi) so Authorization header and proxy are consistent.
export const adminApi = {
  listLogs: (params) => api.get('/admin/logs', { params }),
  getLog: (id) => api.get(`/admin/logs/${id}`),
  listUsers: () => api.get('/admin/users'),
  getUser: (id) => api.get(`/admin/users/${id}`),
  updateUser: (id, data) => api.put(`/admin/users/${id}`, data),
  deleteUser: (id) => api.delete(`/admin/users/${id}`),
};

export default adminApi;
