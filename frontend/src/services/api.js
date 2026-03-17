import axios from 'axios'

/**
 * API Service
 * Handles all communication with the backend API
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add request interceptor for authentication
apiClient.interceptors.request.use(
  (config) => {
    // TODO: Add AWS Cognito token here
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      console.error('Unauthorized access')
      // TODO: Redirect to login
    }
    return Promise.reject(error)
  }
)

/**
 * Submit a natural language query
 * @param {Object} data - { user_id, query }
 * @returns {Promise<Object>} Query result
 */
export const submitQuery = async (data) => {
  try {
    const response = await apiClient.post('/ask', data)
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to submit query')
  }
}

/**
 * Get query history for a user
 * @param {string} userId - User ID
 * @returns {Promise<Array>} Query history
 */
export const getQueryHistory = async (userId) => {
  try {
    const response = await apiClient.get(`/history/${userId}`)
    return response.data
  } catch (error) {
    console.error('Failed to fetch history:', error)
    return []
  }
}

/**
 * Get available query templates
 * @returns {Promise<Array>} Query templates
 */
export const getTemplates = async () => {
  try {
    const response = await apiClient.get('/templates')
    return response.data
  } catch (error) {
    console.error('Failed to fetch templates:', error)
    return []
  }
}

/**
 * Get user profile
 * @param {string} userId - User ID
 * @returns {Promise<Object>} User profile
 */
export const getUserProfile = async (userId) => {
  try {
    const response = await apiClient.get(`/users/${userId}`)
    return response.data
  } catch (error) {
    throw new Error('Failed to fetch user profile')
  }
}

export default apiClient
