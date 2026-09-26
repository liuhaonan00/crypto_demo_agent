import { useRef } from 'react'
import MessageBubble from './MessageBubble.jsx'

export default function ChatWindow({ title, messages, status, streaming, onSend }) {
  const inputRef = useRef(null)
  const scrollRef = useRef(null)

  function submit(e) {
    e.preventDefault()
    const v = inputRef.current.value
    onSend(v)
    inputRef.current.value = ''
  }

  return (
    <main className="chat">
      <header className="chat-head">
        <span className="chat-title">{title || 'Crypto 智能助手'}</span>
      </header>

      <div className="chat-body" ref={scrollRef}>
        {messages.length === 0 && (
          <div className="welcome">
            <h2>你好，我是 Crypto 智能助手 🪙</h2>
            <p>可以问我币价、行情、技术指标、资金费率、持仓量、加密新闻等。</p>
            <p className="muted">（只回答加密货币相关问题，其他问题我会拒绝回答）</p>
          </div>
        )}
        {messages.map((m, i) => (
          <MessageBubble key={i} message={m} />
        ))}
        {status && <div className="status-line">⏳ {status}</div>}
      </div>

      <form className="chat-input" onSubmit={submit}>
        <input
          ref={inputRef}
          placeholder="输入你的问题，例如：BTC 现在的价格是多少？"
          disabled={streaming}
        />
        <button className="btn btn-primary" type="submit" disabled={streaming}>
          {streaming ? '…' : '发送'}
        </button>
      </form>
    </main>
  )
}
