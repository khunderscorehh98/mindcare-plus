// src/services/apiClient.js
import axios from 'axios'
import store from '@/store'

// -------------------------------------------
// axios instance
// -------------------------------------------
const api = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000,
})

// attach Authorization header if available
api.interceptors.request.use((cfg) => {
  const hdr = (store.getters && store.getters.authHeader) ? store.getters.authHeader : {}
  cfg.headers = { ...(cfg.headers || {}), ...hdr }
  return cfg
})

// optional: simple response error logging (keep noise low)
api.interceptors.response.use(
  (r) => r,
  (err) => {
    // eslint-disable-next-line no-console
    if (err && err.response) console.warn('[api]', err.response.status, err.response.data || err.message)
    return Promise.reject(err)
  }
)

// -------------------------------------------
// convenience wrappers (all return parsed data)
// -------------------------------------------

// Auth
async function register (email, password) {
  const { data } = await api.post('/auth/register', { email, password })
  return data // { token, user }
}

async function login (email, password) {
  const { data } = await api.post('/auth/login', { email, password })
  return data // { token, user }
}

async function me () {
  const { data } = await api.get('/me')
  return data // { id, email, plan }
}

// Billing (MVP)
async function upgrade (code) {
  const { data } = await api.post('/billing/upgrade', { code })
  return data // { ok: true, plan: "premium" }
}

// Chat (stateless public demo)
async function chat (message, history = []) {
  const { data } = await api.post('/chat', { message, history })
  return data && data.reply ? data.reply : ''
}
// back-compat alias if your components still call sendMessage()
const sendMessage = chat

// Chat Sessions (persisted, auth required)
async function createChatSession ({ title, checkin_id } = {}) {
  const { data } = await api.post('/chat/sessions', { title, checkin_id })
  return data // { id, title, checkin_id }
}

async function listChatSessions () {
  const { data } = await api.get('/chat/sessions')
  return data // [{ id, title, created_at, ... }]
}

async function renameChatSession (sid, title) {
  const { data } = await api.patch(`/chat/sessions/${sid}`, { title })
  return data // { ok: true }
}

async function deleteChatSession (sid) {
  const { data } = await api.delete(`/chat/sessions/${sid}`)
  return data // { ok: true }
}

async function listSessionMessages (sid) {
  const { data } = await api.get(`/chat/sessions/${sid}/messages`)
  return data // [{ role, content, created_at }]
}

async function sendInSession (sid, message) {
  const { data } = await api.post(`/chat/sessions/${sid}/send`, { message, history: [] })
  // backend builds history from DB; we pass empty array for shape compatibility
  return data && data.reply ? data.reply : ''
}

// Check-ins (auth required)
async function createCheckIn (payload) {
  const { data } = await api.post('/checkin', payload)
  return data // { ok, id }
}

async function getRecentCheckIns (limit = 7) {
  const { data } = await api.get('/checkins', { params: { limit } })
  return data || []
}

// Resources (public)
async function resources () {
  const { data } = await api.get('/resources')
  return Array.isArray(data) ? data : []
}

// Counselors / Slots / Bookings (auth; bookings require premium)
async function getCounselors () {
  const { data } = await api.get('/counselors')
  return data || []
}

async function getSlots (counselorId, days = 14) {
  const { data } = await api.get(`/counselors/${counselorId}/slots`, { params: { days } })
  return data || []
}

async function bookSession ({ counselor_id, slot_id }) {
  const { data } = await api.post('/bookings')
    .catch(async (err) => {
      // some proxies dislike empty body + headers; resend with explicit JSON
      if (err && err.response && err.response.status === 415) {
        const retry = await api.post('/bookings', { counselor_id, slot_id })
        return { data: retry.data }
      }
      throw err
    })
  // if above path didn't send payload, send properly:
  if (!data || !data.id) {
    const { data: data2 } = await api.post('/bookings', { counselor_id, slot_id })
    return data2
  }
  return data
}

async function myBookings () {
  const { data } = await api.get('/bookings/my')
  return data || []
}

// (Optional) Analytics — safe wrapper if endpoint exists later
async function analyticsSummary () {
  try {
    const { data } = await api.get('/analytics/summary')
    return data
  } catch (e) {
    return null
  }
}

// -------------------------------------------
// exports
// -------------------------------------------
export {
  api,                    // raw axios instance (use sparingly)
  // auth
  register, login, me, upgrade,
  // chat (stateless)
  chat, sendMessage,
  // chat sessions
  createChatSession, listChatSessions, renameChatSession,
  deleteChatSession, listSessionMessages, sendInSession,
  // check-ins
  createCheckIn, getRecentCheckIns,
  // resources
  resources,
  // consults
  getCounselors, getSlots, bookSession, myBookings,
  // analytics (optional)
  analyticsSummary,
}

export default {
  api,
  // auth
  register, login, me, upgrade,
  // chat
  chat, sendMessage,
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