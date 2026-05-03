import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

export const projectsAPI = {
  create: (repoUrl) => api.post('/projects', { repo_url: repoUrl }),
  getAll: () => api.get('/projects'),
  get: (id) => api.get(`/projects/${id}`),
  delete: (id) => api.delete(`/projects/${id}`)
}

export const analysisAPI = {
  start: (projectId) => api.post(`/analysis/${projectId}`),
  cancel: (projectId) => api.post(`/analysis/${projectId}/cancel`),
  getProgress: (projectId) => api.get(`/analysis/${projectId}/progress`),
  getReport: (projectId) => api.get(`/analysis/${projectId}/report`),
  streamProgress: (projectId) => `/api/analysis/${projectId}/progress/stream`
}

export const qaAPI = {
  ask: (projectId, question) => api.post('/qa', { project_id: projectId, question }),
  askStream: (projectId, question) => ({
    url: '/api/qa/stream',
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ project_id: projectId, question })
  }),
  getFile: (projectId, filePath) => api.get(`/qa/file/${projectId}`, { params: { file_path: filePath } }),
  search: (projectId, query) => api.get(`/qa/search/${projectId}`, { params: { query } })
}
