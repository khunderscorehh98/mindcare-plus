<template>
  <default-layout>

    <template v-slot:header>
      <div class="mc-page-header d-flex align-center justify-space-between flex-wrap" style="gap: 12px">
        <div>
          <h2 style="font-size: 18px; font-weight: 600; color: #1A2332; margin: 0 0 2px">AI Chat</h2>
          <div class="subtitle" style="color: #546E7A; font-size: 13px">Private, supportive, and stigma-free</div>
        </div>
        <div class="d-flex align-center" style="gap: 8px">
          <v-chip v-if="plan !== 'premium'" small label color="#FFF8E1" style="color: #E65100; font-size: 11px; font-weight: 600">
            Free: 1 session
          </v-chip>
          <v-btn depressed small color="primary" :disabled="disableNewIfFree" @click="newSession">
            <v-icon left small>mdi-plus</v-icon>New Session
          </v-btn>
        </div>
      </div>
    </template>

    <v-row>
      <!-- Session sidebar -->
      <v-col cols="12" md="4" lg="3">
        <v-card elevation="1" class="mc-section-card">
          <div class="d-flex align-center px-4 py-3" style="border-bottom: 1px solid #E1E8EF">
            <v-icon small color="primary" class="mr-2">mdi-chat-outline</v-icon>
            <span style="font-size: 13.5px; font-weight: 600; color: #1A2332">Sessions</span>
            <v-spacer />
            <v-btn icon x-small :disabled="disableNewIfFree" @click="newSession">
              <v-icon small color="primary">mdi-plus</v-icon>
            </v-btn>
          </div>

          <div v-if="sessionsLoading" class="pa-4">
            <v-skeleton-loader type="list-item-two-line" />
          </div>

          <div v-else>
            <div
              v-for="s in sessions"
              :key="s.id"
              class="mc-session-item d-flex align-center px-4 py-3"
              :style="{ background: s.id === activeId ? '#EEF3FB' : 'transparent', borderBottom: '1px solid #F4F7FC', cursor: 'pointer' }"
              @click="selectSession(s.id)"
            >
              <div style="flex: 1; min-width: 0">
                <div style="font-size: 13px; font-weight: 500; color: #1A2332; white-space: nowrap; overflow: hidden; text-overflow: ellipsis">{{ s.title }}</div>
                <div style="font-size: 11px; color: #90A4AE">{{ fmtDateTime(s.created_at) }}</div>
              </div>
              <v-menu offset-y left>
                <template v-slot:activator="{ on, attrs }">
                  <v-btn icon x-small v-bind="attrs" v-on="on" @click.stop>
                    <v-icon x-small color="grey">mdi-dots-vertical</v-icon>
                  </v-btn>
                </template>
                <v-list dense style="border-radius: 8px">
                  <v-list-item @click="renameSessionPrompt(s)">
                    <v-list-item-icon><v-icon small>mdi-pencil-outline</v-icon></v-list-item-icon>
                    <v-list-item-title style="font-size: 13px">Rename</v-list-item-title>
                  </v-list-item>
                  <v-list-item @click="deleteSession(s)">
                    <v-list-item-icon><v-icon small color="error">mdi-delete-outline</v-icon></v-list-item-icon>
                    <v-list-item-title style="font-size: 13px; color: #C62828">Delete</v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-menu>
            </div>

            <div v-if="!sessions.length" class="pa-4 text-center" style="color: #90A4AE; font-size: 13px">
              No sessions yet.<br>
              <v-btn text x-small color="primary" @click="newSession">Create one</v-btn>
            </div>
          </div>
        </v-card>
      </v-col>

      <!-- Chat panel -->
      <v-col cols="12" md="8" lg="9">
        <v-card elevation="1" class="mc-section-card">
          <!-- Chat header -->
          <div class="d-flex align-center px-4 py-3" style="border-bottom: 1px solid #E1E8EF">
            <div style="width: 36px; height: 36px; border-radius: 8px; background: #E3F2FD; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-right: 12px">
              <v-icon small color="primary">mdi-robot-outline</v-icon>
            </div>
            <div style="flex: 1; min-width: 0">
              <div style="font-size: 14px; font-weight: 600; color: #1A2332">{{ activeTitle }}</div>
              <div style="font-size: 12px; color: #90A4AE">{{ activeSubtitle }}</div>
            </div>
            <v-btn v-if="activeId" text x-small color="primary" @click="renameSessionPrompt(activeSession)">
              <v-icon left x-small>mdi-pencil-outline</v-icon>Rename
            </v-btn>
          </div>

          <!-- Messages -->
          <div ref="scroll" style="height: 58vh; overflow-y: auto; background: #F8FAFC; padding: 16px">
            <chat-message
              v-for="(m, i) in uiMessages"
              :key="i"
              :isUser="m.role === 'user'"
              :text="m.content"
              :timestamp="fmtDateTime(m.created_at)"
            />
          </div>

          <!-- Loading bar -->
          <v-progress-linear v-if="loading" indeterminate color="primary" height="2" />

          <!-- Input area -->
          <div class="pa-3" style="border-top: 1px solid #E1E8EF">
            <message-input :loading="loading" @send="handleSend" />
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Rename dialog -->
    <v-dialog v-model="renameDlg.show" max-width="420">
      <v-card style="border-radius: 12px">
        <div class="px-5 py-4" style="border-bottom: 1px solid #E1E8EF">
          <div style="font-size: 16px; font-weight: 600; color: #1A2332">Rename session</div>
        </div>
        <div class="pa-5">
          <v-text-field
            v-model="renameDlg.title"
            outlined dense autofocus
            label="Session name"
            background-color="white"
          />
        </div>
        <div class="d-flex justify-end px-5 pb-4" style="gap: 8px">
          <v-btn outlined @click="renameDlg.show = false">Cancel</v-btn>
          <v-btn depressed color="primary" @click="confirmRename">Save</v-btn>
        </div>
      </v-card>
    </v-dialog>

  </default-layout>
</template>

<script>
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import ChatMessage from '@/components/ChatMessage.vue'
import MessageInput from '@/components/MessageInput.vue'
import api from '@/services/apiClient'
import { mapGetters } from 'vuex'

export default {
  name: 'Chat',
  components: { DefaultLayout, ChatMessage, MessageInput },
  data: () => ({
    sessions: [],
    sessionsLoading: false,
    messages: [],
    loading: false,
    activeId: null,
    renameDlg: { show: false, id: null, title: '' },
  }),
  computed: {
    ...mapGetters(['plan']),
    activeSession ()   { return this.sessions.find(s => s.id === this.activeId) || null },
    activeTitle ()     { return (this.activeSession && this.activeSession.title) || 'New conversation' },
    activeSubtitle ()  {
      if (!this.activeSession) return 'Select a session or create a new one'
      const s = this.activeSession
      const bits = []
      if (s.mood_at_start)  bits.push(`Mood: ${s.mood_at_start}`)
      if (s.stress_at_start != null) bits.push(`Stress: ${s.stress_at_start}/10`)
      return bits.join(' • ') || 'MindCare+ AI • Powered by Llama3'
    },
    uiMessages () {
      if (!this.messages.length) {
        return [{ role: 'assistant', content: 'Hi there. How are you feeling today? I\'m here to listen and support you.', created_at: new Date().toISOString() }]
      }
      return this.messages
    },
    disableNewIfFree () { return this.plan !== 'premium' && this.sessions.length >= 1 },
  },
  async created () {
    await this.loadSessions()
    const qId = Number(this.$route.query.session || 0) || null
    if (qId && this.sessions.some(s => s.id === qId)) {
      this.selectSession(qId)
    } else if (this.sessions.length) {
      this.selectSession(this.sessions[0].id)
    } else {
      this.messages = []
    }
  },
  methods: {
    async loadSessions () {
      this.sessionsLoading = true
      try {
        const { data } = await api.api.get('/chat/sessions')
        this.sessions = Array.isArray(data) ? data : []
      } catch { this.sessions = [] } finally { this.sessionsLoading = false }
    },
    async newSession () {
      if (this.disableNewIfFree) return
      try {
        const { data } = await api.api.post('/chat/sessions', { title: 'New session' })
        await this.loadSessions()
        this.selectSession(data.id)
      } catch { /* silently fail */ }
    },
    async selectSession (id) {
      if (!id) return
      this.activeId = id
      this.$router.replace({ query: { session: String(id) } }).catch(() => {})
      await this.loadMessages()
    },
    async loadMessages () {
      if (!this.activeId) return
      try {
        const { data } = await api.api.get(`/chat/sessions/${this.activeId}/messages`)
        this.messages = Array.isArray(data) ? data : []
        this.$nextTick(this.autoscroll)
      } catch { this.messages = [] }
    },
    renameSessionPrompt (s) {
      if (!s) return
      this.renameDlg = { show: true, id: s.id, title: s.title || '' }
    },
    async confirmRename () {
      try {
        const title = (this.renameDlg.title || '').trim()
        if (title) {
          await api.api.patch(`/chat/sessions/${this.renameDlg.id}`, { title })
          await this.loadSessions()
        }
      } finally {
        this.renameDlg.show = false
      }
    },
    async deleteSession (s) {
      if (!s) return
      if (!window.confirm('Delete this session and all messages?')) return
      try {
        await api.api.delete(`/chat/sessions/${s.id}`)
        await this.loadSessions()
        if (this.sessions.length) {
          this.selectSession(this.sessions[0].id)
        } else {
          this.activeId = null
          this.messages = []
          this.$router.replace({ query: {} }).catch(() => {})
        }
      } catch { /* silently fail */ }
    },
    async handleSend (text) {
      const content = (text || '').trim()
      if (!content) return
      const now = new Date().toISOString()
      const push = (msg) => { this.messages.push(msg); this.$nextTick(this.autoscroll) }
      push({ role: 'user', content, created_at: now })
      this.loading = true
      try {
        if (this.activeId) {
          const { data } = await api.api.post(`/chat/sessions/${this.activeId}/send`, { message: content, history: [] })
          push({ role: 'assistant', content: (data && data.reply) || '…', created_at: new Date().toISOString() })
        } else {
          const replyText = await api.chat(content, [])
          push({ role: 'assistant', content: replyText || '…', created_at: new Date().toISOString() })
        }
      } catch {
        push({ role: 'assistant', content: 'Sorry, I could not reach the server. Please try again.', created_at: new Date().toISOString() })
      } finally {
        this.loading = false
      }
    },
    fmtDateTime (ts) { try { return new Date(ts).toLocaleString() } catch { return ts } },
    autoscroll () { const el = this.$refs.scroll; if (el) el.scrollTop = el.scrollHeight },
  },
}
</script>

<style scoped>
.mc-session-item:hover { background: #F4F7FC !important; }
</style>
