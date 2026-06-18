# Sci-Bot MCP Server

AI-powered research assistant. Search 200M+ academic papers and get answers with real citations.

## Features

- **search_papers**: Search 200M+ academic papers
- **ask_research_question**: Get AI answers with real paper citations
- **get_paper_details**: Get paper details by DOI

## MCP Configuration (STDIO)

```json
{
  "mcpServers": {
    "sci-bot": {
      "command": "python",
      "args": ["-m", "sci_bot_mcp.server_stdio"],
      "env": {
        "DEEPSEEK_API_KEY": "your-api-key",
        "AI_BASE_URL": "https://api.deepseek.com",
        "AI_MODEL": "deepseek-chat"
      }
    }
  }
}
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| DEEPSEEK_API_KEY | Yes | DeepSeek API Key |
| AI_BASE_URL | No | API endpoint (default: https://api.deepseek.com) |
| AI_MODEL | No | Model name (default: deepseek-chat) |

## Install from PyPI

```bash
pip install sci-bot-mcp
```

## Local Development

```bash
git clone https://github.com/lnkvv210-eng/sci-bot-mcp.git
cd sci-bot-mcp
pip install -e .
export DEEPSEEK_API_KEY="sk-your-key"
python server_stdio.py
```

## License

MIT
