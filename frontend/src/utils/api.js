import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8005'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes timeout for long scans
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`)
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const errorMessage = error.response?.data?.detail || error.message || 'Request failed'
    console.error('API Error:', errorMessage)
    return Promise.reject(new Error(errorMessage))
  }
)

export const scanConfiguration = async (formData) => {
  try {
    const response = await api.post('/scan', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response
  } catch (error) {
    throw error
  }
}

export const explainIssue = async (issueDescription, configurationContext, mode = 'devops') => {
  try {
    const response = await api.post('/explain', {
      issue_description: issueDescription,
      configuration_context: configurationContext,
      mode
    })
    return response
  } catch (error) {
    throw error
  }
}

export const getHealthCheck = async () => {
  try {
    const response = await api.get('/')
    return response
  } catch (error) {
    throw error
  }
}

export default api
