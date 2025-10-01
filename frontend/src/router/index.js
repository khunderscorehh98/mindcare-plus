// src/router/index.js
import Vue from 'vue'
import Router from 'vue-router'
import store from '@/store'

// --- Pages (lazy) ---
const Home = () => import('@/pages/Home.vue')
const Login = () => import('@/pages/Login.vue')
const Register = () => import('@/pages/Register.vue')
const Dashboard = () => import('@/pages/Dashboard.vue')
const Chat = () => import('@/pages/Chat.vue')
const Consult = () => import('@/pages/Consult.vue')
const Resources = () => import('@/pages/Resources.vue')
const CheckIns = () => import('@/pages/Checkins.vue')
const Analytics = () => import('@/pages/Analytics.vue') // <— NEW

Vue.use(Router)

// Silence "NavigationDuplicated" rejections on push/replace
const origPush = Router.prototype.push
Router.prototype.push = function push (loc, onResolve, onReject) {
  if (onResolve || onReject) return origPush.call(this, loc, onResolve, onReject)
  return origPush.call(this, loc).catch(err => err)
}
const origReplace = Router.prototype.replace
Router.prototype.replace = function replace (loc, onResolve, onReject) {
  if (onResolve || onReject) return origReplace.call(this, loc, onResolve, onReject)
  return origReplace.call(this, loc).catch(err => err)
}

const router = new Router({
  mode: 'history',
  base: process.env.BASE_URL || '/',
  scrollBehavior () { return { x: 0, y: 0 } },
  routes: [
    // Default: land on Dashboard
    { path: '/', redirect: { name: 'dashboard' } },

    // Optional marketing page
    { path: '/home', name: 'home', component: Home, meta: { title: 'MindCare+ · Home' } },

    // Auth
    { path: '/login', name: 'login', component: Login, meta: { title: 'Sign in · MindCare+', guestOnly: true } },
    { path: '/register', name: 'register', component: Register, meta: { title: 'Create account · MindCare+', guestOnly: true } },

    // App pages
    { path: '/dashboard', name: 'dashboard', component: Dashboard, meta: { title: 'Dashboard · MindCare+', requiresAuth: true } },
    { path: '/chat', name: 'chat', component: Chat, meta: { title: 'AI Chat · MindCare+', requiresAuth: true } },
    {
      path: '/consult',
      name: 'consult',
      component: Consult,
      meta: { title: 'Consultation · MindCare+', requiresAuth: true }, // premium gating handled by API (HTTP 402)
    },
    { path: '/resources', name: 'resources', component: Resources, meta: { title: 'Resources · MindCare+' } },
    { path: '/checkin', name: 'checkin', component: CheckIns, meta: { title: 'Daily Check-In · MindCare+', requiresAuth: true } },

    // NEW: Analytics
    { path: '/analytics', name: 'analytics', component: Analytics, meta: { title: 'Analytics · MindCare+', requiresAuth: true } },

    // 404 -> Dashboard (or make a dedicated NotFound page later)
    { path: '*', redirect: { name: 'dashboard' } },
  ],
})

// Helpers
function isAuthed () {
  return !!(store.getters && store.getters.isAuthenticated)
}

// Global guards
router.beforeEach(async (to, from, next) => {
  if (to.meta && to.meta.title) document.title = to.meta.title

  if (to.matched.some(r => r.meta && r.meta.requiresAuth)) {
    if (!isAuthed()) {
      try { await store.dispatch('refreshMe') } catch (_) {}
    }
    if (!isAuthed()) return next({ name: 'login', query: { redirect: to.fullPath } })
  }

  if (to.matched.some(r => r.meta && r.meta.guestOnly)) {
    if (isAuthed()) return next({ name: 'dashboard' })
  }

  next()
})

export default router