<template>
  <default-layout>
    <template v-slot:header>
      <v-row align="center">
        <v-col cols="12" md="8">
          <h2 class="subtitle-1 mb-0">
            MindCare+ Chat
          </h2>
          <div class="text-caption grey--text">
            Private, supportive, and stigma-free.
          </div>
        </v-col>
        <v-col cols="12" md="4" class="text-md-right mt-2 mt-md-0">
          <v-btn
            :disabled="disableNewIfFree"
            color="primary"
            class="mr-2"
            @click="newSession"
          >
            <v-icon left>mdi-plus</v-icon>
            New Session
          </v-btn>
          <v-chip
            v-if="plan !== 'premium'"
            small
            color="amber lighten-4"
            class="text-uppercase"
            label
          >
            Free plan: 1 session
          </v-chip>
        </v-col>
      </v-row>
    </template>

    <v-row>
      <!-- Sidebar: sessions -->
      <v-col cols="12" md="4" lg="3">
        <v-card outlined class="rounded-xl">
          <v-card-title class="py-3">
            <v-icon left color="primary">mdi-message-text</v-icon>
            Sessions
            <v-spacer />
            <v-btn icon small :disabled="disableNewIfFree" @click="newSession">
              <v-icon>mdi-plus</v-icon>
            </v-btn>
          </v-card-title>
          <v-divider />

          <v-card-text v-if="sessionsLoading">
            <v-skeleton-loader type="list-item-two-line" />
          </v-card-text>

          <v-list v-else dense two-line>
            <template v-if="sessions.length">
              <v-list-item
                v-for="s in sessions"
                :key="s.id"
                :class="{ 'grey lighten-4': s.id === activeId }"
                @click="selectSession(s.id)"
              >
                <v-list-item-content>
                  <v-list-item-title class="font-weight-medium">
                    {{ s.title }}
                  </v-list-item-title>
                  <v-list-item-subtitle class="grey--text">
                    {{ fmtDateTime(s.created_at) }}
                  </v-list-item-subtitle>
                </v-list-item-content>

                <v-menu offset-y left>
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn icon small v-bind="attrs" v-on="on">
                      <v-icon small>mdi-dots-vertical</v-icon>
                    </v-btn>
                  </template>
                  <v-list dense>
                    <v-list-item @click="renameSessionPrompt(s)">
                      <v-list-item-icon><v-icon small>mdi-rename-box</v-icon></v-list-item-icon>
                      <v-list-item-title>Rename</v-list-item-title>
                    </v-list-item>
                    <v-list-item @click="deleteSession(s)">
                      <v-list-item-icon><v-icon small color="red">mdi-delete</v-icon></v-list-item-icon>
                      <v-list-item-title class="red--text">Delete</v-list-item-title>
                    </v-list-item>
                  </v-list>
                </v-menu>
              </v-list-item>
            </template>

            <v-list-item v-else>
              <v-list-item-content>
                <v-list-item-title class="text-body-2">
                  No sessions yet. Create one to get started.
                </v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>

      <!-- Main chat panel -->
      <v-col cols="12" md="8" lg="9">
        <v-card elevation="2" class="rounded-xl">
          <v-card-title class="pb-0">
            <div>
              <div class="text-h6 font-weight-semibold">{{ activeTitle }}</div>
              <div class="text-caption grey--text">
                {{ activeSubtitle }}
              </div>
            </div>
            <v-spacer />
            <v-btn small text color="primary" v-if="activeId" @click="renameSessionPrompt(activeSession)">
              <v-icon left small>mdi-rename-box</v-icon>
              Rename
            </v-btn>
          </v-card-title>

          <v-divider class="my-2"></v-divider>

          <v-card-text>
            <div ref="scroll" class="px-2" style="max-height: 62vh; overflow-y: auto;">
              <chat-message
                v-for="(m, i) in uiMessages"
                :key="i"
                :isUser="m.role === 'user'"
                :text="m.content"
                :timestamp="fmtDateTime(m.created_at)"
              />
            </div>

            <div v-if="loading" class="mt-2">
              <v-progress-linear indeterminate color="primary" />
            </div>

            <div class="mt-2">
              <message-input :loading="loading" @send="handleSend" />
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Rename dialog -->
    <v-dialog v-model="renameDlg.show" max-width="420">
      <v-card>
        <v-card-title class="headline">Rename session</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="renameDlg.title"
            dense outlined autofocus
            label="Title"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="renameDlg.show = false">Cancel</v-btn>
          <v-btn color="primary" @click="confirmRename">Save</v-btn>
        </v-card-actions>
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

    renameDlg: {
      show: false,
      id: null,
      title: '',
    },
  }),
  computed: {
    ...mapGetters(['plan']),
    activeSession() {
      return this.sessions.find(s => s.id === this.activeId) || null
    },
    activeTitle() {
      return (this.activeSession && this.activeSession.title) || 'New conversation'
    },
    activeSubtitle() {
      if (!this.activeSession) return 'Start a chat or create a session'
      const s = this.activeSession
      const bits = []
      if (s.mood_at_start) bits.push(`mood: ${s.mood_at_start}`)
      if (s.stress_at_start !== null && s.stress_at_start !== undefined) bits.push(`stress: ${s.stress_at_start}`)
      const meta = bits.join(' • ')
      return meta || 'Session saved'
    },
    uiMessages() {
      // fallback starter message if empty
      if (!this.messages.length) {
        return [{
          role: 'assistant',
          content: 'Hi, how are you feeling today?',
          created_at: new Date().toISOString(),
        }]
      }
      return this.messages
    },
    disableNewIfFree() {
      return this.plan !== 'premium' && this.sessions.length >= 1
    },
  },
  async created() {
    await this.loadSessions()
    // select session via query ?session=ID if provided
    const qId = Number(this.$route.query.session || 0) || null
    if (qId && this.sessions.some(s => s.id === qId)) {
      this.selectSession(qId)
    } else if (this.sessions.length) {
      this.selectSession(this.sessions[0].id)
    } else {
      // no sessions yet: stay in stateless mode, will use /chat until a session is created
      this.messages = []
    }
  },
  methods: {
    // sessions
    async loadSessions() {
      this.sessionsLoading = true
      try {
        const { data } = await api.api.get('/chat/sessions')
        this.sessions = Array.isArray(data) ? data : []
      } catch (e) {
        this.sessions = []
      } finally {
        this.sessionsLoading = false
      }
    },
    async newSession() {
      if (this.disableNewIfFree) return
      try {
        const { data } = await api.api.post('/chat/sessions', { title: 'New session' })
        await this.loadSessions()
        this.selectSession(data.id)
      } catch (e) {
        this.$toast && this.$toast.error('Could not create session')
      }
    },
    async selectSession(id) {
      if (!id) return
      this.activeId = id
      this.$router.replace({ query: { session: String(id) } }).catch(() => {})
      await this.loadMessages()
    },
    async loadMessages() {
      if (!this.activeId) return
      try {
        const { data } = await api.api.get(`/chat/sessions/${this.activeId}/messages`)
        this.messages = Array.isArray(data) ? data : []
        this.$nextTick(this.autoscroll)
      } catch (e) {
        this.messages = []
      }
    },
    renameSessionPrompt(s) {
      if (!s) return
      this.renameDlg = { show: true, id: s.id, title: s.title || '' }
    },
    async confirmRename() {
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
    async deleteSession(s) {
      if (!s) return
      const yes = window.confirm('Delete this session and all its messages?')
      if (!yes) return
      try {
        await api.api.delete(`/chat/sessions/${s.id}`)
        await this.loadSessions()
        // pick another session or clear
        if (this.sessions.length) {
          this.selectSession(this.sessions[0].id)
        } else {
          this.activeId = null
          this.messages = []
          this.$router.replace({ query: {} }).catch(() => {})
        }
      } catch (e) {
        this.$toast && this.$toast.error('Failed to delete session')
      }
    },

    // chat send
    async handleSend(text) {
      const content = (text || '').trim()
      if (!content) return

      // optimistic append
      const now = new Date().toISOString()
      const pushAndScroll = (msg) => {
        this.messages.push(msg)
        this.$nextTick(this.autoscroll)
      }
      const userMsg = { role: 'user', content, created_at: now }
      pushAndScroll(userMsg)

      this.loading = true
      try {
        if (this.activeId) {
          // sessioned chat
          const { data } = await api.api.post(`/chat/sessions/${this.activeId}/send`, {
            message: content,
            history: [], // backend rebuilds from DB; keep empty for clarity
          })
          const replyText = (data && data.reply) || '…'
          pushAndScroll({ role: 'assistant', content: replyText, created_at: new Date().toISOString() })
        } else {
          // stateless fallback
          const replyText = await api.chat(content, [])
          pushAndScroll({ role: 'assistant', content: replyText || '…', created_at: new Date().toISOString() })
        }
      } catch (e) {
        // revert optimistic user message? we’ll keep it and show an error bot bubble
        pushAndScroll({
          role: 'assistant',
          content: 'Sorry, I could not reach the server. Please try again.',
          created_at: new Date().toISOString(),
        })
        // also log for devs
        /* eslint-disable no-console */
        console.error('chat send failed', e && e.response ? e.response : e)
      } finally {
        this.loading = false
      }
    },

    // ui helpers
    fmtDateTime(ts) {
      try { return new Date(ts).toLocaleString() } catch { return ts }
    },
    autoscroll() {
      const el = this.$refs.scroll
      if (!el) return
      el.scrollTop = el.scrollHeight
    },
  },
}
</script>

<style scoped>
.session-item { cursor: pointer; }
</style>