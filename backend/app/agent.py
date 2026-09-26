"""Agent 核心：crypto-only 过滤 + system 评判 + 反思循环（生成→评判→重写）。"""
import json
import re

from . import llm
from .prompts import JUDGE_TEMPLATE, SYSTEM_PROMPT
from .tools import TOOLS, execute_tool

REFUSAL = "抱歉，我只能回答加密货币（crypto）相关的问题，其他问题我一律不回答。"

# 明显无关话题的关键词快速通道（保守，只拦最明显的；其余交给系统提示词 + judge）
OFF_TOPIC_KEYWORDS = [
    "天气", "天气预报", "气温", "下雨", "明天穿什么",
    "菜谱", "怎么做饭", "食谱", "红烧", "炒菜",
    "讲个笑话", "脑筋急转弯", "写首诗", "写诗", "写作文",
    "推荐电影", "推荐电视剧", "推荐小说", "推荐游戏", "好看的电影",
    "健身计划", "减肥", "瘦身",
    "英语翻译", "翻译这句话", "用日语", "用法语",
    "修车", "空调维修", "水管",
]


def is_off_topic(text: str) -> bool:
    t = (text or "").lower()
    return any(k in t for k in OFF_TOPIC_KEYWORDS)


def judge(settings, user: str, answer: str):
    """返回 (satisfied: bool, reason: str)。解析失败时默认满足，避免死循环。"""
    prompt = JUDGE_TEMPLATE.format(user=user, answer=answer)
    try:
        msg = llm.chat_completion(
            settings.base_url, settings.model_id, settings.api_key,
            [{"role": "system", "content": "你是评判者，只输出一个 JSON 对象。"},
             {"role": "user", "content": prompt}],
            temperature=0.0,
        )
    except llm.LLMError:
        # 评判调用失败时不要阻断整个流程，默认放行
        return True, ""
    content = msg.get("content") or ""
    m = re.search(r"\{.*\}", content, re.DOTALL)
    if m:
        try:
            data = json.loads(m.group(0))
            return bool(data.get("satisfied", True)), str(data.get("reason", ""))
        except Exception:
            pass
    return True, ""


def _build_messages(history, user_message, feedback):
    """history: 历史 [{role, content}]（不含本次 user 消息）。"""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in history[-20:]:
        messages.append({"role": m["role"], "content": m["content"]})
    content = user_message
    if feedback:
        content = user_message + "\n\n[上一版回答未满足要求，请据此改进：]" + feedback
    messages.append({"role": "user", "content": content})
    return messages


def generate_with_tools(settings, history, user_message, feedback=None):
    """带工具调用的生成，返回最终文本回答。"""
    messages = _build_messages(history, user_message, feedback)
    for _ in range(6):
        msg = llm.chat_completion(
            settings.base_url, settings.model_id, settings.api_key,
            messages, tools=TOOLS,
        )
        tool_calls = msg.get("tool_calls")
        if not tool_calls:
            return (msg.get("content") or "").strip()

        messages.append({"role": "assistant",
                         "content": msg.get("content") or "",
                         "tool_calls": tool_calls})
        for tc in tool_calls:
            fn = tc.get("function", {})
            name = fn.get("name")
            try:
                args = json.loads(fn.get("arguments") or "{}")
            except Exception:
                args = {}
            result = execute_tool(name, args, settings)
            messages.append({
                "role": "tool",
                "tool_call_id": tc.get("id", ""),
                "content": json.dumps(result, ensure_ascii=False),
            })
    # 工具轮次用尽，强制要一句总结
    msg = llm.chat_completion(
        settings.base_url, settings.model_id, settings.api_key, messages,
    )
    return (msg.get("content") or "").strip()


def run_agent(settings, history, user_message, max_rounds=3, progress_cb=None):
    """反思循环。返回 (final_answer, rounds_used)。"""
    feedback = None
    best = ""
    rounds = max(1, int(max_rounds))
    for rnd in range(1, rounds + 1):
        if progress_cb:
            progress_cb("第 %d 轮：正在生成回答…" % rnd)
        answer = generate_with_tools(settings, history, user_message, feedback)
        best = answer
        if not answer:
            raise llm.LLMError("模型返回了空回答，请检查 base url / model id / api key 是否正确")
        if progress_cb:
            progress_cb("第 %d 轮：system 评判中…" % rnd)
        satisfied, reason = judge(settings, user_message, answer)
        if satisfied:
            return answer, rnd
        feedback = reason
        if progress_cb:
            progress_cb("第 %d 轮未通过，进入重写…" % rnd)
    return best, rounds


def test_connection(settings) -> None:
    llm.chat_completion(
        settings.base_url, settings.model_id, settings.api_key,
        [{"role": "user", "content": "请回复 ok"}],
        max_tokens=5, temperature=0.0,
    )
