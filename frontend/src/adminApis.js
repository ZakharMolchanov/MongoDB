import api from './api';

// Use core-service endpoints directly; core-service enforces admin checks server-side
export const topicsApi = {
  getAll: ()=> api.get('/topics'),
  getOne: (id)=> api.get(`/topics/${id}`),
  create: (data)=> api.post('/topics', data),
  update: (id, data)=> api.put(`/topics/${id}`, data),
  delete: (id)=> api.delete(`/topics/${id}`),
}

export const assignmentsApi = {
  getAll: (params) => api.get('/assignments', { params }),
  // compatibility alias used across the app
  list: (params) => api.get('/assignments', { params }),
  getOne: (id)=> api.get(`/assignments/${id}`),
  create: (data)=> api.post('/assignments', data),
  update: (id, data)=> api.put(`/assignments/${id}`, data),
  delete: (id)=> api.delete(`/assignments/${id}`),
}

export default { topicsApi, assignmentsApi };
