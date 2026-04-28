<template>
  <div v-if="loading" class="muted">Chargement…</div>
  <div v-else class="page">
    <header class="head">
      <div>
        <h2 class="h2">Tasks</h2>
        <p class="sub">Kanban — création, statut et option de notification Wire (OpenClaw).</p>
      </div>
      <button type="button" class="btn-primary" @click="openModal">Nouvelle tâche</button>
    </header>
    <p v-if="err" class="err">{{ err }}</p>
    <KanbanBoard :tasks="tasks" @move="onMove" />

    <Teleport to="body">
      <div v-if="modalOpen" class="backdrop" @click.self="closeModal">
        <div class="modal" role="dialog" aria-labelledby="task-modal-title">
          <header class="modal-hd">
            <h2 id="task-modal-title" class="modal-title">Nouvelle tâche</h2>
            <button type="button" class="close" aria-label="Fermer" @click="closeModal">×</button>
          </header>
          <form class="form" @submit.prevent="submitCreate">
            <label class="lab">
              <span>Titre</span>
              <input v-model.trim="form.title" type="text" required maxlength="200" class="inp" />
            </label>
            <label class="lab">
              <span>Agent</span>
              <select v-model="form.agent_id" class="inp">
                <option value="">—</option>
                <option v-for="a in agents" :key="a.id" :value="a.id">{{ a.emoji }} {{ a.name }}</option>
              </select>
            </label>
            <label class="lab">
              <span>App</span>
              <select v-model="form.app_id" class="inp">
                <option value="">—</option>
                <option v-for="p in apps" :key="p.id" :value="p.id">{{ p.icon }} {{ p.name }}</option>
              </select>
            </label>
            <label class="lab">
              <span>Priorité</span>
              <select v-model="form.priority" class="inp">
                <option value="low">Basse</option>
                <option value="medium">Moyenne</option>
                <option value="high">Haute</option>
              </select>
            </label>
            <label class="lab">
              <span>Statut initial</span>
              <select v-model="form.status" class="inp">
                <option value="todo">À faire</option>
                <option value="inprogress">En cours</option>
                <option value="done">Terminé</option>
              </select>
            </label>
            <label class="check">
              <input v-model="form.notify_wire" type="checkbox" :disabled="!form.agent_id" />
              <span>Notifier l’agent sur le Wire (OpenClaw)</span>
            </label>
            <p v-if="formErr" class="form-err">{{ formErr }}</p>
            <div class="modal-actions">
              <button type="button" class="btn-ghost" @click="closeModal">Annuler</button>
              <button type="submit" class="btn-primary" :disabled="saving">Créer</button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '@/api'
import KanbanBoard from '@/components/tasks/KanbanBoard.vue'

const loading = ref(true)
const err = ref('')
const tasks = ref([])
const agents = ref([])
const apps = ref([])
const modalOpen = ref(false)
const saving = ref(false)
const formErr = ref('')
const form = ref({
  title: '',
  agent_id: '',
  app_id: '',
  priority: 'medium',
  status: 'todo',
  notify_wire: false,
})

async function load() {
  const { data } = await api.get('/api/tasks')
  tasks.value = data
}

async function loadMeta() {
  const [ag, ap] = await Promise.all([api.get('/api/agents'), api.get('/api/apps')])
  agents.value = ag.data || []
  apps.value = ap.data || []
}

onMounted(async () => {
  err.value = ''
  try {
    await Promise.all([load(), loadMeta()])
  } catch (e) {
    err.value = e.response?.data?.detail || 'Impossible de charger les tâches.'
  } finally {
    loading.value = false
  }
})

async function onMove(t, newStatus) {
  err.value = ''
  try {
    await api.put(`/api/tasks/${t.id}`, { status: newStatus })
    await load()
  } catch (e) {
    err.value = e.response?.data?.detail || e.message
  }
}

function openModal() {
  form.value = {
    title: '',
    agent_id: '',
    app_id: '',
    priority: 'medium',
    status: 'todo',
    notify_wire: false,
  }
  formErr.value = ''
  modalOpen.value = true
}

function closeModal() {
  modalOpen.value = false
}

async function submitCreate() {
  formErr.value = ''
  saving.value = true
  try {
    await api.post('/api/tasks', {
      title: form.value.title,
      agent_id: form.value.agent_id || null,
      app_id: form.value.app_id || null,
      priority: form.value.priority,
      status: form.value.status,
      notify_wire: Boolean(form.value.notify_wire && form.value.agent_id),
    })
    await load()
    closeModal()
  } catch (e) {
    const d = e.response?.data?.detail
    formErr.value = typeof d === 'string' ? d : Array.isArray(d) ? d.map((x) => x.msg).join(', ') : 'Échec de la création.'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.head {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 0.75rem;
}
.h2 {
  margin: 0;
  font-size: 1.15rem;
}
.sub {
  margin: 0.25rem 0 0;
  font-size: 0.8rem;
  color: var(--text-muted);
}
.muted {
  color: var(--text-muted);
  font-family: var(--font-mono);
}
.err,
.form-err {
  color: var(--danger);
  font-size: 0.8rem;
  margin: 0;
}
.btn-primary {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 0.5rem 0.85rem;
  border-radius: 8px;
  border: 1px solid var(--accent);
  background: rgba(245, 158, 11, 0.15);
  color: var(--accent);
  cursor: pointer;
}
.btn-primary:hover:not(:disabled) {
  background: rgba(245, 158, 11, 0.28);
}
.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.btn-ghost {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
}
.btn-ghost:hover {
  border-color: var(--border-hover);
  color: var(--text);
}
.backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.65);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}
.modal {
  width: 100%;
  max-width: 420px;
  max-height: 90vh;
  overflow: auto;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1rem 1.15rem;
}
.modal-hd {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}
.modal-title {
  margin: 0;
  font-size: 1rem;
}
.close {
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 1.5rem;
  cursor: pointer;
  line-height: 1;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.lab {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
  font-family: var(--font-mono);
}
.inp {
  font-size: 0.9rem;
  padding: 0.45rem 0.5rem;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-sans);
}
.check {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: var(--text-muted);
  cursor: pointer;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 0.5rem;
}
</style>
