# Finance AI Bot

The **Finance AI Bot** is an intelligent financial research assistant that provides real-time insights, analysis, and full-length reports on financial markets, stocks, and economic trends. It uses Groq's LLM API and direct web search (via DuckDuckGo) to deliver accurate, source-cited answers.

---

## ✨ Features

- **Quick Answer Mode** — Get a concise, bullet-point answer to any finance question in seconds, with live web sources.
- **Deep Research Mode** — Generate a comprehensive, 1000+ word Financial Report with executive summary, analysis, future outlook, and cited sources.
- **Source Credibility Scores** — Every response includes a color-coded confidence score (High / Medium / Low) based on the credibility of the sources used.
- **XSS-Safe Output** — All AI-generated HTML is sanitized with DOMPurify before rendering.
- **Rate Limiting** — API endpoints are protected (10 req/min for query, 5 req/min for research).
- **Dockerized** — Full Docker Compose setup for one-command deployment.

---

## 🛠️ Technologies Used

| Category       | Technologies                              |
|----------------|-------------------------------------------|
| **Backend**    | Python 3.11, Flask, Groq Python SDK, ddgs |
| **Frontend**   | React 18, Axios, DOMPurify, Nginx         |
| **AI Model**   | Groq — `llama-3.3-70b-versatile`          |
| **Search**     | DuckDuckGo (via `ddgs`)                   |
| **Infra**      | Docker, Docker Compose                    |

---

## 🚀 Getting Started

### Prerequisites

- **Node.js 18+** and **npm**
- **Python 3.11+** and **pip**
- A free **Groq API key** from [console.groq.com](https://console.groq.com)

---

### Local Development (without Docker)

#### 1. Clone and configure

```bash
git clone https://github.com/Kshitij-KS/Finance-AI-Agent.git
cd Finance-AI-Agent/finbot
```

Copy the example env file and add your Groq API key:

```bash
cp .env.example .env
# Edit .env and set: groq_api_key=your_key_here
```

#### 2. Start the Backend

```bash
cd Backend
pip install -r requirements.txt
python FinanceAI.py
# Server runs on http://localhost:5000
```

#### 3. Start the Frontend

```bash
cd ../Frontend
cp .env.example .env.local   # already has REACT_APP_BACKEND_URL=http://localhost:5000
npm install
npm start
# App runs on http://localhost:3000
```

---

### Docker Deployment (one command)

```bash
cd finbot
# Add your Groq key to .env first
docker compose up --build
# Frontend → http://localhost:80
# Backend  → http://localhost:5000
```

---

## 🌐 Free Cloud Deployment

| Service | Platform | Notes |
|---|---|---|
| **Backend** | [Render.com](https://render.com) | Free tier, cold starts after idle |
| **Frontend** | [Vercel.com](https://vercel.com) | Free tier, always-on CDN |

**Steps:**
1. Push `Backend/` to GitHub → Deploy on Render as Python Web Service
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn -w 2 -b 0.0.0.0:$PORT --timeout 120 FinanceAI:app`
   - Env var: `groq_api_key = <your key>` and `FRONTEND_URL = https://your-app.vercel.app`
2. Push `Frontend/` to GitHub → Deploy on Vercel (auto-detects CRA)
   - Env var: `REACT_APP_BACKEND_URL = https://your-backend.onrender.com`

---

## 📁 Project Structure

```
finbot/
├── Backend/
│   ├── FinanceAI.py          # Flask API — search + LLM logic
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile
├── Frontend/
│   ├── src/
│   │   ├── App.js            # Main React component
│   │   └── App.css           # All styles
│   ├── .env.example
│   └── Dockerfile            # Multi-stage Nginx build
├── compose.yaml              # Docker Compose
└── .env                      # API keys (gitignored)
```

---

## ⚙️ Environment Variables

| Variable | Location | Description |
|---|---|---|
| `groq_api_key` | Backend `.env` | Your Groq API key |
| `FRONTEND_URL` | Backend `.env` | CORS allowed origin (production) |
| `REACT_APP_BACKEND_URL` | Frontend `.env.local` | Backend URL for API calls |
| `FLASK_DEBUG` | Backend `.env` | Set `true` for dev debug mode |

---

## 🔒 Security Notes

- API keys are loaded from `.env` and never exposed to the frontend.
- CORS is restricted to `localhost:3000` (dev) and your configured `FRONTEND_URL` (prod).
- All HTML rendered in the browser is sanitized with **DOMPurify**.
- Rate limiting prevents API abuse (10 req/min quick, 5 req/min research).

---

## 🙏 Acknowledgments

- **Groq** — Ultra-fast LLM inference
- **DuckDuckGo (ddgs)** — Privacy-respecting web search
- **React** — Frontend framework

---

## 📬 Contact

**Email**: kshitijsingh2727@gmail.com  
**GitHub**: [Kshitij-KS](https://github.com/Kshitij-KS)  
**Project**: [Finance-AI-Agent](https://github.com/Kshitij-KS/Finance-AI-Agent/tree/main)
