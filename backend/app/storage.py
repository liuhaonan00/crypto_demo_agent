"""session 本地文件存储：一个 session 一个 JSON 文件。"""
import json
import time
import uuid

from .config import SESSIONS_DIR, ensure_dirs


def _path(session_id: str):
    return SESSIONS_DIR / (session_id + ".json")


def _save(session: dict) -> dict:
    session["updatedAt"] = int(time.time())
    _path(session["id"]).write_text(
        json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return session


def list_sessions():
    ensure_dirs()
    sessions = []
    for f in SESSIONS_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            sessions.append({
                "id": data["id"],
                "title": data.get("title", "新会话"),
                "createdAt": data.get("createdAt"),
                "updatedAt": data.get("updatedAt"),
                "messageCount": len(data.get("messages", [])),
            })
        except Exception:
            continue
    sessions.sort(key=lambda s: s.get("updatedAt") or 0, reverse=True)
    return sessions


def get_session(session_id: str):
    p = _path(session_id)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def create_session():
    ensure_dirs()
    now = int(time.time())
    session = {
        "id": uuid.uuid4().hex,
        "title": "新会话",
        "createdAt": now,
        "updatedAt": now,
        "messages": [],
    }
    return _save(session)


def append_message(session_id: str, role: str, content: str):
    session = get_session(session_id)
    if session is None:
        return None
    session.setdefault("messages", []).append({
        "role": role,
        "content": content,
        "ts": int(time.time()),
    })
    # 用第一条用户消息自动生成标题
    if role == "user" and (not session.get("title") or session.get("title") == "新会话"):
        session["title"] = content[:24]
    return _save(session)


def rename_session(session_id: str, title: str):
    session = get_session(session_id)
    if session is None:
        return None
    session["title"] = (title or "").strip() or "新会话"
    return _save(session)


def delete_session(session_id: str) -> bool:
    p = _path(session_id)
    if p.exists():
        p.unlink()
        return True
    return False
