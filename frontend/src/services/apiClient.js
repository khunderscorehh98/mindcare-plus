// src/services/apiClient.js
import axios from 'axios'
import store from '@/store'

// -------------------------
// Axios instance
// -------------------------
const api = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000',
  timeout: 120000,
})

// Attach Authorization if available
api.interceptors.request.use((cfg) => {
  const hdr = (store.getters && store.getters.authHeader) ? store.getters.authHeader : {}
  cfg.headers = { ...(cfg.headers || {}), ...hdr }
  return cfg
})

api.interceptors.response.use(
  r => r,
  err => {
    if (err && err.response) {
      // keep logs terse
      console.warn('[api]', err.response.status, err.response.data || err.message)
    }
    return Promise.reject(err)
  }
)

// -------------------------
// Helper functions
// -------------------------

// Auth
async function register (email, password) {
  const { data } = await api.post('/auth/register', { email, password })
  return data            // { token, user }
}

async function login (email, password) {
  const { data } = await api.post('/auth/login', { email, password })
  return data            // { token, user }
}

async function me () {
  const { data } = await api.get('/me')
  return data            // { id, email, plan }
}

async function upgrade (code) {
  const { data } = await api.post('/billing/upgrade', { code })
  return data            // { ok:true, plan:'premium' }
}

// Stateless chat
async function chat (message, history = []) {
  const { data } = await api.post('/chat', { message, history })
  return data?.reply || ''
}

// Sessions
async function createChatSession ({ title, checkin_id } = {}) {
  const { data } = await api.post('/chat/sessions', { title, checkin_id })
  return data
}
async function listChatSessions () {
  const { data } = await api.get('/chat/sessions')
  return data || []
}
async function renameChatSession (sid, title) {
  const { data } = await api.patch(`/chat/sessions/${sid}`, { title })
  return data
}
async function deleteChatSession (sid) {
  const { data } = await api.delete(`/chat/sessions/${sid}`)
  return data
}
async function listSessionMessages (sid) {
  const { data } = await api.get(`/chat/sessions/${sid}/messages`)
  return data || []
}
async function sendInSession (sid, message) {
  const { data } = await api.post(`/chat/sessions/${sid}/send`, { message, history: [] })
  return data?.reply || ''
}

// Check-ins
async function createCheckIn (payload) {
  const { data } = await api.post('/checkin', payload)
  return data
}
async function getRecentCheckIns (limit = 7) {
  const { data } = await api.get('/checkins', { params: { limit } })
  return data || []
}

// Resources
async function resources () {
  const { data } = await api.get('/resources')
  return Array.isArray(data) ? data : []
}

// Consults
async function getCounselors () {
  const { data } = await api.get('/counselors')
  return data || []
}
async function getSlots (counselorId, days = 14) {
  const { data } = await api.get(`/counselors/${counselorId}/slots`, { params: { days } })
  return data || []
}
async function bookSession ({ counselor_id, slot_id }) {
  const { data } = await api.post('/bookings', { counselor_id, slot_id })
  return data
}
async function myBookings () {
  const { data } = await api.get('/bookings/my')
  return data || []
}

// Analytics (optional)
async function analyticsSummary () {
  try {
    const { data } = await api.get('/analytics/overview')
    return data
  } catch {
    return null
  }
}

// -------------------------
// Exports
// -------------------------
export {
  api,
  // auth
  register, login, me, upgrade,
  // chat
  chat,
  // sessions
  createChatSession, listChatSessions, renameChatSession,
  deleteChatSession, listSessionMessages, sendInSession,
  // check-ins
  createCheckIn, getRecentCheckIns,
  // resources
  resources,
  // consults
  getCounselors, getSlots, bookSession, myBookings,
  // analytics
  analyticsSummary,
}

// Default export with all helpers (so default.getRecentCheckIns works)
export default {
  api,
  register, login, me, upgrade,
  chat,
  createChatSession, listChatSessions, renameChatSession,
  deleteChatSession, listSessionMessages, sendInSession,
  createCheckIn, getRecentCheckIns,
  resources,
  getCounselors, getSlots, bookSession, myBookings,
  analyticsSummary,
}