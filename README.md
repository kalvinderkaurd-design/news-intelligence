# News Intel: AI-Powered Intelligence Platform

News Intel is a premium, real-time news intelligence platform that transforms raw headlines into actionable strategic insights. Built with a modern glassmorphism aesthetic and integrated with AI neural engines, it offers deep analysis and an interactive conversational interface for the latest global events.

---

## Key Features

- **Real-time Intelligence**: Automated fetching and deduplication of global news using the NewsData.io API.
- **Neural Analysis**: Instant generation of AI summaries, sentiment scoring (Positive/Neutral/Negative), and strategic insights via n8n integration.
- **Ask AI**: A dedicated chat interface where you can query your own news database. Uses Retrieval-Augmented Generation (RAG) to provide accurate, context-aware answers.
- **Premium Dashboard**: High-density 5-column grid layout with cinematic glassmorphism UI and fluid micro-animations.
- **Strategic Bookmarking**: Save critical intelligence to your personal dashboard for later review.
- **Secure Access**: Integrated Google OAuth 2.0 for seamless and secure user authentication.

---

## Tech Stack

- **Backend**: Python, Flask, SQLAlchemy, Flask-Login, Authlib.
- **Frontend**: Modern Vanilla HTML5, CSS3, JavaScript (ES6+).
- **Database**: PostgreSQL (Production) / SQLite (Development).
- **Automation**: n8n Webhook architecture for asynchronous AI processing.

---

## Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/paramjeetdhanjal/news-intellegence.git
cd news-intellegence
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file from the provided `.env.example`:
```bash
cp .env.example .env
```
Update the `.env` with your API keys:
- `NEWSDATA_API_KEY`: Get one at [newsdata.io](https://newsdata.io).
- `N8N_WEBHOOK_URL`: Your n8n analysis workflow endpoint.
- `DATABASE_URL`: Your PostgreSQL or SQLite connection string.

### 3. Launch
```bash
python main.py
```

---

## Project Structure

```text
├── app/
│   ├── models.py       # SQLAlchemy Database Models
│   ├── routes.py       # View Controllers and API Endpoints
│   ├── services.py     # AI and News Integration Logic
│   ├── static/         # CSS, JS, and Cinematic Assets
│   └── templates/      # Jinja2 Dynamic Templates
├── database/           # Local SQLite storage (Dev)
├── .env.example        # Template for environment variables
├── requirements.txt    # Project dependencies
└── main.py             # Application entry point
```

---

## Security & Optimization

- **Environment Isolation**: All sensitive keys are managed via `.env`.
- **Deduplication**: Intelligent hashing to prevent redundant news items.
- **Privacy**: No tracking of personal chat data beyond session requirements.
- **Performance**: Pagination and optimized SQL queries for high-density data handling.


