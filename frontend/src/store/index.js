// src/store/index.js
import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'

Vue.use(Vuex)

// A tiny axios instance for auth calls to avoid circular deps with apiClient.js
const authHttp = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000',
  timeout: 20000,
})

function saveState(key, value) { try { localStorage.setItem(key, JSON.stringify(value)) } catch (e) { } }
function loadState(key, fallback = null) {
  try {
    const raw = localStorage.getItem(key)
    return raw ? JSON.parse(raw) : fallback
  } catch (e) { return fallback }
}
function removeState(key) { try { localStorage.removeItem(key) } catch (e) { } }

export default new Vuex.Store({
  state: {
    token: loadState('mc_token', null),
    user: loadState('mc_user', null), // { id, email, plan }
    authLoading: false,
  },


  getters: {
    // preferred names used by components
    isAuthed: (s) => !!s.token,
    user: (s) => s.user,
    plan: (s) => (s.user ? s.user.plan || 'free' : 'free'),
    userEmail: (s) => (s.user ? s.user.email : ''),

    // legacy/aliases (safe to keep for compatibility)
    isAuthenticated: (s) => !!s.token,
    me: (s) => s.user,
    userPlan: (s) => (s.user ? s.user.plan || 'free' : 'free'),
    authHeader: (s) => (s.token ? { Authorization: `Bearer ${s.token}` } : {}),
  },

  mutations: {
    SET_TOKEN(state, token) {
      state.token = token
      if (token) saveState('mc_token', token)
      else removeState('mc_token')
    },
    SET_USER(state, user) {
      state.user = user
      if (user) saveState('mc_user', user)
      else removeState('mc_user')
    },
    SET_AUTH_LOADING(state, v) { state.authLoading = !!v },
    CLEAR_AUTH(state) {
      state.token = null
      state.user = null
      removeState('mc_token')
      removeState('mc_user')
    },
  },

  actions: {
    // Call in main.js on app start (after store creation)
    initFromStorage({ state }) { return !!state.token },

    async register({ commit }, { email, password }) {
      commit('SET_AUTH_LOADING', true)
      try {
        const { data } = await authHttp.post('/auth/register', { email, password })
        commit('SET_TOKEN', data.token || null)
        commit('SET_USER', data.user || null)
        return data
      } finally {
        commit('SET_AUTH_LOADING', false)
      }
    },

    async login({ commit }, { email, password }) {
      commit('SET_AUTH_LOADING', true)
      try {
        const { data } = await authHttp.post('/auth/login', { email, password })
        commit('SET_TOKEN', data.token || null)
        commit('SET_USER', data.user || null)
        return data
      } finally {
        commit('SET_AUTH_LOADING', false)
      }
    },

    logout({ commit }) { commit('CLEAR_AUTH') },

    async refreshMe({ state, commit }) {
      if (!state.token) return null
      try {
        const { data } = await authHttp.get('/me', { headers: { Authorization: `Bearer ${state.token}` } })
        const merged = { ...(state.user || {}), ...(data || {}) }
        commit('SET_USER', merged)
        return merged
      } catch (e) {
        commit('CLEAR_AUTH')
        throw e
      }
    },

    // ✅ action aliases used by your Login.vue/Register.vue
    async loginAction({ dispatch }, payload) {
      return dispatch('login', payload)
    },
    async registerAction({ dispatch }, payload) {
      return dispatch('register', payload)
    },
  },
})