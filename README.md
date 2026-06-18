# sci-bot-mcp

AI-powered research assistant MCP server. Search 200M+ academic papers and get answers with real citations.

## MCP Service Configuration

```json
{
  "mcpServers": {
    "sci-bot": {
      "command": "python",
      "args": ["server_stdio.py"],
      "env": {
        "DEEPSEEK_API_KEY": "${DEEPSEEK_API_KEY}",
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
| DEEPSEEK_API_KEY | Yes | - | DeepSeek API Key |
| AI_BASE_URL | No | https://api.deepseek.com | API endpoint |
| AI_MODEL | No | deepseek-chat | Model name |

## Tools

### search_papers

Search 200M+ academic papers.

- `query` (string): Search query
- `limit` (int): Number of results, default 8

### ask_research_question

Ask a research question with AI-generated answer and citations.

- `question` (string): Research question
- `num_references` (int): Number of references, default 8

### get_paper_details

Get paper details by DOI.

- `doi` (string): Paper DOI

## Install

```bash
pip install mcp requests
```

## Run

```bash
export DEEPSEEK_API_KEY="your-api-key"
python server_stdio.py
```
