// API configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const API_ENDPOINTS = {
  ANALYZE: `${API_BASE_URL}/api/analyze/`,
  SEARCH: `${API_BASE_URL}/api/search/`,
  LIST: `${API_BASE_URL}/api/list/`,
  GET_ANALYSIS: (id) => `${API_BASE_URL}/api/${id}/`
}

export default API_BASE_URL
