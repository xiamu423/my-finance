import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api/',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

export default {
  getSignals(params) {
    return apiClient.get('/signals/', { params })
  },
  getSignal(id) {
    return apiClient.get(`/signals/${id}/`)
  },
  getCompany(id) {
    return apiClient.get(`/companies/${id}/`)
  }
}
