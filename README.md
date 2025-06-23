# AI Shopping Companion

AI Shopping Companion is a modern web application that leverages advanced AI and real-time web search to help users find and compare products using natural language queries. It provides an interactive chat interface and a powerful product search, ranking, and recommendation system.

## Features
- **Natural Language Product Search:** Search for products using everyday language.
- **AI-Powered Recommendations:** Get product suggestions with explanations for each recommendation.
- **Conversational Shopping Agent:** Interact with an AI agent to refine searches, ask follow-up questions, and get personalized suggestions.
- **Rich Product Details:** View price, rating, reviews, availability, source, and AI-generated explanations.
- **Modern UI:** Responsive, user-friendly interface built with React (via CDN), styled for clarity and ease of use.

## Tech Stack
- **Backend:** Python, FastAPI, asyncio, aiohttp
- **Frontend:** React (via CDN), Babel, Axios, HTML/CSS
- **AI & APIs:** Integrates with Together AI (Phi-3 Mini), SerpAPI, and supports fallback logic for robust product results

## Directory Structure
```
AIShoppingCompanion/
├── main.py                  # FastAPI backend entrypoint
├── models.py                # Pydantic data models
├── services.py              # AI and product search logic
├── requirements.txt         # Python dependencies
├── pyproject.toml           # Project metadata
├── .env                     # API keys and secrets (not committed)
├── static/
│   ├── index.html           # Main HTML file
│   ├── app.js               # Main React app logic
│   ├── style.css            # App styling
│   └── components/
│       ├── ProductCard.js   # Product card component
│       ├── SearchResults.js # Product results grid
│       └── Chat.js          # Chat interface
└── ...
```

## Getting Started

### 1. Clone the repository
```sh
git clone <repo-url>
cd AIShoppingCompanion
```

### 2. Install dependencies
It is recommended to use Python 3.11+ and a virtual environment.
```sh
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set up environment variables
Create a `.env` file in the root directory with your API keys:
```
PHI3_API_KEY=your_phi3_api_key
SERPAPI_KEY=your_serpapi_key
TOGETHER_API_KEY=your_together_api_key
OPENROUTER_API_KEY=your_openrouter_api_key
```

### 4. Run the application
```sh
uvicorn main:app --reload
```
The app will be available at [http://localhost:8000](http://localhost:8000).

## Usage
- Open the app in your browser.
- Use the **Search** tab to enter product queries (e.g., "best smartphones under 20000").
- Use the **Chat** tab to interact conversationally with the AI agent. The agent can refine searches, answer follow-up questions, and provide personalized recommendations.
- Click on any product to view it on the source website.

## API Endpoints
- `GET /` — Returns the main HTML page.
- `POST /api/search` — Accepts `{ query: string }`, returns product recommendations.
- `POST /api/chat` — Accepts `{ content: string }`, returns agent response (may include products).
- `GET /api/health` — Health check endpoint.

## Customization
- **Frontend:** Modify `static/app.js`, `static/components/`, and `static/style.css` for UI/UX changes.
- **Backend Logic:** Extend or adjust `services.py` for new AI models, APIs, or business logic.
- **Models:** Update `models.py` for new data fields or API contract changes.

## Dependencies
See `requirements.txt` and `pyproject.toml` for full dependency list. Major packages include:
- fastapi
- aiohttp
- pydantic
- uvicorn
- react (CDN)
- axios (CDN)

## Environment Variables
- `PHI3_API_KEY`, `SERPAPI_KEY`, `TOGETHER_API_KEY`, `OPENROUTER_API_KEY` — Required for AI and product search APIs.

## Security Notes
- **Never commit your `.env` file or API keys to version control.**
- All API keys are loaded from environment variables.

## License
MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgements
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)
- [Together AI](https://www.together.ai/)
- [SerpAPI](https://serpapi.com/)

---

*Last updated: June 23, 2025*
