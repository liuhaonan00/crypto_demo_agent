# Crypto 智能对话机器人

一个**只回答加密货币问题**的智能对话机器人。独立 Web 应用：React + Vite 前端 + FastAPI 后端，通过 OpenAI 兼容 API 接入任意模型（DeepSeek / OpenAI / Ollama / vLLM 等）。

## 功能

- **会话管理**：新建 / 切换 / 重命名 / 删除，每个会话存为本地 JSON 文件（`data/sessions/`）
- **行情工具**（Binance，公开 REST 无需 key）：最新价、K线、EMA、RSI、MACD、资金费率、标记价格、持仓量（现货 + 合约）
- **新闻工具**（CryptoPanic）：加密新闻搜索
- **crypto-only**：只回答加密货币相关问题，其他问题一律拒绝（关键词快速过滤 + 系统提示词 + system 评判三重保障）
- **反思循环**：生成 → system 评判「是否满足用户问题」→ 不满意则带反馈重写，最多 3 轮
- **设置页**：配置 base url / model id / api key / CryptoPanic key，支持「测试连接」

## 目录结构

```
crypto_demo_agent/
├── backend/
│   ├── run.py              # 后端启动入口
│   ├── requirements.txt
│   └── app/
│       ├── main.py         # FastAPI 入口 + CORS
│       ├── config.py       # 数据目录 + settings 读写
│       ├── llm.py          # OpenAI 兼容客户端
│       ├── prompts.py      # 系统提示词 + 评判提示词
│       ├── agent.py        # 过滤 + 评判 + 反思循环
│       ├── storage.py      # session 文件读写
│       ├── routes.py       # chat(SSE)/sessions/settings 路由
│       └── tools/
│           ├── market.py   # Binance 行情
│           ├── indicators.py  # EMA/RSI/MACD
│           └── news.py     # CryptoPanic
├── frontend/               # React + Vite
│   └── src/
│       ├── App.jsx
│       ├── api.js          # fetch + SSE 客户端
│       └── components/     # Sidebar / ChatWindow / MessageBubble / SettingsModal
└── data/                   # 运行时生成（已 gitignore）
    ├── sessions/<id>.json
    └── settings.json
```

## 启动

### 1. 后端（端口 8000）

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python run.py
```

### 2. 前端（端口 5173，已配置 /api 代理到 8000）

```bash
cd frontend
npm install
npm run dev
```

打开 **http://localhost:5173**

## 配置

1. 点击左下角「⚙️ 设置」
2. 填写：
   - **Base URL**：OpenAI 兼容地址，例如 `https://api.deepseek.com/v1`
   - **Model ID**：例如 `deepseek-chat`
   - **API Key**：模型密钥
   - **CryptoPanic Key**（可选）：新闻功能需要，免费申请 cryptopanic.com/developers/api
3. 点「测试连接」验证，再「保存」

设置保存在 `data/settings.json`，会话保存在 `data/sessions/<id>.json`，均为本地明文文件，请勿提交到仓库。

## 说明与注意

- **Binance** 使用公开 REST 接口，无需 key；部分地域访问 `api.binance.com` 可能受限（HTTP 451），此时行情工具会返回错误信息。
- **反思循环** 每回合会额外调用一次模型做评判，会增加延迟和 token 消耗（最多 3 轮）；评判者与生成用同一个模型，如需独立评判模型可改 `backend/app/agent.py` 里的 `judge()`。
- **crypto-only 过滤**：明显无关话题由关键词快速拒绝（不消耗模型）；边界情况交给系统提示词 + 评判者兜底。
- 只有 base url 和 model id 必填；api key 部分本地/开源模型（如 Ollama）可为空。
