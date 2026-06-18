# sci-bot-mcp

AI-powered research assistant MCP server for searching academic papers and answering research questions with DOI citations.

## Basic Information

- English name: sci-bot
- Chinese name: 科研论文助手
- Hosting type: Hosted deployment
- Supported deploy transport: sse
- Category: Research, Academic Search
- Source: https://github.com/lnkvv210-eng/sci-bot-mcp

## MCP Service Configuration

Use SSE for ModelScope hosted deployment. The service starts with this exact command:

python -m sci_bot_mcp.server

The MCP endpoint is exposed at `/sse`.

```json
{
  "mcpServers": {
    "sci-bot": {
      "command": "python -m sci_bot_mcp.server",
      "env": {
        "DEEPSEEK_API_KEY": "your_deepseek_api_key",
        "AI_BASE_URL": "https://api.deepseek.com",
        "AI_MODEL": "deepseek-chat",
        "MCP_TRANSPORT": "sse"
      }
    }
  }
}
```

Hosted start command:

```
python -m sci_bot_mcp.server
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| DEEPSEEK_API_KEY | Yes | - | DeepSeek API key used by `ask_research_question`. |
| AI_BASE_URL | No | https://api.deepseek.com | OpenAI-compatible API endpoint. |
| AI_MODEL | No | deepseek-chat | Chat model name. |
| MCP_TRANSPORT | No | sse | Hosted transport. Use `sse` for ModelScope deployment. |
| PORT | No | 8000 | HTTP port supplied by the platform. |
| HOST | No | 0.0.0.0 | HTTP bind host. |

## Tools

### search_papers

Search academic papers through CrossRef.

- `query` (string): search query.
- `limit` (integer): number of results, default 8, max 20.

### ask_research_question

Search papers and synthesize an answer with DOI references.

- `question` (string): research question.
- `num_references` (integer): number of reference papers, default 8, max 15.

### get_paper_details

Get detailed paper metadata by DOI.

- `doi` (string): paper DOI.

## Run Locally

Install dependencies:

```
pip install -r requirements.txt
```

Run as hosted SSE service:

```
MCP_TRANSPORT=sse PORT=8000 python -m sci_bot_mcp.server
```

Health check:

- `/`
- `/health`

MCP endpoint:

- `/sse`

Run with stdio for local MCP clients:

```
python server_stdio.py
```

After package installation, run the console entrypoint:

```
sci-bot-mcp
```
