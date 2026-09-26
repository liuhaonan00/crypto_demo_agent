"""OpenAI 兼容 API 客户端（base url + model id + api key）。"""
import json

import httpx


class LLMError(Exception):
    """模型调用失败时抛出，消息面向用户展示。"""


def _headers(api_key: str) -> dict:
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = "Bearer " + api_key
    return headers


def chat_completion(base_url, model_id, api_key, messages,
                    tools=None, temperature=0.3, max_tokens=None, timeout=120):
    """调用 OpenAI 兼容的 /chat/completions，返回 assistant message dict。"""
    if not base_url or not model_id:
        raise LLMError("未配置 base url 或 model id，请先在设置页填写")

    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model_id,
        "messages": messages,
        "temperature": temperature,
        "stream": False,
    }
    if tools:
        payload["tools"] = tools
    if max_tokens:
        payload["max_tokens"] = max_tokens

    try:
        resp = httpx.post(url, json=payload, headers=_headers(api_key), timeout=timeout)
    except httpx.HTTPError as exc:
        raise LLMError("请求模型失败：" + str(exc)) from exc

    if resp.status_code != 200:
        raise LLMError("模型返回错误 %s：%s" % (resp.status_code, resp.text[:300]))

    try:
        data = resp.json()
        return data["choices"][0]["message"]
    except (KeyError, IndexError, json.JSONDecodeError) as exc:
        raise LLMError("解析模型响应失败：" + str(exc)) from exc
