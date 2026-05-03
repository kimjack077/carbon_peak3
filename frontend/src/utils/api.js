// frontend/src/utils/api.js
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
})

// 请求拦截器
api.interceptors.request.use(config => {
  return config
}, error => Promise.reject(error))

// 响应拦截器 - 统一错误处理
api.interceptors.response.use(
  response => response.data,
  error => {
    const resp = error.response
    const data = resp && resp.data
    const message = (data && data.error) || error.message || '请求失败'
    return Promise.reject(new Error(message))
  }
)

// API 方法
export const dataApi = {
  uploadCustom: (formData) => api.post('/upload/custom', formData),
  validate: (data) => api.post('/data/validate', data),
  loadExample: () => api.post('/upload/example'),
  getTrends: () => api.get('/data/trends')
}

export const scenarioApi = {
  list: () => api.get('/scenarios'),
  create: (data) => api.post('/scenarios', data),
  delete: (name) => api.delete(`/scenarios/${encodeURIComponent(name)}`),
  copy: (data) => api.post('/scenarios/copy', data),
  compare: (names) => api.post('/scenarios/compare', { scenarios: names })
}

export const predictApi = {
  run: (scenarios, years = 36) => api.post('/predict', { scenarios, forecast_years: years }),
  status: () => api.post('/predict/status'),
  results: (name) => api.get(`/results/${name}`),
  chartData: () => api.get('/chart-data')
}

export const exportApi = {
  excel: (name) => api.get(`/export/excel/${name}`, { responseType: 'blob' }),
  pdf: (name) => api.get(`/export/pdf/${name}`, { responseType: 'blob' }),
  csv: (name) => `/api/results/${name}/download`
}

export const recommendApi = {
  parameters: () => api.get('/recommend/parameters')
}

export default api