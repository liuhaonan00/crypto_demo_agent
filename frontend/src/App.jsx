import { useEffect, useRef, useState } from 'react'
import Sidebar from './components/Sidebar.jsx'
import ChatWindow from './components/ChatWindow.jsx'
import SettingsModal from './components/SettingsModal.jsx'
import * as api from './api.js'

export default function App() {
  const [sessions, setSessions] = useState([])
  const [activeId, setActiveId] = useState(null)
  const [messages, setMessages] = useState([])
  const [status, setStatus] = useState('')
  const [streaming, setStreaming] = useState(false)
  const [settingsOpen, setSettingsOpen] = useState(false)
  const initialized = useRef(false)

  async function refreshSessions() {
    try {
      setSessions(await api.listSessions())
    } catch (e) {
      console.error(e)
    }
  }

  async function init() {
    if (initialized.current) return
    initialized.current = true
    await refreshSessions()
    const list = await api.listSessions()
    if (list.length) {
      await openSession(list[0].id)
    } else {
      await handleNewSession()
    }
  }

  useEffect(() => {
    init()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function openSession(id) {
    try {
      const s = await api.getSession(id)
      setActiveId(id)
      setMessages((s.messages || []).map((m) => ({ ...m, streaming: false, error: false })))
      setStatus('')
    } catch (e) {
      console.error(e)
    }
  }

  async function handleNewSession() {
    const s = await api.createSession()
    await refreshSessions()
    setActiveId(s.id)
    setMessages([])
    setStatus('')
  }

  async function handleDelete(id) {
    if (!window.confirm('确认删除该会话？')) return
    await api.deleteSession(id)
    await refreshSessions()
    if (id === activeId) {
      const list = await api.listSessions()
      if (list.length) await openSession(list[0].id)
      else await handleNewSession()
    }
  }

  async function handleRename(id) {
    const title = window.prompt('重命名会话', '')
    if (title == null) return
    await api.renameSession(id, title)
    await refreshSessions()
  }

  async function handleSend(text) {
    const content = (text || '').trim()
    if (!content || streaming || !activeId) return
    const userMsg = { role: 'user', content }
    const assistantMsg = { role: 'assistant', content: '', streaming: true, error: false }
    setMessages((prev) => [...prev, userMsg, assistantMsg])
    setStreaming(true)
    setStatus('思考中…')

    try {
      await api.sendMessage(activeId, content, {
        onStatus: (m) => setStatus(m),
        onDelta: (chunk) => {
          setMessages((prev) => {
            const next = [...prev]
            const last = next[next.length - 1]
            next[next.length - 1] = { ...last, content: last.content + chunk }
            return next
          })
        },
        onDone: () => {
          setMessages((prev) => {
            const next = [...prev]
            const last = next[next.length - 1]
            next[next.length - 1] = { ...last, streaming: false }
            return next
          })
          refreshSessions()
        },
        onError: (m) => {
          setMessages((prev) => {
            const next = [...prev]
            const last = next[next.length - 1]
            next[next.length - 1] = { ...last, content: m, streaming: false, error: true }
            return next
          })
        },
      })
    } catch (e) {
      setMessages((prev) => {
        const next = [...prev]
        const last = next[next.length - 1]
        next[next.length - 1] = {
          ...last,
          content: '请求失败：' + e.message,
          streaming: false,
          error: true,
        }
        return next
      })
    } finally {
      setStreaming(false)
      setStatus('')
    }
  }

  const activeTitle = sessions.find((s) => s.id === activeId)?.title || ''

  return (
    <div className="app">
      <Sidebar
        sessions={sessions}
        activeId={activeId}
        onSelect={openSession}
        onNew={handleNewSession}
        onDelete={handleDelete}
        onRename={handleRename}
        onOpenSettings={() => setSettingsOpen(true)}
      />
      <ChatWindow
        title={activeTitle}
        messages={messages}
        status={status}
        streaming={streaming}
        onSend={handleSend}
      />
      {settingsOpen && (
        <SettingsModal onClose={() => setSettingsOpen(false)} />
      )}
    </div>
  )
}
