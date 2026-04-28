/**
 * Parse agent markdown-ish reports (## headings, **bold**, NICHE blocks) into a safe structure for Vue rendering.
 */

function tsSortKey(m) {
  const raw = m?.created_at
  if (!raw) return 0
  const d = new Date(typeof raw === 'string' ? raw.trim() : raw)
  return Number.isNaN(d.getTime()) ? 0 : d.getTime()
}

function compareChronological(a, b) {
  const ta = tsSortKey(a)
  const tb = tsSortKey(b)
  if (ta !== tb) return ta - tb
  return String(a?.id ?? '').localeCompare(String(b?.id ?? ''), undefined, { numeric: true })
}

/**
 * Dernier message de l’agent strictement après le dernier message humain
 * (`from_agent_id === "dashboard"`), sur la timeline du fil.
 * Si aucun envoi dashboard dans les données, retourne null (pas d’ancienne réponse hors contexte).
 */
export function pickLatestAgentReplyAfterHuman(items, agentId) {
  const list = (items || []).slice().sort(compareChronological)
  let lastHumanIdx = -1
  for (let i = 0; i < list.length; i++) {
    if (list[i].from_agent_id === 'dashboard') {
      lastHumanIdx = i
    }
  }
  if (lastHumanIdx < 0) {
    return null
  }
  const after = list.slice(lastHumanIdx + 1).filter((m) => m.from_agent_id === agentId)
  if (!after.length) {
    return null
  }
  after.sort((a, b) => compareChronological(b, a))
  return after[0] || null
}

function stripMdHeading(line) {
  return line.replace(/^#{1,6}\s+/, '').trim()
}

/**
 * Split body into blocks starting with ## at line start.
 * @returns {{ title: string, lines: string[], isNiche: boolean, score: string|null }[]}
 */
export function parseReportBlocks(body) {
  const text = (body || '').replace(/\r\n/g, '\n').trim()
  if (!text) return []

  const chunks = text.split(/(?=^##\s+)/m).map((s) => s.trim()).filter(Boolean)
  const out = []
  for (let i = 0; i < chunks.length; i++) {
    let c = chunks[i]
    if (i === 0 && !/^##\s/.test(c)) {
      out.push({
        title: 'Contexte',
        lines: c.split('\n'),
        isNiche: false,
        score: null,
        preamble: true,
      })
      continue
    }
    const lines = c.split('\n')
    const head = lines[0] || ''
    const title = stripMdHeading(head)
    const isNiche = /^##\s*NICHE\s+/i.test(head) || /^NICHE\s+/i.test(title)
    let score = null
    const sm = c.match(/SCORE\s*:\s*([\d.]+)(?:\s*\/\s*10)?/i)
    if (sm) score = sm[1]
    out.push({
      title,
      lines: lines.slice(1),
      isNiche,
      score,
      preamble: false,
    })
  }
  return out
}
