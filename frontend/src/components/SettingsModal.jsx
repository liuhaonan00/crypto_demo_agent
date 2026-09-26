import { useEffect, useState } from 'react'
import * as api from '../api.js'

export default function SettingsModal({ onClose }) {
  const [form, setForm] = useState({ base_url: '', model_id: '', api_key: '', cryptopanic_key: '' })
  const [saving, setSaving] = useState(false)
  const [testing, setTesting] = useState(false)
  const [msg, setMsg] = useState(null)

  useEffect(() => {
    api.getSettings().then(setForm).catch((e) => setMsg({ type: 'error', text: e.message }))
  }, [])

  function set(field) {
    return (e) => setForm((f) => ({ ...f, [field]: e.target.value }))
  }

  async function handleSave() {
    setSaving(true)
    setMsg(null)
    try {
      await api.saveSettings(form)
      setMsg({ type: 'ok', text: '已保存' })
    } catch (e) {
      setMsg({ type: 'error', text: e.message })
    } finally {
      setSaving(false)
    }
  }

  async function handleTest() {
    setTesting(true)
    setMsg(null)
    try {
      const r = await api.testSettings(form)
      if (r.ok) setMsg({ type: 'ok', text: '连接成功 ✅' })
      else setMsg({ type: 'error', text: '连接失败：' + (r.error || '') })
    } catch (e) {
      setMsg({ type: 'error', text: '连接失败：' + e.message })
    } finally {
      setTesting(false)
    }
  }

  return (
    <div className="modal-mask" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <h3>设置</h3>
          <button className="icon-btn" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">
          <label>
            Base URL（OpenAI 兼容）
            <input
              value={form.base_url}
              onChange={set('base_url')}
              placeholder="例如 https://api.deepseek.com/v1"
            />
          </label>
          <label>
            Model ID
            <input
              value={form.model_id}
              onChange={set('model_id')}
              placeholder="例如 deepseek-chat"
            />
          </label>
          <label>
            API Key
            <input
              type="password"
              value={form.api_key}
              onChange={set('api_key')}
              placeholder="sk-..."
            />
          </label>
          <label>
            CryptoPanic Key（新闻工具，可选）
            <input
              value={form.cryptopanic_key}
              onChange={set('cryptopanic_key')}
              placeholder="免费申请 cryptopanic.com/developers/api"
            />
          </label>
          {msg && <div className={'form-msg ' + msg.type}>{msg.text}</div>}
        </div>
        <div className="modal-foot">
          <button className="btn" onClick={handleTest} disabled={testing}>
            {testing ? '测试中…' : '测试连接'}
          </button>
          <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
            {saving ? '保存中…' : '保存'}
          </button>
        </div>
      </div>
    </div>
  )
}
