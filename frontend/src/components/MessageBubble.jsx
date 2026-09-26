export default function MessageBubble({ message }) {
  const isUser = message.role === 'user'
  return (
    <div className={'msg ' + (isUser ? 'msg-user' : 'msg-assistant')}>
      <div className={'bubble' + (message.error ? ' error' : '')}>
        {message.content
          ? message.content
          : message.streaming
            ? <span className="typing">▋</span>
            : ''}
      </div>
    </div>
  )
}
