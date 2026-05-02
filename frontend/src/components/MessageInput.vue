<template>
  <div class="mc-message-input">
    <v-form ref="form" @submit.prevent="trySend">
      <div class="d-flex align-end" style="gap: 8px; background: white; border: 1px solid #E1E8EF; border-radius: 10px; padding: 8px 8px 8px 14px">
        <v-textarea
          v-model="draft"
          :auto-grow="true"
          :rows="1"
          :disabled="disabled || loading"
          :maxlength="maxLength"
          :placeholder="placeholder"
          :clearable="false"
          hide-details flat solo
          background-color="transparent"
          style="font-size: 13.5px; line-height: 1.5"
          class="flex-grow-1 mc-textarea"
          @keydown.native="onKeyDown"
        />
        <v-btn
          color="primary"
          depressed
          :loading="loading"
          :disabled="disabled || loading || !canSend"
          @click="trySend"
          aria-label="Send message"
          style="border-radius: 8px; min-width: 80px; height: 38px; font-weight: 600; font-size: 13px; align-self: flex-end; flex-shrink: 0"
        >
          <v-icon left small>mdi-send</v-icon>
          <span class="d-none d-sm-inline">Send</span>
        </v-btn>
      </div>
    </v-form>
    <div style="font-size: 11px; color: #B0BEC5; margin-top: 5px; padding-left: 2px">
      <kbd>Enter</kbd> to send &nbsp;•&nbsp; <kbd>Shift</kbd>+<kbd>Enter</kbd> for new line
    </div>
  </div>
</template>

<script>
export default {
  name: 'MessageInput',
  props: {
    loading:     { type: Boolean, default: false },
    disabled:    { type: Boolean, default: false },
    placeholder: { type: String,  default: 'Type your message…' },
    maxLength:   { type: Number,  default: 1000 },
  },
  data () { return { draft: '' } },
  computed: {
    canSend () { return (this.draft || '').trim().length > 0 },
  },
  methods: {
    onKeyDown (e) {
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); this.trySend() }
    },
    trySend () {
      if (this.loading || this.disabled) return
      const text = (this.draft || '').trim()
      if (!text) return
      this.$emit('send', text)
      this.draft = ''
    },
  },
}
</script>

<style scoped>
.mc-textarea :deep(.v-input__control),
.mc-textarea :deep(.v-input__slot) {
  background: transparent !important;
  box-shadow: none !important;
  padding: 0 !important;
  min-height: unset !important;
}
.mc-textarea :deep(textarea) {
  line-height: 1.5 !important;
  padding: 4px 0 !important;
}
kbd {
  background: #F4F7FC;
  border: 1px solid #E1E8EF;
  border-radius: 4px;
  padding: 1px 6px;
  font-size: 10px;
  color: #546E7A;
}
</style>
