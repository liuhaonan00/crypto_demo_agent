"""CryptoPanic 新闻工具（需要免费 API Key，配置在设置的 cryptopanic_key 字段）。"""
import httpx

CRYPTOPANIC_URL = "https://cryptopanic.com/api/v1/posts/"


def search_news(key="", query="", currencies=None, limit=10):
    if not key:
        return {"error": "未配置 CryptoPanic API Key，请在设置页填写 cryptopanic_key（免费申请：cryptopanic.com/developers/api）"}
    params = {"auth_token": key, "kind": "news", "limit": max(1, min(int(limit or 10), 50))}
    if query:
        params["search"] = query
    if currencies:
        params["currencies"] = currencies

    try:
        r = httpx.get(CRYPTOPANIC_URL, params=params, timeout=20)
    except httpx.HTTPError as exc:
        return {"error": "请求 CryptoPanic 失败：" + str(exc)}
    if r.status_code != 200:
        return {"error": "CryptoPanic 返回 %s：%s" % (r.status_code, r.text[:200])}

    try:
        data = r.json()
    except Exception as exc:
        return {"error": "解析 CryptoPanic 响应失败：" + str(exc)}

    posts = []
    for p in data.get("results", []):
        src = p.get("source")
        posts.append({
            "title": p.get("title"),
            "url": p.get("url"),
            "published_at": p.get("published_at"),
            "source": src.get("title") if isinstance(src, dict) else src,
            "currencies": [c.get("code") for c in p.get("currencies", []) if isinstance(c, dict)],
        })
    return {"count": len(posts), "posts": posts}
