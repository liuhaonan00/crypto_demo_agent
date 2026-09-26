export default function Sidebar({
  sessions,
  activeId,
  onSelect,
  onNew,
  onDelete,
  onRename,
  onOpenSettings,
}) {
  return (
    <aside className="sidebar">
      <div className="sidebar-head">
        <span className="logo">🪙 Crypto 助手</span>
        <button className="btn btn-primary" onClick={onNew}>
          ＋ 新建
        </button>
      </div>
      <div className="session-list">
        {sessions.map((s) => (
          <div
            key={s.id}
            className={'session-item' + (s.id === activeId ? ' active' : '')}
            onClick={() => onSelect(s.id)}
          >
            <div className="session-main">
              <div className="session-title">{s.title || '新会话'}</div>
              <div className="session-meta">{s.messageCount} 条消息</div>
            </div>
            <div className="session-actions">
              <button
                className="icon-btn"
                title="重命名"
                onClick={(e) => {
                  e.stopPropagation()
                  onRename(s.id)
                }}
              >
                ✎
              </button>
              <button
                className="icon-btn danger"
                title="删除"
                onClick={(e) => {
                  e.stopPropagation()
                  onDelete(s.id)
                }}
              >
                🗑
              </button>
            </div>
          </div>
        ))}
        {sessions.length === 0 && <div className="empty-hint">暂无会话</div>}
      </div>
      <div className="sidebar-foot">
        <button className="btn" onClick={onOpenSettings}>
          ⚙️ 设置
        </button>
      </div>
    </aside>
  )
}
