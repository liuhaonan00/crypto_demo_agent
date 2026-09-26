"""HTTP 路由：session 增删改查、设置读写/测试、chat SSE 流式。"""
import asyncio
import json
import queue as _queue
import threading

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from . import agent, config, storage

router = APIRouter()


# ---------- SSE 辅助 ----------

def _sse(event, obj):
    return "event: %s\ndata: %s\n\n" % (event, json.dumps(obj, ensure_ascii=False))


def _chunks(text, size=6):
    for i in range(0, len(text), size):
        yield text[i:i + size]


# ---------- sessions ----------

@router.get("/sessions")
def list_sessions():
    return storage.list_sessions()


@router.post("/sessions")
def create_session():
    return storage.create_session()


@router.get("/sessions/{sid}")
def get_session(sid: str):
    s = storage.get_session(sid)
    if s is None:
        raise HTTPException(404, "会话不存在")
    return s


@router.patch("/sessions/{sid}")
def rename_session(sid: str, body: dict):
    s = storage.rename_session(sid, body.get("title", ""))
    if s is None:
        raise HTTPException(404, "会话不存在")
    return s


@router.delete("/sessions/{sid}")
def delete_session(sid: str):
    if not storage.delete_session(sid):
        raise HTTPException(404, "会话不存在")
    return {"ok": True}


# ---------- settings ----------

@router.get("/settings")
def get_settings():
    return config.load_settings().model_dump()


@router.post("/settings")
def set_settings(body: dict):
    s = config.save_settings(config.Settings(**body))
    return s.model_dump()


@router.post("/settings/test")
def test_settings(body: dict):
    s = config.Settings(**body)
    try:
        agent.test_connection(s)
        return {"ok": True}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


# ---------- chat ----------

@router.post("/chat")
async def chat(body: dict):
    session_id = body.get("sessionId")
    message = (body.get("message") or "").strip()
    if not session_id or not message:
        raise HTTPException(400, "sessionId 和 message 不能为空")

    session = storage.get_session(session_id)
    if session is None:
        raise HTTPException(404, "会话不存在")

    history = list(session.get("messages", []))
    storage.append_message(session_id, "user", message)

    # crypto-only 快速过滤：明显无关直接拒绝，不浪费模型与工具调用（无需模型，先于设置检查）
    if agent.is_off_topic(message):
        storage.append_message(session_id, "assistant", agent.REFUSAL)
        async def _refuse():
            for c in _chunks(agent.REFUSAL):
                yield _sse("delta", {"content": c})
                await asyncio.sleep(0.01)
            yield _sse("done", {"sessionId": session_id})
        return StreamingResponse(_refuse(), media_type="text/event-stream")

    settings = config.load_settings()
    if not settings.base_url or not settings.model_id:
        async def _err():
            yield _sse("error", {"message": "请先在设置页配置 base url 和 model id，然后重新提问"})
            yield _sse("done", {"sessionId": session_id})
        return StreamingResponse(_err(), media_type="text/event-stream")

    qq = _queue.Queue()

    def progress(text):
        qq.put(("status", text))

    def work():
        try:
            answer, _rounds = agent.run_agent(settings, history, message, progress_cb=progress)
            qq.put(("answer", answer))
            storage.append_message(session_id, "assistant", answer)
        except Exception as exc:
            qq.put(("error", str(exc)))
        finally:
            qq.put(("done", None))

    threading.Thread(target=work, daemon=True).start()

    async def gen():
        while True:
            kind, payload = await asyncio.to_thread(qq.get)
            if kind == "status":
                yield _sse("status", {"message": payload})
            elif kind == "answer":
                for c in _chunks(payload):
                    yield _sse("delta", {"content": c})
                    await asyncio.sleep(0.008)
            elif kind == "error":
                yield _sse("error", {"message": payload})
            elif kind == "done":
                yield _sse("done", {"sessionId": session_id})
                return

    return StreamingResponse(gen(), media_type="text/event-stream")
