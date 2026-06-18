# sci-bot-mcp

AI-powered research assistant MCP server for searching academic papers and answering research questions with DOI citations.

## Basic Information

- English name: sci-bot
- Chinese name: 科研论文助手
- Hosting type: Hosted deployment
- Category: Research, Academic Search
- Source: https://github.com/lnkvv210-eng/sci-bot-mcp

## MCP Service Configuration

```json
{
  "mcpServers": {
    "sci-bot": {
      "command": "python",
      "args": ["server_stdio.py"],
      "env": {
        "DEEPSEEK_API_KEY": "your_deepseek_api_key",
        "AI_BASE_URL": "https://api.deepseek.com",
        "AI_MODEL": "deepseek-chat"
      }
    }
  }
}
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| DEEPSEEK_API_KEY | Yes | - | DeepSeek API key used by `ask_research_question`. |
| AI_BASE_URL | No | https://api.deepseek.com | OpenAI-compatible API endpoint. |
| AI_MODEL | No | deepseek-chat | Chat model name. |
| MCP_TRANSPORT | No | auto | `stdio`, `streamable-http`, or `sse`. |
| PORT | No | 8000 | Hosted HTTP port supplied by the platform. |
| MCP_PORT | No | 8000 | HTTP port fallback when `PORT` is not set. |
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

```bash
pip install -r requirements.txt
```

Run with stdio for local MCP clients:

```bash
python server_stdio.py
```

Run with SSE for direct HTTP deployment:

```bash
set MCP_TRANSPORT=sse
set PORT=8000
python server.py
```

Health check endpoints:

- `/`
- `/health`

MCP endpoints:

- `/mcp`
- `/sse`
