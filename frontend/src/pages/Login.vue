<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="5" lg="4">
        <v-card elevation="2" class="rounded-xl">
          <v-card-title class="justify-center">
            <div class="text-h5 font-weight-bold">
              Welcome back to <span class="primary--text">MindCare+</span>
            </div>
          </v-card-title>

          <v-card-text>
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
                outlined dense clearable autofocus
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
              />

              <div class="d-flex align-center justify-space-between mb-2">
                <v-checkbox v-model="remember" label="Remember me" dense hide-details />
                <v-btn text small class="text-none" @click="$router.push('/register')">
                  Create account
                </v-btn>
              </div>

              <v-btn
                :loading="loading"
                :disabled="!valid || loading"
                color="primary"
                large block class="text-none"
                @click="onSubmit"
              >
                <v-icon left>mdi-login</v-icon>
                Log in
              </v-btn>
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
  created() {
    if (this.isAuthed) this.$router.replace('/dashboard')
  },
  methods: {
    ...mapActions(['loginAction']),
    async onSubmit() {
      this.error = ''
      if (!this.$refs.form || !this.$refs.form.validate()) return
      this.loading = true
      try {
        await this.loginAction({
          email: this.email.trim(),
          password: this.password,
          remember: this.remember,
        })
        // Redirect after login
        const redirectTo = this.$route.query.redirect || '/dashboard'
        this.$router.replace(redirectTo).catch(() => {}) // prevent navigation errors
      } catch (e) {
        this.error =
          (e && e.response && e.response.data && e.response.data.detail) ||
          e.message || 'Login failed.'
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style scoped>
.text-none { text-transform: none; }
</style>