import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth API calls
export const authAPI = {
  register: (userData) => api.post('/auth/register', userData),
  login: (credentials) => api.post('/auth/login', credentials, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  }),
  getCurrentUser: () => api.get('/auth/me'),
}

// Resume API calls
export const resumeAPI = {
  create: (resumeData) => api.post('/resume', resumeData),
  getAll: (skip = 0, limit = 100) => api.get(`/resume?skip=${skip}&limit=${limit}`),
  getById: (id) => api.get(`/resume/${id}`),
  update: (id, resumeData) => api.put(`/resume/${id}`, resumeData),
  delete: (id) => api.delete(`/resume/${id}`),
}

// Job Posting API calls
export const jobPostingAPI = {
  create: (jobData) => api.post('/job-posting', jobData),
  getAll: (skip = 0, limit = 100) => api.get(`/job-posting?skip=${skip}&limit=${limit}`),
  getById: (id) => api.get(`/job-posting/${id}`),
  update: (id, jobData) => api.put(`/job-posting/${id}`, jobData),
  delete: (id) => api.delete(`/job-posting/${id}`),
}

// Analysis API calls
export const analysisAPI = {
  create: (analysisData) => api.post('/analysis', analysisData),
  getAll: (skip = 0, limit = 100) => api.get(`/analysis?skip=${skip}&limit=${limit}`),
  getById: (id) => api.get(`/analysis/${id}`),
  delete: (id) => api.delete(`/analysis/${id}`),
}

// Upload API calls
export const uploadAPI = {
  uploadResume: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/upload/resume', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  uploadJobPosting: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/upload/job-posting', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  deleteFile: (filePath) => api.delete(`/upload/file?file_path=${encodeURIComponent(filePath)}`),
}

// LaTeX API calls
export const latexAPI = {
  generatePDF: (resumeId, templateName = 'modern') =>
    api.post(`/latex/generate-pdf/${resumeId}?template_name=${templateName}`),
  getTemplates: () => api.get('/latex/templates'),
}

export default api