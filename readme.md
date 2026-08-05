# MCP Weather 

### An Intelligent, Multi-Region Weather Intelligence Platform Built on the Model Context Protocol

---

## Executive Summary

The **MCP Weather Agent** is a conversational, AI-driven meteorological assistant engineered atop the **Model Context Protocol (MCP)** — an emerging standard for connecting language models to external tools in a modular, composable fashion. At its core sits **GPT-4o-mini**, which serves as the system's reasoning engine, interpreting natural-language queries and autonomously determining which specialized backend is best suited to resolve them.

Rather than centralizing all logic within a single service, the platform adopts a distributed, tool-oriented design: distinct MCP servers handle distinct geographies, each optimized for the data source most appropriate to its region. This architecture allows the system to combine an official government API for the United States with an automated browser-based retrieval pipeline for Israel — all orchestrated transparently behind a single, unified conversational interface.

---

## Key Capabilities

- **Autonomous tool selection** — the language model independently determines which server, and which specific tool, should handle each incoming request.
- **Region-specific data pipelines** — U.S. queries are resolved through the National Weather Service's official REST API, while Israeli queries are resolved through automated browser interaction with a localized weather portal.
- **Bilingual query handling** — the Israeli pipeline transparently translates common English place names into Hebrew prior to executing a search.
- **Extensible by design** — new MCP servers, and therefore new regions or data domains, can be introduced with minimal structural change to the host application.
- **Transparent orchestration** — the underlying model has no knowledge of *how* a tool retrieves its data; it only knows *what* the tool can accomplish, keeping the reasoning layer cleanly decoupled from the data-access layer.

---

## System Architecture

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

Upon initialization, the host aggregates the complete inventory of tools exposed by every connected MCP server and presents them to the language model as a single, unified toolkit. When the model elects to invoke a tool, the host silently dispatches that call to whichever server implements it — a process entirely invisible to the model itself. This clean separation of concerns is what allows the system to scale gracefully: additional servers can be introduced without requiring any modification to the model's reasoning logic.

---

## Prerequisites

| Requirement | Version / Notes |
|---|---|
| Python | ≥ 3.13 |
| Package manager | `uv` (recommended) or `pip` |
| OpenAI API key | Any credential with access to `gpt-4o-mini` |
| Playwright Chromium | Required exclusively for the Israeli weather pipeline |

---

## Installation

```bash
# 1a. Install project dependencies with uv (recommended)
uv sync

# 1b. Alternatively, install with pip
pip install -e .

# 2. Provision the Playwright browser engine (required for Israel weather)
playwright install chromium
```

---

## Configuration

Within the `project-template/` directory, create a `.env` file containing your OpenAI credential:

```env
OPENAI_API_KEY=sk-...your-key-here...
```

---

## Launching the Agent

```bash
cd project-template
python host.py
```

Upon execution, the agent establishes connections to all configured MCP servers and initiates an interactive command-line session:

```
Connected to server with tools: ['get_alerts_in_USA', 'get_forecast_in_USA']
Connected to server with tools: ['open_weather_forecast_israel', 'enter_weather_forecast_city_israel', ...]

MCP Client Started!
Type your queries or 'quit' to exit.

Query:
```

Submit any natural-language question and press **Enter**. To terminate the session at any point, type `quit`.

---

## Usage Examples

### 🇺🇸 United States — National Weather Service Integration

| Sample Query | System Response |
|---|---|
| `Has the National Weather Service issued any active advisories for California?` | Queries and returns live NWS alerts for the state of `CA` |
| `Summarize the current severe weather warnings affecting Texas.` | Queries and returns live NWS alerts for the state of `TX` |
| `Could you outline the upcoming forecast trajectory for New York City?` | Resolves and returns the forecast for coordinates `40.71, -74.01` |
| `Provide a five-period outlook for the Chicago metropolitan area.` | Resolves and returns the forecast for coordinates `41.85, -87.65` |
| `Is there any indication of tornadic activity across Oklahoma at present?` | Queries and filters live NWS alerts for the state of `OK` |
| `What atmospheric conditions are expected in Miami over the coming days?` | Resolves and returns the forecast for Miami's registered coordinates |

### 🇮🇱 Israel — Automated Portal Retrieval via weather2day.co.il

| Sample Query | System Response |
|---|---|
| `Could you retrieve the latest forecast for Jerusalem?` | Launches a browser session and queries ירושלים |
| `What conditions should I expect in Tel Aviv this afternoon?` | Launches a browser session and queries תל אביב |
| `Please provide today's meteorological outlook for Haifa.` | Launches a browser session and queries חיפה |
| `How is the weather shaping up in Beer Sheva this week?` | Launches a browser session and queries באר שבע |
| `I'd like the current forecast for Eilat, please.` | Launches a browser session and queries אילת |
| `What's the temperature outlook for Netanya today?` | Translates the city name and queries נתניה |

> **Note:** The Israeli pipeline automatically translates recognized English place names into Hebrew prior to executing each search, requiring no manual transliteration from the user.

---

## Repository Structure

```
project-template/
├── host.py              # ChatHost — orchestrates OpenAI, all MCP clients, and the interactive session
├── client.py             # MCPClient — manages a single stdio connection to an MCP server
├── weather_USA.py         # MCP server: alerts and forecasts via the NWS REST API
├── weather_Israel.py       # MCP server: Israeli city forecasts via Playwright automation
└── pyproject.toml        # Project metadata and dependency declarations
```

---

## Operational Notes

- **SSL configuration (Netfree compatibility):** The project disables SSL certificate verification (`verify=False`) to ensure compatibility with Netfree-filtered network environments. Deployments outside such environments should remove the `httpx.HTTPTransport(verify=False)` declarations to restore standard certificate validation.
- **Browser visibility:** The Israeli server launches Chromium in **visible** mode (`headless=False`) by default, allowing the scraping workflow to be observed in real time — a useful behavior during development and debugging. For production or unattended deployments, set this to `headless=True`.
- **Extensibility:** Incorporating additional regions or data domains requires only the registration of a new `MCPClient` instance within the `ChatHost.__init__` method in `host.py`. Tools exposed by any newly connected server are discovered and namespaced automatically, with no further changes required elsewhere in the codebase.

---

## Suggested Future Enhancements

- Introducing caching to reduce redundant calls to the NWS API and the Israeli weather portal.
- Adding a lightweight web-based front end alongside the existing terminal interface.
- Expanding regional coverage to additional countries via new, purpose-built MCP servers.
