<template>
  <div class="login">
    <div class="card">
      <div class="header">
        <h1>APP EMPIRE</h1>
        <p>Command Center</p>
      </div>
      <form @submit.prevent="submit">
        <label>
          <span>Utilisateur</span>
          <input v-model="username" type="text" autocomplete="username" required />
        </label>
        <label>
          <span>Mot de passe</span>
          <input v-model="password" type="password" autocomplete="current-password" required />
        </label>
        <p v-if="error" class="err">{{ error }}</p>
        <button type="submit" :disabled="loading">
          {{ loading ? 'Connexion…' : 'Entrer' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const username = ref('admin')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    const r = route.query.redirect || '/'
    router.replace(typeof r === 'string' ? r : '/')
  } catch (e) {
    const d = e.response?.data?.detail
    error.value =
      typeof d === 'string'
        ? d
        : Array.isArray(d)
          ? d.map((x) => x.msg || x).join(' ')
          : 'Identifiants invalides ou serveur indisponible.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background:
    radial-gradient(ellipse 80% 50% at 50% -20%, rgba(245, 158, 11, 0.15), transparent),
    var(--bg);
}
.card {
  width: 100%;
  max-width: 380px;
  padding: 2rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.45);
}
.header {
  text-align: center;
  margin-bottom: 1.75rem;
}
.header h1 {
  font-family: var(--font-mono);
  font-size: 1.25rem;
  letter-spacing: 0.12em;
  margin: 0 0 0.35rem;
  color: var(--accent);
}
.header p {
  margin: 0;
  font-size: 0.8rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.2em;
}
form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
label {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
label span {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
  font-family: var(--font-mono);
}
input {
  padding: 0.6rem 0.75rem;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: #05050f;
  color: var(--text);
  font-size: 0.95rem;
  font-family: var(--font-sans);
}
input:focus {
  outline: none;
  border-color: #f59e0b66;
  box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.12);
}
button {
  margin-top: 0.5rem;
  padding: 0.7rem;
  font-family: var(--font-mono);
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  border: none;
  border-radius: 6px;
  background: linear-gradient(180deg, #f59e0b, #d97706);
  color: #0a0a0c;
  cursor: pointer;
}
button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.err {
  color: var(--danger);
  font-size: 0.8rem;
  margin: 0;
}
</style>
