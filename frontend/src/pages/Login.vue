<template>
  <v-container fluid class="fill-height login-wrap">
    <v-row no-gutters class="fill-height">
      <!-- Left brand / message -->
      <v-col
        cols="12" md="6"
        class="left-panel d-none d-md-flex align-center justify-center"
      >
        <div class="px-10">
          <div class="brand-row mb-6">
            <v-avatar size="44" color="primary" class="elev">
              <v-icon dark>mdi-heart</v-icon>
            </v-avatar>
            <div class="ml-3">
              <div class="text-h5 font-weight-bold">MindCare+</div>
              <div class="subtitle-2 grey--text text--lighten-1">Welcome back</div>
            </div>
          </div>

          <div class="text-h4 font-weight-bold mb-3">
            Good to see you again.
          </div>
          <div class="subtitle-1 grey--text text--lighten-1 mb-8">
            Pick up where you left off with your check-ins, chats, and resources —
            all in one calm, private space.
          </div>

          <v-chip label class="chip-soft mr-2 mb-2" color="primary" text-color="white">
            <v-icon left small>mdi-lock</v-icon> Private by default
          </v-chip>
          <v-chip label class="chip-soft mb-2" color="primary" text-color="white">
            <v-icon left small>mdi-timer-sand</v-icon> Under a minute
          </v-chip>
        </div>
      </v-col>

      <!-- Right form -->
      <v-col cols="12" md="6" class="d-flex align-center justify-center">
        <v-card class="form-card rounded-xl elevation-8 mx-4 my-10" max-width="520">
          <v-card-text class="pa-8">
            <div class="text-h5 font-weight-bold mb-1">Log in to your account</div>
            <div class="caption grey--text mb-6">
              New here?
              <router-link :to="{ name: 'register', query: $route.query }">Create account</router-link>
            </div>

            <v-alert v-if="error" type="error" dense border="left" class="mb-4">
              {{ error }}
            </v-alert>

            <v-form ref="form" v-model="valid" @submit.prevent="onSubmit">
              <v-text-field
                v-model="email"
                label="Email"
                type="email"
                prepend-inner-icon="mdi-email"
                :rules="[rules.required, rules.email]"
                :disabled="loading"
                outlined dense clearable
                autocomplete="email"
              />

              <v-text-field
                v-model="password"
                :type="showPass ? 'text' : 'password'"
                label="Password"
                prepend-inner-icon="mdi-lock"
                :append-icon="showPass ? 'mdi-eye-off' : 'mdi-eye'"
                @click:append="showPass = !showPass"
                :rules="[rules.required, rules.min(6)]"
                :disabled="loading"
                outlined dense
                autocomplete="current-password"
                @keydown.native="checkCaps"
                @keyup.native="checkCaps"
              />
              <div v-if="capsOn" class="caption red--text mb-2">
                <v-icon x-small color="red" class="mr-1">mdi-alert</v-icon>
                Caps Lock is ON
              </div>

              <div class="d-flex align-center justify-space-between mb-4">
                <v-checkbox v-model="remember" label="Remember me" dense hide-details :disabled="loading" />
                <v-btn text small class="text-none" :disabled="loading" @click.prevent="$router.push({ name: 'register' })">
                  Create account
                </v-btn>
              </div>

              <v-btn
                type="submit"
                :loading="loading"
                :disabled="!valid || loading"
                color="primary"
                large block class="text-none mb-2"
              >
                <v-icon left>mdi-login</v-icon>
                Log in
              </v-btn>

              <div class="caption grey--text text--darken-1 mt-3 text-center">
                Forgot password?
                <a href="#" @click.prevent>Reset it</a>
              </div>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'Login',
  data: () => ({
    email: '',
    password: '',
    remember: true,
    showPass: false,
    capsOn: false,
    loading: false,
    error: '',
    valid: false,
    rules: {
      required: v => (!!v && String(v).trim().length > 0) || 'This field is required',
      email: v => /.+@.+\..+/.test(v) || 'Enter a valid email',
      min: n => v => (v && v.length >= n) || `Minimum ${n} characters`,
    },
  }),
  computed: { ...mapGetters(['isAuthed']) },
  created () {
    if (this.isAuthed) this.$router.replace('/dashboard').catch(() => {})
  },
  methods: {
    ...mapActions(['loginAction']),
    checkCaps (e) {
      // basic caps lock detection
      if (!e || typeof e.getModifierState !== 'function') return
      this.capsOn = !!e.getModifierState('CapsLock')
    },
    async onSubmit () {
      this.error = ''
      if (!this.$refs.form || !this.$refs.form.validate()) return
      this.loading = true
      try {
        await this.loginAction({
          email: this.email.trim(),
          password: this.password,
          remember: this.remember,
        })
        const redirectTo = this.$route.query.redirect || '/dashboard'
        this.$router.replace(redirectTo).catch(() => {})
      } catch (e) {
        // Prefer backend detail -> fallback to generic
        this.error =
          (e && e.response && e.response.data && (e.response.data.detail || e.response.data.message)) ||
          e.message ||
          'Login failed. Please try again.'
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style scoped>
.login-wrap {
  background: radial-gradient(1100px 600px at 20% 20%, rgba(63,81,181,.10), transparent 60%),
              radial-gradient(900px 500px at 80% 90%, rgba(3,169,244,.08), transparent 60%);
}
.left-panel {
  background: linear-gradient(135deg, rgba(33,150,243,.12), rgba(156,39,176,.10));
  backdrop-filter: blur(2px);
}
.form-card {
  backdrop-filter: saturate(140%) blur(4px);
}
.brand-row .elev {
  box-shadow: 0 6px 18px rgba(33,150,243,.25) !important;
}
.text-none { text-transform: none; }
.chip-soft { opacity: .95; }
</style>