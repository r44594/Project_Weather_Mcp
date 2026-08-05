# MCP Weather Agent

An AI-powered weather assistant built on the **Model Context Protocol (MCP)** architecture. The agent uses **GPT-4o-mini** as its reasoning engine and routes queries to specialized MCP tool-servers — one for the United States and one for Israel.

---

## Architecture

```
User (terminal)
    │
    ▼
host.py  ──  ChatHost
    │         ├── OpenAI GPT-4o-mini  (reasoning + tool selection)
    │         └── MCPClient (client.py)
    │                 ├── weather_USA.py    ← NWS REST API
    │                 └── weather_Israel.py ← Playwright browser scraping
    ▼
Answer
```

The host collects all tools from every connected MCP server, exposes them to the model, and automatically dispatches tool calls to the correct server. The model never needs to know which server owns which tool.

---

## Prerequisites

| Requirement | Version |
|---|---|
| Python | ≥ 3.13 |
| Package manager | `uv` (recommended) or `pip` |
| OpenAI API key | Any key with access to `gpt-4o-mini` |
| Playwright Chromium | Required for Israel weather |

---

## Installation

```bash

# 1a. Install dependencies with uv (recommended)
uv sync

# 1b. Or with pip
pip install -e .

# 2. Install the Playwright browser (needed for Israel weather)
playwright install chromium
```

---

## Configuration

Create a `.env` file inside `project-template/`:

```env
OPENAI_API_KEY=sk-...your-key-here...
```

---

## How to Run

```bash
cd project-template
python host.py
```

The agent starts an interactive chat loop in the terminal:

```
Connected to server with tools: ['get_alerts_in_USA', 'get_forecast_in_USA']
Connected to server with tools: ['open_weather_forecast_israel', 'enter_weather_forecast_city_israel', ...]

MCP Client Started!
Type your queries or 'quit' to exit.

Query: 
```

Type your question and press **Enter**. Type `quit` to exit.

---

## Example Questions the Agent Can Answer

### 🇺🇸 United States — powered by the National Weather Service API

| Question | What the agent does |
|---|---|
| `Are there any weather alerts in California?` | Fetches active NWS alerts for state `CA` |
| `What are the current warnings in Texas?` | Fetches active NWS alerts for state `TX` |
| `What is the weather forecast for New York City?` | Looks up forecast for lat `40.71`, lon `-74.01` |
| `Give me a 5-period forecast for Chicago.` | Looks up forecast for lat `41.85`, lon `-87.65` |
| `Is there a tornado watch anywhere in Oklahoma?` | Fetches and filters alerts for state `OK` |

### 🇮🇱 Israel — powered by Playwright browser automation on weather2day.co.il

| Question | What the agent does |
|---|---|
| `What is the weather forecast in Jerusalem?` | Opens browser, searches for ירושלים |
| `Tell me the forecast for Tel Aviv.` | Opens browser, searches for תל אביב |
| `How is the weather in Haifa today?` | Opens browser, searches for חיפה |
| `What is the weather in Beer Sheva?` | Opens browser, searches for באר שבע |
| `Show me the forecast for Eilat.` | Opens browser, searches for אילת |

> **Note:** The Israel server translates common English city names to Hebrew automatically before searching.

---

## Project Structure

```
project-template/
├── host.py              # ChatHost — orchestrates OpenAI + all MCP clients + chat loop
├── client.py            # MCPClientcts to a single MCP server via stdio
├── weather_USA.py       # MCP server: US alerts & forecast via NWS REST API
├── weather_Israel.py    # MCP server: Israeli city forecast via Playwright scraping
└── pyproject.toml       # Project metadata and dependencies
```

---

## Notes

- **SSL (Netfree):** The project disables SSL verification (`verify=False`) to work behind a Netfree-filtered network. Remove the `httpx.HTTPTransport(verify=False)` lines if you are not on a filtered network.
- **Browser window:** The Israel server launches a **visible** Chromium window (`headless=False`) so you can see the scraping in action. Change to `headless=True` to run silently.
- **Adding more servers:** Register additional `MCPClient` instances in the `ChatHost.__init__` method in `host.py`. Tools are discovered and namespaced automatically.