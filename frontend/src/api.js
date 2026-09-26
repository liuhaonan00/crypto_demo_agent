const BASE = '/api'

export async function listSessions() {
  const r = await fetch(`${BASE}/sessions`)
  if (!r.ok) throw new Error('加载会话失败')
  return r.json()
}

export async function createSession() {
  const r = await fetch(`${BASE}/sessions`, { method: 'POST' })
  if (!r.ok) throw new Error('创建会话失败')
  return r.json()
}

export async function getSession(id) {
  const r = await fetch(`${BASE}/sessions/${id}`)
  if (!r.ok) throw new Error('会话不存在')
  return r.json()
}

export async function renameSession(id, title) {
  const r = await fetch(`${BASE}/sessions/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title }),
  })
  if (!r.ok) throw new Error('重命名失败')
  return r.json()
}

export async function deleteSession(id) {
  const r = await fetch(`${BASE}/sessions/${id}`, { method: 'DELETE' })
  if (!r.ok) throw new Error('删除失败')
  return r.json()
}

export async function getSettings() {
  const r = await fetch(`${BASE}/settings`)
  if (!r.ok) throw new Error('读取设置失败')
  return r.json()
}

export async function saveSettings(settings) {
  const r = await fetch(`${BASE}/settings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings),
  })
  if (!r.ok) throw new Error('保存设置失败')
  return r.json()
}

export async function testSettings(settings) {
  const r = await fetch(`${BASE}/settings/test`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings),
  })
  return r.json()
}

// POST + SSE（EventSource 只支持 GET，故用 fetch 流式读取）
export async function sendMessage(sessionId, message, { onStatus, onDelta, onDone, onError }) {
  const resp = await fetch(`${BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sessionId, message }),
  })
  if (!resp.ok || !resp.body) {
    throw new Error('请求失败（HTTP ' + resp.status + '）')
  }
  const reader = resp.body.getReader()
  const decoder = new TextDecoder()
  let buf = ''
  for (;;) {
    const { done, value } = await reader.read()
    if (done) break
    buf += decoder.decode(value, { stream: true })
    let idx
    while ((idx = buf.indexOf('\n\n')) >= 0) {
      const raw = buf.slice(0, idx)
      buf = buf.slice(idx + 2)
      const evt = parseSSE(raw)
      if (!evt) continue
      if (evt.event === 'status' && onStatus) onStatus(evt.data.message || '')
      else if (evt.event === 'delta' && onDelta) onDelta(evt.data.content || '')
      else if (evt.event === 'done' && onDone) onDone(evt.data)
      else if (evt.event === 'error' && onError) onError(evt.data.message || '出错')
    }
  }
}

function parseSSE(raw) {
  let event = 'message'
  const dataLines = []
  for (const line of raw.split('\n')) {
    if (line.startsWith('event:')) event = line.slice(6).trim()
    else if (line.startsWith('data:')) dataLines.push(line.slice(5).trim())
  }
  if (!dataLines.length) return null
  try {
    return { event, data: JSON.parse(dataLines.join('\n')) }
  } catch {
    return { event, data: {} }
  }
}
