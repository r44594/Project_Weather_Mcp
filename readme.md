# MCP Weather Agent

An AI-powered weather assistant built on the **Model Context Protocol (MCP)**. The agent employs **GPT-4o-mini** as its reasoning engine and intelligently routes user queries to two specialized MCP tool-servers: one dedicated to the United States and one dedicated to Israel.

---

## Overview

The MCP Weather Agent demonstrates how a large language model can be paired with dedicated, purpose-built tool-servers to deliver accurate, real-time information without requiring the model itself to know how that information is retrieved. Rather than relying on a single monolithic integration, the system separates concerns cleanly: one server retrieves official U.S. weather data through a government API, while a second automates a browser session to extract Israeli forecast data from a local weather portal. The host application unifies both sources behind a single conversational interface, allowing the model to select the correct tool automatically based on the intent of the question.

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

The host collects the full set of tools exposed by every connected MCP server and presents them to the model as a unified toolkit. When the model selects a tool, the host transparently dispatches the call to the server that owns it. The model itself has no awareness of which server implements which capability — this separation keeps the reasoning layer decoupled from the data-access layer and makes the system straightforward to extend.

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

# 2. Install the Playwright browser (required for Israel weather)
playwright install chromium
```

---

## Configuration

Create a `.env` file inside `project-template/`:

```env
OPENAI_API_KEY=sk-...your-key-here...
```

---

## Running the Agent

```bash
cd project-template
python host.py
```

The agent launches an interactive chat loop directly in the terminal:

```
Connected to server with tools: ['get_alerts_in_USA', 'get_forecast_in_USA']
Connected to server with tools: ['open_weather_forecast_israel', 'enter_weather_forecast_city_israel', ...]

MCP Client Started!
Type your queries or 'quit' to exit.

Query:
```

Enter a question and press **Enter**. Type `quit` at any time to exit the session.

---

## Example Queries

### 🇺🇸 United States — powered by the National Weather Service API

| Question | Agent Behavior |
|---|---|
| `Are there any weather alerts in California?` | Retrieves active NWS alerts for the state of `CA` |
| `What are the current warnings in Texas?` | Retrieves active NWS alerts for the state of `TX` |
| `What is the weather forecast for New York City?` | Looks up the forecast for coordinates `40.71, -74.01` |
| `Give me a 5-period forecast for Chicago.` | Looks up the forecast for coordinates `41.85, -87.65` |
| `Is there a tornado watch anywhere in Oklahoma?` | Retrieves and filters active alerts for the state of `OK` |

### 🇮🇱 Israel — powered by Playwright browser automation on weather2day.co.il

| Question | Agent Behavior |
|---|---|
| `What is the weather forecast in Jerusalem?` | Opens a browser session and searches for ירושלים |
| `Tell me the forecast for Tel Aviv.` | Opens a browser session and searches for תל אביב |
| `How is the weather in Haifa today?` | Opens a browser session and searches for חיפה |
| `What is the weather in Beer Sheva?` | Opens a browser session and searches for באר שבע |
| `Show me the forecast for Eilat.` | Opens a browser session and searches for אילת |

> **Note:** The Israel server automatically translates common English city names into Hebrew before performing the search.

---

## Project Structure

```
project-template/
├── host.py              # ChatHost — orchestrates OpenAI, all MCP clients, and the chat loop
├── client.py             # MCPClient — connects to a single MCP server via stdio
├── weather_USA.py         # MCP server: U.S. alerts and forecasts via the NWS REST API
├── weather_Israel.py       # MCP server: Israeli city forecasts via Playwright scraping
└── pyproject.toml        # Project metadata and dependencies
```

---

## Notes

- **SSL (Netfree):** The project disables SSL verification (`verify=False`) to operate correctly behind a Netfree-filtered network. If you are not operating on a filtered network, remove the `httpx.HTTPTransport(verify=False)` lines.
- **Browser window:** The Israel server launches a **visible** Chromium window (`headless=False`) so that the scraping process can be observed directly. Set this to `headless=True` to run the browser silently in the background.
- **Extending the system:** Additional MCP servers can be registered by adding further `MCPClient` instances inside the `ChatHost.__init__` method in `host.py`. Tools exposed by new servers are discovered and namespaced automatically, with no further configuration required.
