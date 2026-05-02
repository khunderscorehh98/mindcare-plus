<template>
  <div :class="['d-flex', isUser ? 'justify-end' : 'justify-start', 'mb-3']">
    <div class="d-flex align-end" :style="{ flexDirection: isUser ? 'row-reverse' : 'row', gap: '8px', maxWidth: '80%' }">

      <!-- AI avatar -->
      <div
        v-if="!isUser"
        style="width: 30px; height: 30px; border-radius: 8px; background: #E3F2FD; display: flex; align-items: center; justify-content: center; flex-shrink: 0"
      >
        <v-icon x-small color="primary">mdi-robot-outline</v-icon>
      </div>

      <!-- Bubble -->
      <div :style="bubbleStyle">
        <div style="font-size: 13.5px; line-height: 1.6" aria-live="polite">
          <template v-if="typing">
            <span class="dot" v-for="i in 3" :key="i">•</span>
          </template>
          <template v-else>
            <span v-for="(part, i) in parts" :key="i">
              <a
                v-if="part.type === 'link'"
                :href="part.href"
                target="_blank"
                rel="noopener"
                :style="{ color: isUser ? 'rgba(255,255,255,0.85)' : '#1565C0' }"
              >{{ part.text }}</a>
              <span v-else>{{ part.text }}</span>
            </span>
          </template>
        </div>
        <div :style="{ fontSize: '11px', marginTop: '4px', opacity: 0.6, textAlign: isUser ? 'right' : 'left' }">
          {{ timeLabel }}
        </div>
      </div>

      <!-- User avatar -->
      <div
        v-if="isUser"
        style="width: 30px; height: 30px; border-radius: 8px; background: #1565C0; display: flex; align-items: center; justify-content: center; flex-shrink: 0"
      >
        <v-icon x-small dark>mdi-account</v-icon>
      </div>

    </div>
  </div>
</template>

<script>
export default {
  name: 'ChatMessage',
  props: {
    isUser:     { type: Boolean, default: false },
    text:       { type: String,  default: '' },
    timestamp:  { type: [String, Number, Date], default: () => new Date() },
    showAvatar: { type: Boolean, default: true },
    typing:     { type: Boolean, default: false },
  },
  computed: {
    bubbleStyle () {
      return this.isUser
        ? { background: '#1565C0', color: 'white', borderRadius: '12px 4px 12px 12px', padding: '10px 14px', boxShadow: '0 1px 4px rgba(21,101,192,0.2)' }
        : { background: 'white',   color: '#1A2332', borderRadius: '4px 12px 12px 12px', padding: '10px 14px', boxShadow: '0 1px 4px rgba(0,0,0,0.06)', border: '1px solid #E1E8EF' }
    },
    timeLabel () {
      try { return new Date(this.timestamp).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' }) }
      catch { return '' }
    },
    parts () {
      const urlRegex = /(https?:\/\/[^\s)]+|www\.[^\s)]+)/gi
      const text = this.text || ''
      const out = []
      let last = 0, m
      while ((m = urlRegex.exec(text)) !== null) {
        if (m.index > last) out.push({ type: 'text', text: text.slice(last, m.index) })
        const url = m[0]
        out.push({ type: 'link', text: url, href: url.startsWith('http') ? url : `https://${url}` })
        last = m.index + url.length
      }
      if (last < text.length) out.push({ type: 'text', text: text.slice(last) })
      if (!out.length) out.push({ type: 'text', text })
      return out
    },
  },
}
</script>

<style scoped>
.dot {
  animation: blink 1.2s infinite;
  padding: 0 2px;
  font-size: 18px;
  opacity: 0.5;
}
.dot:nth-child(2) { animation-delay: .15s; }
.dot:nth-child(3) { animation-delay: .3s; }
@keyframes blink {
  0%, 80%, 100% { opacity: .2 }
  40%            { opacity: 1 }
}
</style>
