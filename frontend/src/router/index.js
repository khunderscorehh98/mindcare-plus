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
const Analytics = () => import('@/pages/Analytics.vue')

// (optional) if you have an Upgrade page, uncomment this and route below
// const Upgrade = () => import('@/pages/Upgrade.vue')

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
    { path: '/', redirect: { name: 'dashboard' } },

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
      meta: { title: 'Consultation · MindCare+', requiresAuth: true } // API will still enforce plan
    },
    { path: '/resources', name: 'resources', component: Resources, meta: { title: 'Resources · MindCare+' } },
    { path: '/checkin', name: 'checkin', component: CheckIns, meta: { title: 'Daily Check-In · MindCare+', requiresAuth: true } },

    // PREMIUM route – gate with requiresPlan
    { path: '/analytics', name: 'analytics', component: Analytics, meta: { title: 'Analytics · MindCare+', requiresAuth: true, requiresPlan: 'premium' } },

    // (optional) Upgrade page
    // { path: '/upgrade', name: 'upgrade', component: Upgrade, meta: { title: 'Upgrade · MindCare+' } },

    { path: '*', redirect: { name: 'dashboard' } }
  ]
})

// Helpers
function isAuthed () {
  return !!(store.getters && store.getters.isAuthenticated)
}

function currentPlan () {
  // Try store first (adjust getter / path if your store differs)
  const fromStore = (store.getters && (store.getters.me?.plan || store.getters.user?.plan)) ||
                    (store.state && store.state.auth && store.state.auth.user && store.state.auth.user.plan)
  if (fromStore) return fromStore

  // Fallback to localStorage
  try {
    const raw = localStorage.getItem('mc_user')
    if (raw) {
      const u = JSON.parse(raw)
      return u?.plan || 'free'
    }
  } catch (_) {}
  return 'free'
}

// Global guards
router.beforeEach(async (to, from, next) => {
  if (to.meta && to.meta.title) document.title = to.meta.title

  // auth gate
  if (to.matched.some(r => r.meta && r.meta.requiresAuth)) {
    if (!isAuthed()) {
      try { await store.dispatch('refreshMe') } catch (_) {}
    }
    if (!isAuthed()) return next({ name: 'login', query: { redirect: to.fullPath } })
  }

  // guest-only gate
  if (to.matched.some(r => r.meta && r.meta.guestOnly)) {
    if (isAuthed()) return next({ name: 'dashboard' })
  }

  // plan gate (e.g., /analytics)
  const requiresPlan = to.matched.find(r => r.meta && r.meta.requiresPlan)?.meta?.requiresPlan
  if (requiresPlan) {
    const plan = currentPlan()
    if (plan !== requiresPlan) {
      // If you have an Upgrade page, send them there:
      // return next({ name: 'upgrade', query: { from: to.fullPath } })
      // Otherwise, bounce to dashboard with a hint:
      return next({ name: 'dashboard', query: { need_premium: '1' } })
    }
  }

  next()
})

export default router